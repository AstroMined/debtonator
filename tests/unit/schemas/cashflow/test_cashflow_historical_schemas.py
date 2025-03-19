from datetime import datetime, timezone, timedelta
from decimal import Decimal
from typing import Dict, List, Tuple
from zoneinfo import ZoneInfo  # Only needed for non-UTC timezone tests

import pytest
from pydantic import ValidationError

from src.schemas.cashflow.historical import (
    HistoricalTrendMetrics,
    HistoricalPeriodAnalysis,
    SeasonalityAnalysis,
    HistoricalTrendsResponse
)


# Test valid object creation
def test_historical_trend_metrics_valid():
    """Test valid historical trend metrics schema creation"""
    metrics = HistoricalTrendMetrics(
        average_daily_change=Decimal("25.50"),
        volatility=Decimal("75.25"),
        trend_direction="increasing",
        trend_strength=Decimal("0.75"),
        seasonal_factors={"monthly": Decimal("0.5"), "holiday": Decimal("0.3")},
        confidence_score=Decimal("0.85")
    )
    
    assert metrics.average_daily_change == Decimal("25.50")
    assert metrics.volatility == Decimal("75.25")
    assert metrics.trend_direction == "increasing"
    assert metrics.trend_strength == Decimal("0.75")
    assert metrics.seasonal_factors == {"monthly": Decimal("0.5"), "holiday": Decimal("0.3")}
    assert metrics.confidence_score == Decimal("0.85")


def test_historical_period_analysis_valid():
    """Test valid historical period analysis schema creation"""
    now = datetime.now(timezone.utc)
    past = now - timedelta(days=30)
    
    analysis = HistoricalPeriodAnalysis(
        period_start=past,
        period_end=now,
        average_balance=Decimal("2500.00"),
        peak_balance=Decimal("3500.00"),
        lowest_balance=Decimal("1800.00"),
        total_inflow=Decimal("5000.00"),
        total_outflow=Decimal("4200.00"),
        net_change=Decimal("800.00"),
        significant_events=[
            {"date": "2025-02-15", "description": "Large deposit received"},
            {"date": "2025-02-28", "description": "Annual subscription payment"}
        ]
    )
    
    assert analysis.period_start == past
    assert analysis.period_end == now
    assert analysis.average_balance == Decimal("2500.00")
    assert analysis.peak_balance == Decimal("3500.00")
    assert analysis.lowest_balance == Decimal("1800.00")
    assert analysis.total_inflow == Decimal("5000.00")
    assert analysis.total_outflow == Decimal("4200.00")
    assert analysis.net_change == Decimal("800.00")
    assert len(analysis.significant_events) == 2
    assert analysis.significant_events[0]["description"] == "Large deposit received"


def test_seasonality_analysis_valid():
    """Test valid seasonality analysis schema creation"""
    seasonality = SeasonalityAnalysis(
        monthly_patterns={
            1: Decimal("0.8"),  # January
            2: Decimal("0.7"),  # February
            3: Decimal("0.6")   # March
        },
        day_of_week_patterns={
            0: Decimal("0.4"),  # Sunday
            1: Decimal("0.6"),  # Monday
            5: Decimal("0.8")   # Friday
        },
        day_of_month_patterns={
            1: Decimal("0.9"),   # 1st of month
            15: Decimal("0.7"),  # 15th of month
            30: Decimal("0.5")   # 30th of month
        },
        holiday_impacts={
            "Christmas": Decimal("0.9"),
            "Thanksgiving": Decimal("0.7")
        },
        seasonal_strength=Decimal("0.75")
    )
    
    assert seasonality.monthly_patterns[1] == Decimal("0.8")
    assert seasonality.day_of_week_patterns[5] == Decimal("0.8")
    assert seasonality.day_of_month_patterns[15] == Decimal("0.7")
    assert seasonality.holiday_impacts["Christmas"] == Decimal("0.9")
    assert seasonality.seasonal_strength == Decimal("0.75")


