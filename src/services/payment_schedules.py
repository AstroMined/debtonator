"""
Payment schedule service implementation.

This module provides a service for managing payment schedules.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.payment_schedules import PaymentSchedule
from src.repositories.accounts import AccountRepository
from src.repositories.liabilities import LiabilityRepository
from src.repositories.payment_schedules import PaymentScheduleRepository
from src.schemas.payment_schedules import PaymentScheduleCreate
from src.schemas.payments import PaymentCreate, PaymentSourceCreate
from src.services.base import BaseService
from src.services.feature_flags import FeatureFlagService
from src.services.payments import PaymentService
from src.utils.datetime_utils import ensure_utc, utc_now


class PaymentScheduleService(BaseService):
    """
    Service for managing payment schedules.

    This service provides methods for creating, retrieving, and processing
    payment schedules. It follows the repository pattern for data access
    and inherits from BaseService for standardized repository management.
    """

    def __init__(
        self,
        session: AsyncSession,
        feature_flag_service: Optional[FeatureFlagService] = None,
        config_provider: Optional[any] = None,
    ):
        """
        Initialize payment schedule service with database session and optional dependencies.

        Args:
            session (AsyncSession): SQLAlchemy async session
            feature_flag_service (Optional[FeatureFlagService]): Feature flag service for feature toggling
            config_provider (Optional[Any]): Configuration provider
        """
        super().__init__(session, feature_flag_service, config_provider)
        self.payment_service = PaymentService(
            session, feature_flag_service, config_provider
        )

    async def create_schedule(
        self, schedule_data: PaymentScheduleCreate
    ) -> PaymentSchedule:
        """
        Create a new payment schedule.

        Args:
            schedule_data (PaymentScheduleCreate): Payment schedule data

        Returns:
            PaymentSchedule: Created payment schedule

        Raises:
            ValueError: If liability or account does not exist, or liability is already paid
        """
        # Get repositories
        liability_repo = await self._get_repository(LiabilityRepository)
        account_repo = await self._get_repository(AccountRepository)
        schedule_repo = await self._get_repository(PaymentScheduleRepository)

        # Verify liability exists and is not paid
        liability = await liability_repo.get(schedule_data.liability_id)
        if not liability:
            raise ValueError("Liability not found")
        if liability.paid:
            raise ValueError("Cannot schedule payment for already paid liability")

        # Verify account exists
        account = await account_repo.get(schedule_data.account_id)
        if not account:
            raise ValueError("Account not found")

        # Create schedule
        schedule_dict = {
            "liability_id": schedule_data.liability_id,
            "account_id": schedule_data.account_id,
            "scheduled_date": schedule_data.scheduled_date,
            "amount": Decimal(str(schedule_data.amount)),
            "description": schedule_data.description,
            "auto_process": schedule_data.auto_process,
        }

        return await schedule_repo.create(schedule_dict)

    async def get_schedule(self, schedule_id: int) -> Optional[PaymentSchedule]:
        """
        Get a payment schedule by ID.

        Args:
            schedule_id (int): Payment schedule ID

        Returns:
            Optional[PaymentSchedule]: Payment schedule or None if not found
        """
        schedule_repo = await self._get_repository(PaymentScheduleRepository)
        return await schedule_repo.get(schedule_id)

    async def get_schedules_by_date_range(
        self, start_date: datetime, end_date: datetime, include_processed: bool = False
    ) -> List[PaymentSchedule]:
        """
        Get payment schedules within a date range.

        Args:
            start_date (datetime): Start date (inclusive)
            end_date (datetime): End date (inclusive)
            include_processed (bool): Whether to include processed schedules

        Returns:
            List[PaymentSchedule]: Payment schedules within date range
        """
        schedule_repo = await self._get_repository(PaymentScheduleRepository)

        # Ensure UTC timezone awareness for datetime parameters
        start_date = ensure_utc(start_date)
        end_date = ensure_utc(end_date)

        # Get schedules by date range
        schedules = await schedule_repo.get_by_date_range(start_date, end_date)

        # Filter by processed status if needed
        if not include_processed:
            schedules = [s for s in schedules if not s.processed]

        return schedules

    async def get_schedules_by_liability(
        self, liability_id: int, include_processed: bool = False
    ) -> List[PaymentSchedule]:
        """
        Get payment schedules for a specific liability.

        Args:
            liability_id (int): Liability ID
            include_processed (bool): Whether to include processed schedules

        Returns:
            List[PaymentSchedule]: Payment schedules for the liability
        """
        schedule_repo = await self._get_repository(PaymentScheduleRepository)

        # Get schedules by liability
        schedules = await schedule_repo.get_by_liability(liability_id)

        # Filter by processed status if needed
        if not include_processed:
            schedules = [s for s in schedules if not s.processed]

        return schedules

    async def process_schedule(self, schedule_id: int) -> PaymentSchedule:
        """
        Process a payment schedule, creating the actual payment.

        Args:
            schedule_id (int): Payment schedule ID

        Returns:
            PaymentSchedule: Processed payment schedule

        Raises:
            ValueError: If schedule not found or already processed
        """
        schedule_repo = await self._get_repository(PaymentScheduleRepository)

        # Get schedule
        schedule = await schedule_repo.get(schedule_id)
        if not schedule:
            raise ValueError("Schedule not found")

        if schedule.processed:
            raise ValueError("Schedule already processed")

        # Create the payment using PaymentCreate schema
        payment_data = PaymentCreate(
            liability_id=schedule.liability_id,
            amount=schedule.amount,
            payment_date=schedule.scheduled_date,
            description=schedule.description or "Scheduled payment",
            category="Scheduled Payment",  # Default category for scheduled payments
            sources=[
                PaymentSourceCreate(
                    account_id=schedule.account_id, amount=schedule.amount
                )
            ],
        )
        await self.payment_service.create_payment(payment_data)

        # Mark schedule as processed using repository method
        return await schedule_repo.mark_as_processed(schedule_id)

    async def delete_schedule(self, schedule_id: int) -> bool:
        """
        Delete a payment schedule.

        Args:
            schedule_id (int): Payment schedule ID

        Returns:
            bool: True if deleted successfully, False otherwise

        Raises:
            ValueError: If schedule is already processed
        """
        schedule_repo = await self._get_repository(PaymentScheduleRepository)

        # Get schedule
        schedule = await schedule_repo.get(schedule_id)
        if not schedule:
            return False

        if schedule.processed:
            raise ValueError("Cannot delete processed schedule")

        # Cancel/delete schedule using repository method
        return await schedule_repo.cancel_schedule(schedule_id)

    async def process_due_schedules(self) -> List[PaymentSchedule]:
        """
        Process all auto-process schedules that are due today.

        Returns:
            List[PaymentSchedule]: List of processed payment schedules
        """
        schedule_repo = await self._get_repository(PaymentScheduleRepository)

        # Get current date
        today = utc_now()

        # Get auto-process schedules for today
        date_range = (today, today)
        due_schedules = await schedule_repo.get_auto_process_schedules(date_range)

        # Process each schedule
        processed_schedules = []
        for schedule in due_schedules:
            try:
                processed_schedule = await self.process_schedule(schedule.id)
                processed_schedules.append(processed_schedule)
            except Exception as e:
                # Log error but continue processing other schedules
                print(f"Error processing schedule {schedule.id}: {str(e)}")

        return processed_schedules

    async def get_upcoming_schedules(
        self, days: int = 30, account_id: Optional[int] = None
    ) -> List[PaymentSchedule]:
        """
        Get upcoming payment schedules for the next specified number of days.

        Args:
            days (int): Number of days to look ahead (default: 30)
            account_id (Optional[int]): Filter by specific account

        Returns:
            List[PaymentSchedule]: List of upcoming payment schedules
        """
        schedule_repo = await self._get_repository(PaymentScheduleRepository)
        return await schedule_repo.get_upcoming_schedules(days, account_id)

    async def find_overdue_schedules(
        self, account_id: Optional[int] = None
    ) -> List[PaymentSchedule]:
        """
        Find overdue payment schedules (scheduled date in the past, not processed).

        Args:
            account_id (Optional[int]): Filter by specific account

        Returns:
            List[PaymentSchedule]: List of overdue payment schedules
        """
        schedule_repo = await self._get_repository(PaymentScheduleRepository)
        return await schedule_repo.find_overdue_schedules(account_id)

    async def get_total_scheduled_payments(
        self,
        start_date: datetime,
        end_date: datetime,
        account_id: Optional[int] = None,
    ) -> float:
        """
        Get total amount of scheduled payments within a date range.

        Args:
            start_date (datetime): Start date (inclusive)
            end_date (datetime): End date (inclusive)
            account_id (Optional[int]): Filter by specific account

        Returns:
            float: Total amount of scheduled payments
        """
        # Ensure UTC timezone awareness for datetime parameters
        start_date = ensure_utc(start_date)
        end_date = ensure_utc(end_date)

        schedule_repo = await self._get_repository(PaymentScheduleRepository)
        return await schedule_repo.get_total_scheduled_payments(
            start_date, end_date, account_id
        )

    async def get_schedules_with_relationships(
        self, date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> List[PaymentSchedule]:
        """
        Get payment schedules with all relationships loaded.

        Args:
            date_range (Optional[Tuple[datetime, datetime]]): Date range filter (start_date, end_date)

        Returns:
            List[PaymentSchedule]: Payment schedules with relationships loaded
        """
        schedule_repo = await self._get_repository(PaymentScheduleRepository)
        return await schedule_repo.get_schedules_with_relationships(date_range)
