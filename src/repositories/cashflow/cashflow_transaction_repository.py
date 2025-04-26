"""
Repository for cashflow transaction operations.

This module provides a repository for cashflow transaction operations,
including retrieving day transactions, historical transactions, and projected transactions.
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.accounts import Account
from src.models.income import Income
from src.models.liabilities import Liability
from src.models.payments import Payment
from src.repositories.cashflow.cashflow_base import CashflowBaseRepository
from src.utils.datetime_utils import naive_end_of_day, naive_start_of_day


class CashflowTransactionRepository(CashflowBaseRepository[Liability]):
    """
    Repository for cashflow transaction operations.

    This repository provides methods for retrieving and analyzing transactions
    related to cashflow, including day transactions, historical transactions,
    and projected transactions.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the cashflow transaction repository.

        Args:
            session (AsyncSession): SQLAlchemy async session
        """
        super().__init__(
            session, Liability
        )  # Use Liability as base model for simplicity

    async def get_bills_due_on_date(
        self, account_id: int, target_date, include_pending: bool = True
    ) -> List[Liability]:
        """
        Get bills due on a specific date.

        Args:
            account_id (int): Account ID to get bills for
            target_date: Target date to check
            include_pending (bool): Whether to include pending bills

        Returns:
            List[Liability]: List of bills due on the specified date
        """
        # Prepare date range for exact date match
        day_start = naive_start_of_day(target_date)
        day_end = naive_end_of_day(target_date)

        # Build query
        query = select(Liability).where(
            Liability.primary_account_id == account_id,
            Liability.due_date >= day_start,
            Liability.due_date <= day_end,
        )

        # Add status filter if not including pending
        if not include_pending:
            query = query.where(Liability.status != "pending")

        # Execute query
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_income_expected_on_date(
        self, account_id: int, target_date, include_pending: bool = True
    ) -> List[Income]:
        """
        Get income expected on a specific date.

        Args:
            account_id (int): Account ID to get income for
            target_date: Target date to check
            include_pending (bool): Whether to include pending income

        Returns:
            List[Income]: List of income expected on the specified date
        """
        # Prepare date range for exact date match
        day_start = naive_start_of_day(target_date)
        day_end = naive_end_of_day(target_date)

        # Build query
        query = select(Income).where(
            Income.account_id == account_id,
            Income.date >= day_start,
            Income.date <= day_end,
        )

        # Add deposit status filter if not including pending
        if not include_pending:
            query = query.where(Income.deposited == True)

        # Execute query
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_recurring_bills(self, account_id: int) -> List[Liability]:
        """
        Get recurring bills for an account.

        Args:
            account_id (int): Account ID to get recurring bills for

        Returns:
            List[Liability]: List of recurring bills for the account
        """
        # Query for recurring bills
        query = select(Liability).where(
            Liability.primary_account_id == account_id, Liability.recurring == True
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_historical_payments(
        self, account_ids: List[int], start_date, end_date
    ) -> List[Payment]:
        """
        Get historical payments for accounts in a date range.

        Args:
            account_ids (List[int]): List of account IDs to get payments for
            start_date: Start date for range
            end_date: End date for range

        Returns:
            List[Payment]: List of payments with sources loaded
        """
        # Prepare date range
        range_start, range_end = self._prepare_date_range(start_date, end_date)

        # Query for payments in date range
        query = (
            select(Payment)
            .options(selectinload(Payment.sources))
            .where(Payment.payment_date.between(range_start, range_end))
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_historical_income(
        self, account_ids: List[int], start_date, end_date
    ) -> List[Income]:
        """
        Get historical income for accounts in a date range.

        Args:
            account_ids (List[int]): List of account IDs to get income for
            start_date: Start date for range
            end_date: End date for range

        Returns:
            List[Income]: List of income entries
        """
        # Prepare date range
        range_start, range_end = self._prepare_date_range(start_date, end_date)

        # Query for income in date range
        query = select(Income).where(
            Income.account_id.in_(account_ids),
            Income.date.between(range_start, range_end),
            Income.deposited == True,  # Only include deposited income
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_bills_in_date_range(
        self, account_id: int, start_date, end_date, include_pending: bool = True
    ) -> List[Liability]:
        """
        Get bills due in a date range.

        Args:
            account_id (int): Account ID to get bills for
            start_date: Start date for range
            end_date: End date for range
            include_pending (bool): Whether to include pending bills

        Returns:
            List[Liability]: List of bills due in the specified date range
        """
        # Prepare date range
        range_start, range_end = self._prepare_date_range(start_date, end_date)

        # Build query
        query = select(Liability).where(
            Liability.primary_account_id == account_id,
            Liability.due_date.between(range_start, range_end),
        )

        # Add status filter if not including pending
        if not include_pending:
            query = query.where(Liability.status != "pending")

        # Execute query
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_income_in_date_range(
        self, account_id: int, start_date, end_date, include_pending: bool = True
    ) -> List[Income]:
        """
        Get income expected in a date range.

        Args:
            account_id (int): Account ID to get income for
            start_date: Start date for range
            end_date: End date for range
            include_pending (bool): Whether to include pending income

        Returns:
            List[Income]: List of income expected in the specified date range
        """
        # Prepare date range
        range_start, range_end = self._prepare_date_range(start_date, end_date)

        # Build query
        query = select(Income).where(
            Income.account_id == account_id,
            Income.date.between(range_start, range_end),
        )

        # Add deposit status filter if not including pending
        if not include_pending:
            query = query.where(Income.deposited == True)

        # Execute query
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_account_by_id(self, account_id: int) -> Optional[Account]:
        """
        Get an account by ID.

        Args:
            account_id (int): Account ID to get

        Returns:
            Optional[Account]: Account if found, None otherwise
        """
        query = select(Account).where(Account.id == account_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
