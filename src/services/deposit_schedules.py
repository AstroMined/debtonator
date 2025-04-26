from datetime import date, datetime
from typing import Any, List, Optional, Tuple

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.deposit_schedules import DepositSchedule
from src.models.income import Income
from src.repositories.deposit_schedules import DepositScheduleRepository
from src.schemas.deposit_schedules import DepositScheduleCreate, DepositScheduleUpdate
from src.services.base import BaseService
from src.services.feature_flags import FeatureFlagService
from src.utils.datetime_utils import (
    ensure_utc,
    naive_end_of_day,
    naive_start_of_day,
    utc_now,
)


class DepositScheduleService(BaseService):
    """
    Service for deposit schedule operations.

    This service handles deposit schedule management including creating, updating,
    and retrieving deposit schedules with proper validation.
    """

    def __init__(
        self,
        session: AsyncSession,
        feature_flag_service: Optional[FeatureFlagService] = None,
        config_provider: Optional[Any] = None,
    ):
        """
        Initialize deposit schedule service with required dependencies.

        Args:
            session (AsyncSession): SQLAlchemy async session
            feature_flag_service (Optional[FeatureFlagService]): Feature flag service
            config_provider (Optional[Any]): Configuration provider
        """
        super().__init__(session, feature_flag_service, config_provider)

    async def create_deposit_schedule(
        self, schedule: DepositScheduleCreate
    ) -> Tuple[bool, Optional[str], Optional[DepositSchedule]]:
        """
        Create a new deposit schedule.

        Args:
            schedule (DepositScheduleCreate): Deposit schedule data

        Returns:
            Tuple[bool, Optional[str], Optional[DepositSchedule]]:
                Success flag, error message (if any), and created schedule
        """
        try:
            # Get repositories
            deposit_repo = await self._get_repository(DepositScheduleRepository)

            # Verify income exists (repository will validate relationships)
            # For simplicity, we'll use a direct get operation for these checks
            income = await self._session.get(Income, schedule.income_id)
            if not income:
                return False, "Income not found", None

            # Verify account exists
            account = await self._session.get(Account, schedule.account_id)
            if not account:
                return False, "Account not found", None

            # Verify amount doesn't exceed income amount
            if schedule.amount > income.amount:
                return False, "Schedule amount cannot exceed income amount", None

            # Create deposit schedule using repository
            schedule_data = schedule.model_dump()
            db_schedule = await deposit_repo.create(schedule_data)

            return True, None, db_schedule
        except Exception as e:
            return False, str(e), None

    async def get_deposit_schedule(self, schedule_id: int) -> Optional[DepositSchedule]:
        """
        Get a deposit schedule by ID.

        Args:
            schedule_id (int): Deposit schedule ID

        Returns:
            Optional[DepositSchedule]: Deposit schedule or None if not found
        """
        deposit_repo = await self._get_repository(DepositScheduleRepository)
        return await deposit_repo.get(schedule_id)

    async def update_deposit_schedule(
        self, schedule_id: int, schedule_update: DepositScheduleUpdate
    ) -> Tuple[bool, Optional[str], Optional[DepositSchedule]]:
        """
        Update a deposit schedule.

        Args:
            schedule_id (int): Deposit schedule ID
            schedule_update (DepositScheduleUpdate): Updated deposit schedule data

        Returns:
            Tuple[bool, Optional[str], Optional[DepositSchedule]]:
                Success flag, error message (if any), and updated schedule
        """
        try:
            # Get repositories
            deposit_repo = await self._get_repository(DepositScheduleRepository)

            # Check if schedule exists
            db_schedule = await deposit_repo.get(schedule_id)
            if not db_schedule:
                return False, "Deposit schedule not found", None

            # If amount is updated, verify it doesn't exceed income amount
            if schedule_update.amount is not None:
                income = await self._session.get(Income, db_schedule.income_id)
                if schedule_update.amount > income.amount:
                    return False, "Schedule amount cannot exceed income amount", None

            # Update through repository
            update_data = schedule_update.model_dump(exclude_unset=True)
            updated_schedule = await deposit_repo.update(schedule_id, update_data)

            return True, None, updated_schedule
        except Exception as e:
            return False, str(e), None

    async def delete_deposit_schedule(
        self, schedule_id: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Delete a deposit schedule.

        Args:
            schedule_id (int): Deposit schedule ID

        Returns:
            Tuple[bool, Optional[str]]: Success flag and error message (if any)
        """
        try:
            # Get repository
            deposit_repo = await self._get_repository(DepositScheduleRepository)

            # Check if schedule exists
            db_schedule = await deposit_repo.get(schedule_id)
            if not db_schedule:
                return False, "Deposit schedule not found"

            # Delete through repository
            result = await deposit_repo.delete(schedule_id)

            # Return success based on deletion result
            if result:
                return True, None
            else:
                return False, "Failed to delete deposit schedule"
        except Exception as e:
            return False, str(e)

    async def list_deposit_schedules(
        self,
        income_id: Optional[int] = None,
        account_id: Optional[int] = None,
        status: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
    ) -> List[DepositSchedule]:
        """
        List deposit schedules with optional filters.

        Args:
            income_id (Optional[int]): Filter by income ID
            account_id (Optional[int]): Filter by account ID
            status (Optional[str]): Filter by status
            from_date (Optional[date]): Start date for date range filter
            to_date (Optional[date]): End date for date range filter

        Returns:
            List[DepositSchedule]: List of deposit schedules matching filters
        """
        # Get repository
        deposit_repo = await self._get_repository(DepositScheduleRepository)

        # Setup date range if provided
        date_range = None
        if from_date is not None and to_date is not None:
            # Convert dates to datetime if needed
            from_datetime = datetime.combine(from_date, datetime.min.time())
            to_datetime = datetime.combine(to_date, datetime.max.time())

            # Ensure UTC timezone awareness
            from_datetime = ensure_utc(from_datetime)
            to_datetime = ensure_utc(to_datetime)

            date_range = (from_datetime, to_datetime)

        # Handle different filter combinations
        if account_id is not None:
            # If filtering by account
            if status == "pending":
                return await deposit_repo.get_pending_schedules()
            schedules = await deposit_repo.get_by_account(account_id)
        elif income_id is not None:
            # If filtering by income
            schedules = await deposit_repo.get_by_income(income_id)
        elif date_range:
            # If filtering by date range
            schedules = await deposit_repo.get_by_date_range(*date_range)
        elif status == "pending":
            # If filtering by pending status
            schedules = await deposit_repo.get_pending_schedules()
        elif status == "processed":
            # If filtering by processed status
            schedules = await deposit_repo.get_processed_schedules()
        else:
            # Get all schedules
            schedules = await deposit_repo.get_all()

        return schedules

    async def get_pending_deposits(
        self, account_id: Optional[int] = None
    ) -> List[DepositSchedule]:
        """
        Get all pending deposits, optionally filtered by account.

        Args:
            account_id (Optional[int]): Filter by account ID

        Returns:
            List[DepositSchedule]: List of pending deposit schedules
        """
        # Get repository
        deposit_repo = await self._get_repository(DepositScheduleRepository)

        # Get upcoming schedules for the next 30 days
        return await deposit_repo.get_upcoming_schedules(days=30, account_id=account_id)
