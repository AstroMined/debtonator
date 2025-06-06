from datetime import datetime
from typing import Dict, List

from pydantic import Field

from src.schemas.base_schema import (
    BaseSchemaValidator,
    IntPercentageDict,
    MoneyDecimal,
    PercentageDecimal,
    PercentageDict,
)


class HistoricalTrendMetrics(BaseSchemaValidator):
    """
    Schema for historical trend metrics.

    Contains metrics describing historical trends in account balances.
    """

    average_daily_change: MoneyDecimal = Field(
        ..., description="Average daily change in balance"
    )
    volatility: MoneyDecimal = Field(
        ..., description="Standard deviation of daily changes"
    )
    trend_direction: str = Field(
        ...,
        pattern="^(increasing|decreasing|stable)$",
        description="Overall direction of the trend",
    )
    trend_strength: PercentageDecimal = Field(
        ..., description="Strength of the trend (0-1 scale)"
    )
    seasonal_factors: PercentageDict = Field(
        ..., description="Seasonal factors affecting the trend"
    )
    confidence_score: PercentageDecimal = Field(
        ..., description="Confidence in the trend analysis (0-1 scale)"
    )


class HistoricalPeriodAnalysis(BaseSchemaValidator):
    """
    Schema for analyzing specific historical periods.

    Provides detailed analysis of a specific date range in account history.
    All datetime fields are stored in UTC timezone.
    """

    period_start: datetime = Field(
        ..., description="Start date of this analysis period in UTC timezone"
    )
    period_end: datetime = Field(
        ..., description="End date of this analysis period in UTC timezone"
    )
    average_balance: MoneyDecimal = Field(
        ..., description="Average balance during this period"
    )
    peak_balance: MoneyDecimal = Field(
        ..., description="Highest balance during this period"
    )
    lowest_balance: MoneyDecimal = Field(
        ..., description="Lowest balance during this period"
    )
    total_inflow: MoneyDecimal = Field(
        ..., description="Total money coming in during this period"
    )
    total_outflow: MoneyDecimal = Field(
        ..., description="Total money going out during this period"
    )
    net_change: MoneyDecimal = Field(
        ..., description="Net change in balance during this period"
    )
    significant_events: List[Dict[str, str]] = Field(
        ..., description="Significant financial events during this period"
    )


class SeasonalityAnalysis(BaseSchemaValidator):
    """
    Schema for seasonal patterns.

    Describes seasonal patterns in financial activity.
    """

    monthly_patterns: IntPercentageDict = Field(
        ..., description="Patterns by month (1-12 for Jan-Dec)"
    )
    day_of_week_patterns: IntPercentageDict = Field(
        ..., description="Patterns by day of week (0-6 for Sun-Sat)"
    )
    day_of_month_patterns: IntPercentageDict = Field(
        ..., description="Patterns by day of month (1-31)"
    )
    holiday_impacts: PercentageDict = Field(
        ..., description="Impact of holidays on financial patterns"
    )
    seasonal_strength: PercentageDecimal = Field(
        ..., description="Overall strength of seasonality (0-1 scale)"
    )


class HistoricalTrendsResponse(BaseSchemaValidator):
    """
    Schema for historical trends analysis response.

    Contains complete analysis of historical financial trends.
    All datetime fields are stored in UTC timezone.
    """

    metrics: HistoricalTrendMetrics = Field(
        ..., description="Overall metrics for historical trends"
    )
    period_analysis: List[HistoricalPeriodAnalysis] = Field(
        ..., description="Analysis of specific historical periods"
    )
    seasonality: SeasonalityAnalysis = Field(
        ..., description="Analysis of seasonal patterns"
    )
    timestamp: datetime = Field(
        ..., description="When this analysis was generated in UTC timezone"
    )
