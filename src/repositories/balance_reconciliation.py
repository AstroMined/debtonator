"""
Repository for balance reconciliation operations.

This module provides a repository for managing balance reconciliation records,
which track manual adjustments to account balances and their justifications.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models.balance_reconciliation import BalanceReconciliation
from src.repositories.base import BaseRepository
from src.utils.datetime_utils import days_ago, utc_now


class BalanceReconciliationRepository(BaseRepository[BalanceReconciliation, int]):
    """
    Repository for balance reconciliation operations.

    This repository handles CRUD operations and specialized queries for
    BalanceReconciliation records, which track balance adjustments.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session (AsyncSession): Database session for operations
        """
        super().__init__(session, BalanceReconciliation)

    async def get_by_account(
        self, account_id: int, limit: int = 100
    ) -> List[BalanceReconciliation]:
        """
        Get balance reconciliation entries for an account.

        Args:
            account_id (int): Account ID to get entries for
            limit (int, optional): Maximum number of entries to return

        Returns:
            List[BalanceReconciliation]: List of balance reconciliation entries
        """
        query = (
            select(BalanceReconciliation)
            .where(BalanceReconciliation.account_id == account_id)
            .order_by(BalanceReconciliation.reconciliation_date.desc())
            .limit(limit)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_with_account(self, id: int) -> Optional[BalanceReconciliation]:
        """
        Get a balance reconciliation entry with account relationship loaded.

        Args:
            id (int): ID of the reconciliation entry

        Returns:
            Optional[BalanceReconciliation]: Entry with account loaded or None
        """
        return await self.get_with_joins(id, relationships=["account"])

    async def get_by_date_range(
        self, account_id: int, start_date: datetime, end_date: datetime
    ) -> List[BalanceReconciliation]:
        """
        Get balance reconciliation entries within a date range.

        Args:
            account_id (int): Account ID to get entries for
            start_date (datetime): Start date for range (inclusive)
            end_date (datetime): End date for range (inclusive)

        Returns:
            List[BalanceReconciliation]: List of reconciliation entries
        """
        query = (
            select(BalanceReconciliation)
            .where(
                BalanceReconciliation.account_id == account_id,
                BalanceReconciliation.reconciliation_date >= start_date,
                BalanceReconciliation.reconciliation_date <= end_date,
            )
            .order_by(BalanceReconciliation.reconciliation_date)
        )
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_most_recent(self, account_id: int) -> Optional[BalanceReconciliation]:
        """
        Get the most recent balance reconciliation for an account.

        Args:
            account_id (int): Account ID to get reconciliation for

        Returns:
            Optional[BalanceReconciliation]: Most recent entry or None
        """
        query = (
            select(BalanceReconciliation)
            .where(BalanceReconciliation.account_id == account_id)
            .order_by(BalanceReconciliation.reconciliation_date.desc())
            .limit(1)
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_largest_adjustments(
        self, account_id: Optional[int] = None, limit: int = 10
    ) -> List[BalanceReconciliation]:
        """
        Get largest balance adjustments by absolute value.

        Args:
            account_id (int, optional): Account ID to filter by
            limit (int, optional): Maximum number of entries to return

        Returns:
            List[BalanceReconciliation]: List of largest adjustments
        """
        query = (
            select(BalanceReconciliation)
            .order_by(func.abs(BalanceReconciliation.adjustment_amount).desc())
            .limit(limit)
        )

        if account_id is not None:
            query = query.where(BalanceReconciliation.account_id == account_id)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_total_adjustment_amount(
        self,
        account_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Decimal:
        """
        Calculate total adjustment amount for an account.

        Args:
            account_id (int): Account ID to calculate for
            start_date (datetime, optional): Start date for filtering
            end_date (datetime, optional): End date for filtering

        Returns:
            Decimal: Total adjustment amount
        """
        query = select(func.sum(BalanceReconciliation.adjustment_amount)).where(
            BalanceReconciliation.account_id == account_id
        )

        if start_date:
            query = query.where(BalanceReconciliation.reconciliation_date >= start_date)

        if end_date:
            query = query.where(BalanceReconciliation.reconciliation_date <= end_date)

        result = await self.session.execute(query)
        total = result.scalar_one_or_none()
        return total or Decimal("0.0")

    async def get_adjustment_count_by_reason(
        self, account_id: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Count adjustments grouped by reason.

        Args:
            account_id (int, optional): Account ID to filter by

        Returns:
            Dict[str, int]: Count of adjustments by reason
        """
        query = select(
            BalanceReconciliation.reason,
            func.count(BalanceReconciliation.id).label("count"),
        ).group_by(BalanceReconciliation.reason)

        if account_id is not None:
            query = query.where(BalanceReconciliation.account_id == account_id)

        result = await self.session.execute(query)
        reason_counts = {row[0]: row[1] for row in result.fetchall()}
        return reason_counts

    async def get_reconciliation_frequency(
        self, account_id: int, lookback_days: int = 365
    ) -> float:
        """
        Calculate average days between reconciliations.

        Args:
            account_id (int): Account ID to calculate for
            lookback_days (int, optional): Number of days to look back

        Returns:
            float: Average days between reconciliations or 0 if insufficient data
        """
        start_date = days_ago(days=lookback_days)

        reconciliations = await self.get_by_date_range(
            account_id, start_date, utc_now()
        )

        if len(reconciliations) < 2:
            return 0

        # Sort by date ascending
        reconciliations.sort(key=lambda r: r.reconciliation_date)

        # Calculate differences in days
        day_diffs = []
        for i in range(1, len(reconciliations)):
            prev_date = reconciliations[i - 1].reconciliation_date
            curr_date = reconciliations[i].reconciliation_date
            diff_days = (curr_date - prev_date).total_seconds() / (60 * 60 * 24)
            day_diffs.append(diff_days)

        # Calculate average
        return sum(day_diffs) / len(day_diffs)
