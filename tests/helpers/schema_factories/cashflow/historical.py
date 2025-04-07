"""
Historical cashflow schema factory functions.

This module provides factory functions for creating valid historical cashflow
Pydantic schema instances for use in tests.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

from src.schemas.cashflow.historical import (
    HistoricalPeriodAnalysis,
    HistoricalTrendMetrics,
    HistoricalTrendsResponse,
    SeasonalityAnalysis,
)
from src.utils.datetime_utils import utc_now

from tests.helpers.schema_factories.base import (
    MEDIUM_AMOUNT,
    SMALL_AMOUNT,
    factory_function,
)


@factory_function(HistoricalTrendMetrics)
def create_historical_trend_metrics_schema(
    average_daily_change: Optional[Decimal] = None,
    volatility: Optional[Decimal] = None,
    trend_direction: str = "increasing",
    trend_strength: Optional[Decimal] = None,
    seasonal_factors: Optional[Dict[str, Decimal]] = None,
    confidence_score: Optional[Decimal] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid HistoricalTrendMetrics schema instance.

    Args:
        average_daily_change: Average daily change in balance (defaults to 15.00)
        volatility: Standard deviation of daily changes (defaults to 45.00)
        trend_direction: Overall direction of the trend
        trend_strength: Strength of the trend (0-1 scale)
        seasonal_factors: Seasonal factors affecting the trend
        confidence_score: Confidence in the trend analysis
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create HistoricalTrendMetrics schema
    """
    if average_daily_change is None:
        average_daily_change = SMALL_AMOUNT * Decimal("1.5")  # 15.00

    if volatility is None:
        volatility = SMALL_AMOUNT * Decimal("4.5")  # 45.00

    if trend_strength is None:
        trend_strength = Decimal("0.65")

    if seasonal_factors is None:
        seasonal_factors = {
            "Monthly": Decimal("0.35"),
            "Weekly": Decimal("0.25"),
            "Quarterly": Decimal("0.40"),
        }

    if confidence_score is None:
        confidence_score = Decimal("0.78")

    data = {
        "average_daily_change": average_daily_change,
        "volatility": volatility,
        "trend_direction": trend_direction,
        "trend_strength": trend_strength,
        "seasonal_factors": seasonal_factors,
        "confidence_score": confidence_score,
        **kwargs,
    }

    return data


