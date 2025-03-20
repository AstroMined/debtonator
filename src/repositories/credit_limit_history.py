"""
Repository for credit limit history operations.

This module provides a repository for managing credit limit history records,
with specialized methods for tracking credit limit changes over time.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models.credit_limit_history import CreditLimitHistory
from src.repositories.base import BaseRepository


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
        query = (
            select(CreditLimitHistory)
            .where(CreditLimitHistory.account_id == account_id)
            .order_by(CreditLimitHistory.effective_date.desc())
            .limit(limit)
        )
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
        self, account_id: int, start_date: datetime, end_date: datetime
    ) -> List[CreditLimitHistory]:
        """
        Get credit limit history entries within a date range.

        Args:
            account_id (int): Account ID to get history for
            start_date (datetime): Start date for range (inclusive)
            end_date (datetime): End date for range (inclusive)

        Returns:
            List[CreditLimitHistory]: List of credit limit history entries
        """
        query = (
            select(CreditLimitHistory)
            .where(
                CreditLimitHistory.account_id == account_id,
                CreditLimitHistory.effective_date >= start_date,
                CreditLimitHistory.effective_date <= end_date,
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
        self, account_id: int, target_date: datetime
    ) -> Optional[CreditLimitHistory]:
        """
        Get the credit limit that was effective at a specific date.

        Args:
            account_id (int): Account ID to get limit for
            target_date (datetime): Date to get limit at

        Returns:
            Optional[CreditLimitHistory]: History entry or None
        """
        query = (
            select(CreditLimitHistory)
            .where(
                CreditLimitHistory.account_id == account_id,
                CreditLimitHistory.effective_date <= target_date,
            )
            .order_by(CreditLimitHistory.effective_date.desc())
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_limit_increases(
        self, account_id: int, since_date: Optional[datetime] = None
    ) -> List[CreditLimitHistory]:
        """
        Get credit limit increases for an account.

        Args:
            account_id (int): Account ID to get increases for
            since_date (datetime, optional): Only get increases since this date

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
            query = query.where(CreditLimitHistory.effective_date >= since_date)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_limit_decreases(
        self, account_id: int, since_date: Optional[datetime] = None
    ) -> List[CreditLimitHistory]:
        """
        Get credit limit decreases for an account.

        Args:
            account_id (int): Account ID to get decreases for
            since_date (datetime, optional): Only get decreases since this date

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
            query = query.where(CreditLimitHistory.effective_date >= since_date)

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
        self, account_id: int, start_date: datetime, end_date: datetime
    ) -> Optional[Decimal]:
        """
        Calculate the average credit limit over a period.

        Args:
            account_id (int): Account ID to calculate for
            start_date (datetime): Start date for period
            end_date (datetime): End date for period

        Returns:
            Optional[Decimal]: Average credit limit or None if no data
        """
        history_entries = await self.get_by_date_range(account_id, start_date, end_date)

        if not history_entries:
            return None

        total = sum(entry.credit_limit for entry in history_entries)
        return total / len(history_entries)
