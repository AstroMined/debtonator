from datetime import date, datetime
from decimal import Decimal
from typing import Dict, List, Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.schemas.cashflow import (AccountForecastRequest,
                                  AccountForecastResponse,
                                  CustomForecastParameters,
                                  CustomForecastResponse,
                                  HistoricalTrendsResponse)

from .base import BaseService
from .forecast_service import ForecastService
from .historical_service import HistoricalService
from .metrics_service import MetricsService
from .transaction_service import TransactionService
from .types import DateType


class CashflowService(BaseService):
    """Main cashflow service that delegates to specialized services."""

    def __init__(self, db: AsyncSession):
        """Initialize the cashflow service with specialized sub-services.

        Args:
            db: SQLAlchemy async session for database operations
        """
        super().__init__(db)
        self._forecast = ForecastService(db)
        self._historical = HistoricalService(db)
        self._metrics = MetricsService(db)
        self._transactions = TransactionService(db)

    # Forecast Methods
    async def get_account_forecast(
        self, params: AccountForecastRequest
    ) -> AccountForecastResponse:
        """Get account-specific forecast."""
        return await self._forecast.get_account_forecast(params)

    async def get_custom_forecast(
        self, params: CustomForecastParameters
    ) -> CustomForecastResponse:
        """Get custom forecast based on parameters."""
        return await self._forecast.get_custom_forecast(params)

    # Historical Analysis Methods
    async def get_historical_trends(
        self, account_ids: List[int], start_date: DateType, end_date: DateType
    ) -> HistoricalTrendsResponse:
        """Get historical trends analysis."""
        return await self._historical.get_historical_trends(
            account_ids, start_date, end_date
        )

    # Metrics Methods
    async def get_metrics_for_date(
        self, target_date: DateType
    ) -> Optional[CustomForecastResponse]:
        """Get metrics for a specific date."""
        return await self._metrics.get_metrics_for_date(target_date)

    async def calculate_required_funds(
        self, account_id: int, start_date: DateType, end_date: DateType
    ) -> Decimal:
        """Calculate required funds for date range."""
        return await self._metrics.calculate_required_funds(
            account_id, start_date, end_date
        )

    def calculate_daily_deficit(self, min_amount: Decimal, days: int) -> Decimal:
        """Calculate daily deficit needed."""
        return self._metrics.calculate_daily_deficit(min_amount, days)

    def calculate_yearly_deficit(self, daily_deficit: Decimal) -> Decimal:
        """Calculate yearly deficit."""
        return self._metrics.calculate_yearly_deficit(daily_deficit)

    def calculate_required_income(
        self, yearly_deficit: Decimal, tax_rate: Decimal = Decimal("0.80")
    ) -> Decimal:
        """Calculate required gross income."""
        return self._metrics.calculate_required_income(yearly_deficit, tax_rate)

    # Transaction Methods
    async def get_day_transactions(
        self,
        account_id: int,
        target_date: DateType,
        include_pending: bool = True,
        include_recurring: bool = True,
        include_transfers: bool = True,
    ) -> List[Dict]:
        """Get transactions for a specific day."""
        account = await self.db.get(Account, account_id)
        if not account:
            raise ValueError(f"Account with id {account_id} not found")
        return await self._transactions.get_day_transactions(
            account, target_date, include_pending, include_recurring, include_transfers
        )

    async def get_historical_transactions(
        self, account_ids: List[int], start_date: DateType, end_date: DateType
    ) -> List[Dict]:
        """Get historical transactions for analysis."""
        return await self._transactions.get_historical_transactions(
            account_ids, start_date, end_date
        )

    async def get_projected_transactions(
        self,
        account_id: int,
        start_date: DateType,
        end_date: DateType,
        include_pending: bool = True,
        include_recurring: bool = True,
    ) -> List[Dict]:
        """Get projected transactions for date range."""
        account = await self.db.get(Account, account_id)
        if not account:
            raise ValueError(f"Account with id {account_id} not found")
        return await self._transactions.get_projected_transactions(
            account, start_date, end_date, include_pending, include_recurring
        )