@factory_function(HistoricalPeriodAnalysis)
def create_historical_period_analysis_schema(
    period_start: Optional[datetime] = None,
    period_end: Optional[datetime] = None,
    average_balance: Optional[Decimal] = None,
    peak_balance: Optional[Decimal] = None,
    lowest_balance: Optional[Decimal] = None,
    total_inflow: Optional[Decimal] = None,
    total_outflow: Optional[Decimal] = None,
    net_change: Optional[Decimal] = None,
    significant_events: Optional[List[Dict[str, str]]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid HistoricalPeriodAnalysis schema instance.

    Args:
        period_start: Start date of analysis period (defaults to 90 days ago)
        period_end: End date of analysis period (defaults to current date)
        average_balance: Average balance during period (defaults to 1500.00)
        peak_balance: Highest balance during period (defaults to 2200.00)
        lowest_balance: Lowest balance during period (defaults to 800.00)
        total_inflow: Total money coming in (defaults to 3000.00)
        total_outflow: Total money going out (defaults to 2300.00)
        net_change: Net change in balance (defaults to 700.00)
        significant_events: Significant financial events
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create HistoricalPeriodAnalysis schema
    """
    now = utc_now()
    if period_end is None:
        period_end = now
    if period_start is None:
        period_start = now - timedelta(days=90)

    if average_balance is None:
        average_balance = MEDIUM_AMOUNT * Decimal("15")  # 1500.00

    if peak_balance is None:
        peak_balance = MEDIUM_AMOUNT * Decimal("22")  # 2200.00

    if lowest_balance is None:
        lowest_balance = MEDIUM_AMOUNT * Decimal("8")  # 800.00

    if total_inflow is None:
        total_inflow = MEDIUM_AMOUNT * Decimal("30")  # 3000.00

    if total_outflow is None:
        total_outflow = MEDIUM_AMOUNT * Decimal("23")  # 2300.00

    if net_change is None:
        net_change = total_inflow - total_outflow  # 700.00

    if significant_events is None:
        significant_events = [
            {
                "date": (period_start + timedelta(days=15)).isoformat(),
                "event": "Large deposit",
            },
            {
                "date": (period_start + timedelta(days=45)).isoformat(),
                "event": "Major expense",
            },
        ]

    data = {
        "period_start": period_start,
        "period_end": period_end,
        "average_balance": average_balance,
        "peak_balance": peak_balance,
        "lowest_balance": lowest_balance,
        "total_inflow": total_inflow,
        "total_outflow": total_outflow,
        "net_change": net_change,
        "significant_events": significant_events,
        **kwargs,
    }

    return data


@factory_function(SeasonalityAnalysis)
def create_seasonality_analysis_schema(
    monthly_patterns: Optional[Dict[int, Decimal]] = None,
    day_of_week_patterns: Optional[Dict[int, Decimal]] = None,
    day_of_month_patterns: Optional[Dict[int, Decimal]] = None,
    holiday_impacts: Optional[Dict[str, Decimal]] = None,
    seasonal_strength: Optional[Decimal] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid SeasonalityAnalysis schema instance.

    Args:
        monthly_patterns: Patterns by month (1-12 for Jan-Dec)
        day_of_week_patterns: Patterns by day of week (0-6 for Sun-Sat)
        day_of_month_patterns: Patterns by day of month (1-31)
        holiday_impacts: Impact of holidays on financial patterns
        seasonal_strength: Overall strength of seasonality (0-1 scale)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create SeasonalityAnalysis schema
    """
    if monthly_patterns is None:
        # Sample monthly patterns (higher values in December, January)
        monthly_patterns = {
            1: Decimal("0.12"),  # January
            2: Decimal("0.07"),
            3: Decimal("0.08"),
            4: Decimal("0.06"),
            5: Decimal("0.07"),
            6: Decimal("0.07"),
            7: Decimal("0.08"),
            8: Decimal("0.08"),
            9: Decimal("0.09"),
            10: Decimal("0.08"),
            11: Decimal("0.09"),
            12: Decimal("0.11"),  # December
        }

    if day_of_week_patterns is None:
        # Sample day of week patterns (higher on weekends)
        day_of_week_patterns = {
            0: Decimal("0.18"),  # Sunday
            1: Decimal("0.12"),
            2: Decimal("0.13"),
            3: Decimal("0.14"),
            4: Decimal("0.15"),
            5: Decimal("0.16"),
            6: Decimal("0.12"),  # Saturday
        }

    if day_of_month_patterns is None:
        # Sample day of month patterns (higher at start, mid, and end)
        day_of_month_patterns = {}
        for day in range(1, 32):
            if day == 1 or day == 15 or day == 30:
                day_of_month_patterns[day] = Decimal("0.08")
            else:
                day_of_month_patterns[day] = Decimal("0.025")

    if holiday_impacts is None:
        holiday_impacts = {
            "Christmas": Decimal("0.25"),
            "New Year": Decimal("0.20"),
            "Thanksgiving": Decimal("0.15"),
            "Easter": Decimal("0.10"),
            "Other": Decimal("0.30"),
        }

    if seasonal_strength is None:
        seasonal_strength = Decimal("0.72")

    data = {
        "monthly_patterns": monthly_patterns,
        "day_of_week_patterns": day_of_week_patterns,
        "day_of_month_patterns": day_of_month_patterns,
        "holiday_impacts": holiday_impacts,
        "seasonal_strength": seasonal_strength,
        **kwargs,
    }

    return data


@factory_function(HistoricalTrendsResponse)
def create_historical_trends_response_schema(
    metrics: Optional[Dict[str, Any]] = None,
    period_analysis: Optional[List[Dict[str, Any]]] = None,
    seasonality: Optional[Dict[str, Any]] = None,
    timestamp: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid HistoricalTrendsResponse schema instance.

    Args:
        metrics: Overall metrics for historical trends
        period_analysis: Analysis of specific historical periods
        seasonality: Analysis of seasonal patterns
        timestamp: When analysis was generated (defaults to current UTC time)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create HistoricalTrendsResponse schema
    """
    if metrics is None:
        metrics = create_historical_trend_metrics_schema().model_dump()

    if period_analysis is None:
        # Create two period analyses - last quarter and last month
        now = utc_now()

        last_quarter = create_historical_period_analysis_schema(
            period_start=now - timedelta(days=90), period_end=now
        ).model_dump()

        last_month = create_historical_period_analysis_schema(
            period_start=now - timedelta(days=30),
            period_end=now,
            average_balance=MEDIUM_AMOUNT * Decimal("16"),  # 1600.00
            peak_balance=MEDIUM_AMOUNT * Decimal("23"),  # 2300.00
            lowest_balance=MEDIUM_AMOUNT * Decimal("10"),  # 1000.00
        ).model_dump()

        period_analysis = [last_quarter, last_month]

    if seasonality is None:
        seasonality = create_seasonality_analysis_schema().model_dump()

    if timestamp is None:
        timestamp = utc_now()

    data = {
        "metrics": metrics,
        "period_analysis": period_analysis,
        "seasonality": seasonality,
        "timestamp": timestamp,
        **kwargs,
    }

    return data
