from datetime import date, datetime
from typing import Dict, List
from zoneinfo import ZoneInfo

from sqlalchemy import select
from sqlalchemy.orm import selectinload

from src.models.accounts import Account
from src.models.income import Income
from src.models.liabilities import Liability
from src.models.payments import Payment

from .base import BaseService
from .types import DateType


class TransactionService(BaseService):
    """Service for managing and retrieving cashflow transactions."""

    async def get_day_transactions(
        self,
        account: Account,
        target_date: DateType,
        include_pending: bool = True,
        include_recurring: bool = True,
        include_transfers: bool = True,
    ) -> List[Dict]:
        """Get all transactions for a specific day.

        Args:
            account: Account to get transactions for
            target_date: Date to get transactions for
            include_pending: Whether to include pending transactions
            include_recurring: Whether to include recurring transactions
            include_transfers: Whether to include transfers

        Returns:
            List of transaction dictionaries
        """
        transactions = []

        # Get bills due on this date
        bills_query = select(Liability).where(
            Liability.primary_account_id == account.id,
            Liability.due_date == target_date,
        )
        if not include_pending:
            bills_query = bills_query.where(Liability.status != "pending")
        bills = (await self.db.execute(bills_query)).scalars().all()

        for bill in bills:
            transactions.append(
                {
                    "amount": -bill.amount,
                    "description": f"Bill: {bill.name}",
                    "type": "bill",
                }
            )

        # Get income expected on this date
        income_query = select(Income).where(
            Income.account_id == account.id, Income.date == target_date
        )
        if not include_pending:
            income_query = income_query.where(Income.deposited == True)
        income_entries = (await self.db.execute(income_query)).scalars().all()

        for income in income_entries:
            transactions.append(
                {
                    "amount": income.amount,
                    "description": f"Income: {income.source}",
                    "type": "income",
                }
            )

        # Add recurring transactions if requested
        if include_recurring:
            recurring_query = select(Liability).where(
                Liability.primary_account_id == account.id, Liability.recurring == True
            )
            recurring_bills = (await self.db.execute(recurring_query)).scalars().all()

            for bill in recurring_bills:
                # Check if this is a recurring instance for this date
                current_date = bill.due_date
                while current_date <= target_date:
                    if current_date == target_date:
                        transactions.append(
                            {
                                "amount": -bill.amount,
                                "description": f"Recurring Bill: {bill.name}",
                                "type": "recurring_bill",
                            }
                        )
                        break
                    # Advance to next occurrence
                    next_month = current_date.month + 1
                    next_year = current_date.year
                    if next_month > 12:
                        next_month = 1
                        next_year += 1
                    current_date = date(next_year, next_month, current_date.day)

        # Add transfers if requested
        if include_transfers:
            # Implementation for transfers would go here
            pass

        return transactions

    async def get_historical_transactions(
        self, account_ids: List[int], start_date: DateType, end_date: DateType
    ) -> List[Dict]:
        """Retrieve historical transactions for analysis.

        Args:
            account_ids: List of account IDs to get transactions for
            start_date: Start date for transaction range
            end_date: End date for transaction range

        Returns:
            List of transaction dictionaries
        """
        # Get payments
        payments_query = (
            select(Payment)
            .options(selectinload(Payment.sources))
            .where(Payment.payment_date.between(start_date, end_date))
        )
        payments = (await self.db.execute(payments_query)).scalars().all()

        # Get income with explicit account filtering
        income_query = select(Income).where(
            Income.account_id.in_(account_ids),
            Income.date.between(start_date, end_date),
            Income.deposited == True,  # Only include deposited income
        )
        income_entries = (await self.db.execute(income_query)).scalars().all()

        # Combine and format transactions
        transactions = []

        for payment in payments:
            for source in payment.sources:
                if source.account_id in account_ids:
                    transactions.append(
                        {
                            "date": (
                                payment.payment_date
                                if payment.payment_date.tzinfo
                                else payment.payment_date.replace(
                                    tzinfo=ZoneInfo("UTC")
                                )
                            ),
                            "amount": -source.amount,  # Negative for outflow
                            "type": "payment",
                            "account_id": source.account_id,
                            "category": payment.category,
                        }
                    )

        for income in income_entries:
            transactions.append(
                {
                    "date": datetime.combine(
                        income.date, datetime.min.time(), tzinfo=ZoneInfo("UTC")
                    ),
                    "amount": income.amount,  # Positive for inflow
                    "type": "income",
                    "account_id": income.account_id,
                    "category": "income",
                }
            )

        return sorted(transactions, key=lambda x: x["date"])

    async def get_projected_transactions(
        self,
        account: Account,
        start_date: DateType,
        end_date: DateType,
        include_pending: bool = True,
        include_recurring: bool = True,
    ) -> List[Dict]:
        """Get projected transactions for an account in the specified date range.

        Args:
            account: Account to get projections for
            start_date: Start date for projection range
            end_date: End date for projection range
            include_pending: Whether to include pending transactions
            include_recurring: Whether to include recurring transactions

        Returns:
            List of projected transaction dictionaries
        """
        transactions = []

        # Get bills due in the date range
        bills_query = select(Liability).where(
            Liability.primary_account_id == account.id,
            Liability.due_date.between(start_date, end_date),
        )
        if not include_pending:
            bills_query = bills_query.where(Liability.status != "pending")
        bills = (await self.db.execute(bills_query)).scalars().all()

        for bill in bills:
            transactions.append(
                {
                    "date": bill.due_date,
                    "amount": -bill.amount,  # Negative for outflow
                    "description": f"Bill: {bill.name}",
                    "type": "bill",
                }
            )

        # Get expected income in the date range
        income_query = select(Income).where(
            Income.account_id == account.id, Income.date.between(start_date, end_date)
        )
        if not include_pending:
            income_query = income_query.where(Income.deposited == True)
        income_entries = (await self.db.execute(income_query)).scalars().all()

        for income in income_entries:
            transactions.append(
                {
                    "date": income.date,
                    "amount": income.amount,  # Positive for inflow
                    "description": f"Income: {income.source}",
                    "type": "income",
                }
            )

        # Add recurring transactions if requested
        if include_recurring:
            recurring_query = select(Liability).where(
                Liability.primary_account_id == account.id, Liability.recurring == True
            )
            recurring_bills = (await self.db.execute(recurring_query)).scalars().all()

            for bill in recurring_bills:
                # Generate recurring instances within date range
                current_date = bill.due_date
                while current_date <= end_date:
                    if current_date >= start_date:
                        transactions.append(
                            {
                                "date": current_date,
                                "amount": -bill.amount,
                                "description": f"Recurring Bill: {bill.name}",
                                "type": "recurring_bill",
                            }
                        )
                    # Advance to next occurrence
                    next_month = current_date.month + 1
                    next_year = current_date.year
                    if next_month > 12:
                        next_month = 1
                        next_year += 1
                    current_date = date(next_year, next_month, current_date.day)

        # Sort transactions by date
        return sorted(transactions, key=lambda x: x["date"])
