"""
Repository for realtime cashflow operations.

This module provides a repository for realtime cashflow operations,
including account balances, upcoming bills, transfer patterns,
usage patterns, and risk assessments.

This implementation is part of the ADR-014 Repository Layer Compliance effort,
moving all database operations from the RealtimeCashflowService to this dedicated
repository layer. This maintains clear separation between:
1. Data access (repository layer)
2. Business logic (service layer)
3. API endpoints

The repository follows architectural patterns established in other cashflow
repositories, including proper datetime handling following ADR-011 and
consistent decimal precision handling for financial calculations.
"""

from collections import defaultdict
from datetime import datetime, timedelta
from decimal import Decimal
from typing import Dict, List, Optional, Set, Tuple

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.liabilities import Liability
from src.models.payments import Payment, PaymentSource
from src.models.transaction_history import TransactionHistory
from src.repositories.cashflow.cashflow_base import CashflowBaseRepository
from src.utils.decimal_precision import DecimalPrecision


class RealtimeCashflowRepository(CashflowBaseRepository[Account]):
    """
    Repository for realtime cashflow operations.

    This repository provides methods for retrieving and analyzing
    realtime cashflow data, including account balances, upcoming bills,
    transfer patterns, usage patterns, and risk assessments.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the realtime cashflow repository.

        Args:
            session (AsyncSession): SQLAlchemy async session
        """
        super().__init__(session, Account)  # Use Account as base model

    async def get_all_accounts(self) -> List[Account]:
        """
        Get all accounts in the system.

        Returns:
            List[Account]: List of all accounts
        """
        query = select(Account)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_upcoming_bill(self) -> Tuple[Optional[datetime], Optional[int]]:
        """
        Get the next upcoming bill and days until due.

        Returns:
            Tuple[Optional[datetime], Optional[int]]: Tuple of due date and days until due,
            or (None, None) if no upcoming bills
        """
        # Get current date (naive for database query)
        current_date = datetime.now().replace(tzinfo=None)

        # Query for upcoming unpaid bills
        query = (
            select(Liability)
            .where(
                Liability.paid == False,  # noqa: E712
                Liability.due_date >= current_date,
            )
            .order_by(Liability.due_date)
        )

        result = await self.session.execute(query)
        bills = result.scalars().all()

        if not bills:
            return None, None

        # Get the earliest bill
        next_bill = min(bills, key=lambda x: x.due_date)
        days_until = (next_bill.due_date - current_date.date()).days
        return next_bill.due_date, days_until

    async def calculate_minimum_balance(self, days: int = 14) -> Decimal:
        """
        Calculate minimum balance required for upcoming bills.

        Args:
            days (int): Number of days to look ahead (default: 14)

        Returns:
            Decimal: Minimum balance required
        """
        # Calculate date range
        current_date = datetime.now().replace(tzinfo=None)
        end_date = current_date + timedelta(days=days)

        # Prepare date range for database query
        range_start, range_end = self._prepare_date_range(current_date, end_date)

        # Query for upcoming unpaid bills in range
        query = select(Liability).where(
            Liability.paid == False,  # noqa: E712
            Liability.due_date >= range_start,
            Liability.due_date <= range_end,
        )
        result = await self.session.execute(query)
        upcoming_bills = result.scalars().all()

        # Sum bill amounts with proper precision
        total = sum((bill.amount for bill in upcoming_bills), Decimal(0))
        return DecimalPrecision.round_for_calculation(total)

    async def get_unpaid_liabilities(
        self, current_date: Optional[datetime] = None
    ) -> List[Liability]:
        """
        Get all unpaid liabilities from current date forward.

        Args:
            current_date (Optional[datetime]): Date to check from (default: now)

        Returns:
            List[Liability]: List of unpaid liabilities
        """
        # Use provided date or current date
        if current_date is None:
            current_date = datetime.now().replace(tzinfo=None)
        else:
            # Ensure date is naive for database query
            current_date = current_date.replace(tzinfo=None)

        # Query for unpaid liabilities
        query = select(Liability).where(
            Liability.paid == False,  # noqa: E712
            Liability.due_date >= current_date,
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_transfers_between_accounts(
        self, account_ids: List[int]
    ) -> List[PaymentSource]:
        """
        Get transfers between the specified accounts.

        Args:
            account_ids (List[int]): List of account IDs to check

        Returns:
            List[PaymentSource]: List of payment sources representing transfers
        """
        # Query for transfers between accounts
        transfers_query = (
            select(PaymentSource)
            .join(Payment, PaymentSource.payment_id == Payment.id)
            .where(
                and_(
                    PaymentSource.account_id.in_(account_ids),
                    Payment.category == "Transfer",
                )
            )
        )
        result = await self.session.execute(transfers_query)
        return result.scalars().all()

    async def get_transaction_history(
        self, account_id: int, days: int = 30
    ) -> List[TransactionHistory]:
        """
        Get transaction history for an account over specified days.

        Args:
            account_id (int): Account ID to get history for
            days (int): Number of days to look back (default: 30)

        Returns:
            List[TransactionHistory]: List of transactions
        """
        # Calculate date range
        end_date = datetime.now().replace(tzinfo=None)
        start_date = end_date - timedelta(days=days)

        # Prepare date range for database query
        range_start, range_end = self._prepare_date_range(start_date, end_date)

        # Query for transactions in date range
        query = (
            select(TransactionHistory)
            .where(
                and_(
                    TransactionHistory.account_id == account_id,
                    TransactionHistory.transaction_date >= range_start,
                    TransactionHistory.transaction_date <= range_end,
                )
            )
            .order_by(TransactionHistory.transaction_date)
        )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_transactions_with_description(
        self, account_id: int, days: int = 30
    ) -> Dict[str, int]:
        """
        Get transaction descriptions and their frequencies for an account.

        Args:
            account_id (int): Account ID to get transactions for
            days (int): Number of days to look back (default: 30)

        Returns:
            Dict[str, int]: Dictionary of description to frequency count
        """
        # Get transaction history
        transactions = await self.get_transaction_history(account_id, days)

        # Count frequencies of descriptions
        merchants = defaultdict(int)
        for tx in transactions:
            if tx.description:
                merchants[tx.description] += 1

        return dict(merchants)

    async def get_balance_history_in_range(
        self, account_id: int, days: int = 30
    ) -> List[Decimal]:
        """
        Get balance history for an account over specified days.

        Args:
            account_id (int): Account ID to get balance history for
            days (int): Number of days to look back (default: 30)

        Returns:
            List[Decimal]: List of balance amounts
        """
        # Get transaction history
        transactions = await self.get_transaction_history(account_id, days)

        # Extract balance amounts
        return [tx.amount for tx in transactions]

    async def get_payment_categories(
        self, account_id: int, days: int = 30
    ) -> Dict[str, Decimal]:
        """
        Get payment categories and their total amounts for an account.

        Args:
            account_id (int): Account ID to get categories for
            days (int): Number of days to look back (default: 30)

        Returns:
            Dict[str, Decimal]: Dictionary of category to total amount
        """
        # Calculate date range
        end_date = datetime.now().replace(tzinfo=None)
        start_date = end_date - timedelta(days=days)

        # Prepare date range for database query
        range_start, range_end = self._prepare_date_range(start_date, end_date)

        # Query for payment categories in date range
        category_query = (
            select(
                Payment.category,
                func.sum(PaymentSource.amount).label("total_amount"),
            )
            .join(PaymentSource, PaymentSource.payment_id == Payment.id)
            .where(
                and_(
                    PaymentSource.account_id == account_id,
                    Payment.payment_date >= range_start,
                    Payment.payment_date <= range_end,
                )
            )
            .group_by(Payment.category)
        )

        result = await self.session.execute(category_query)
        categories = {row[0]: Decimal(str(row[1])) for row in result}
        return categories

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

    async def get_common_transaction_descriptions(
        self, account_ids: List[int]
    ) -> Set[str]:
        """
        Get common transaction descriptions across multiple accounts.

        Args:
            account_ids (List[int]): List of account IDs to check

        Returns:
            Set[str]: Set of common description strings
        """
        # Initialize empty set for each account
        account_descriptions = {}

        # For each account, get distinct descriptions
        for account_id in account_ids:
            # Get transaction history
            transactions = await self.get_transaction_history(account_id)

            # Extract descriptions
            descriptions = {tx.description for tx in transactions if tx.description}
            account_descriptions[account_id] = descriptions

        # Find intersection of all description sets
        if not account_descriptions:
            return set()

        # Start with first account's descriptions
        common = account_descriptions.get(account_ids[0], set())

        # Intersect with each other account's descriptions
        for account_id in account_ids[1:]:
            common = common.intersection(account_descriptions.get(account_id, set()))

        return common
