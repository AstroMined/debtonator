"""
Cashflow Forecast repository implementation.

This module provides a repository for CashflowForecast model operations and specialized
forecast-related queries.
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.cashflow import CashflowForecast
from src.repositories.cashflow.base import BaseCashflowRepository
from src.utils.datetime_utils import (
    days_ago,
    days_from_now,
    naive_end_of_day,
    naive_start_of_day,
    utc_now,
)


class CashflowForecastRepository(BaseCashflowRepository[CashflowForecast]):
    """
    Repository for CashflowForecast model operations.

    This repository handles CRUD operations for cashflow forecasts and provides specialized
    queries for forecast-related functionality, including trend analysis and financial metrics.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session (AsyncSession): SQLAlchemy async session
        """
        super().__init__(session, CashflowForecast)

    # Core forecast retrieval methods

    async def get_by_date(self, forecast_date) -> Optional[CashflowForecast]:
        """
        Get forecast for a specific date.

        If multiple forecasts exist for the same date (rare), the most recently created is returned.

        Args:
            forecast_date (datetime): Date to get forecast for (time component is ignored)

        Returns:
            Optional[CashflowForecast]: Forecast for the specified date or None
        """
        # Extract date part only for comparison
        day_start = naive_start_of_day(forecast_date)
        day_end = naive_end_of_day(forecast_date)  # Use end_of_day for inclusive range

        result = await self.session.execute(
            select(CashflowForecast)
            .where(
                and_(
                    CashflowForecast.forecast_date >= day_start,
                    CashflowForecast.forecast_date <= day_end,
                )
            )
            .order_by(desc(CashflowForecast.created_at))
        )
        return result.scalars().first()

    async def get_by_date_range(
        self, start_date, end_date
    ) -> List[CashflowForecast]:
        """
        Get forecasts within a date range.

        If multiple forecasts exist for the same date, the most recently created is used.

        Args:
            start_date (datetime): Start date (inclusive)
            end_date (datetime): End date (inclusive)

        Returns:
            List[CashflowForecast]: List of forecasts within the date range
        """
        # Prepare date range using helper from base repository
        range_start, range_end = self._prepare_date_range(start_date, end_date)

        # Get the distinct dates in the range
        date_subquery = (
            select(
                func.date(CashflowForecast.forecast_date).label("forecast_day"),
                func.max(CashflowForecast.created_at).label("latest_created"),
            )
            .where(
                and_(
                    CashflowForecast.forecast_date >= range_start,
                    CashflowForecast.forecast_date <= range_end,  # Use <= for inclusive end date per ADR-011
                )
            )
            .group_by(func.date(CashflowForecast.forecast_date))
            .subquery()
        )

        # Join with the main table to get the latest forecast for each day
        result = await self.session.execute(
            select(CashflowForecast)
            .join(
                date_subquery,
                and_(
                    func.date(CashflowForecast.forecast_date)
                    == date_subquery.c.forecast_day,
                    CashflowForecast.created_at == date_subquery.c.latest_created,
                ),
            )
            .order_by(CashflowForecast.forecast_date)
        )
        return result.scalars().all()

    async def get_latest_forecast(self) -> Optional[CashflowForecast]:
        """
        Get the most recent forecast.

        Returns the forecast with the most recent forecast_date, or if multiple
        forecasts exist for that date, the most recently created one.

        Returns:
            Optional[CashflowForecast]: Most recent forecast or None if no forecasts exist
        """
        # Find the max forecast date
        max_date_result = await self.session.execute(
            select(func.max(CashflowForecast.forecast_date))
        )
        max_date = max_date_result.scalar_one_or_none()

        if not max_date:
            return None

        # Find the most recently created forecast for this date
        result = await self.session.execute(
            select(CashflowForecast)
            .where(CashflowForecast.forecast_date == max_date)
            .order_by(desc(CashflowForecast.created_at))
        )
        return result.scalars().first()

    # Trend analysis methods

    async def get_forecast_trend(
        self, days: int = 90, include_min_values: bool = False
    ) -> List[Dict[str, Any]]:
        """
        Get daily forecast trend over a period.

        For each day, returns the forecast value and optionally minimum lookout values.

        Args:
            days (int): Number of days to include (default: 90)
            include_min_values (bool): Whether to include minimum lookout values

        Returns:
            List[Dict[str, Any]]: List of dictionaries with trend data
        """
        # Get the latest forecast for each day in the specified range
        end_date = utc_now()
        start_date = days_ago(days)

        forecasts = await self.get_by_date_range(start_date, end_date)

        trend_data = []
        for forecast in forecasts:
            data_point = {
                "date": forecast.forecast_date,
                "forecast": forecast.forecast,
                "balance": forecast.balance,
                "total_bills": forecast.total_bills,
                "total_income": forecast.total_income,
            }

            if include_min_values:
                data_point.update(
                    {
                        "min_14_day": forecast.min_14_day,
                        "min_30_day": forecast.min_30_day,
                        "min_60_day": forecast.min_60_day,
                        "min_90_day": forecast.min_90_day,
                    }
                )

            trend_data.append(data_point)

        return trend_data

    async def get_deficit_trend(self, days: int = 90) -> List[Dict[str, Any]]:
        """
        Get daily deficit trend over a period.

        For each day, returns the daily and yearly deficit values.

        Args:
            days (int): Number of days to include (default: 90)

        Returns:
            List[Dict[str, Any]]: List of dictionaries with deficit trend data
        """
        # Get the latest forecast for each day in the specified range
        end_date = utc_now()
        start_date = days_ago(days)

        forecasts = await self.get_by_date_range(start_date, end_date)

        trend_data = []
        for forecast in forecasts:
            trend_data.append(
                {
                    "date": forecast.forecast_date,
                    "daily_deficit": forecast.daily_deficit,
                    "yearly_deficit": forecast.yearly_deficit,
                    "required_income": forecast.required_income,
                }
            )

        return trend_data

    async def get_required_income_trend(self, days: int = 90) -> List[Dict[str, Any]]:
        """
        Get trend of required income over a period.

        For each day, returns the required income and hourly rates at different work hours.

        Args:
            days (int): Number of days to include (default: 90)

        Returns:
            List[Dict[str, Any]]: List of dictionaries with required income trend data
        """
        # Get the latest forecast for each day in the specified range
        end_date = utc_now()
        start_date = days_ago(days)

        forecasts = await self.get_by_date_range(start_date, end_date)

        trend_data = []
        for forecast in forecasts:
            trend_data.append(
                {
                    "date": forecast.forecast_date,
                    "required_income": forecast.required_income,
                    "hourly_rate_40": forecast.hourly_rate_40,
                    "hourly_rate_30": forecast.hourly_rate_30,
                    "hourly_rate_20": forecast.hourly_rate_20,
                }
            )

        return trend_data

    # Extended analysis methods

    async def get_forecast_with_metrics(
        self, forecast_date: Optional = None
    ) -> Dict[str, Any]:
        """
        Get a forecast with additional calculated metrics.

        Args:
            forecast_date (Optional[datetime]): Date to get forecast for (defaults to latest)

        Returns:
            Dict[str, Any]: Dictionary with forecast and metrics
        """
        # Get the forecast
        forecast = None
        if forecast_date:
            forecast = await self.get_by_date(forecast_date)
        else:
            forecast = await self.get_latest_forecast()

        if not forecast:
            return {}

        # Calculate additional metrics
        income_to_bills_ratio = Decimal("0.00")
        if forecast.total_bills and forecast.total_bills > 0:
            income_to_bills_ratio = (
                forecast.total_income / forecast.total_bills
            ).quantize(Decimal("0.01"))

        deficit_percentage = Decimal("0.00")
        if forecast.total_bills > 0:
            deficit_percentage = (
                (forecast.total_bills - forecast.total_income)
                / forecast.total_bills
                * 100
            ).quantize(Decimal("0.01"))
            if deficit_percentage < 0:
                deficit_percentage = Decimal("0.00")

        # Return comprehensive metrics
        return {
            "forecast": forecast,
            "date": forecast.forecast_date,
            "metrics": {
                "income_to_bills_ratio": income_to_bills_ratio,
                "deficit_percentage": deficit_percentage,
                "balance_to_min_ratio": (
                    (forecast.balance / forecast.min_30_day).quantize(Decimal("0.01"))
                    if forecast.min_30_day > 0
                    else Decimal("0.00")
                ),
                "daily_deficit_to_income_ratio": (
                    (forecast.daily_deficit / forecast.total_income * 100).quantize(
                        Decimal("0.01")
                    )
                    if forecast.total_income > 0
                    else Decimal("0.00")
                ),
            },
        }

    async def get_forecast_summary(
        self, start_date = None, end_date = None
    ) -> Dict[str, Any]:
        """
        Get a summary of forecasts over a period.

        Args:
            start_date (Optional[datetime]): Start date (defaults to 90 days ago)
            end_date (Optional[datetime]): End date (defaults to current date)

        Returns:
            Dict[str, Any]: Dictionary with summary metrics
        """
        if not end_date:
            end_date = utc_now()
        if not start_date:
            start_date = days_ago(90)

        # Get forecasts in the date range
        forecasts = await self.get_by_date_range(start_date, end_date)

        if not forecasts:
            return {}

        # Calculate summary metrics
        total_bills = sum(f.total_bills for f in forecasts)
        total_income = sum(f.total_income for f in forecasts)
        avg_daily_deficit = sum(f.daily_deficit for f in forecasts) / len(forecasts)
        avg_required_income = sum(f.required_income for f in forecasts) / len(forecasts)

        min_balance = min(f.balance for f in forecasts)
        min_forecast = min(f.forecast for f in forecasts)
        max_daily_deficit = max(f.daily_deficit for f in forecasts)

        min_14 = min(f.min_14_day for f in forecasts)
        min_30 = min(f.min_30_day for f in forecasts)
        min_60 = min(f.min_60_day for f in forecasts)
        min_90 = min(f.min_90_day for f in forecasts)

        return {
            "period": {
                "start_date": start_date,
                "end_date": end_date,
                "days": (end_date - start_date).days,
            },
            "totals": {
                "total_bills": total_bills,
                "total_income": total_income,
                "deficit": (
                    total_bills - total_income
                    if total_bills > total_income
                    else Decimal("0.00")
                ),
            },
            "averages": {
                "avg_daily_deficit": avg_daily_deficit,
                "avg_required_income": avg_required_income,
            },
            "extremes": {
                "min_balance": min_balance,
                "min_forecast": min_forecast,
                "max_daily_deficit": max_daily_deficit,
            },
            "minimums": {
                "min_14_day": min_14,
                "min_30_day": min_30,
                "min_60_day": min_60,
                "min_90_day": min_90,
            },
        }

    async def get_forecast_by_account(
        self, account_id: int, days: int = 90
    ) -> List[Dict[str, Any]]:
        """
        Get account-specific forecast data.

        Note: This is a placeholder implementation as the current CashflowForecast model
        doesn't store account-specific data. In a future enhancement, this would query
        a related table with account-specific forecast data.

        Args:
            account_id (int): Account ID to get forecast for
            days (int): Number of days to include (default: 90)

        Returns:
            List[Dict[str, Any]]: List of dictionaries with account-specific forecast data
        """
        # This is a placeholder implementation.
        # In the current model, we don't have account-specific forecast data,
        # so we're returning a generic forecast with a note.
        #
        # In a real implementation, this would query a related table with
        # account-specific forecast data.

        # Get the basic forecast data
        forecasts = await self.get_forecast_trend(days=days)

        # Add a note about this being a placeholder
        for forecast in forecasts:
            forecast["account_id"] = account_id
            forecast["note"] = "Account-specific forecast data not implemented"

        return forecasts
