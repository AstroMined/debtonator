"""
Repository for cashflow metrics operations.

This module provides a repository for cashflow metrics operations,
including required funds calculation, deficit analysis, and other metrics.
"""

from decimal import Decimal
from typing import Dict, List

from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.cashflow import CashflowForecast
from src.models.liabilities import Liability
from src.models.payments import Payment
from src.repositories.cashflow.cashflow_base import CashflowBaseRepository
from src.utils.datetime_utils import days_ago, utc_now
from src.utils.decimal_precision import DecimalPrecision


class CashflowMetricsRepository(CashflowBaseRepository[CashflowForecast]):
    """
    Repository for cashflow metrics operations.

    This repository provides methods for calculating and retrieving various
    cashflow metrics, including required funds, deficits, and confidence scores.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize the cashflow metrics repository.

        Args:
            session (AsyncSession): SQLAlchemy async session
        """
        super().__init__(session, CashflowForecast)

    async def get_required_funds(
        self, account_id: int, start_date, end_date
    ) -> Decimal:
        """
        Calculate total required funds for bills in the specified date range.

        Args:
            account_id (int): Account ID to calculate for
            start_date: Start date of range
            end_date: End date of range

        Returns:
            Decimal: Total required funds
        """
        # Prepare date range using helper from base repository
        range_start, range_end = self._prepare_date_range(start_date, end_date)

        # Build query for unpaid liabilities in date range for account
        query = (
            select(func.sum(Liability.amount))
            .outerjoin(Payment)
            .where(
                Liability.primary_account_id == account_id,
                Liability.due_date >= range_start,
                Liability.due_date <= range_end,
                Payment.id == None,  # No associated payments
            )
        )

        # Execute query and get result
        result = await self.session.execute(query)
        total = result.scalar_one_or_none() or Decimal("0.0000")

        # Use 4 decimal precision for internal calculations
        return DecimalPrecision.round_for_calculation(total)

    async def get_all_accounts(self) -> List[Account]:
        """
        Get all active accounts in the system.

        Returns:
            List[Account]: List of all accounts
        """
        # Query for all accounts
        query = select(Account)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_liabilities_for_metrics(
        self, account_id: int, start_date, end_date
    ) -> List[Liability]:
        """
        Get unpaid liabilities for an account in the specified date range.

        Args:
            account_id (int): Account ID to get liabilities for
            start_date: Start date of range
            end_date: End date of range

        Returns:
            List[Liability]: List of unpaid liabilities
        """
        # Prepare date range using helper from base repository
        range_start, range_end = self._prepare_date_range(start_date, end_date)

        # Build query for unpaid liabilities in date range for account
        query = (
            select(Liability)
            .outerjoin(Payment)
            .where(
                Liability.primary_account_id == account_id,
                Liability.due_date >= range_start,
                Liability.due_date <= range_end,
                Payment.id == None,  # No associated payments
            )
            .order_by(Liability.due_date)
        )

        # Execute query and get results
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_min_forecast_values(self, days: int = 90) -> Dict[str, Decimal]:
        """
        Get minimum forecast values across all lookout periods.

        Args:
            days (int): Number of days to consider (default: 90)

        Returns:
            Dict[str, Decimal]: Dictionary with minimum values for each lookout period
        """
        # Calculate date range
        end_date = await self.utc_now()
        start_date = await self.days_ago(days)

        # Prepare date range for database query
        range_start, range_end = self._prepare_date_range(start_date, end_date)

        # Query for minimum values
        result = await self.session.execute(
            select(
                func.min(CashflowForecast.min_14_day).label("min_14_day"),
                func.min(CashflowForecast.min_30_day).label("min_30_day"),
                func.min(CashflowForecast.min_60_day).label("min_60_day"),
                func.min(CashflowForecast.min_90_day).label("min_90_day"),
            ).where(
                and_(
                    CashflowForecast.forecast_date >= range_start,
                    CashflowForecast.forecast_date <= range_end,
                )
            )
        )

        # Process results
        row = result.one()
        return {
            "min_14_day": row.min_14_day or Decimal("0.00"),
            "min_30_day": row.min_30_day or Decimal("0.00"),
            "min_60_day": row.min_60_day or Decimal("0.00"),
            "min_90_day": row.min_90_day or Decimal("0.00"),
        }

    # Helper methods for date manipulation with proper async interfaces

    async def utc_now(self):
        """
        Get current UTC datetime.

        Returns:
            datetime: Current UTC datetime
        """
        return utc_now()

    async def days_ago(self, days: int):
        """
        Get datetime for specified number of days ago.

        Args:
            days (int): Number of days ago

        Returns:
            datetime: Datetime for specified number of days ago
        """
        return days_ago(days)
