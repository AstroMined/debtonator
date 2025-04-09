"""
Unit tests for historical cashflow schema factory functions.

Tests ensure that historical cashflow schema factories produce valid schema instances
that pass validation and maintain ADR-011 compliance for datetime handling.
"""

# pylint: disable=no-member

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Dict, List

from src.schemas.cashflow.cashflow_historical import (
    HistoricalPeriodAnalysis,
    HistoricalTrendMetrics,
    HistoricalTrendsResponse,
    SeasonalityAnalysis,
)
from src.utils.datetime_utils import datetime_equals, utc_now
from tests.helpers.schema_factories.base_schema_schema_factories import (
    MEDIUM_AMOUNT,
    SMALL_AMOUNT,
)
from tests.helpers.schema_factories.cashflow.cashflow_historical_schema_factories import (
    create_historical_period_analysis_schema,
    create_historical_trend_metrics_schema,
    create_historical_trends_response_schema,
    create_seasonality_analysis_schema,
)


def test_create_historical_trend_metrics_schema():
    """Test creating a HistoricalTrendMetrics schema with default values."""
    schema = create_historical_trend_metrics_schema()

    assert isinstance(schema, HistoricalTrendMetrics)
    assert schema.average_daily_change == SMALL_AMOUNT * Decimal("1.5")  # 15.00
    assert schema.volatility == SMALL_AMOUNT * Decimal("4.5")  # 45.00
    assert schema.trend_direction == "increasing"
    assert schema.trend_strength == Decimal("0.65")
    assert schema.confidence_score == Decimal("0.78")

    # Verify seasonal_factors is a dictionary with expected keys
    assert "Monthly" in schema.seasonal_factors
    assert "Weekly" in schema.seasonal_factors
    assert "Quarterly" in schema.seasonal_factors

    # Verify the sum of seasonal_factors values equals 1.0
    assert sum(schema.seasonal_factors.values()) == Decimal("1.0")


def test_create_historical_trend_metrics_schema_with_custom_values():
    """Test creating a HistoricalTrendMetrics schema with custom values."""
    seasonal_factors = {
        "Annual": Decimal("0.5"),
        "Monthly": Decimal("0.3"),
        "Weekly": Decimal("0.2"),
    }

    schema = create_historical_trend_metrics_schema(
        average_daily_change=Decimal("25.00"),
        volatility=Decimal("75.00"),
        trend_direction="decreasing",
        trend_strength=Decimal("0.8"),
        seasonal_factors=seasonal_factors,
        confidence_score=Decimal("0.9"),
    )

    assert isinstance(schema, HistoricalTrendMetrics)
    assert schema.average_daily_change == Decimal("25.00")
    assert schema.volatility == Decimal("75.00")
    assert schema.trend_direction == "decreasing"
    assert schema.trend_strength == Decimal("0.8")
    assert schema.confidence_score == Decimal("0.9")

    # Verify custom seasonal_factors
    assert schema.seasonal_factors == seasonal_factors
    assert sum(schema.seasonal_factors.values()) == Decimal("1.0")


def test_create_historical_period_analysis_schema():
    """Test creating a HistoricalPeriodAnalysis schema with default values."""
    schema = create_historical_period_analysis_schema()

    assert isinstance(schema, HistoricalPeriodAnalysis)

    # Verify period_start and period_end are timezone-aware and in UTC per ADR-011
    assert schema.period_start.tzinfo is not None
    assert schema.period_start.tzinfo == timezone.utc
    assert schema.period_end.tzinfo is not None
    assert schema.period_end.tzinfo == timezone.utc

    # Verify period_end is 90 days after period_start
    delta = schema.period_end - schema.period_start
    assert delta.days == 90

    assert schema.average_balance == MEDIUM_AMOUNT * Decimal("15")  # 1500.00
    assert schema.peak_balance == MEDIUM_AMOUNT * Decimal("22")  # 2200.00
    assert schema.lowest_balance == MEDIUM_AMOUNT * Decimal("8")  # 800.00
    assert schema.total_inflow == MEDIUM_AMOUNT * Decimal("30")  # 3000.00
    assert schema.total_outflow == MEDIUM_AMOUNT * Decimal("23")  # 2300.00
    assert schema.net_change == schema.total_inflow - schema.total_outflow  # 700.00

    # Verify significant_events
    assert len(schema.significant_events) == 2
    assert "date" in schema.significant_events[0]
    assert "event" in schema.significant_events[0]