def test_historical_trends_response_valid():
    """Test valid historical trends response schema creation"""
    now = datetime.now(timezone.utc)
    past = now - timedelta(days=30)
    
    metrics = HistoricalTrendMetrics(
        average_daily_change=Decimal("25.50"),
        volatility=Decimal("75.25"),
        trend_direction="increasing",
        trend_strength=Decimal("0.75"),
        seasonal_factors={"monthly": Decimal("0.5")},
        confidence_score=Decimal("0.85")
    )
    
    analysis = HistoricalPeriodAnalysis(
        period_start=past,
        period_end=now,
        average_balance=Decimal("2500.00"),
        peak_balance=Decimal("3500.00"),
        lowest_balance=Decimal("1800.00"),
        total_inflow=Decimal("5000.00"),
        total_outflow=Decimal("4200.00"),
        net_change=Decimal("800.00"),
        significant_events=[
            {"date": "2025-02-15", "description": "Large deposit"}
        ]
    )
    
    seasonality = SeasonalityAnalysis(
        monthly_patterns={
            1: Decimal("0.8"),
            2: Decimal("0.7")
        },
        day_of_week_patterns={
            0: Decimal("0.4"),
            1: Decimal("0.6")
        },
        day_of_month_patterns={
            1: Decimal("0.9"),
            15: Decimal("0.7")
        },
        holiday_impacts={
            "Christmas": Decimal("0.9")
        },
        seasonal_strength=Decimal("0.75")
    )
    
    response = HistoricalTrendsResponse(
        metrics=metrics,
        period_analysis=[analysis],
        seasonality=seasonality,
        timestamp=now
    )
    
    assert response.metrics == metrics
    assert len(response.period_analysis) == 1
    assert response.period_analysis[0] == analysis
    assert response.seasonality == seasonality
    assert response.timestamp == now


# Test field validations
def test_trend_direction_validation():
    """Test trend direction enum validation"""
    # Test invalid trend direction
    with pytest.raises(ValidationError, match="String should match pattern"):
        HistoricalTrendMetrics(
            average_daily_change=Decimal("25.50"),
            volatility=Decimal("75.25"),
            trend_direction="sideways",  # Invalid value
            trend_strength=Decimal("0.75"),
            seasonal_factors={"monthly": Decimal("0.5")},
            confidence_score=Decimal("0.85")
        )


def test_trend_strength_range():
    """Test trend strength range validation"""
    # Test below minimum
    with pytest.raises(ValidationError, match="Input should be greater than or equal to 0"):
        HistoricalTrendMetrics(
            average_daily_change=Decimal("25.50"),
            volatility=Decimal("75.25"),
            trend_direction="increasing",
            trend_strength=Decimal("-0.1"),  # Below minimum
            seasonal_factors={"monthly": Decimal("0.5")},
            confidence_score=Decimal("0.85")
        )
    
    # Test above maximum
    with pytest.raises(ValidationError, match="Input should be less than or equal to 1"):
        HistoricalTrendMetrics(
            average_daily_change=Decimal("25.50"),
            volatility=Decimal("75.25"),
            trend_direction="increasing",
            trend_strength=Decimal("1.1"),  # Above maximum
            seasonal_factors={"monthly": Decimal("0.5")},
            confidence_score=Decimal("0.85")
        )


def test_confidence_score_range():
    """Test confidence score range validation"""
    # Test below minimum
    with pytest.raises(ValidationError, match="Input should be greater than or equal to 0"):
        HistoricalTrendMetrics(
            average_daily_change=Decimal("25.50"),
            volatility=Decimal("75.25"),
            trend_direction="increasing",
            trend_strength=Decimal("0.75"),
            seasonal_factors={"monthly": Decimal("0.5")},
            confidence_score=Decimal("-0.1")  # Below minimum
        )
    
    # Test above maximum
    with pytest.raises(ValidationError, match="Input should be less than or equal to 1"):
        HistoricalTrendMetrics(
            average_daily_change=Decimal("25.50"),
            volatility=Decimal("75.25"),
            trend_direction="increasing",
            trend_strength=Decimal("0.75"),
            seasonal_factors={"monthly": Decimal("0.5")},
            confidence_score=Decimal("1.1")  # Above maximum
        )


