"""
Unit tests for income trends schema factory functions.

Tests ensure that income trends schema factories produce valid schema instances
that pass validation and maintain ADR-011 compliance for datetime handling.
"""

# pylint: disable=no-member

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Dict, List

import pytest

from src.schemas.income_trends import (
    FrequencyType,
    IncomePattern,
    IncomeTrendsAnalysis,
    IncomeTrendsRequest,
    PeriodType,
    SeasonalityMetrics,
    SourceStatistics,
)
from src.utils.datetime_utils import datetime_equals, utc_now
from tests.helpers.schema_factories.base import MEDIUM_AMOUNT
from tests.helpers.schema_factories.income_trends import (
    create_income_pattern_schema,
    create_income_trends_analysis_schema,
    create_income_trends_request_schema,
    create_seasonality_metrics_schema,
    create_source_statistics_schema,
)


def test_create_income_pattern_schema():
    """Test creating an IncomePattern schema with default values."""
    schema = create_income_pattern_schema()
    
    assert isinstance(schema, IncomePattern)
    assert schema.source == "Salary"
    assert schema.frequency == FrequencyType.BIWEEKLY
    assert schema.average_amount == MEDIUM_AMOUNT * Decimal("20")  # 2000.00
    assert schema.confidence_score == Decimal("0.85")
    
    # Verify last_occurrence is timezone-aware and in UTC per ADR-011
    assert schema.last_occurrence.tzinfo is not None
    assert schema.last_occurrence.tzinfo == timezone.utc
    
    # Verify next_predicted is calculated based on frequency (BIWEEKLY = 14 days)
    assert schema.next_predicted is not None
    delta = schema.next_predicted - schema.last_occurrence
    assert delta.days == 14


def test_create_income_pattern_schema_with_custom_values():
    """Test creating an IncomePattern schema with custom values."""
    last_occurrence = utc_now()
    next_predicted = last_occurrence + timedelta(days=30)
    
    schema = create_income_pattern_schema(
        source="Freelance",
        frequency=FrequencyType.MONTHLY,
        average_amount=Decimal("3000.00"),
        confidence_score=Decimal("0.7"),
        last_occurrence=last_occurrence,
        next_predicted=next_predicted
    )
    
    assert isinstance(schema, IncomePattern)
    assert schema.source == "Freelance"
    assert schema.frequency == FrequencyType.MONTHLY
    assert schema.average_amount == Decimal("3000.00")
    assert schema.confidence_score == Decimal("0.7")
    
    # Verify datetime fields using datetime_equals for proper ADR-011 comparison
    assert datetime_equals(schema.last_occurrence, last_occurrence)
    assert datetime_equals(schema.next_predicted, next_predicted)


def test_create_income_pattern_schema_irregular_frequency():
    """Test creating an IncomePattern schema with irregular frequency."""
    last_occurrence = utc_now()
    
    schema = create_income_pattern_schema(
        source="Side Gig",
        frequency=FrequencyType.IRREGULAR,
        average_amount=Decimal("500.00"),
        confidence_score=Decimal("0.6"),
        last_occurrence=last_occurrence
    )
    
    assert isinstance(schema, IncomePattern)
    assert schema.source == "Side Gig"
    assert schema.frequency == FrequencyType.IRREGULAR
    assert schema.average_amount == Decimal("500.00")
    assert schema.confidence_score == Decimal("0.6")
    
    # Irregular frequency may have next_predicted as None, but the field still exists
    assert schema.next_predicted is None


def test_create_seasonality_metrics_schema():
    """Test creating a SeasonalityMetrics schema with default values."""
    schema = create_seasonality_metrics_schema()
    
    assert isinstance(schema, SeasonalityMetrics)
    assert schema.period == PeriodType.MONTHLY
    assert schema.peak_months == [3, 11, 12]  # March, November, December
    assert schema.trough_months == [1, 7, 8]  # January, July, August
    assert schema.variance_coefficient == 0.35
    assert schema.confidence_score == Decimal("0.75")


def test_create_seasonality_metrics_schema_with_custom_values():
    """Test creating a SeasonalityMetrics schema with custom values."""
    peak_months = [5, 6, 7]  # May, June, July
    trough_months = [11, 12, 1]  # November, December, January
    
    schema = create_seasonality_metrics_schema(
        period=PeriodType.QUARTERLY,
        peak_months=peak_months,
        trough_months=trough_months,
        variance_coefficient=0.5,
        confidence_score=Decimal("0.85")
    )
    
    assert isinstance(schema, SeasonalityMetrics)
    assert schema.period == PeriodType.QUARTERLY
    assert schema.peak_months == peak_months
    assert schema.trough_months == trough_months
    assert schema.variance_coefficient == 0.5
    assert schema.confidence_score == Decimal("0.85")


