"""
Repository for transaction history operations.

This module provides a repository for managing transaction history records,
which track account transactions such as credits and debits.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models.transaction_history import TransactionHistory, TransactionType
from src.repositories.base import BaseRepository


class TransactionHistoryRepository(BaseRepository[TransactionHistory, int]):
    """
    Repository for transaction history operations.

    This repository handles CRUD operations and specialized queries for
    TransactionHistory records, which track account transactions.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session (AsyncSession): Database session for operations
        """
        super().__init__(session, TransactionHistory)

    async def get_debit_sum_for_account(self, account_id: int) -> Decimal:
        """
        Get sum of debit transactions for an account.

        Args:
            account_id (int): Account ID to get sum for

        Returns:
            Decimal: Sum of debit transactions
        """
        return await self.get_total_by_type(account_id, TransactionType.DEBIT)

    async def get_credit_sum_for_account(self, account_id: int) -> Decimal:
        """
        Get sum of credit transactions for an account.

        Args:
            account_id (int): Account ID to get sum for

        Returns:
            Decimal: Sum of credit transactions
        """
        return await self.get_total_by_type(account_id, TransactionType.CREDIT)

    async def get_by_account(
        self, account_id: int, limit: int = 100
    ) -> List[TransactionHistory]:
        """
        Get transaction history for an account.

        Args:
            account_id (int): Account ID to get transactions for
            limit (int, optional): Maximum number of transactions to return

        Returns:
            List[TransactionHistory]: List of transactions
        """
        query = (
            select(TransactionHistory)
            .where(TransactionHistory.account_id == account_id)
            .order_by(TransactionHistory.transaction_date.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_with_account(self, id: int) -> Optional[TransactionHistory]:
        """
        Get a transaction with account relationship loaded.

        Args:
            id (int): Transaction ID

        Returns:
            Optional[TransactionHistory]: Transaction with account or None
        """
        return await self.get_with_joins(id, relationships=["account"])

    async def get_by_date_range(
        self, account_id: int, start_date: datetime, end_date: datetime
    ) -> List[TransactionHistory]:
        """
        Get transactions within a date range.

        Args:
            account_id (int): Account ID to get transactions for
            start_date (datetime): Start date for range (inclusive)
            end_date (datetime): End date for range (inclusive)

        Returns:
            List[TransactionHistory]: List of transactions
        """
        query = (
            select(TransactionHistory)
            .where(
                TransactionHistory.account_id == account_id,
                TransactionHistory.transaction_date >= start_date,
                TransactionHistory.transaction_date <= end_date,
            )
            .order_by(TransactionHistory.transaction_date)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_by_type(
        self, account_id: int, transaction_type: TransactionType, limit: int = 100
    ) -> List[TransactionHistory]:
        """
        Get transactions of a specific type.

        Args:
            account_id (int): Account ID to get transactions for
            transaction_type (TransactionType): Type of transactions to get
            limit (int, optional): Maximum number of transactions to return

        Returns:
            List[TransactionHistory]: List of transactions
        """
        query = (
            select(TransactionHistory)
            .where(
                TransactionHistory.account_id == account_id,
                TransactionHistory.transaction_type == transaction_type,
            )
            .order_by(TransactionHistory.transaction_date.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def search_by_description(
        self, account_id: int, search_term: str, limit: int = 100
    ) -> List[TransactionHistory]:
        """
        Search transactions by description.

        Args:
            account_id (int): Account ID to search transactions for
            search_term (str): Term to search for in description
            limit (int, optional): Maximum number of transactions to return

        Returns:
            List[TransactionHistory]: List of matching transactions
        """
        query = (
            select(TransactionHistory)
            .where(
                TransactionHistory.account_id == account_id,
                TransactionHistory.description.ilike(f"%{search_term}%"),
            )
            .order_by(TransactionHistory.transaction_date.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_total_by_type(
        self,
        account_id: int,
        transaction_type: TransactionType,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Decimal:
        """
        Calculate total amount for transactions of a specific type.

        Args:
            account_id (int): Account ID to calculate for
            transaction_type (TransactionType): Type of transactions to sum
            start_date (datetime, optional): Start date for filtering
            end_date (datetime, optional): End date for filtering

        Returns:
            Decimal: Total amount
        """
        query = select(func.sum(TransactionHistory.amount)).where(
            TransactionHistory.account_id == account_id,
            TransactionHistory.transaction_type == transaction_type,
        )

        if start_date:
            query = query.where(TransactionHistory.transaction_date >= start_date)

        if end_date:
            query = query.where(TransactionHistory.transaction_date <= end_date)

        result = await self.session.execute(query)
        total = result.scalar_one_or_none()
        return total or Decimal("0.0")

    async def get_transaction_count(
        self,
        account_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, int]:
        """
        Count transactions by type.

        Args:
            account_id (int): Account ID to count for
            start_date (datetime, optional): Start date for filtering
            end_date (datetime, optional): End date for filtering

        Returns:
            Dict[str, int]: Count of transactions by type
        """
        query = (
            select(
                TransactionHistory.transaction_type,
                func.count(TransactionHistory.id).label("count"),
            )
            .where(TransactionHistory.account_id == account_id)
            .group_by(TransactionHistory.transaction_type)
        )

        if start_date:
            query = query.where(TransactionHistory.transaction_date >= start_date)

        if end_date:
            query = query.where(TransactionHistory.transaction_date <= end_date)

        result = await self.session.execute(query)
        type_counts = {row[0].value: row[1] for row in result.fetchall()}

        # Ensure both types are in the result
        if TransactionType.CREDIT.value not in type_counts:
            type_counts[TransactionType.CREDIT.value] = 0
        if TransactionType.DEBIT.value not in type_counts:
            type_counts[TransactionType.DEBIT.value] = 0

        return type_counts

    async def get_net_change(
        self,
        account_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Decimal:
        """
        Calculate net change in account balance from transactions.

        Args:
            account_id (int): Account ID to calculate for
            start_date (datetime, optional): Start date for filtering
            end_date (datetime, optional): End date for filtering

        Returns:
            Decimal: Net change (positive for net increase, negative for net decrease)
        """
        # Get total credits
        credits = await self.get_total_by_type(
            account_id, TransactionType.CREDIT, start_date, end_date
        )

        # Get total debits
        debits = await self.get_total_by_type(
            account_id, TransactionType.DEBIT, start_date, end_date
        )

        # Calculate net change (credits - debits)
        return credits - debits

    async def get_monthly_totals(
        self, account_id: int, months: int = 2
    ) -> List[Dict[str, Any]]:
        """
        Get monthly transaction totals.

        Args:
            account_id (int): Account ID to get totals for
            months (int, optional): Number of months to include (default: 2)

        Returns:
            List[Dict[str, Any]]: Monthly totals with credits, debits, and net
        """
        # Calculate date range
        from datetime import datetime, timezone, timedelta
        from decimal import Decimal
        
        end_date = datetime.now(timezone.utc)
        start_date = end_date - timedelta(days=30 * months)
        
        # Get raw transaction data using database-agnostic query
        # instead of using date_trunc SQL function which varies by database engine
        query = select(
            TransactionHistory.transaction_date,
            TransactionHistory.transaction_type,
            TransactionHistory.amount
        ).where(
            and_(
                TransactionHistory.account_id == account_id,
                TransactionHistory.transaction_date >= start_date,
                TransactionHistory.transaction_date <= end_date
            )
        )
        
        result = await self.session.execute(query)
        transactions = result.all()
        
        # Process with Python - database-agnostic solution that works
        # across SQLite, MySQL, PostgreSQL, etc.
        monthly_data = {}
        for transaction in transactions:
            # Format the month key
            month_key = transaction.transaction_date.strftime('%Y-%m')
            tx_type = transaction.transaction_type
            
            # Initialize if needed
            if month_key not in monthly_data:
                # Store first day of month as datetime for proper compatibility with test
                monthly_data[month_key] = {
                    "month": transaction.transaction_date.replace(day=1),
                    "credits": Decimal("0.0"),
                    "debits": Decimal("0.0"),
                    "net": Decimal("0.0"),
                }
                
            # Add to total based on transaction type
            if tx_type == TransactionType.CREDIT:
                monthly_data[month_key]["credits"] += transaction.amount
            else:
                monthly_data[month_key]["debits"] += transaction.amount
            
            # Update net change (credits - debits)
            monthly_data[month_key]["net"] = (
                monthly_data[month_key]["credits"] - monthly_data[month_key]["debits"]
            )
        
        # Convert to list sorted by month (matches expected test output format)
        return [v for k, v in sorted(monthly_data.items())]

    async def get_transaction_patterns(
        self, account_id: int, lookback_days: int = 90
    ) -> List[Dict[str, Any]]:
        """
        Identify recurring transaction patterns.

        Args:
            account_id (int): Account ID to analyze
            lookback_days (int, optional): Number of days to look back

        Returns:
            List[Dict[str, Any]]: Identified transaction patterns
        """
        # Get transactions within lookback period
        start_date = datetime.utcnow() - timedelta(days=lookback_days)
        transactions = await self.get_by_date_range(
            account_id, start_date, datetime.utcnow()
        )

        # Group transactions by description (simplified pattern detection)
        patterns = {}
        for tx in transactions:
            # Skip transactions with no description
            if not tx.description:
                continue

            key = tx.description.lower()
            if key not in patterns:
                patterns[key] = {
                    "description": tx.description,
                    "count": 0,
                    "average_amount": Decimal("0.0"),
                    "transaction_type": tx.transaction_type,
                    "occurrences": [],
                }

            patterns[key]["count"] += 1
            patterns[key]["occurrences"].append(
                {"date": tx.transaction_date, "amount": tx.amount}
            )

        # Calculate statistics for each pattern
        result = []
        for key, data in patterns.items():
            if data["count"] < 2:
                continue  # Skip one-time transactions

            # Calculate average amount
            total = sum(o["amount"] for o in data["occurrences"])
            data["average_amount"] = total / data["count"]

            # Calculate average days between occurrences
            if data["count"] > 1:
                dates = sorted([o["date"] for o in data["occurrences"]])
                day_diffs = []
                for i in range(1, len(dates)):
                    diff_days = (dates[i] - dates[i - 1]).total_seconds() / (
                        60 * 60 * 24
                    )
                    day_diffs.append(diff_days)

                data["average_days_between"] = sum(day_diffs) / len(day_diffs)

                # Estimate confidence (higher count and consistent intervals = higher confidence)
                count_factor = min(
                    data["count"] / 10, 1.0
                )  # Max 1.0 at 10+ occurrences

                # Check for consistency in intervals
                if day_diffs:
                    std_dev = (
                        sum(
                            (x - (sum(day_diffs) / len(day_diffs))) ** 2
                            for x in day_diffs
                        )
                        / len(day_diffs)
                    ) ** 0.5
                    consistency_factor = max(
                        0, 1.0 - (std_dev / 30)
                    )  # Lower std_dev = higher consistency
                else:
                    consistency_factor = 0.0

                data["confidence"] = (count_factor * 0.6) + (consistency_factor * 0.4)

                # Identify potential recurrence pattern
                if data["average_days_between"] > 0:
                    if 25 <= data["average_days_between"] <= 35:
                        data["pattern_type"] = "Monthly"
                    elif 6 <= data["average_days_between"] <= 8:
                        data["pattern_type"] = "Weekly"
                    elif 13 <= data["average_days_between"] <= 16:
                        data["pattern_type"] = "Bi-weekly"
                    else:
                        data["pattern_type"] = (
                            f'Every {round(data["average_days_between"])} days'
                        )

            result.append(data)

        # Sort by confidence (if available) or count
        return sorted(
            result,
            key=lambda x: x.get("confidence", 0) if "confidence" in x else x["count"],
            reverse=True,
        )

    async def bulk_create_transactions(
        self, account_id: int, transactions: List[Dict[str, Any]]
    ) -> List[TransactionHistory]:
        """
        Create multiple transactions for an account.

        Args:
            account_id (int): Account ID for transactions
            transactions (List[Dict[str, Any]]): List of transaction data

        Returns:
            List[TransactionHistory]: Created transaction records
        """
        # Add account_id to each transaction if not present
        for tx in transactions:
            if "account_id" not in tx:
                tx["account_id"] = account_id

        # Use bulk_create method from BaseRepository
        return await self.bulk_create(transactions)

    async def get_by_account_ordered(
        self, account_id: int, order_by_desc: bool = False, limit: int = 100
    ) -> List[TransactionHistory]:
        """
        Get transaction history entries for an account with ordering option.

        Args:
            account_id (int): Account ID to get history for
            order_by_desc (bool): Order by transaction_date descending if True
            limit (int, optional): Maximum number of entries to return

        Returns:
            List[TransactionHistory]: List of transaction history entries
        """
        query = select(TransactionHistory).where(
            TransactionHistory.account_id == account_id
        )

        if order_by_desc:
            query = query.order_by(TransactionHistory.transaction_date.desc())
        else:
            query = query.order_by(TransactionHistory.transaction_date)

        query = query.limit(limit)

        result = await self.session.execute(query)
        return result.scalars().all()
