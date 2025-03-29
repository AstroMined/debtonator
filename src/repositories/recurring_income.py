"""
RecurringIncome repository implementation for CRUD operations.

This module provides a specialized repository for RecurringIncome model operations,
implementing standard CRUD functionality along with RecurringIncome-specific query methods.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, func, or_, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.models.income import Income
from src.models.recurring_income import RecurringIncome
from src.repositories.base_repository import BaseRepository


class RecurringIncomeRepository(BaseRepository[RecurringIncome, int]):
    """
    Repository for RecurringIncome model operations.

    This class extends the base repository with RecurringIncome-specific methods for
    querying and managing recurring income records, providing a clean data access layer
    separate from business logic.

    Attributes:
        session (AsyncSession): The SQLAlchemy async session for database operations
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize RecurringIncome repository with session.

        Args:
            session (AsyncSession): SQLAlchemy async session
        """
        super().__init__(session, RecurringIncome)

    async def get_by_source(self, source: str) -> List[RecurringIncome]:
        """
        Get recurring income records by source name (partial match).

        Args:
            source (str): Income source to search for

        Returns:
            List[RecurringIncome]: List of matching recurring income records
        """
        query = select(RecurringIncome).where(
            RecurringIncome.source.ilike(f"%{source}%")
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_account(self, account_id: int) -> List[RecurringIncome]:
        """
        Get all recurring income records for a specific account.

        Args:
            account_id (int): ID of the account

        Returns:
            List[RecurringIncome]: List of recurring income records for the account
        """
        query = (
            select(RecurringIncome)
            .options(joinedload(RecurringIncome.account))
            .where(RecurringIncome.account_id == account_id)
        )

        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def get_active_income(self) -> List[RecurringIncome]:
        """
        Get all active recurring income records.

        Returns:
            List[RecurringIncome]: List of active recurring income records
        """
        query = (
            select(RecurringIncome)
            .options(joinedload(RecurringIncome.account))
            .where(RecurringIncome.active == True)
        )

        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def get_by_day_of_month(self, day: int) -> List[RecurringIncome]:
        """
        Get recurring income records for a specific day of the month.

        Args:
            day (int): Day of the month (1-31)

        Returns:
            List[RecurringIncome]: List of recurring income records for the specified day
        """
        query = (
            select(RecurringIncome)
            .options(joinedload(RecurringIncome.account))
            .where(RecurringIncome.day_of_month == day)
        )

        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def get_with_income_entries(
        self, recurring_id: int
    ) -> Optional[RecurringIncome]:
        """
        Get a recurring income record with its associated income entries.

        Args:
            recurring_id (int): ID of the recurring income record

        Returns:
            Optional[RecurringIncome]: Recurring income record with income entries or None
        """
        query = (
            select(RecurringIncome)
            .options(selectinload(RecurringIncome.income_entries))
            .where(RecurringIncome.id == recurring_id)
        )

        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_with_account(self, recurring_id: int) -> Optional[RecurringIncome]:
        """
        Get a recurring income record with its associated account.

        Args:
            recurring_id (int): ID of the recurring income record

        Returns:
            Optional[RecurringIncome]: Recurring income record with account or None
        """
        query = (
            select(RecurringIncome)
            .options(joinedload(RecurringIncome.account))
            .where(RecurringIncome.id == recurring_id)
        )

        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_with_category(self, recurring_id: int) -> Optional[RecurringIncome]:
        """
        Get a recurring income record with its associated category.

        Args:
            recurring_id (int): ID of the recurring income record

        Returns:
            Optional[RecurringIncome]: Recurring income record with category or None
        """
        query = (
            select(RecurringIncome)
            .options(joinedload(RecurringIncome.category))
            .where(RecurringIncome.id == recurring_id)
        )

        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_with_relationships(
        self, recurring_id: int
    ) -> Optional[RecurringIncome]:
        """
        Get a recurring income record with all relevant relationships loaded.

        Args:
            recurring_id (int): ID of the recurring income record

        Returns:
            Optional[RecurringIncome]: Recurring income record with relationships or None
        """
        query = (
            select(RecurringIncome)
            .options(
                joinedload(RecurringIncome.account),
                joinedload(RecurringIncome.category),
                selectinload(RecurringIncome.income_entries),
            )
            .where(RecurringIncome.id == recurring_id)
        )

        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def toggle_active(self, recurring_id: int) -> Optional[RecurringIncome]:
        """
        Toggle the active status of a recurring income record.

        Args:
            recurring_id (int): ID of the recurring income record

        Returns:
            Optional[RecurringIncome]: Updated recurring income record or None if not found
        """
        # Get the recurring income first to check if it exists and get current status
        recurring = await self.get(recurring_id)
        if not recurring:
            return None

        # Toggle the active status
        update_data = {"active": not recurring.active}

        # Update the record
        return await self.update(recurring_id, update_data)

    async def toggle_auto_deposit(self, recurring_id: int) -> Optional[RecurringIncome]:
        """
        Toggle the auto_deposit status of a recurring income record.

        Args:
            recurring_id (int): ID of the recurring income record

        Returns:
            Optional[RecurringIncome]: Updated recurring income record or None if not found
        """
        # Get the recurring income first to check if it exists and get current status
        recurring = await self.get(recurring_id)
        if not recurring:
            return None

        # Toggle the auto_deposit status
        update_data = {"auto_deposit": not recurring.auto_deposit}

        # Update the record
        return await self.update(recurring_id, update_data)

    async def update_day_of_month(
        self, recurring_id: int, day: int
    ) -> Optional[RecurringIncome]:
        """
        Update the day_of_month for a recurring income record.

        Args:
            recurring_id (int): ID of the recurring income record
            day (int): New day of the month (1-31)

        Returns:
            Optional[RecurringIncome]: Updated recurring income record or None if not found
        """
        # Validate day of month
        if day < 1 or day > 31:
            raise ValueError("Day of month must be between 1 and 31")

        # Update the record
        update_data = {"day_of_month": day}

        return await self.update(recurring_id, update_data)

    async def get_monthly_total(self, account_id: Optional[int] = None) -> Decimal:
        """
        Calculate the total monthly amount of recurring income.

        Args:
            account_id (Optional[int]): Optional account ID to filter by

        Returns:
            Decimal: Total monthly amount
        """
        query = select(func.sum(RecurringIncome.amount)).where(
            RecurringIncome.active == True
        )

        if account_id is not None:
            query = query.where(RecurringIncome.account_id == account_id)

        result = await self.session.execute(query)
        total = result.scalar_one() or Decimal("0.00")
        return total

    async def get_upcoming_deposits(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get estimated upcoming deposits based on recurring income records.

        This method calculates projected income entries for the next specified
        number of days based on the day_of_month and amount of active recurring incomes.

        Args:
            days (int): Number of days to look ahead (default: 30)

        Returns:
            List[Dict[str, Any]]: List of projected income entries with:
                - source: income source name
                - amount: income amount
                - projected_date: estimated date of the income
                - account_id: target account ID
                - recurring_id: associated recurring income ID
        """
        # Get all active recurring incomes
        query = (
            select(RecurringIncome)
            .options(joinedload(RecurringIncome.account))
            .where(RecurringIncome.active == True)
        )

        result = await self.session.execute(query)
        recurring_incomes = result.unique().scalars().all()

        # Calculate upcoming deposit dates based on day_of_month
        today = datetime.utcnow()
        current_month = today.month
        current_year = today.year
        current_day = today.day

        upcoming_deposits = []

        for income in recurring_incomes:
            # Determine if the day has already passed this month
            if income.day_of_month < current_day:
                # If passed, schedule for next month
                deposit_month = current_month + 1
                deposit_year = current_year
                if deposit_month > 12:
                    deposit_month = 1
                    deposit_year += 1
            else:
                # If not passed, schedule for current month
                deposit_month = current_month
                deposit_year = current_year

            # Create deposit date (handle edge cases like Feb 30)
            try:
                deposit_date = datetime(
                    deposit_year, deposit_month, income.day_of_month
                )
            except ValueError:
                # Handle invalid dates (e.g., Feb 30) by using the last day of the month
                if deposit_month == 2:
                    # Check for leap year
                    if (
                        deposit_year % 4 == 0 and deposit_year % 100 != 0
                    ) or deposit_year % 400 == 0:
                        deposit_date = datetime(deposit_year, deposit_month, 29)
                    else:
                        deposit_date = datetime(deposit_year, deposit_month, 28)
                elif deposit_month in [4, 6, 9, 11]:
                    deposit_date = datetime(deposit_year, deposit_month, 30)
                else:
                    deposit_date = datetime(deposit_year, deposit_month, 31)

            # Check if it's within the specified days range
            delta = (deposit_date - today).days
            if 0 <= delta <= days:
                upcoming_deposits.append(
                    {
                        "source": income.source,
                        "amount": income.amount,
                        "projected_date": deposit_date,
                        "account_id": income.account_id,
                        "recurring_id": income.id,
                    }
                )

        # Sort by date
        upcoming_deposits.sort(key=lambda x: x["projected_date"])

        return upcoming_deposits

    async def find_by_pattern(self, pattern: str) -> List[RecurringIncome]:
        """
        Find recurring income records by pattern in source name.

        Args:
            pattern (str): Pattern to search for

        Returns:
            List[RecurringIncome]: List of matching recurring income records
        """
        query = (
            select(RecurringIncome)
            .options(joinedload(RecurringIncome.account))
            .where(RecurringIncome.source.ilike(f"%{pattern}%"))
        )

        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def get_total_by_source(self, source_pattern: str) -> Decimal:
        """
        Calculate total amount for recurring incomes matching a source pattern.

        Args:
            source_pattern (str): Pattern to match against source names

        Returns:
            Decimal: Total amount
        """
        query = select(func.sum(RecurringIncome.amount)).where(
            and_(
                RecurringIncome.active == True,
                RecurringIncome.source.ilike(f"%{source_pattern}%"),
            )
        )

        result = await self.session.execute(query)
        total = result.scalar_one() or Decimal("0.00")
        return total