def test_seasonal_strength_range():
    """Test seasonal strength range validation"""
    # Test below minimum
    with pytest.raises(ValidationError, match="Input should be greater than or equal to 0"):
        SeasonalityAnalysis(
            monthly_patterns={1: Decimal("0.8")},
            day_of_week_patterns={0: Decimal("0.4")},
            day_of_month_patterns={1: Decimal("0.9")},
            holiday_impacts={"Christmas": Decimal("0.9")},
            seasonal_strength=Decimal("-0.1")  # Below minimum
        )
    
    # Test above maximum
    with pytest.raises(ValidationError, match="Input should be less than or equal to 1"):
        SeasonalityAnalysis(
            monthly_patterns={1: Decimal("0.8")},
            day_of_week_patterns={0: Decimal("0.4")},
            day_of_month_patterns={1: Decimal("0.9")},
            holiday_impacts={"Christmas": Decimal("0.9")},
            seasonal_strength=Decimal("1.1")  # Above maximum
        )


def test_decimal_precision():
    """Test decimal precision validation"""
    # Test too many decimal places in average_daily_change
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        HistoricalTrendMetrics(
            average_daily_change=Decimal("25.501"),  # Too many decimal places
            volatility=Decimal("75.25"),
            trend_direction="increasing",
            trend_strength=Decimal("0.75"),
            seasonal_factors={"monthly": Decimal("0.5")},
            confidence_score=Decimal("0.85")
        )
    
    # Test too many decimal places in average_balance
    now = datetime.now(timezone.utc)
    past = now - timedelta(days=30)
    
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        HistoricalPeriodAnalysis(
            period_start=past,
            period_end=now,
            average_balance=Decimal("2500.123"),  # Too many decimal places
            peak_balance=Decimal("3500.00"),
            lowest_balance=Decimal("1800.00"),
            total_inflow=Decimal("5000.00"),
            total_outflow=Decimal("4200.00"),
            net_change=Decimal("800.00"),
            significant_events=[]
        )
        
    # Test too many decimal places in percentage fields
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.0001"):
        HistoricalTrendMetrics(
            average_daily_change=Decimal("25.50"),
            volatility=Decimal("75.25"),
            trend_direction="increasing",
            trend_strength=Decimal("0.75001"),  # Too many decimal places
            seasonal_factors={"monthly": Decimal("0.5")},
            confidence_score=Decimal("0.85")
        )


def test_datetime_utc_validation():
    """Test datetime UTC validation per ADR-011"""
    now = datetime.now(timezone.utc)
    past = now - timedelta(days=30)
    
    # Test naive datetime in period_start
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        HistoricalPeriodAnalysis(
            period_start=datetime.now(),  # Naive datetime
            period_end=now,
            average_balance=Decimal("2500.00"),
            peak_balance=Decimal("3500.00"),
            lowest_balance=Decimal("1800.00"),
            total_inflow=Decimal("5000.00"),
            total_outflow=Decimal("4200.00"),
            net_change=Decimal("800.00"),
            significant_events=[]
        )
    
    # Test non-UTC timezone in period_end
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        HistoricalPeriodAnalysis(
            period_start=past,
            period_end=datetime.now(ZoneInfo("America/New_York")),  # Non-UTC timezone
            average_balance=Decimal("2500.00"),
            peak_balance=Decimal("3500.00"),
            lowest_balance=Decimal("1800.00"),
            total_inflow=Decimal("5000.00"),
            total_outflow=Decimal("4200.00"),
            net_change=Decimal("800.00"),
            significant_events=[]
        )
    
    # Create valid component schemas for testing response
    metrics = HistoricalTrendMetrics(
        average_daily_change=Decimal("25.50"),
        volatility=Decimal("75.25"),
        trend_direction="increasing",
        trend_strength=Decimal("0.75"),
        seasonal_factors={"monthly": Decimal("0.5")},
        confidence_score=Decimal("0.85")
    )
    
    analysis = HistoricalPeriodAnalysis(
        period_start=past,
        period_end=now,
        average_balance=Decimal("2500.00"),
        peak_balance=Decimal("3500.00"),
        lowest_balance=Decimal("1800.00"),
        total_inflow=Decimal("5000.00"),
        total_outflow=Decimal("4200.00"),
        net_change=Decimal("800.00"),
        significant_events=[]
    )
    
    seasonality = SeasonalityAnalysis(
        monthly_patterns={1: Decimal("0.8")},
        day_of_week_patterns={0: Decimal("0.4")},
        day_of_month_patterns={1: Decimal("0.9")},
        holiday_impacts={"Christmas": Decimal("0.9")},
        seasonal_strength=Decimal("0.75")
    )
    
    # Test naive datetime in timestamp
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        HistoricalTrendsResponse(
            metrics=metrics,
            period_analysis=[analysis],
            seasonality=seasonality,
            timestamp=datetime.now()  # Naive datetime
        )
    
    # Test non-UTC timezone in timestamp
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        HistoricalTrendsResponse(
            metrics=metrics,
            period_analysis=[analysis],
            seasonality=seasonality,
            timestamp=datetime.now(ZoneInfo("America/New_York"))  # Non-UTC timezone
        )


