"""
Income repository implementation for CRUD operations.

This module provides a specialized repository for Income model operations,
implementing standard CRUD functionality along with Income-specific query methods.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.models.income import Income
from src.repositories.base_repository import BaseRepository


class IncomeRepository(BaseRepository[Income, int]):
    """
    Repository for Income model operations.

    This class extends the base repository with Income-specific methods for
    querying and managing income records, providing a clean data access layer
    separate from business logic.

    Attributes:
        session (AsyncSession): The SQLAlchemy async session for database operations
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize Income repository with session.

        Args:
            session (AsyncSession): SQLAlchemy async session
        """
        super().__init__(session, Income)

    async def get_by_source(self, source: str) -> List[Income]:
        """
        Get income records by source name (partial match).

        Args:
            source (str): Income source to search for

        Returns:
            List[Income]: List of matching income records
        """
        query = select(Income).where(Income.source.ilike(f"%{source}%"))
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_income_in_date_range(
        self, start_date: datetime, end_date: datetime, account_id: Optional[int] = None
    ) -> List[Income]:
        """
        Get income records within a date range.

        Args:
            start_date (datetime): Start date (inclusive)
            end_date (datetime): End date (inclusive)
            account_id (Optional[int]): Optional account ID to filter by

        Returns:
            List[Income]: List of income records in the date range
        """
        conditions = [Income.date >= start_date, Income.date <= end_date]

        if account_id is not None:
            conditions.append(Income.account_id == account_id)

        query = (
            select(Income)
            .options(joinedload(Income.account))
            .where(and_(*conditions))
            .order_by(Income.date)
        )

        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def get_income_by_account(self, account_id: int) -> List[Income]:
        """
        Get all income records for a specific account.

        Args:
            account_id (int): ID of the account

        Returns:
            List[Income]: List of income records for the account
        """
        query = (
            select(Income)
            .options(joinedload(Income.account))
            .where(Income.account_id == account_id)
            .order_by(Income.date.desc())
        )

        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def get_undeposited_income(
        self, account_id: Optional[int] = None
    ) -> List[Income]:
        """
        Get all undeposited income records.

        Args:
            account_id (Optional[int]): Optional account ID to filter by

        Returns:
            List[Income]: List of undeposited income records
        """
        conditions = [Income.deposited == False]

        if account_id is not None:
            conditions.append(Income.account_id == account_id)

        query = (
            select(Income)
            .options(joinedload(Income.account))
            .where(and_(*conditions))
            .order_by(Income.date.desc())
        )

        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def get_total_undeposited(self) -> Decimal:
        """
        Calculate the total amount of undeposited income.

        Returns:
            Decimal: Total undeposited amount
        """
        query = select(func.sum(Income.amount)).where(Income.deposited == False)

        result = await self.session.execute(query)
        total = result.scalar_one() or Decimal("0.00")
        return total

    async def get_total_undeposited_by_account(self, account_id: int) -> Decimal:
        """
        Calculate the total undeposited income for a specific account.

        Args:
            account_id (int): ID of the account

        Returns:
            Decimal: Total undeposited amount for the account
        """
        query = select(func.sum(Income.amount)).where(
            and_(Income.account_id == account_id, Income.deposited == False)
        )

        result = await self.session.execute(query)
        total = result.scalar_one() or Decimal("0.00")
        return total

    async def get_with_relationships(self, income_id: int) -> Optional[Income]:
        """
        Get an income record with all relevant relationships loaded.

        Args:
            income_id (int): ID of the income record

        Returns:
            Optional[Income]: Income record with relationships loaded or None
        """
        query = (
            select(Income)
            .options(
                joinedload(Income.account),
                joinedload(Income.category),
                joinedload(Income.recurring_income),
                selectinload(Income.payments),
                selectinload(Income.deposit_schedules),
            )
            .where(Income.id == income_id)
        )

        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_income_by_category(self, category_id: int) -> List[Income]:
        """
        Get income records by category.

        Args:
            category_id (int): ID of the category

        Returns:
            List[Income]: List of income records with the specified category
        """
        query = (
            select(Income)
            .options(joinedload(Income.category), joinedload(Income.account))
            .where(Income.category_id == category_id)
            .order_by(Income.date.desc())
        )

        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def mark_as_deposited(self, income_id: int) -> Optional[Income]:
        """
        Mark an income record as deposited.

        Note: This only updates the deposited status and undeposited_amount.
        Account balance updates should be handled by the service layer.

        Args:
            income_id (int): ID of the income record

        Returns:
            Optional[Income]: Updated income record or None if not found
        """
        # Get the income record first to ensure it exists
        income = await self.get(income_id)
        if not income:
            return None

        # Update the deposited status and undeposited_amount
        income.deposited = True
        income.undeposited_amount = Decimal("0.00")

        await self.session.flush()
        await self.session.refresh(income)

        return income

    async def get_income_by_recurring(self, recurring_id: int) -> List[Income]:
        """
        Get income records associated with a recurring income pattern.

        Args:
            recurring_id (int): ID of the recurring income

        Returns:
            List[Income]: List of income records associated with the recurring pattern
        """
        query = (
            select(Income)
            .options(joinedload(Income.account), joinedload(Income.recurring_income))
            .where(Income.recurring_income_id == recurring_id)
            .order_by(Income.date.desc())
        )

        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def get_income_statistics_by_period(
        self,
        start_date: datetime,
        end_date: datetime,
        account_id: Optional[int] = None,
        category_id: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Calculate income statistics for a specific period.

        Args:
            start_date (datetime): Start date of the period
            end_date (datetime): End date of the period
            account_id (Optional[int]): Optional account ID to filter by
            category_id (Optional[int]): Optional category ID to filter by

        Returns:
            Dict[str, Any]: Dictionary with statistics (total, average, count, etc.)
        """
        # Build conditions based on parameters
        conditions = [Income.date >= start_date, Income.date <= end_date]

        if account_id is not None:
            conditions.append(Income.account_id == account_id)

        if category_id is not None:
            conditions.append(Income.category_id == category_id)

        # Query for total amount
        total_query = select(func.sum(Income.amount)).where(and_(*conditions))

        # Query for count
        count_query = select(func.count()).select_from(Income).where(and_(*conditions))

        # Query for average amount
        avg_query = select(func.avg(Income.amount)).where(and_(*conditions))

        # Query for minimum amount
        min_query = select(func.min(Income.amount)).where(and_(*conditions))

        # Query for maximum amount
        max_query = select(func.max(Income.amount)).where(and_(*conditions))

        # Execute all queries
        total_result = await self.session.execute(total_query)
        count_result = await self.session.execute(count_query)
        avg_result = await self.session.execute(avg_query)
        min_result = await self.session.execute(min_query)
        max_result = await self.session.execute(max_query)

        # Extract results
        total_amount = total_result.scalar_one() or Decimal("0.00")
        count = count_result.scalar_one() or 0
        avg_amount = avg_result.scalar_one() or Decimal("0.00")
        min_amount = min_result.scalar_one() or Decimal("0.00")
        max_amount = max_result.scalar_one() or Decimal("0.00")

        # Return statistics dictionary
        return {
            "total_amount": total_amount,
            "count": count,
            "average_amount": avg_amount,
            "minimum_amount": min_amount,
            "maximum_amount": max_amount,
        }

    async def get_income_with_filters(
        self,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        source: Optional[str] = None,
        deposited: Optional[bool] = None,
        min_amount: Optional[Decimal] = None,
        max_amount: Optional[Decimal] = None,
        account_id: Optional[int] = None,
        category_id: Optional[int] = None,
        recurring: Optional[bool] = None,
    ) -> Tuple[List[Income], int]:
        """
        Get income records with comprehensive filtering.

        This method provides a flexible way to query income records with various filters.

        Args:
            skip (int): Number of records to skip
            limit (int): Maximum number of records to return
            start_date (Optional[datetime]): Filter by start date
            end_date (Optional[datetime]): Filter by end date
            source (Optional[str]): Filter by source (partial match)
            deposited (Optional[bool]): Filter by deposit status
            min_amount (Optional[Decimal]): Filter by minimum amount
            max_amount (Optional[Decimal]): Filter by maximum amount
            account_id (Optional[int]): Filter by account ID
            category_id (Optional[int]): Filter by category ID
            recurring (Optional[bool]): Filter by recurring status

        Returns:
            Tuple[List[Income], int]: Tuple of (income_records, total_count)
        """
        # Build conditions based on parameters
        conditions = []

        if start_date is not None:
            conditions.append(Income.date >= start_date)

        if end_date is not None:
            conditions.append(Income.date <= end_date)

        if source is not None:
            conditions.append(Income.source.ilike(f"%{source}%"))

        if deposited is not None:
            conditions.append(Income.deposited == deposited)

        if min_amount is not None:
            conditions.append(Income.amount >= min_amount)

        if max_amount is not None:
            conditions.append(Income.amount <= max_amount)

        if account_id is not None:
            conditions.append(Income.account_id == account_id)

        if category_id is not None:
            conditions.append(Income.category_id == category_id)

        if recurring is not None:
            conditions.append(Income.recurring == recurring)

        # Build base query
        query = select(Income).options(joinedload(Income.account))

        if conditions:
            query = query.where(and_(*conditions))

        # Get total count
        count_query = select(func.count()).select_from(Income)
        if conditions:
            count_query = count_query.where(and_(*conditions))

        count_result = await self.session.execute(count_query)
        total = count_result.scalar_one() or 0

        # Apply pagination and get results
        query = query.order_by(Income.date.desc()).offset(skip).limit(limit)
        result = await self.session.execute(query)

        return result.unique().scalars().all(), total
