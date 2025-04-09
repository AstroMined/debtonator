"""
Unit tests for payment pattern schema factory functions.

Tests ensure that payment pattern schema factories produce valid schema instances
that pass validation.
"""

# pylint: disable=no-member

from datetime import datetime, timezone
from decimal import Decimal

from src.schemas.payment_patterns import (
    AmountStatistics,
    FrequencyMetrics,
    PatternType,
    PaymentPatternAnalysis,
    PaymentPatternRequest,
    SeasonalMetrics,
)
from tests.helpers.schema_factories.payment_patterns_schema_factories import (
    create_amount_statistics_schema,
    create_frequency_metrics_schema,
    create_payment_pattern_analysis_schema,
    create_payment_pattern_request_schema,
    create_seasonal_metrics_schema,
)


def test_create_amount_statistics_schema():
    """Test creating an AmountStatistics schema with default values."""
    schema = create_amount_statistics_schema()

    assert isinstance(schema, AmountStatistics)
    assert schema.average_amount == Decimal("150.00")
    assert schema.std_dev_amount == Decimal("15.00")
    assert schema.min_amount == Decimal("100.00")
    assert schema.max_amount == Decimal("200.00")
    assert schema.total_amount == Decimal("1500.00")


def test_create_amount_statistics_schema_with_custom_values():
    """Test creating an AmountStatistics schema with custom values."""
    schema = create_amount_statistics_schema(
        average_amount=Decimal("250.00"),
        std_dev_amount=Decimal("25.00"),
        min_amount=Decimal("200.00"),
        max_amount=Decimal("300.00"),
        total_amount=Decimal("2500.00"),
    )

    assert isinstance(schema, AmountStatistics)
    assert schema.average_amount == Decimal("250.00")
    assert schema.std_dev_amount == Decimal("25.00")
    assert schema.min_amount == Decimal("200.00")
    assert schema.max_amount == Decimal("300.00")
    assert schema.total_amount == Decimal("2500.00")


def test_create_frequency_metrics_schema():
    """Test creating a FrequencyMetrics schema with default values."""
    schema = create_frequency_metrics_schema()

    assert isinstance(schema, FrequencyMetrics)
    assert schema.average_days_between == 30.5
    assert schema.std_dev_days == 1.5
    assert schema.min_days == 29
    assert schema.max_days == 32


def test_create_frequency_metrics_schema_with_custom_values():
    """Test creating a FrequencyMetrics schema with custom values."""
    schema = create_frequency_metrics_schema(
        average_days_between=15.25, std_dev_days=0.75, min_days=14, max_days=16
    )

    assert isinstance(schema, FrequencyMetrics)
    assert schema.average_days_between == 15.25
    assert schema.std_dev_days == 0.75
    assert schema.min_days == 14
    assert schema.max_days == 16


def test_create_seasonal_metrics_schema():
    """Test creating a SeasonalMetrics schema with default values."""
    schema = create_seasonal_metrics_schema()

    assert isinstance(schema, SeasonalMetrics)
    assert schema.avg_days_before_due == 3.5
    assert schema.std_dev_days == 1.2
    assert schema.sample_size == 10


def test_create_seasonal_metrics_schema_with_custom_values():
    """Test creating a SeasonalMetrics schema with custom values."""
    schema = create_seasonal_metrics_schema(
        avg_days_before_due=5.5, std_dev_days=2.1, sample_size=20
    )

    assert isinstance(schema, SeasonalMetrics)
    assert schema.avg_days_before_due == 5.5
    assert schema.std_dev_days == 2.1
    assert schema.sample_size == 20