def test_create_historical_period_analysis_schema_with_custom_values():
    """Test creating a HistoricalPeriodAnalysis schema with custom values."""
    period_start = utc_now() - timedelta(days=60)
    period_end = utc_now()
    significant_events = [
        {
            "date": (period_start + timedelta(days=10)).isoformat(),
            "event": "Big deposit",
        },
        {
            "date": (period_start + timedelta(days=30)).isoformat(),
            "event": "Major bill payment",
        },
        {
            "date": (period_start + timedelta(days=50)).isoformat(),
            "event": "Income deposit",
        },
    ]

    schema = create_historical_period_analysis_schema(
        period_start=period_start,
        period_end=period_end,
        average_balance=Decimal("2500.00"),
        peak_balance=Decimal("3500.00"),
        lowest_balance=Decimal("1500.00"),
        total_inflow=Decimal("5000.00"),
        total_outflow=Decimal("4000.00"),
        net_change=Decimal("1000.00"),
        significant_events=significant_events,
    )

    assert isinstance(schema, HistoricalPeriodAnalysis)

    # Verify datetime fields using datetime_equals for proper ADR-011 comparison
    assert datetime_equals(schema.period_start, period_start)
    assert datetime_equals(schema.period_end, period_end)

    assert schema.average_balance == Decimal("2500.00")
    assert schema.peak_balance == Decimal("3500.00")
    assert schema.lowest_balance == Decimal("1500.00")
    assert schema.total_inflow == Decimal("5000.00")
    assert schema.total_outflow == Decimal("4000.00")
    assert schema.net_change == Decimal("1000.00")

    # Verify custom significant_events
    assert schema.significant_events == significant_events
    assert len(schema.significant_events) == 3


def test_create_seasonality_analysis_schema():
    """Test creating a SeasonalityAnalysis schema with default values."""
    schema = create_seasonality_analysis_schema()

    assert isinstance(schema, SeasonalityAnalysis)

    # Verify monthly_patterns
    assert isinstance(schema.monthly_patterns, Dict)
    assert len(schema.monthly_patterns) == 12  # One for each month
    for month in range(1, 13):
        assert month in schema.monthly_patterns

    # Verify day_of_week_patterns
    assert isinstance(schema.day_of_week_patterns, Dict)
    assert len(schema.day_of_week_patterns) == 7  # One for each day of the week
    for day in range(7):
        assert day in schema.day_of_week_patterns

    # Verify day_of_month_patterns
    assert isinstance(schema.day_of_month_patterns, Dict)
    assert len(schema.day_of_month_patterns) == 31  # One for each day of month
    for day in range(1, 32):
        assert day in schema.day_of_month_patterns

    # Verify holiday_impacts
    assert "Christmas" in schema.holiday_impacts
    assert "New Year" in schema.holiday_impacts
    assert "Thanksgiving" in schema.holiday_impacts

    assert schema.seasonal_strength == Decimal("0.72")

    # Verify the sum of each pattern group is approximately 1.0
    assert sum(schema.monthly_patterns.values()).quantize(Decimal("0.01")) == Decimal(
        "1.00"
    )
    assert sum(schema.day_of_week_patterns.values()).quantize(
        Decimal("0.01")
    ) == Decimal("1.00")

    # Allow a small tolerance for day_of_month_patterns since they may not sum exactly to 1.0
    day_of_month_sum = sum(schema.day_of_month_patterns.values()).quantize(
        Decimal("0.01")
    )
    assert Decimal("0.94") <= day_of_month_sum <= Decimal("1.00")

    assert sum(schema.holiday_impacts.values()) == Decimal("1.0")


def test_create_seasonality_analysis_schema_with_custom_values():
    """Test creating a SeasonalityAnalysis schema with custom values."""
    monthly_patterns = {
        1: Decimal("0.10"),  # January
        2: Decimal("0.05"),  # February
        3: Decimal("0.05"),  # March
        4: Decimal("0.05"),  # April
        5: Decimal("0.05"),  # May
        6: Decimal("0.05"),  # June
        7: Decimal("0.05"),  # July
        8: Decimal("0.10"),  # August
        9: Decimal("0.10"),  # September
        10: Decimal("0.10"),  # October
        11: Decimal("0.15"),  # November
        12: Decimal("0.15"),  # December
    }

    day_of_week_patterns = {
        0: Decimal("0.10"),  # Sunday
        1: Decimal("0.15"),  # Monday
        2: Decimal("0.15"),  # Tuesday
        3: Decimal("0.15"),  # Wednesday
        4: Decimal("0.15"),  # Thursday
        5: Decimal("0.15"),  # Friday
        6: Decimal("0.15"),  # Saturday
    }

    holiday_impacts = {
        "Christmas": Decimal("0.3"),
        "New Year": Decimal("0.3"),
        "Thanksgiving": Decimal("0.2"),
        "Easter": Decimal("0.2"),
    }

    schema = create_seasonality_analysis_schema(
        monthly_patterns=monthly_patterns,
        day_of_week_patterns=day_of_week_patterns,
        holiday_impacts=holiday_impacts,
        seasonal_strength=Decimal("0.85"),
    )

    assert isinstance(schema, SeasonalityAnalysis)

    # Verify custom monthly_patterns
    assert schema.monthly_patterns == monthly_patterns
    assert sum(schema.monthly_patterns.values()) == Decimal("1.0")

    # Verify custom day_of_week_patterns
    assert schema.day_of_week_patterns == day_of_week_patterns
    assert sum(schema.day_of_week_patterns.values()) == Decimal("1.0")

    # Verify custom holiday_impacts
    assert schema.holiday_impacts == holiday_impacts
    assert sum(schema.holiday_impacts.values()) == Decimal("1.0")

    assert schema.seasonal_strength == Decimal("0.85")


