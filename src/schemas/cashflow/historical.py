from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Tuple

from pydantic import Field

from src.schemas import BaseSchemaValidator

class HistoricalTrendMetrics(BaseSchemaValidator):
    """
    Schema for historical trend metrics.
    
    Contains metrics describing historical trends in account balances.
    """
    average_daily_change: Decimal = BaseSchemaValidator.money_field(
        "Average daily change in balance",
        default=...
    )
    volatility: Decimal = BaseSchemaValidator.money_field(
        "Standard deviation of daily changes",
        default=...
    )
    trend_direction: str = Field(
        ..., 
        pattern="^(increasing|decreasing|stable)$",
        description="Overall direction of the trend"
    )
    trend_strength: Decimal = BaseSchemaValidator.percentage_field(
        "Strength of the trend (0-1 scale)",
        default=...
    )
    seasonal_factors: Dict[str, Decimal] = Field(
        ...,
        description="Seasonal factors affecting the trend"
    )
    confidence_score: Decimal = BaseSchemaValidator.percentage_field(
        "Confidence in the trend analysis (0-1 scale)",
        default=...
    )

class HistoricalPeriodAnalysis(BaseSchemaValidator):
    """
    Schema for analyzing specific historical periods.
    
    Provides detailed analysis of a specific date range in account history.
    All datetime fields are stored in UTC timezone.
    """
    period_start: datetime = Field(
        ...,
        description="Start date of this analysis period in UTC timezone"
    )
    period_end: datetime = Field(
        ...,
        description="End date of this analysis period in UTC timezone"
    )
    average_balance: Decimal = BaseSchemaValidator.money_field(
        "Average balance during this period",
        default=...
    )
    peak_balance: Decimal = BaseSchemaValidator.money_field(
        "Highest balance during this period",
        default=...
    )
    lowest_balance: Decimal = BaseSchemaValidator.money_field(
        "Lowest balance during this period",
        default=...
    )
    total_inflow: Decimal = BaseSchemaValidator.money_field(
        "Total money coming in during this period",
        default=...
    )
    total_outflow: Decimal = BaseSchemaValidator.money_field(
        "Total money going out during this period",
        default=...
    )
    net_change: Decimal = BaseSchemaValidator.money_field(
        "Net change in balance during this period",
        default=...
    )
    significant_events: List[Dict[str, str]] = Field(
        ...,
        description="Significant financial events during this period"
    )

class SeasonalityAnalysis(BaseSchemaValidator):
    """
    Schema for seasonal patterns.
    
    Describes seasonal patterns in financial activity.
    """
    monthly_patterns: Dict[int, Decimal] = Field(
        ...,
        description="Patterns by month (1-12 for Jan-Dec)"
    )
    day_of_week_patterns: Dict[int, Decimal] = Field(
        ...,
        description="Patterns by day of week (0-6 for Sun-Sat)"
    )
    day_of_month_patterns: Dict[int, Decimal] = Field(
        ...,
        description="Patterns by day of month (1-31)"
    )
    holiday_impacts: Dict[str, Decimal] = Field(
        ...,
        description="Impact of holidays on financial patterns"
    )
    seasonal_strength: Decimal = BaseSchemaValidator.percentage_field(
        "Overall strength of seasonality (0-1 scale)",
        default=...
    )

class HistoricalTrendsResponse(BaseSchemaValidator):
    """
    Schema for historical trends analysis response.
    
    Contains complete analysis of historical financial trends.
    All datetime fields are stored in UTC timezone.
    """
    metrics: HistoricalTrendMetrics = Field(
        ...,
        description="Overall metrics for historical trends"
    )
    period_analysis: List[HistoricalPeriodAnalysis] = Field(
        ...,
        description="Analysis of specific historical periods"
    )
    seasonality: SeasonalityAnalysis = Field(
        ...,
        description="Analysis of seasonal patterns"
    )
    timestamp: datetime = Field(
        ...,
        description="When this analysis was generated in UTC timezone"
    )
