"""
Liability repository implementation.

This module provides a repository for Liability model CRUD operations and specialized
queries for bill/liability-related functionality.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple, Union

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.models.bill_splits import BillSplit
from src.models.liabilities import Liability, LiabilityStatus
from src.models.payments import Payment
from src.repositories.base import BaseRepository


class LiabilityRepository(BaseRepository[Liability, int]):
    """
    Repository for Liability model operations.

    This repository handles CRUD operations for bills/liabilities and provides specialized
    queries for bill-related functionality.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session (AsyncSession): SQLAlchemy async session
        """
        super().__init__(session, Liability)

    async def get_with_splits(self, liability_id: int) -> Optional[Liability]:
        """
        Get a liability with its bill splits loaded.

        Args:
            liability_id (int): Liability ID

        Returns:
            Optional[Liability]: Liability with loaded splits or None
        """
        result = await self.session.execute(
            select(Liability)
            .options(selectinload(Liability.splits))
            .where(Liability.id == liability_id)
        )
        return result.scalars().first()

    async def get_with_payments(self, liability_id: int) -> Optional[Liability]:
        """
        Get a liability with its payment history loaded.

        Args:
            liability_id (int): Liability ID

        Returns:
            Optional[Liability]: Liability with loaded payments or None
        """
        result = await self.session.execute(
            select(Liability)
            .options(selectinload(Liability.payments))
            .where(Liability.id == liability_id)
        )
        return result.scalars().first()

    async def get_with_relationships(
        self,
        liability_id: int,
        include_splits: bool = False,
        include_payments: bool = False,
        include_payment_schedules: bool = False,
        include_primary_account: bool = False,
        include_category: bool = False,
    ) -> Optional[Liability]:
        """
        Get a liability with specified relationships loaded.

        Args:
            liability_id (int): Liability ID
            include_splits (bool): Load bill splits
            include_payments (bool): Load payment history
            include_payment_schedules (bool): Load payment schedules
            include_primary_account (bool): Load primary account
            include_category (bool): Load category

        Returns:
            Optional[Liability]: Liability with loaded relationships or None
        """
        query = select(Liability).where(Liability.id == liability_id)

        if include_splits:
            query = query.options(selectinload(Liability.splits))

        if include_payments:
            query = query.options(selectinload(Liability.payments))

        if include_payment_schedules:
            query = query.options(selectinload(Liability.payment_schedules))

        if include_primary_account:
            query = query.options(joinedload(Liability.primary_account))

        if include_category:
            query = query.options(joinedload(Liability.category))

        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_bills_due_in_range(
        self, start_date: datetime, end_date: datetime, include_paid: bool = False
    ) -> List[Liability]:
        """
        Get bills due within a specified date range.

        Args:
            start_date (datetime): Start date (inclusive)
            end_date (datetime): End date (inclusive)
            include_paid (bool): Whether to include paid bills

        Returns:
            List[Liability]: Bills due in the specified date range
        """
        query = (
            select(Liability)
            .where(
                and_(
                    Liability.due_date >= start_date,
                    Liability.due_date <= end_date,
                    Liability.active == True,
                )
            )
            .order_by(Liability.due_date)
        )

        if not include_paid:
            query = query.where(Liability.paid == False)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_bills_by_category(
        self, category_id: int, include_paid: bool = False, limit: int = 100
    ) -> List[Liability]:
        """
        Get bills filtered by category.

        Args:
            category_id (int): Category ID
            include_paid (bool): Whether to include paid bills
            limit (int): Maximum number of bills to return

        Returns:
            List[Liability]: Bills in the specified category
        """
        query = (
            select(Liability)
            .where(and_(Liability.category_id == category_id, Liability.active == True))
            .order_by(desc(Liability.due_date))
            .limit(limit)
        )

        if not include_paid:
            query = query.where(Liability.paid == False)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_recurring_bills(self, active_only: bool = True) -> List[Liability]:
        """
        Get recurring bills.

        Args:
            active_only (bool): Whether to include only active bills

        Returns:
            List[Liability]: Recurring bills
        """
        query = (
            select(Liability)
            .where(Liability.recurring == True)
            .order_by(Liability.due_date)
        )

        if active_only:
            query = query.where(Liability.active == True)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def find_bills_by_status(
        self, status: LiabilityStatus, limit: int = 100
    ) -> List[Liability]:
        """
        Find bills with specific status.

        Args:
            status (LiabilityStatus): Status to filter by
            limit (int): Maximum number of bills to return

        Returns:
            List[Liability]: Bills with the specified status
        """
        query = (
            select(Liability)
            .where(and_(Liability.status == status, Liability.active == True))
            .order_by(Liability.due_date)
            .limit(limit)
        )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_bills_for_account(
        self, account_id: int, include_paid: bool = False, include_splits: bool = True
    ) -> List[Liability]:
        """
        Get bills associated with a specific account.

        This includes both bills where the account is the primary account
        and bills that have splits assigned to this account.

        Args:
            account_id (int): Account ID
            include_paid (bool): Whether to include paid bills
            include_splits (bool): Whether to include bills via splits

        Returns:
            List[Liability]: Bills associated with the account
        """
        # First get IDs from primary account bills
        primary_ids_query = select(Liability.id).where(
            and_(Liability.primary_account_id == account_id, Liability.active == True)
        )
        if not include_paid:
            primary_ids_query = primary_ids_query.where(Liability.paid == False)

        # Then get IDs from split bills if needed
        if include_splits:
            split_ids_query = (
                select(Liability.id)
                .join(BillSplit, BillSplit.liability_id == Liability.id)
                .where(
                    and_(BillSplit.account_id == account_id, Liability.active == True)
                )
            )
            if not include_paid:
                split_ids_query = split_ids_query.where(Liability.paid == False)

            # Get all IDs (primary and splits)
            # Use union instead of union_all to ensure uniqueness
            primary_ids = await self.session.execute(primary_ids_query)
            primary_ids_list = [id for (id,) in primary_ids.all()]

            split_ids = await self.session.execute(split_ids_query)
            split_ids_list = [id for (id,) in split_ids.all()]

            # Combine without duplicates
            combined_ids = list(set(primary_ids_list + split_ids_list))
        else:
            # Only use primary ids
            primary_ids = await self.session.execute(primary_ids_query)
            combined_ids = [id for (id,) in primary_ids.all()]

        if not combined_ids:
            return []

        # Final query that selects full entities by ID
        final_query = (
            select(Liability)
            .where(Liability.id.in_(combined_ids))
            .order_by(Liability.due_date)
        )

        result = await self.session.execute(final_query)
        return result.scalars().all()

    async def get_upcoming_payments(
        self, days: int = 30, include_paid: bool = False
    ) -> List[Liability]:
        """
        Get upcoming bills due within specified number of days.

        Args:
            days (int): Number of days to look ahead
            include_paid (bool): Whether to include paid bills

        Returns:
            List[Liability]: Upcoming bills
        """
        now = datetime.utcnow()
        end_date = datetime.utcnow().replace(hour=23, minute=59, second=59) + timedelta(
            days=days
        )

        return await self.get_bills_due_in_range(now, end_date, include_paid)

    async def get_overdue_bills(self) -> List[Liability]:
        """
        Get overdue bills (due date in the past and not paid).

        Returns:
            List[Liability]: Overdue bills
        """
        now = datetime.utcnow()

        query = (
            select(Liability)
            .where(
                and_(
                    Liability.due_date < now,
                    Liability.paid == False,
                    Liability.active == True,
                )
            )
            .order_by(Liability.due_date)
        )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_monthly_liability_amount(self, year: int, month: int) -> Decimal:
        """
        Get total liability amount for a specific month.

        Args:
            year (int): Year
            month (int): Month (1-12)

        Returns:
            Decimal: Total liability amount
        """
        # Create date range for the month
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)
        end_date = end_date - timedelta(seconds=1)

        # Query for total amount
        query = select(func.sum(Liability.amount)).where(
            and_(
                Liability.due_date >= start_date,
                Liability.due_date <= end_date,
                Liability.active == True,
            )
        )

        result = await self.session.execute(query)
        total = result.scalar_one_or_none()
        return total if total is not None else Decimal("0")

    async def mark_as_paid(
        self, liability_id: int, payment_date: Optional[datetime] = None
    ) -> Optional[Liability]:
        """
        Mark a liability as paid.

        Args:
            liability_id (int): Liability ID
            payment_date (datetime, optional): Date of payment (defaults to now)

        Returns:
            Optional[Liability]: Updated liability or None if not found
        """
        if payment_date is None:
            payment_date = datetime.utcnow()

        update_data = {"paid": True, "status": LiabilityStatus.PAID}

        return await self.update(liability_id, update_data)

    async def reset_payment_status(self, liability_id: int) -> Optional[Liability]:
        """
        Reset a liability payment status to unpaid.

        Args:
            liability_id (int): Liability ID

        Returns:
            Optional[Liability]: Updated liability or None if not found
        """
        update_data = {"paid": False, "status": LiabilityStatus.PENDING}

        return await self.update(liability_id, update_data)