def test_create_source_statistics_schema():
    """Test creating a SourceStatistics schema with default values."""
    schema = create_source_statistics_schema()
    
    assert isinstance(schema, SourceStatistics)
    assert schema.source == "Salary"
    assert schema.total_occurrences == 24
    assert schema.total_amount == MEDIUM_AMOUNT * Decimal("20") * Decimal("24")  # 48000.00
    assert schema.average_amount == MEDIUM_AMOUNT * Decimal("20")  # 2000.00
    assert schema.min_amount == MEDIUM_AMOUNT * Decimal("20") - MEDIUM_AMOUNT * Decimal("1.5")  # 1850.00
    assert schema.max_amount == MEDIUM_AMOUNT * Decimal("20") + MEDIUM_AMOUNT * Decimal("2")  # 2200.00
    assert schema.standard_deviation == 150.0
    assert schema.reliability_score == Decimal("0.9")


def test_create_source_statistics_schema_with_custom_values():
    """Test creating a SourceStatistics schema with custom values."""
    schema = create_source_statistics_schema(
        source="Consulting",
        total_occurrences=12,
        total_amount=Decimal("36000.00"),
        average_amount=Decimal("3000.00"),
        min_amount=Decimal("2000.00"),
        max_amount=Decimal("4000.00"),
        standard_deviation=250.0,
        reliability_score=Decimal("0.8")
    )
    
    assert isinstance(schema, SourceStatistics)
    assert schema.source == "Consulting"
    assert schema.total_occurrences == 12
    assert schema.total_amount == Decimal("36000.00")
    assert schema.average_amount == Decimal("3000.00")
    assert schema.min_amount == Decimal("2000.00")
    assert schema.max_amount == Decimal("4000.00")
    assert schema.standard_deviation == 250.0
    assert schema.reliability_score == Decimal("0.8")


def test_create_income_trends_analysis_schema():
    """Test creating an IncomeTrendsAnalysis schema with default values."""
    schema = create_income_trends_analysis_schema()
    
    assert isinstance(schema, IncomeTrendsAnalysis)
    
    # Verify datetime fields are timezone-aware and in UTC per ADR-011
    assert schema.analysis_date.tzinfo is not None
    assert schema.analysis_date.tzinfo == timezone.utc
    assert schema.data_start_date.tzinfo is not None
    assert schema.data_start_date.tzinfo == timezone.utc
    assert schema.data_end_date.tzinfo is not None
    assert schema.data_end_date.tzinfo == timezone.utc
    
    # Verify data_start_date is 2 years before data_end_date
    delta = schema.data_end_date - schema.data_start_date
    assert delta.days >= 730  # ~2 years
    
    # Verify patterns list contains IncomePattern instances
    assert isinstance(schema.patterns, List)
    assert len(schema.patterns) >= 1
    assert isinstance(schema.patterns[0], IncomePattern)
    
    # Verify source_statistics list contains SourceStatistics instances
    assert isinstance(schema.source_statistics, List)
    assert len(schema.source_statistics) >= 1
    assert isinstance(schema.source_statistics[0], SourceStatistics)
    
    # Seasonality is optional but should be included about 50% of the time
    # We'll just check if it exists without asserting either way
    if hasattr(schema, "seasonality"):
        assert isinstance(schema.seasonality, SeasonalityMetrics)
    
    assert schema.overall_predictability_score == Decimal("0.82")


