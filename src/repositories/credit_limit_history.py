"""
Repository for credit limit history operations.

This module provides a repository for managing credit limit history records,
with specialized methods for tracking credit limit changes over time.
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.credit_limit_history import CreditLimitHistory
from src.repositories.base_repository import BaseRepository
from src.utils.datetime_utils import ensure_utc, naive_end_of_day, naive_start_of_day


class CreditLimitHistoryRepository(BaseRepository[CreditLimitHistory, int]):
    """
    Repository for credit limit history operations.

    This repository handles CRUD operations and specialized queries for
    CreditLimitHistory records, which track changes to credit limits over time.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session (AsyncSession): Database session for operations
        """
        super().__init__(session, CreditLimitHistory)

    async def get_by_account(
        self, account_id: int, limit: int = 100
    ) -> List[CreditLimitHistory]:
        """
        Get credit limit history entries for an account.

        Args:
            account_id (int): Account ID to get history for
            limit (int, optional): Maximum number of entries to return

        Returns:
            List[CreditLimitHistory]: List of credit limit history entries
        """
        return await self.get_by_account_ordered(
            account_id=account_id, order_by_desc=True, limit=limit
        )

    async def get_by_account_ordered(
        self, account_id: int, order_by_desc: bool = False, limit: int = 100
    ) -> List[CreditLimitHistory]:
        """
        Get credit limit history entries for an account with ordering option.

        Args:
            account_id (int): Account ID to get history for
            order_by_desc (bool): Order by effective_date descending if True
            limit (int, optional): Maximum number of entries to return

        Returns:
            List[CreditLimitHistory]: List of credit limit history entries
        """
        query = select(CreditLimitHistory).where(
            CreditLimitHistory.account_id == account_id
        )

        if order_by_desc:
            query = query.order_by(CreditLimitHistory.effective_date.desc())
        else:
            query = query.order_by(CreditLimitHistory.effective_date)

        query = query.limit(limit)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_with_account(self, id: int) -> Optional[CreditLimitHistory]:
        """
        Get a credit limit history entry with account relationship loaded.

        Args:
            id (int): ID of the credit limit history entry

        Returns:
            Optional[CreditLimitHistory]: History entry with account loaded or None
        """
        return await self.get_with_joins(id, relationships=["account"])

    async def get_by_date_range(
        self, account_id: int, start_date, end_date
    ) -> List[CreditLimitHistory]:
        """
        Get credit limit history entries within a date range.

        Args:
            account_id (int): Account ID to get history for
            start_date: Start date for range (inclusive)
            end_date: End date for range (inclusive)

        Returns:
            List[CreditLimitHistory]: List of credit limit history entries
        """
        # Following ADR-011, convert to naive datetimes for database queries
        # and ensure inclusive range semantics
        naive_start = naive_start_of_day(start_date)
        naive_end = naive_end_of_day(end_date)

        query = (
            select(CreditLimitHistory)
            .where(
                CreditLimitHistory.account_id == account_id,
                CreditLimitHistory.effective_date >= naive_start,
                CreditLimitHistory.effective_date <= naive_end,
            )
            .order_by(CreditLimitHistory.effective_date)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_latest_limit(self, account_id: int) -> Optional[CreditLimitHistory]:
        """
        Get the most recent credit limit history entry for an account.

        Args:
            account_id (int): Account ID to get latest limit for

        Returns:
            Optional[CreditLimitHistory]: Latest history entry or None
        """
        query = (
            select(CreditLimitHistory)
            .where(CreditLimitHistory.account_id == account_id)
            .order_by(CreditLimitHistory.effective_date.desc())
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_limit_at_date(
        self, account_id: int, target_date
    ) -> Optional[CreditLimitHistory]:
        """
        Get the credit limit that was effective at a specific date.

        Args:
            account_id (int): Account ID to get limit for
            target_date: Date to get limit at

        Returns:
            Optional[CreditLimitHistory]: History entry or None
        """
        # Ensure target_date is UTC-compliant per ADR-011
        target_date = ensure_utc(target_date)

        # Convert to naive for database query
        naive_target = target_date.replace(tzinfo=None)

        query = (
            select(CreditLimitHistory)
            .where(
                CreditLimitHistory.account_id == account_id,
                CreditLimitHistory.effective_date <= naive_target,
            )
            .order_by(CreditLimitHistory.effective_date.desc())
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_limit_increases(
        self, account_id: int, since_date=None
    ) -> List[CreditLimitHistory]:
        """
        Get credit limit increases for an account.

        Args:
            account_id (int): Account ID to get increases for
            since_date (optional): Only get increases since this date

        Returns:
            List[CreditLimitHistory]: List of credit limit increases
        """
        # Subquery to get previous limit
        prev_limits = (
            select(
                CreditLimitHistory.id,
                CreditLimitHistory.credit_limit,
                func.lag(CreditLimitHistory.credit_limit)
                .over(
                    partition_by=CreditLimitHistory.account_id,
                    order_by=CreditLimitHistory.effective_date,
                )
                .label("previous_limit"),
            )
            .where(CreditLimitHistory.account_id == account_id)
            .alias("prev_limits")
        )

        # Main query to get increases only
        query = (
            select(CreditLimitHistory)
            .join(prev_limits, CreditLimitHistory.id == prev_limits.c.id)
            .where(
                CreditLimitHistory.account_id == account_id,
                prev_limits.c.credit_limit > prev_limits.c.previous_limit,
            )
            .order_by(CreditLimitHistory.effective_date)
        )

        if since_date:
            # Following ADR-011, using naive datetime for database query
            naive_since = naive_start_of_day(since_date)
            query = query.where(CreditLimitHistory.effective_date >= naive_since)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_limit_decreases(
        self, account_id: int, since_date=None
    ) -> List[CreditLimitHistory]:
        """
        Get credit limit decreases for an account.

        Args:
            account_id (int): Account ID to get decreases for
            since_date (optional): Only get decreases since this date

        Returns:
            List[CreditLimitHistory]: List of credit limit decreases
        """
        # Subquery to get previous limit
        prev_limits = (
            select(
                CreditLimitHistory.id,
                CreditLimitHistory.credit_limit,
                func.lag(CreditLimitHistory.credit_limit)
                .over(
                    partition_by=CreditLimitHistory.account_id,
                    order_by=CreditLimitHistory.effective_date,
                )
                .label("previous_limit"),
            )
            .where(CreditLimitHistory.account_id == account_id)
            .alias("prev_limits")
        )

        # Main query to get decreases only
        query = (
            select(CreditLimitHistory)
            .join(prev_limits, CreditLimitHistory.id == prev_limits.c.id)
            .where(
                CreditLimitHistory.account_id == account_id,
                prev_limits.c.credit_limit < prev_limits.c.previous_limit,
            )
            .order_by(CreditLimitHistory.effective_date)
        )

        if since_date:
            # Following ADR-011, using naive datetime for database query
            naive_since = naive_start_of_day(since_date)
            query = query.where(CreditLimitHistory.effective_date >= naive_since)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_limit_change_trend(
        self, account_id: int, lookback_months: int = 12
    ) -> List[Dict[str, Any]]:
        """
        Get credit limit change trend over time.

        Args:
            account_id (int): Account ID to get trend for
            lookback_months (int, optional): Number of months to look back

        Returns:
            List[Dict[str, Any]]: List of limit changes with trend data
        """
        # Get history entries ordered by date
        history_entries = await self.get_by_account(account_id)

        # Process into trend data
        trend_data = []

        for i, entry in enumerate(history_entries):
            # Calculate change from previous
            change = None
            change_percent = None

            if i > 0:
                previous = history_entries[i - 1]
                change = entry.credit_limit - previous.credit_limit
                if previous.credit_limit > 0:
                    change_percent = (change / previous.credit_limit) * 100

            trend_data.append(
                {
                    "date": entry.effective_date,
                    "credit_limit": entry.credit_limit,
                    "change": change,
                    "change_percent": change_percent,
                    "reason": entry.reason,
                }
            )

        return trend_data

    async def calculate_average_credit_limit(
        self, account_id: int, start_date, end_date
    ) -> Optional[Decimal]:
        """
        Calculate the average credit limit over a period.

        Args:
            account_id (int): Account ID to calculate for
            start_date: Start date for period
            end_date: End date for period

        Returns:
            Optional[Decimal]: Average credit limit or None if no data
        """
        history_entries = await self.get_by_date_range(account_id, start_date, end_date)

        if not history_entries:
            return None

        total = sum(entry.credit_limit for entry in history_entries)
        return total / len(history_entries)
