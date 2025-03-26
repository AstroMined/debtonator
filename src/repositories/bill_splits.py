"""
Bill split repository implementation for CRUD operations.

This module provides a BillSplitRepository class that handles database operations
for bill splits, including specialized methods for split-specific queries and operations.
"""

from datetime import date, datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.core.decimal_precision import DecimalPrecision
from src.models.accounts import Account
from src.models.bill_splits import BillSplit
from src.models.liabilities import Liability
from src.repositories.base import BaseRepository
from src.utils.datetime_utils import days_ago


class BillSplitRepository(BaseRepository[BillSplit, int]):
    """
    Repository for bill split operations.

    This class provides standard and specialized database operations for BillSplit models,
    focusing on split-specific functionality and relationship handling.

    Attributes:
        session (AsyncSession): The SQLAlchemy async session for database operations
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the bill split repository.

        Args:
            session (AsyncSession): AsyncSession for database operations
        """
        super().__init__(session, BillSplit)

    async def get_with_relationships(self, split_id: int) -> Optional[BillSplit]:
        """
        Get a bill split with its relationships (liability and account).

        Args:
            split_id (int): ID of the bill split to retrieve

        Returns:
            Optional[BillSplit]: Bill split with relationships or None if not found
        """
        query = (
            select(BillSplit)
            .options(joinedload(BillSplit.liability), joinedload(BillSplit.account))
            .where(BillSplit.id == split_id)
        )
        result = await self.session.execute(query)
        return result.unique().scalar_one_or_none()

    async def get_splits_for_bill(self, liability_id: int) -> List[BillSplit]:
        """
        Get all splits for a specific liability.

        Args:
            liability_id (int): ID of the liability to get splits for

        Returns:
            List[BillSplit]: List of bill splits for the liability
        """
        query = (
            select(BillSplit)
            .options(joinedload(BillSplit.liability), joinedload(BillSplit.account))
            .where(BillSplit.liability_id == liability_id)
        )
        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def get_splits_for_account(self, account_id: int) -> List[BillSplit]:
        """
        Get all splits for a specific account.

        Args:
            account_id (int): ID of the account to get splits for

        Returns:
            List[BillSplit]: List of bill splits for the account
        """
        query = (
            select(BillSplit)
            .options(joinedload(BillSplit.liability), joinedload(BillSplit.account))
            .where(BillSplit.account_id == account_id)
        )
        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def get_splits_in_date_range(
        self, account_id: int, start_date: datetime, end_date: datetime
    ) -> List[BillSplit]:
        """
        Get all splits for an account within a date range.

        Args:
            account_id (int): ID of the account to get splits for
            start_date (datetime): Start date of the range
            end_date (datetime): End date of the range

        Returns:
            List[BillSplit]: List of bill splits in the date range
        """
        query = (
            select(BillSplit)
            .join(BillSplit.liability)
            .options(joinedload(BillSplit.liability), joinedload(BillSplit.account))
            .where(
                and_(
                    BillSplit.account_id == account_id,
                    Liability.due_date >= start_date,
                    Liability.due_date <= end_date,
                )
            )
        )
        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def get_splits_by_amount_range(
        self, min_amount: Decimal, max_amount: Decimal
    ) -> List[BillSplit]:
        """
        Get all splits with amounts in a specific range.

        Args:
            min_amount (Decimal): Minimum split amount
            max_amount (Decimal): Maximum split amount

        Returns:
            List[BillSplit]: List of bill splits in the amount range
        """
        query = (
            select(BillSplit)
            .options(joinedload(BillSplit.liability), joinedload(BillSplit.account))
            .where(and_(BillSplit.amount >= min_amount, BillSplit.amount <= max_amount))
        )
        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def bulk_create_splits(
        self, liability_id: int, splits: List[Dict[str, Any]]
    ) -> List[BillSplit]:
        """
        Create multiple bill splits for a liability in a single transaction.

        Args:
            liability_id (int): ID of the liability to create splits for
            splits (List[Dict[str, Any]]): List of split data dictionaries
                Each dict should contain account_id and amount.

        Returns:
            List[BillSplit]: List of created bill splits
        """
        db_splits = []
        for split_data in splits:
            # Ensure liability_id is set for each split
            split_data["liability_id"] = liability_id

            # Create the split
            db_split = BillSplit(**split_data)
            self.session.add(db_split)
            db_splits.append(db_split)

        # Flush to get IDs assigned
        await self.session.flush()

        # Refresh splits to get complete objects with relationships
        for split in db_splits:
            await self.session.refresh(split)

        return db_splits

    async def delete_splits_for_liability(self, liability_id: int) -> int:
        """
        Delete all splits for a liability.

        Args:
            liability_id (int): ID of the liability to delete splits for

        Returns:
            int: Number of splits deleted
        """
        result = await self.session.execute(
            delete(BillSplit).where(BillSplit.liability_id == liability_id)
        )
        return result.rowcount

    async def calculate_split_totals(self, liability_id: int) -> Decimal:
        """
        Calculate the total amount of all splits for a given liability.

        Args:
            liability_id (int): ID of the liability to calculate splits for

        Returns:
            Decimal: Total amount of all splits
        """
        query = select(func.sum(BillSplit.amount)).where(
            BillSplit.liability_id == liability_id
        )
        result = await self.session.execute(query)
        total = result.scalar_one_or_none() or Decimal("0")

        # Use DecimalPrecision to handle rounding consistently
        return DecimalPrecision.round_for_calculation(total)

    async def get_account_split_totals(
        self,
        account_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Decimal:
        """
        Calculate the total amount of all splits for an account, optionally within a date range.

        Args:
            account_id (int): ID of the account to calculate splits for
            start_date (datetime, optional): Start date of the range
            end_date (datetime, optional): End date of the range

        Returns:
            Decimal: Total amount of all splits for the account
        """
        query = select(func.sum(BillSplit.amount)).where(
            BillSplit.account_id == account_id
        )

        # Add date range filtering if provided
        if start_date or end_date:
            query = query.join(BillSplit.liability)

            if start_date:
                query = query.where(Liability.due_date >= start_date)

            if end_date:
                query = query.where(Liability.due_date <= end_date)

        result = await self.session.execute(query)
        total = result.scalar_one_or_none() or Decimal("0")

        # Use DecimalPrecision for consistent handling
        return DecimalPrecision.round_for_calculation(total)

    async def get_split_distribution(self, liability_id: int) -> Dict[int, Decimal]:
        """
        Get the distribution of splits across accounts for a liability.

        Args:
            liability_id (int): ID of the liability to analyze

        Returns:
            Dict[int, Decimal]: Mapping of account IDs to their split amounts
        """
        query = select(BillSplit.account_id, BillSplit.amount).where(
            BillSplit.liability_id == liability_id
        )
        result = await self.session.execute(query)

        # Build the distribution dictionary
        distribution = {}
        for account_id, amount in result:
            distribution[account_id] = amount

        return distribution

    async def get_splits_with_liability_details(
        self, account_id: int, paid_only: bool = False
    ) -> List[BillSplit]:
        """
        Get splits for an account with detailed liability information.

        Args:
            account_id (int): ID of the account to get splits for
            paid_only (bool, optional): If True, return only splits for paid liabilities

        Returns:
            List[BillSplit]: List of bill splits with liability details
        """
        query = (
            select(BillSplit)
            .join(BillSplit.liability)
            .options(joinedload(BillSplit.liability), joinedload(BillSplit.account))
            .where(BillSplit.account_id == account_id)
        )

        if paid_only:
            query = query.where(Liability.paid == True)

        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def get_recent_split_patterns(
        self, days: int = 90
    ) -> List[Tuple[int, Dict[int, Decimal]]]:
        """
        Analyze recent split patterns to identify common distribution patterns.

        Args:
            days (int, optional): Number of days to look back

        Returns:
            List[Tuple[int, Dict[int, Decimal]]]: List of (liability_id, account_distribution) pairs
        """
        # Calculate the cutoff date
        cutoff_date = days_ago(days)

        # Get all recent liabilities with their splits
        query = (
            select(Liability)
            .options(selectinload(Liability.splits))
            .where(Liability.due_date >= cutoff_date)
        )
        result = await self.session.execute(query)
        liabilities = result.unique().scalars().all()

        # Analyze split patterns
        patterns = []
        for liability in liabilities:
            if not liability.splits:
                continue

            # Create distribution map
            distribution = {}
            for split in liability.splits:
                distribution[split.account_id] = split.amount

            patterns.append((liability.id, distribution))

        return patterns