def test_create_historical_trends_response_schema():
    """Test creating a HistoricalTrendsResponse schema with default values."""
    schema = create_historical_trends_response_schema()

    assert isinstance(schema, HistoricalTrendsResponse)

    # Verify metrics is a HistoricalTrendMetrics instance
    assert isinstance(schema.metrics, HistoricalTrendMetrics)

    # Verify period_analysis is a list of HistoricalPeriodAnalysis instances
    assert isinstance(schema.period_analysis, List)
    assert len(schema.period_analysis) == 2  # Default creates 2 periods
    assert isinstance(schema.period_analysis[0], HistoricalPeriodAnalysis)

    # Verify seasonality is a SeasonalityAnalysis instance
    assert isinstance(schema.seasonality, SeasonalityAnalysis)

    # Verify timestamp is timezone-aware and in UTC per ADR-011
    assert schema.timestamp.tzinfo is not None
    assert schema.timestamp.tzinfo == timezone.utc


def test_create_historical_trends_response_schema_with_custom_values():
    """Test creating a HistoricalTrendsResponse schema with custom values."""
    timestamp = utc_now()

    # Create custom metrics
    metrics = create_historical_trend_metrics_schema(
        average_daily_change=Decimal("30.00"),
        trend_direction="stable",
        confidence_score=Decimal("0.9"),
    ).model_dump()

    # Create custom period_analysis
    now = utc_now()

    quarterly_analysis = create_historical_period_analysis_schema(
        period_start=now - timedelta(days=90),
        period_end=now,
        average_balance=Decimal("3500.00"),
    ).model_dump()

    monthly_analysis = create_historical_period_analysis_schema(
        period_start=now - timedelta(days=30),
        period_end=now,
        average_balance=Decimal("4000.00"),
    ).model_dump()

    weekly_analysis = create_historical_period_analysis_schema(
        period_start=now - timedelta(days=7),
        period_end=now,
        average_balance=Decimal("4500.00"),
    ).model_dump()

    period_analysis = [quarterly_analysis, monthly_analysis, weekly_analysis]

    # Create custom seasonality
    seasonality = create_seasonality_analysis_schema(
        seasonal_strength=Decimal("0.95")
    ).model_dump()

    schema = create_historical_trends_response_schema(
        metrics=metrics,
        period_analysis=period_analysis,
        seasonality=seasonality,
        timestamp=timestamp,
    )

    assert isinstance(schema, HistoricalTrendsResponse)

    # Verify custom metrics
    assert schema.metrics.average_daily_change == Decimal("30.00")
    assert schema.metrics.trend_direction == "stable"
    assert schema.metrics.confidence_score == Decimal("0.9")

    # Verify custom period_analysis
    assert len(schema.period_analysis) == 3  # We provided 3 periods
    assert schema.period_analysis[0].average_balance == Decimal("3500.00")
    assert schema.period_analysis[1].average_balance == Decimal("4000.00")
    assert schema.period_analysis[2].average_balance == Decimal("4500.00")

    # Verify custom seasonality
    assert schema.seasonality.seasonal_strength == Decimal("0.95")

    # Verify timestamp using datetime_equals for proper ADR-011 comparison
    assert datetime_equals(schema.timestamp, timestamp)


def test_nested_datetime_handling():
    """Test proper datetime handling in nested structures per ADR-011."""
    now = utc_now()

    # Create a response with nested datetime objects
    schema = create_historical_trends_response_schema(timestamp=now)

    # Verify all datetime fields in the response and nested objects are properly handled
    assert datetime_equals(schema.timestamp, now)

    # Check period_analysis datetimes
    for period in schema.period_analysis:
        assert period.period_start.tzinfo is not None
        assert period.period_start.tzinfo == timezone.utc
        assert period.period_end.tzinfo is not None
        assert period.period_end.tzinfo == timezone.utc

        # Check significant_events dates (stored as ISO strings)
        for event in period.significant_events:
            # Parse the ISO string to datetime for comparison
            event_date = datetime.fromisoformat(event["date"])
            assert event_date.tzinfo is not None
