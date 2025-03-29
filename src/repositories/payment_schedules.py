"""
Payment schedule repository implementation.

This module provides a repository for PaymentSchedule model CRUD operations and
specialized payment schedule-related queries.
"""

from datetime import datetime
from typing import List, Optional, Tuple

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models.payment_schedules import PaymentSchedule
from src.repositories.base_repository import BaseRepository
from src.utils.datetime_utils import safe_end_date, utc_now


class PaymentScheduleRepository(BaseRepository[PaymentSchedule, int]):
    """
    Repository for PaymentSchedule model operations.

    This repository handles CRUD operations for payment schedules and provides
    specialized queries for payment schedule-related functionality.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session (AsyncSession): SQLAlchemy async session
        """
        super().__init__(session, PaymentSchedule)

    async def get_by_account(self, account_id: int) -> List[PaymentSchedule]:
        """
        Get payment schedules for a specific account.

        Args:
            account_id (int): Account ID

        Returns:
            List[PaymentSchedule]: List of payment schedules for the account
        """
        result = await self.session.execute(
            select(PaymentSchedule)
            .where(PaymentSchedule.account_id == account_id)
            .order_by(PaymentSchedule.scheduled_date)
        )
        return result.scalars().all()

    async def get_by_liability(self, liability_id: int) -> List[PaymentSchedule]:
        """
        Get payment schedules for a specific liability.

        Args:
            liability_id (int): Liability ID

        Returns:
            List[PaymentSchedule]: List of payment schedules for the liability
        """
        result = await self.session.execute(
            select(PaymentSchedule)
            .where(PaymentSchedule.liability_id == liability_id)
            .order_by(PaymentSchedule.scheduled_date)
        )
        return result.scalars().all()

    async def get_with_account(self, schedule_id: int) -> Optional[PaymentSchedule]:
        """
        Get payment schedule with account relationship loaded.

        Args:
            schedule_id (int): Payment schedule ID

        Returns:
            Optional[PaymentSchedule]: Payment schedule with account relationship or None
        """
        result = await self.session.execute(
            select(PaymentSchedule)
            .options(joinedload(PaymentSchedule.account))
            .where(PaymentSchedule.id == schedule_id)
        )
        return result.scalars().first()

    async def get_with_liability(self, schedule_id: int) -> Optional[PaymentSchedule]:
        """
        Get payment schedule with liability relationship loaded.

        Args:
            schedule_id (int): Payment schedule ID

        Returns:
            Optional[PaymentSchedule]: Payment schedule with liability relationship or None
        """
        result = await self.session.execute(
            select(PaymentSchedule)
            .options(joinedload(PaymentSchedule.liability))
            .where(PaymentSchedule.id == schedule_id)
        )
        return result.scalars().first()

    async def get_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[PaymentSchedule]:
        """
        Get payment schedules within a date range.

        Args:
            start_date (datetime): Start date (inclusive)
            end_date (datetime): End date (inclusive)

        Returns:
            List[PaymentSchedule]: Payment schedules within the date range
        """
        result = await self.session.execute(
            select(PaymentSchedule)
            .where(
                and_(
                    PaymentSchedule.scheduled_date >= start_date,
                    PaymentSchedule.scheduled_date <= end_date,
                )
            )
            .order_by(PaymentSchedule.scheduled_date)
        )
        return result.scalars().all()

    async def get_pending_schedules(self) -> List[PaymentSchedule]:
        """
        Get pending payment schedules (not processed).

        Returns:
            List[PaymentSchedule]: List of pending payment schedules
        """
        result = await self.session.execute(
            select(PaymentSchedule)
            .where(PaymentSchedule.processed == False)
            .order_by(PaymentSchedule.scheduled_date)
        )
        return result.scalars().all()

    async def get_processed_schedules(self) -> List[PaymentSchedule]:
        """
        Get processed payment schedules.

        Returns:
            List[PaymentSchedule]: List of processed payment schedules
        """
        result = await self.session.execute(
            select(PaymentSchedule)
            .where(PaymentSchedule.processed == True)
            .order_by(desc(PaymentSchedule.processed_date))
        )
        return result.scalars().all()

    async def mark_as_processed(
        self, schedule_id: int, processed_date: Optional[datetime] = None
    ) -> Optional[PaymentSchedule]:
        """
        Mark a payment schedule as processed.

        Args:
            schedule_id (int): Payment schedule ID
            processed_date (datetime, optional): Processing date, defaults to current UTC time

        Returns:
            Optional[PaymentSchedule]: Updated payment schedule or None if not found
        """
        schedule = await self.get(schedule_id)
        if not schedule:
            return None

        # Use provided processed_date or current UTC time
        current_time = processed_date or utc_now()

        update_data = {
            "processed": True,
            "processed_date": current_time,
        }

        return await self.update(schedule_id, update_data)

    async def get_schedules_with_relationships(
        self, date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> List[PaymentSchedule]:
        """
        Get payment schedules with all relationships loaded.

        Args:
            date_range (Tuple[datetime, datetime], optional): Date range filter (start_date, end_date)

        Returns:
            List[PaymentSchedule]: Payment schedules with all relationships loaded
        """
        query = (
            select(PaymentSchedule)
            .options(
                joinedload(PaymentSchedule.account),
                joinedload(PaymentSchedule.liability),
            )
            .order_by(PaymentSchedule.scheduled_date)
        )

        if date_range:
            start_date, end_date = date_range
            query = query.where(
                and_(
                    PaymentSchedule.scheduled_date >= start_date,
                    PaymentSchedule.scheduled_date <= end_date,
                )
            )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_upcoming_schedules(
        self, days: int = 30, account_id: Optional[int] = None
    ) -> List[PaymentSchedule]:
        """
        Get upcoming payment schedules for the next specified number of days.

        Args:
            days (int, optional): Number of days to look ahead, defaults to 30
            account_id (int, optional): Filter by specific account

        Returns:
            List[PaymentSchedule]: List of upcoming payment schedules
        """
        today = utc_now()
        end_date = safe_end_date(today, days)

        query = (
            select(PaymentSchedule)
            .options(
                joinedload(PaymentSchedule.account),
                joinedload(PaymentSchedule.liability),
            )
            .where(
                and_(
                    PaymentSchedule.scheduled_date >= today,
                    PaymentSchedule.scheduled_date <= end_date,
                    PaymentSchedule.processed == False,
                )
            )
            .order_by(PaymentSchedule.scheduled_date)
        )

        if account_id is not None:
            query = query.where(PaymentSchedule.account_id == account_id)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def find_overdue_schedules(
        self, account_id: Optional[int] = None
    ) -> List[PaymentSchedule]:
        """
        Find overdue payment schedules (scheduled date in the past, not processed).

        Args:
            account_id (int, optional): Filter by specific account

        Returns:
            List[PaymentSchedule]: List of overdue payment schedules
        """
        today = utc_now()

        query = (
            select(PaymentSchedule)
            .options(
                joinedload(PaymentSchedule.account),
                joinedload(PaymentSchedule.liability),
            )
            .where(
                and_(
                    PaymentSchedule.scheduled_date < today,
                    PaymentSchedule.processed == False,
                )
            )
            .order_by(PaymentSchedule.scheduled_date)
        )

        if account_id is not None:
            query = query.where(PaymentSchedule.account_id == account_id)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_auto_process_schedules(
        self, date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> List[PaymentSchedule]:
        """
        Get payment schedules set for auto-processing.

        Args:
            date_range (Tuple[datetime, datetime], optional): Date range filter (start_date, end_date)

        Returns:
            List[PaymentSchedule]: Payment schedules set for auto-processing
        """
        query = (
            select(PaymentSchedule)
            .options(
                joinedload(PaymentSchedule.account),
                joinedload(PaymentSchedule.liability),
            )
            .where(
                and_(
                    PaymentSchedule.auto_process == True,
                    PaymentSchedule.processed == False,
                )
            )
            .order_by(PaymentSchedule.scheduled_date)
        )

        if date_range:
            start_date, end_date = date_range
            query = query.where(
                and_(
                    PaymentSchedule.scheduled_date >= start_date,
                    PaymentSchedule.scheduled_date <= end_date,
                )
            )

        result = await self.session.execute(query)
        return result.scalars().all()

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
            account_id (int, optional): Filter by specific account

        Returns:
            float: Total amount of scheduled payments
        """
        query = select(func.sum(PaymentSchedule.amount)).where(
            and_(
                PaymentSchedule.scheduled_date >= start_date,
                PaymentSchedule.scheduled_date <= end_date,
            )
        )

        if account_id is not None:
            query = query.where(PaymentSchedule.account_id == account_id)

        result = await self.session.execute(query)
        total = result.scalar_one()
        return float(total) if total is not None else 0.0

    async def cancel_schedule(self, schedule_id: int) -> bool:
        """
        Cancel a payment schedule by deleting it.

        Args:
            schedule_id (int): Payment schedule ID

        Returns:
            bool: True if deleted successfully, False otherwise
        """
        return await self.delete(schedule_id)
