"""
Balance history repository implementation.

This module provides a repository for BalanceHistory model CRUD operations and specialized
balance history-related queries.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models.balance_history import BalanceHistory
from src.repositories.base_repository import BaseRepository
from src.utils.datetime_utils import date_in_collection, normalize_db_date, utc_now


class BalanceHistoryRepository(BaseRepository[BalanceHistory, int]):
    """
    Repository for BalanceHistory model operations.

    This repository handles CRUD operations for balance history records and provides specialized
    queries for balance history-related functionality.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session (AsyncSession): SQLAlchemy async session
        """
        super().__init__(session, BalanceHistory)

    async def get_by_account(
        self, account_id: int, limit: int = 30
    ) -> List[BalanceHistory]:
        """
        Get balance history for an account.

        Args:
            account_id (int): Account ID
            limit (int): Maximum number of records to return

        Returns:
            List[BalanceHistory]: List of balance history records
        """
        result = await self.session.execute(
            select(BalanceHistory)
            .where(BalanceHistory.account_id == account_id)
            .order_by(desc(BalanceHistory.timestamp))
            .limit(limit)
        )
        return result.scalars().all()

    async def get_latest_balance(self, account_id: int) -> Optional[BalanceHistory]:
        """
        Get latest balance record for an account.

        Args:
            account_id (int): Account ID

        Returns:
            Optional[BalanceHistory]: Latest balance record or None
        """
        result = await self.session.execute(
            select(BalanceHistory)
            .where(BalanceHistory.account_id == account_id)
            .order_by(desc(BalanceHistory.timestamp))
            .limit(1)
        )
        return result.scalars().first()

    async def get_with_account(self, balance_id: int) -> Optional[BalanceHistory]:
        """
        Get balance history with associated account.

        Args:
            balance_id (int): Balance history ID

        Returns:
            Optional[BalanceHistory]: Balance with account or None
        """
        result = await self.session.execute(
            select(BalanceHistory)
            .options(joinedload(BalanceHistory.account))
            .where(BalanceHistory.id == balance_id)
        )
        return result.scalars().first()

    async def get_by_date_range(
        self, account_id: int, start_date: datetime, end_date: datetime
    ) -> List[BalanceHistory]:
        """
        Get balance history within a date range.

        Args:
            account_id (int): Account ID
            start_date (datetime): Start date (inclusive)
            end_date (datetime): End date (inclusive)

        Returns:
            List[BalanceHistory]: List of balance history records
        """
        result = await self.session.execute(
            select(BalanceHistory)
            .where(
                and_(
                    BalanceHistory.account_id == account_id,
                    BalanceHistory.timestamp >= start_date,
                    BalanceHistory.timestamp <= end_date,
                )
            )
            .order_by(BalanceHistory.timestamp)
        )
        return result.scalars().all()

    async def get_reconciled_balances(
        self, account_id: int, limit: int = 12
    ) -> List[BalanceHistory]:
        """
        Get reconciled balance records for an account.

        Args:
            account_id (int): Account ID
            limit (int): Maximum number of records to return

        Returns:
            List[BalanceHistory]: List of reconciled balance records
        """
        result = await self.session.execute(
            select(BalanceHistory)
            .where(
                and_(
                    BalanceHistory.account_id == account_id,
                    BalanceHistory.is_reconciled == True,
                )
            )
            .order_by(desc(BalanceHistory.timestamp))
            .limit(limit)
        )
        return result.scalars().all()

    async def get_min_max_balance(
        self, account_id: int, days: int = 30
    ) -> Tuple[Optional[BalanceHistory], Optional[BalanceHistory]]:
        """
        Get minimum and maximum balance records within specified days.

        Args:
            account_id (int): Account ID
            days (int): Number of days to look back

        Returns:
            Tuple[Optional[BalanceHistory], Optional[BalanceHistory]]: (min_balance, max_balance)
        """
        # Get date range
        end_date = utc_now()
        start_date = end_date - timedelta(days=days)

        # Get all balances in the range
        balances = await self.get_by_date_range(account_id, start_date, end_date)

        if not balances:
            return None, None

        # Find min and max
        min_balance = min(balances, key=lambda x: x.balance)
        max_balance = max(balances, key=lambda x: x.balance)

        return min_balance, max_balance

    async def get_balance_trend(
        self, account_id: int, days: int = 30
    ) -> List[Tuple[datetime, Decimal]]:
        """
        Get balance trend over time.

        Args:
            account_id (int): Account ID
            days (int): Number of days of history

        Returns:
            List[Tuple[datetime, Decimal]]: List of (timestamp, balance) tuples
        """
        # Get date range
        end_date = utc_now()
        start_date = end_date - timedelta(days=days)

        balances = await self.get_by_date_range(account_id, start_date, end_date)
        return [(b.timestamp, b.balance) for b in balances]

    async def get_average_balance(
        self, account_id: int, days: int = 30
    ) -> Optional[Decimal]:
        """
        Get average balance over specified period.

        Args:
            account_id (int): Account ID
            days (int): Number of days to average

        Returns:
            Optional[Decimal]: Average balance or None
        """
        # Get date range
        end_date = utc_now()
        start_date = end_date - timedelta(days=days)

        # Query for average balance
        result = await self.session.execute(
            select(func.avg(BalanceHistory.balance)).where(
                and_(
                    BalanceHistory.account_id == account_id,
                    BalanceHistory.timestamp >= start_date,
                    BalanceHistory.timestamp <= end_date,
                )
            )
        )
        return result.scalar_one_or_none()

    async def get_balance_history_with_notes(
        self, account_id: int, limit: int = 10
    ) -> List[BalanceHistory]:
        """
        Get balance history records with notes.

        Args:
            account_id (int): Account ID
            limit (int): Maximum number of records to return

        Returns:
            List[BalanceHistory]: List of balance history records with notes
        """
        result = await self.session.execute(
            select(BalanceHistory)
            .where(
                and_(
                    BalanceHistory.account_id == account_id,
                    BalanceHistory.notes.isnot(None),
                    BalanceHistory.notes != "",
                )
            )
            .order_by(desc(BalanceHistory.timestamp))
            .limit(limit)
        )
        return result.scalars().all()

    async def mark_as_reconciled(
        self, balance_id: int, reconciled: bool = True
    ) -> Optional[BalanceHistory]:
        """
        Mark a balance record as reconciled or unreconciled.

        Args:
            balance_id (int): Balance history ID
            reconciled (bool): Reconciliation status

        Returns:
            Optional[BalanceHistory]: Updated balance record or None if not found
        """
        return await self.update(balance_id, {"is_reconciled": reconciled})

    async def add_balance_note(
        self, balance_id: int, note: str
    ) -> Optional[BalanceHistory]:
        """
        Add or update note for a balance record.

        Args:
            balance_id (int): Balance history ID
            note (str): Note text

        Returns:
            Optional[BalanceHistory]: Updated balance record or None if not found
        """
        return await self.update(balance_id, {"notes": note})

    async def get_missing_days(self, account_id: int, days: int = 30) -> List[date]:
        """
        Find days with no balance records within a period.

        Args:
            account_id (int): Account ID
            days (int): Number of days to check

        Returns:
            List[date]: List of dates with no balance records
        """

        # Normalize to start of day for consistent day counting
        today = utc_now().replace(hour=0, minute=0, second=0, microsecond=0)
        end_date = today
        start_date = today - timedelta(days=days)

        # Get all dates with balance records
        result = await self.session.execute(
            select(func.date(BalanceHistory.timestamp))
            .where(
                and_(
                    BalanceHistory.account_id == account_id,
                    BalanceHistory.timestamp >= start_date,
                    BalanceHistory.timestamp <= end_date,
                )
            )
            .group_by(func.date(BalanceHistory.timestamp))
        )

        # Process results to normalize date format using our utility
        recorded_dates = []
        for row in result.all():
            date_val = row[0]
            # Use our utility to handle any date format from the database
            normalized_date = normalize_db_date(date_val)
            recorded_dates.append(normalized_date)

        # Find missing dates
        missing_dates = []
        current_date = start_date.date()
        end = end_date.date()

        while current_date <= end:
            if not date_in_collection(current_date, recorded_dates):
                missing_dates.append(current_date)
            current_date += timedelta(days=1)

        return missing_dates

    async def get_available_credit_trend(
        self, account_id: int, days: int = 30
    ) -> List[Tuple[datetime, Optional[Decimal]]]:
        """
        Get available credit trend over time.

        Args:
            account_id (int): Account ID
            days (int): Number of days of history

        Returns:
            List[Tuple[datetime, Optional[Decimal]]]: List of (timestamp, available_credit) tuples
        """
        # Get date range
        end_date = utc_now()
        start_date = end_date - timedelta(days=days)

        balances = await self.get_by_date_range(account_id, start_date, end_date)
        return [(b.timestamp, b.available_credit) for b in balances]
