"""
Deposit schedule repository implementation.

This module provides a repository for DepositSchedule model CRUD operations and
specialized deposit schedule-related queries.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.models.deposit_schedules import DepositSchedule
from src.models.income import Income
from src.models.accounts import Account
from src.repositories.base import BaseRepository


class DepositScheduleRepository(BaseRepository[DepositSchedule, int]):
    """
    Repository for DepositSchedule model operations.

    This repository handles CRUD operations for deposit schedules and provides
    specialized queries for deposit schedule-related functionality.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session (AsyncSession): SQLAlchemy async session
        """
        super().__init__(session, DepositSchedule)

    async def get_by_account(self, account_id: int) -> List[DepositSchedule]:
        """
        Get deposit schedules for a specific account.

        Args:
            account_id (int): Account ID

        Returns:
            List[DepositSchedule]: List of deposit schedules for the account
        """
        result = await self.session.execute(
            select(DepositSchedule)
            .where(DepositSchedule.account_id == account_id)
            .order_by(DepositSchedule.schedule_date)
        )
        return result.scalars().all()

    async def get_by_income(self, income_id: int) -> List[DepositSchedule]:
        """
        Get deposit schedules for a specific income.

        Args:
            income_id (int): Income ID

        Returns:
            List[DepositSchedule]: List of deposit schedules for the income
        """
        result = await self.session.execute(
            select(DepositSchedule)
            .where(DepositSchedule.income_id == income_id)
            .order_by(DepositSchedule.schedule_date)
        )
        return result.scalars().all()

    async def get_with_account(self, schedule_id: int) -> Optional[DepositSchedule]:
        """
        Get deposit schedule with account relationship loaded.

        Args:
            schedule_id (int): Deposit schedule ID

        Returns:
            Optional[DepositSchedule]: Deposit schedule with account relationship or None
        """
        result = await self.session.execute(
            select(DepositSchedule)
            .options(joinedload(DepositSchedule.account))
            .where(DepositSchedule.id == schedule_id)
        )
        return result.scalars().first()

    async def get_with_income(self, schedule_id: int) -> Optional[DepositSchedule]:
        """
        Get deposit schedule with income relationship loaded.

        Args:
            schedule_id (int): Deposit schedule ID

        Returns:
            Optional[DepositSchedule]: Deposit schedule with income relationship or None
        """
        result = await self.session.execute(
            select(DepositSchedule)
            .options(joinedload(DepositSchedule.income))
            .where(DepositSchedule.id == schedule_id)
        )
        return result.scalars().first()

    async def get_by_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> List[DepositSchedule]:
        """
        Get deposit schedules within a date range.

        Args:
            start_date (datetime): Start date (inclusive)
            end_date (datetime): End date (inclusive)

        Returns:
            List[DepositSchedule]: Deposit schedules within the date range
        """
        result = await self.session.execute(
            select(DepositSchedule)
            .where(
                and_(
                    DepositSchedule.schedule_date >= start_date,
                    DepositSchedule.schedule_date <= end_date,
                )
            )
            .order_by(DepositSchedule.schedule_date)
        )
        return result.scalars().all()

    async def get_pending_schedules(self) -> List[DepositSchedule]:
        """
        Get pending deposit schedules (status=pending).

        Returns:
            List[DepositSchedule]: List of pending deposit schedules
        """
        result = await self.session.execute(
            select(DepositSchedule)
            .where(DepositSchedule.status == "pending")
            .order_by(DepositSchedule.schedule_date)
        )
        return result.scalars().all()

    async def get_processed_schedules(self) -> List[DepositSchedule]:
        """
        Get processed deposit schedules (status=processed).

        Returns:
            List[DepositSchedule]: List of processed deposit schedules
        """
        result = await self.session.execute(
            select(DepositSchedule)
            .where(DepositSchedule.status == "processed")
            .order_by(desc(DepositSchedule.schedule_date))
        )
        return result.scalars().all()

    async def mark_as_processed(
        self, schedule_id: int
    ) -> Optional[DepositSchedule]:
        """
        Mark a deposit schedule as processed.

        Args:
            schedule_id (int): Deposit schedule ID

        Returns:
            Optional[DepositSchedule]: Updated deposit schedule or None if not found
        """
        schedule = await self.get(schedule_id)
        if not schedule:
            return None

        update_data = {
            "status": "processed",
        }

        return await self.update(schedule_id, update_data)

    async def get_schedules_with_relationships(
        self, date_range: Optional[Tuple[datetime, datetime]] = None
    ) -> List[DepositSchedule]:
        """
        Get deposit schedules with all relationships loaded.

        Args:
            date_range (Tuple[datetime, datetime], optional): Date range filter (start_date, end_date)

        Returns:
            List[DepositSchedule]: Deposit schedules with all relationships loaded
        """
        query = (
            select(DepositSchedule)
            .options(
                joinedload(DepositSchedule.account),
                joinedload(DepositSchedule.income),
            )
            .order_by(DepositSchedule.schedule_date)
        )

        if date_range:
            start_date, end_date = date_range
            query = query.where(
                and_(
                    DepositSchedule.schedule_date >= start_date,
                    DepositSchedule.schedule_date <= end_date,
                )
            )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_upcoming_schedules(
        self, days: int = 30, account_id: Optional[int] = None
    ) -> List[DepositSchedule]:
        """
        Get upcoming deposit schedules for the next specified number of days.

        Args:
            days (int, optional): Number of days to look ahead, defaults to 30
            account_id (int, optional): Filter by specific account

        Returns:
            List[DepositSchedule]: List of upcoming deposit schedules
        """
        today = datetime.utcnow()
        end_date = datetime.utcnow().replace(
            hour=23, minute=59, second=59, microsecond=999999
        )
        end_date = datetime(
            end_date.year,
            end_date.month,
            end_date.day + days,
            end_date.hour,
            end_date.minute,
            end_date.second,
        )

        query = (
            select(DepositSchedule)
            .options(
                joinedload(DepositSchedule.account),
                joinedload(DepositSchedule.income),
            )
            .where(
                and_(
                    DepositSchedule.schedule_date >= today,
                    DepositSchedule.schedule_date <= end_date,
                    DepositSchedule.status == "pending",
                )
            )
            .order_by(DepositSchedule.schedule_date)
        )

        if account_id is not None:
            query = query.where(DepositSchedule.account_id == account_id)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def find_overdue_schedules(
        self, account_id: Optional[int] = None
    ) -> List[DepositSchedule]:
        """
        Find overdue deposit schedules (scheduled date in the past, still pending).

        Args:
            account_id (int, optional): Filter by specific account

        Returns:
            List[DepositSchedule]: List of overdue deposit schedules
        """
        today = datetime.utcnow()

        query = (
            select(DepositSchedule)
            .options(
                joinedload(DepositSchedule.account),
                joinedload(DepositSchedule.income),
            )
            .where(
                and_(
                    DepositSchedule.schedule_date < today,
                    DepositSchedule.status == "pending",
                )
            )
            .order_by(DepositSchedule.schedule_date)
        )

        if account_id is not None:
            query = query.where(DepositSchedule.account_id == account_id)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_recurring_schedules(self) -> List[DepositSchedule]:
        """
        Get deposit schedules that are recurring.

        Returns:
            List[DepositSchedule]: List of recurring deposit schedules
        """
        result = await self.session.execute(
            select(DepositSchedule)
            .where(DepositSchedule.recurring == True)
            .order_by(DepositSchedule.schedule_date)
        )
        return result.scalars().all()

    async def get_total_scheduled_deposits(
        self,
        start_date: datetime,
        end_date: datetime,
        account_id: Optional[int] = None,
    ) -> float:
        """
        Get total amount of scheduled deposits within a date range.

        Args:
            start_date (datetime): Start date (inclusive)
            end_date (datetime): End date (inclusive)
            account_id (int, optional): Filter by specific account

        Returns:
            float: Total amount of scheduled deposits
        """
        query = select(func.sum(DepositSchedule.amount)).where(
            and_(
                DepositSchedule.schedule_date >= start_date,
                DepositSchedule.schedule_date <= end_date,
                DepositSchedule.status == "pending",
            )
        )

        if account_id is not None:
            query = query.where(DepositSchedule.account_id == account_id)

        result = await self.session.execute(query)
        total = result.scalar_one()
        return float(total) if total is not None else 0.0

    async def cancel_schedule(self, schedule_id: int) -> bool:
        """
        Cancel a deposit schedule by deleting it.

        Args:
            schedule_id (int): Deposit schedule ID

        Returns:
            bool: True if deleted successfully, False otherwise
        """
        return await self.delete(schedule_id)

    async def update_status(
        self, schedule_id: int, status: str
    ) -> Optional[DepositSchedule]:
        """
        Update the status of a deposit schedule.

        Args:
            schedule_id (int): Deposit schedule ID
            status (str): New status value

        Returns:
            Optional[DepositSchedule]: Updated deposit schedule or None if not found
        """
        if status not in ["pending", "processed", "cancelled", "failed"]:
            raise ValueError(
                "Invalid status. Must be one of: pending, processed, cancelled, failed"
            )

        return await self.update(schedule_id, {"status": status})