def test_create_payment_pattern_analysis_schema():
    """Test creating a PaymentPatternAnalysis schema with default values."""
    schema = create_payment_pattern_analysis_schema()

    assert isinstance(schema, PaymentPatternAnalysis)
    assert schema.pattern_type == PatternType.REGULAR
    assert schema.confidence_score == Decimal("0.95")
    assert isinstance(schema.frequency_metrics, FrequencyMetrics)
    assert isinstance(schema.amount_statistics, AmountStatistics)
    assert schema.sample_size == 10
    assert isinstance(schema.analysis_period_start, datetime)
    assert isinstance(schema.analysis_period_end, datetime)
    assert schema.suggested_category is None
    assert schema.notes is None
    assert schema.seasonal_metrics is None


def test_create_payment_pattern_analysis_schema_with_custom_values():
    """Test creating a PaymentPatternAnalysis schema with custom values."""
    start_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(2023, 12, 31, tzinfo=timezone.utc)
    notes = ["Pattern shows high consistency", "Recommend setting up auto-payment"]

    frequency_metrics = create_frequency_metrics_schema(
        average_days_between=14.0, std_dev_days=0.5, min_days=13, max_days=15
    )

    amount_statistics = create_amount_statistics_schema(
        average_amount=Decimal("300.00"),
        std_dev_amount=Decimal("10.00"),
        min_amount=Decimal("280.00"),
        max_amount=Decimal("320.00"),
        total_amount=Decimal("3000.00"),
    )

    seasonal_metrics = {
        1: create_seasonal_metrics_schema().model_dump(),
        7: create_seasonal_metrics_schema(avg_days_before_due=2.0).model_dump(),
    }

    schema = create_payment_pattern_analysis_schema(
        pattern_type=PatternType.SEASONAL,
        confidence_score=Decimal("0.85"),
        frequency_metrics=frequency_metrics.model_dump(),
        amount_statistics=amount_statistics.model_dump(),
        sample_size=15,
        analysis_period_start=start_date,
        analysis_period_end=end_date,
        suggested_category="Utilities",
        notes=notes,
        seasonal_metrics=seasonal_metrics,
    )

    assert isinstance(schema, PaymentPatternAnalysis)
    assert schema.pattern_type == PatternType.SEASONAL
    assert schema.confidence_score == Decimal("0.85")
    assert schema.frequency_metrics.average_days_between == 14.0
    assert schema.amount_statistics.average_amount == Decimal("300.00")
    assert schema.sample_size == 15
    assert schema.analysis_period_start == start_date
    assert schema.analysis_period_end == end_date
    assert schema.suggested_category == "Utilities"
    assert schema.notes == notes
    assert 1 in schema.seasonal_metrics
    assert 7 in schema.seasonal_metrics
    assert schema.seasonal_metrics[1].avg_days_before_due == 3.5
    assert schema.seasonal_metrics[7].avg_days_before_due == 2.0


def test_create_payment_pattern_request_schema():
    """Test creating a PaymentPatternRequest schema with default values."""
    schema = create_payment_pattern_request_schema()

    assert isinstance(schema, PaymentPatternRequest)
    assert schema.account_id is None
    assert schema.category_id is None
    assert schema.start_date is None
    assert schema.end_date is None
    assert schema.min_sample_size == 3
    assert schema.liability_id is None


def test_create_payment_pattern_request_schema_with_custom_values():
    """Test creating a PaymentPatternRequest schema with custom values."""
    start_date = datetime(2023, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(2023, 12, 31, tzinfo=timezone.utc)

    schema = create_payment_pattern_request_schema(
        account_id=1,
        category_id="utilities",
        start_date=start_date,
        end_date=end_date,
        min_sample_size=5,
        liability_id=2,
    )

    assert isinstance(schema, PaymentPatternRequest)
    assert schema.account_id == 1
    assert schema.category_id == "utilities"
    assert schema.start_date == start_date
    assert schema.end_date == end_date
    assert schema.min_sample_size == 5
    assert schema.liability_id == 2


def test_create_payment_pattern_request_schema_with_minimum_sample_size():
    """Test creating a PaymentPatternRequest schema with minimum sample size."""
    schema = create_payment_pattern_request_schema(min_sample_size=2)

    assert isinstance(schema, PaymentPatternRequest)
    assert schema.min_sample_size == 2