def test_required_fields():
    """Test required fields validation"""
    # Test missing fields in HistoricalTrendMetrics
    with pytest.raises(ValidationError, match="Field required"):
        HistoricalTrendMetrics(
            volatility=Decimal("75.25"),
            trend_direction="increasing",
            trend_strength=Decimal("0.75"),
            seasonal_factors={"monthly": Decimal("0.5")},
            confidence_score=Decimal("0.85")
        )
    
    # Test missing fields in HistoricalPeriodAnalysis
    now = datetime.now(timezone.utc)
    past = now - timedelta(days=30)
    
    with pytest.raises(ValidationError, match="Field required"):
        HistoricalPeriodAnalysis(
            period_start=past,
            period_end=now,
            peak_balance=Decimal("3500.00"),
            lowest_balance=Decimal("1800.00"),
            total_inflow=Decimal("5000.00"),
            total_outflow=Decimal("4200.00"),
            net_change=Decimal("800.00"),
            significant_events=[]
        )
    
    # Test missing fields in SeasonalityAnalysis
    with pytest.raises(ValidationError, match="Field required"):
        SeasonalityAnalysis(
            monthly_patterns={1: Decimal("0.8")},
            day_of_week_patterns={0: Decimal("0.4")},
            day_of_month_patterns={1: Decimal("0.9")},
            holiday_impacts={"Christmas": Decimal("0.9")}
            # Missing seasonal_strength
        )
    
    # Test missing fields in HistoricalTrendsResponse
    metrics = HistoricalTrendMetrics(
        average_daily_change=Decimal("25.50"),
        volatility=Decimal("75.25"),
        trend_direction="increasing",
        trend_strength=Decimal("0.75"),
        seasonal_factors={"monthly": Decimal("0.5")},
        confidence_score=Decimal("0.85")
    )
    
    analysis = HistoricalPeriodAnalysis(
        period_start=past,
        period_end=now,
        average_balance=Decimal("2500.00"),
        peak_balance=Decimal("3500.00"),
        lowest_balance=Decimal("1800.00"),
        total_inflow=Decimal("5000.00"),
        total_outflow=Decimal("4200.00"),
        net_change=Decimal("800.00"),
        significant_events=[]
    )
    
    seasonality = SeasonalityAnalysis(
        monthly_patterns={1: Decimal("0.8")},
        day_of_week_patterns={0: Decimal("0.4")},
        day_of_month_patterns={1: Decimal("0.9")},
        holiday_impacts={"Christmas": Decimal("0.9")},
        seasonal_strength=Decimal("0.75")
    )
    
    with pytest.raises(ValidationError, match="Field required"):
        HistoricalTrendsResponse(
            period_analysis=[analysis],
            seasonality=seasonality,
            timestamp=now
        )