def test_create_income_trends_analysis_schema_with_custom_values():
    """Test creating an IncomeTrendsAnalysis schema with custom values."""
    analysis_date = utc_now()
    data_start_date = analysis_date - timedelta(days=365)  # 1 year ago
    data_end_date = analysis_date
    
    # Create custom patterns
    patterns = [
        create_income_pattern_schema(
            source="Main Job",
            frequency=FrequencyType.BIWEEKLY,
            average_amount=Decimal("2500.00")
        ).model_dump(),
        create_income_pattern_schema(
            source="Side Project",
            frequency=FrequencyType.MONTHLY,
            average_amount=Decimal("1000.00")
        ).model_dump(),
    ]
    
    # Create custom source_statistics
    source_statistics = [
        create_source_statistics_schema(
            source="Main Job",
            total_occurrences=26,
            average_amount=Decimal("2500.00")
        ).model_dump(),
        create_source_statistics_schema(
            source="Side Project",
            total_occurrences=12,
            average_amount=Decimal("1000.00")
        ).model_dump(),
    ]
    
    # Create custom seasonality
    seasonality = create_seasonality_metrics_schema(
        period=PeriodType.QUARTERLY,
        confidence_score=Decimal("0.9")
    ).model_dump()
    
    schema = create_income_trends_analysis_schema(
        patterns=patterns,
        seasonality=seasonality,
        source_statistics=source_statistics,
        analysis_date=analysis_date,
        data_start_date=data_start_date,
        data_end_date=data_end_date,
        overall_predictability_score=Decimal("0.88")
    )
    
    assert isinstance(schema, IncomeTrendsAnalysis)
    
    # Verify datetime fields using datetime_equals for proper ADR-011 comparison
    assert datetime_equals(schema.analysis_date, analysis_date)
    assert datetime_equals(schema.data_start_date, data_start_date)
    assert datetime_equals(schema.data_end_date, data_end_date)
    
    # Verify custom patterns
    assert len(schema.patterns) == 2
    assert schema.patterns[0].source == "Main Job"
    assert schema.patterns[0].average_amount == Decimal("2500.00")
    assert schema.patterns[1].source == "Side Project"
    
    # Verify custom source_statistics
    assert len(schema.source_statistics) == 2
    assert schema.source_statistics[0].source == "Main Job"
    assert schema.source_statistics[0].total_occurrences == 26
    
    # Verify custom seasonality
    assert schema.seasonality.period == PeriodType.QUARTERLY
    assert schema.seasonality.confidence_score == Decimal("0.9")
    
    assert schema.overall_predictability_score == Decimal("0.88")


def test_create_income_trends_request_schema_empty():
    """Test creating an empty IncomeTrendsRequest schema."""
    schema = create_income_trends_request_schema()
    
    assert isinstance(schema, IncomeTrendsRequest)
    assert schema.start_date is None
    assert schema.end_date is None
    assert schema.source is None
    assert schema.min_confidence == Decimal("0.5")


def test_create_income_trends_request_schema_with_all_fields():
    """Test creating an IncomeTrendsRequest schema with all fields."""
    start_date = utc_now() - timedelta(days=90)
    end_date = utc_now()
    
    schema = create_income_trends_request_schema(
        start_date=start_date,
        end_date=end_date,
        source="Salary",
        min_confidence=Decimal("0.7")
    )
    
    assert isinstance(schema, IncomeTrendsRequest)
    
    # Verify datetime fields using datetime_equals for proper ADR-011 comparison
    assert datetime_equals(schema.start_date, start_date)
    assert datetime_equals(schema.end_date, end_date)
    
    assert schema.source == "Salary"
    assert schema.min_confidence == Decimal("0.7")


def test_create_income_trends_request_schema_with_partial_fields():
    """Test creating an IncomeTrendsRequest schema with partial fields."""
    start_date = utc_now() - timedelta(days=90)
    
    schema = create_income_trends_request_schema(
        start_date=start_date,
        source="Freelance"
    )
    
    assert isinstance(schema, IncomeTrendsRequest)
    
    # Verify datetime field using datetime_equals for proper ADR-011 comparison
    assert datetime_equals(schema.start_date, start_date)
    
    assert schema.end_date is None
    assert schema.source == "Freelance"
    assert schema.min_confidence == Decimal("0.5")  # Default value


def test_enum_handling():
    """Test proper enum handling in schema factories."""
    # Test FrequencyType enum
    schema1 = create_income_pattern_schema(frequency=FrequencyType.WEEKLY)
    assert schema1.frequency == FrequencyType.WEEKLY
    
    schema2 = create_income_pattern_schema(frequency=FrequencyType.MONTHLY)
    assert schema2.frequency == FrequencyType.MONTHLY
    
    # Test PeriodType enum
    schema3 = create_seasonality_metrics_schema(period=PeriodType.MONTHLY)
    assert schema3.period == PeriodType.MONTHLY
    
    schema4 = create_seasonality_metrics_schema(period=PeriodType.ANNUAL)
    assert schema4.period == PeriodType.ANNUAL
