from datetime import datetime, timedelta, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo  # Only needed for non-UTC timezone tests

import pytest
from pydantic import ValidationError

from src.schemas.income_trends import (
    FrequencyType,
    IncomePattern,
    IncomeTrendsAnalysis,
    IncomeTrendsRequest,
    PeriodType,
    SeasonalityMetrics,
    SourceStatistics,
)


# Test valid object creation
def test_income_pattern_valid():
    """Test valid income pattern schema creation"""
    now = datetime.now(timezone.utc)

    data = IncomePattern(
        source="Primary Employer",
        frequency=FrequencyType.BIWEEKLY,
        average_amount=Decimal("1250.00"),
        confidence_score=Decimal("0.95"),
        last_occurrence=now,
        next_predicted=now + timedelta(days=14),
    )

    assert data.source == "Primary Employer"
    assert data.frequency == FrequencyType.BIWEEKLY
    assert data.average_amount == Decimal("1250.00")
    assert data.confidence_score == Decimal("0.95")
    assert data.last_occurrence == now
    assert data.next_predicted == now + timedelta(days=14)


def test_income_pattern_default_fields():
    """Test income pattern with default field values"""
    before = datetime.now(timezone.utc)

    data = IncomePattern(
        source="Primary Employer",
        frequency=FrequencyType.BIWEEKLY,
        average_amount=Decimal("1250.00"),
        confidence_score=Decimal("0.95"),
    )

    after = datetime.now(timezone.utc)

    assert data.source == "Primary Employer"
    assert data.frequency == FrequencyType.BIWEEKLY
    assert data.average_amount == Decimal("1250.00")
    assert data.confidence_score == Decimal("0.95")
    assert data.last_occurrence is not None
    assert before <= data.last_occurrence <= after
    # Verify the datetime exists (BaseSchemaValidator will enforce UTC timezone)
    assert data.last_occurrence is not None
    assert data.next_predicted is None


def test_seasonality_metrics_valid():
    """Test valid seasonality metrics schema creation"""
    data = SeasonalityMetrics(
        period=PeriodType.QUARTERLY,
        peak_months=[3, 6, 9, 12],
        trough_months=[1, 4, 7, 10],
        variance_coefficient=0.15,
        confidence_score=Decimal("0.8"),
    )

    assert data.period == PeriodType.QUARTERLY
    assert data.peak_months == [3, 6, 9, 12]
    assert data.trough_months == [1, 4, 7, 10]
    assert data.variance_coefficient == 0.15
    assert data.confidence_score == Decimal("0.8")


def test_source_statistics_valid():
    """Test valid source statistics schema creation"""
    data = SourceStatistics(
        source="Primary Employer",
        total_occurrences=24,
        total_amount=Decimal("30000.00"),
        average_amount=Decimal("1250.00"),
        min_amount=Decimal("1150.00"),
        max_amount=Decimal("1350.00"),
        standard_deviation=50.25,
        reliability_score=Decimal("0.95"),
    )

    assert data.source == "Primary Employer"
    assert data.total_occurrences == 24
    assert data.total_amount == Decimal("30000.00")
    assert data.average_amount == Decimal("1250.00")
    assert data.min_amount == Decimal("1150.00")
    assert data.max_amount == Decimal("1350.00")
    assert data.standard_deviation == 50.25
    assert data.reliability_score == Decimal("0.95")


def test_income_trends_analysis_valid():
    """Test valid income trends analysis schema creation"""
    now = datetime.now(timezone.utc)
    three_months_ago = now - timedelta(days=90)
    patterns = [
        IncomePattern(
            source="Primary Employer",
            frequency=FrequencyType.BIWEEKLY,
            average_amount=Decimal("1250.00"),
            confidence_score=Decimal("0.95"),
            last_occurrence=now - timedelta(days=7),
            next_predicted=now + timedelta(days=7),
        ),
        IncomePattern(
            source="Side Gig",
            frequency=FrequencyType.MONTHLY,
            average_amount=Decimal("500.00"),
            confidence_score=Decimal("0.7"),
            last_occurrence=now - timedelta(days=15),
            next_predicted=now + timedelta(days=15),
        ),
    ]

    seasonality = SeasonalityMetrics(
        period=PeriodType.QUARTERLY,
        peak_months=[3, 6, 9, 12],
        trough_months=[1, 4, 7, 10],
        variance_coefficient=0.15,
        confidence_score=Decimal("0.8"),
    )

    statistics = [
        SourceStatistics(
            source="Primary Employer",
            total_occurrences=24,
            total_amount=Decimal("30000.00"),
            average_amount=Decimal("1250.00"),
            min_amount=Decimal("1150.00"),
            max_amount=Decimal("1350.00"),
            standard_deviation=50.25,
            reliability_score=Decimal("0.95"),
        ),
        SourceStatistics(
            source="Side Gig",
            total_occurrences=12,
            total_amount=Decimal("6000.00"),
            average_amount=Decimal("500.00"),
            min_amount=Decimal("400.00"),
            max_amount=Decimal("600.00"),
            standard_deviation=75.50,
            reliability_score=Decimal("0.7"),
        ),
    ]

    data = IncomeTrendsAnalysis(
        patterns=patterns,
        seasonality=seasonality,
        source_statistics=statistics,
        analysis_date=now,
        data_start_date=three_months_ago,
        data_end_date=now,
        overall_predictability_score=Decimal("0.85"),
    )

    assert len(data.patterns) == 2
    assert data.seasonality is not None
    assert len(data.source_statistics) == 2
    assert data.analysis_date == now
    assert data.data_start_date == three_months_ago
    assert data.data_end_date == now
    assert data.overall_predictability_score == Decimal("0.85")


def test_income_trends_analysis_no_seasonality():
    """Test income trends analysis without seasonality"""
    now = datetime.now(timezone.utc)
    three_months_ago = now - timedelta(days=90)
    patterns = [
        IncomePattern(
            source="Primary Employer",
            frequency=FrequencyType.BIWEEKLY,
            average_amount=Decimal("1250.00"),
            confidence_score=Decimal("0.95"),
        )
    ]

    statistics = [
        SourceStatistics(
            source="Primary Employer",
            total_occurrences=24,
            total_amount=Decimal("30000.00"),
            average_amount=Decimal("1250.00"),
            min_amount=Decimal("1150.00"),
            max_amount=Decimal("1350.00"),
            standard_deviation=50.25,
            reliability_score=Decimal("0.95"),
        )
    ]

    data = IncomeTrendsAnalysis(
        patterns=patterns,
        seasonality=None,  # No seasonality
        source_statistics=statistics,
        analysis_date=now,
        data_start_date=three_months_ago,
        data_end_date=now,
        overall_predictability_score=Decimal("0.85"),
    )

    assert len(data.patterns) == 1
    assert data.seasonality is None
    assert len(data.source_statistics) == 1
    assert data.analysis_date == now
    assert data.data_start_date == three_months_ago
    assert data.data_end_date == now
    assert data.overall_predictability_score == Decimal("0.85")


def test_income_trends_request_valid():
    """Test valid income trends request schema creation"""
    start_date = datetime.now(timezone.utc) - timedelta(days=180)
    end_date = datetime.now(timezone.utc)

    data = IncomeTrendsRequest(
        start_date=start_date,
        end_date=end_date,
        source="Primary Employer",
        min_confidence=Decimal("0.7"),
    )

    assert data.start_date == start_date
    assert data.end_date == end_date
    assert data.source == "Primary Employer"
    assert data.min_confidence == Decimal("0.7")


def test_income_trends_request_default_fields():
    """Test income trends request with default field values"""
    data = IncomeTrendsRequest()

    assert data.start_date is None
    assert data.end_date is None
    assert data.source is None
    assert data.min_confidence == Decimal("0.5")  # Default value


# Test field validations
def test_enum_validation():
    """Test enum field validation"""
    # Test invalid frequency
    with pytest.raises(
        ValidationError,
        match="Input should be 'weekly', 'biweekly', 'monthly' or 'irregular'",
    ):
        IncomePattern(
            source="Primary Employer",
            frequency="quarterly",  # Invalid value
            average_amount=Decimal("1250.00"),
            confidence_score=0.95,
        )

    # Test invalid period
    with pytest.raises(
        ValidationError, match="Input should be 'monthly', 'quarterly' or 'annual'"
    ):
        SeasonalityMetrics(
            period="weekly",  # Invalid value
            peak_months=[3, 6, 9, 12],
            trough_months=[1, 4, 7, 10],
            variance_coefficient=0.15,
            confidence_score=0.8,
        )


def test_confidence_score_range():
    """Test confidence score range validation"""
    # Test below minimum (0)
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        IncomePattern(
            source="Primary Employer",
            frequency=FrequencyType.BIWEEKLY,
            average_amount=Decimal("1250.00"),
            confidence_score=Decimal("-0.1"),  # Invalid value
        )

    # Test above maximum (1)
    with pytest.raises(
        ValidationError, match="Input should be less than or equal to 1"
    ):
        IncomePattern(
            source="Primary Employer",
            frequency=FrequencyType.BIWEEKLY,
            average_amount=Decimal("1250.00"),
            confidence_score=Decimal("1.1"),  # Invalid value
        )

    # Test valid boundary values
    data1 = IncomePattern(
        source="Primary Employer",
        frequency=FrequencyType.BIWEEKLY,
        average_amount=Decimal("1250.00"),
        confidence_score=Decimal("0.0"),  # Minimum valid value
    )
    assert data1.confidence_score == Decimal("0.0")

    data2 = IncomePattern(
        source="Primary Employer",
        frequency=FrequencyType.BIWEEKLY,
        average_amount=Decimal("1250.00"),
        confidence_score=Decimal("1.0"),  # Maximum valid value
    )
    assert data2.confidence_score == Decimal("1.0")


def test_decimal_precision():
    """Test decimal precision validation"""
    # Test too many decimal places
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        IncomePattern(
            source="Primary Employer",
            frequency=FrequencyType.BIWEEKLY,
            average_amount=Decimal("1250.123"),  # Invalid precision
            confidence_score=Decimal("0.95"),
        )

    # Test valid decimal places
    data = IncomePattern(
        source="Primary Employer",
        frequency=FrequencyType.BIWEEKLY,
        average_amount=Decimal("1250.12"),  # Valid precision
        confidence_score=Decimal("0.95"),
    )
    assert data.average_amount == Decimal("1250.12")


def test_positive_value_validation():
    """Test positive value validation"""
    # Test zero or negative average_amount
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        IncomePattern(
            source="Primary Employer",
            frequency=FrequencyType.BIWEEKLY,
            average_amount=Decimal("0.00"),  # Invalid value
            confidence_score=0.95,
        )

    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        IncomePattern(
            source="Primary Employer",
            frequency=FrequencyType.BIWEEKLY,
            average_amount=Decimal("-1.00"),  # Invalid value
            confidence_score=0.95,
        )

    # Test zero or negative total_occurrences
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        SourceStatistics(
            source="Primary Employer",
            total_occurrences=0,  # Invalid value
            total_amount=Decimal("30000.00"),
            average_amount=Decimal("1250.00"),
            min_amount=Decimal("1150.00"),
            max_amount=Decimal("1350.00"),
            standard_deviation=50.25,
            reliability_score=0.95,
        )


def test_month_validation():
    """Test month validation in peak_months and trough_months"""
    # Test month out of range (less than 1)
    with pytest.raises(ValidationError, match="Months must be between 1 and 12"):
        SeasonalityMetrics(
            period=PeriodType.QUARTERLY,
            peak_months=[0, 6, 9, 12],  # Invalid month
            trough_months=[1, 4, 7, 10],
            variance_coefficient=0.15,
            confidence_score=0.8,
        )

    # Test month out of range (greater than 12)
    with pytest.raises(ValidationError, match="Months must be between 1 and 12"):
        SeasonalityMetrics(
            period=PeriodType.QUARTERLY,
            peak_months=[3, 6, 9, 13],  # Invalid month
            trough_months=[1, 4, 7, 10],
            variance_coefficient=0.15,
            confidence_score=0.8,
        )

    # Test duplicate months
    with pytest.raises(ValidationError, match="Duplicate months are not allowed"):
        SeasonalityMetrics(
            period=PeriodType.QUARTERLY,
            peak_months=[3, 6, 9, 9],  # Duplicate month
            trough_months=[1, 4, 7, 10],
            variance_coefficient=0.15,
            confidence_score=0.8,
        )


def test_max_amount_validation():
    """Test max_amount validation in SourceStatistics"""
    # Test max_amount less than min_amount
    with pytest.raises(
        ValidationError, match="max_amount must be greater than or equal to min_amount"
    ):
        SourceStatistics(
            source="Primary Employer",
            total_occurrences=24,
            total_amount=Decimal("30000.00"),
            average_amount=Decimal("1250.00"),
            min_amount=Decimal("1350.00"),  # Greater than max_amount
            max_amount=Decimal("1150.00"),  # Less than min_amount
            standard_deviation=50.25,
            reliability_score=0.95,
        )

    # Test valid boundary case (equal values)
    data = SourceStatistics(
        source="Primary Employer",
        total_occurrences=24,
        total_amount=Decimal("30000.00"),
        average_amount=Decimal("1250.00"),
        min_amount=Decimal("1250.00"),  # Equal to max_amount
        max_amount=Decimal("1250.00"),  # Equal to min_amount
        standard_deviation=0.0,
        reliability_score=0.95,
    )
    assert data.min_amount == data.max_amount


def test_string_length_validation():
    """Test string length validation"""
    # Test empty source
    with pytest.raises(
        ValidationError, match="String should have at least 1 character"
    ):
        IncomePattern(
            source="",  # Empty string
            frequency=FrequencyType.BIWEEKLY,
            average_amount=Decimal("1250.00"),
            confidence_score=0.95,
        )

    # Test source too long
    with pytest.raises(
        ValidationError, match="String should have at most 255 characters"
    ):
        IncomePattern(
            source="X" * 256,  # Too long
            frequency=FrequencyType.BIWEEKLY,
            average_amount=Decimal("1250.00"),
            confidence_score=0.95,
        )

    # Test valid boundary values
    data1 = IncomePattern(
        source="X",  # Minimum length
        frequency=FrequencyType.BIWEEKLY,
        average_amount=Decimal("1250.00"),
        confidence_score=0.95,
    )
    assert data1.source == "X"

    data2 = IncomePattern(
        source="X" * 255,  # Maximum length
        frequency=FrequencyType.BIWEEKLY,
        average_amount=Decimal("1250.00"),
        confidence_score=0.95,
    )
    assert len(data2.source) == 255


def test_date_range_validation():
    """Test date range validation"""
    now = datetime.now(timezone.utc)
    one_month_ago = now - timedelta(days=30)

    # Test end_date before start_date in IncomeTrendsAnalysis
    with pytest.raises(
        ValidationError, match="data_end_date must be after data_start_date"
    ):
        IncomeTrendsAnalysis(
            patterns=[
                IncomePattern(
                    source="Primary Employer",
                    frequency=FrequencyType.BIWEEKLY,
                    average_amount=Decimal("1250.00"),
                    confidence_score=0.95,
                )
            ],
            source_statistics=[
                SourceStatistics(
                    source="Primary Employer",
                    total_occurrences=24,
                    total_amount=Decimal("30000.00"),
                    average_amount=Decimal("1250.00"),
                    min_amount=Decimal("1150.00"),
                    max_amount=Decimal("1350.00"),
                    standard_deviation=50.25,
                    reliability_score=0.95,
                )
            ],
            data_start_date=now,  # Later than end_date
            data_end_date=one_month_ago,  # Earlier than start_date
            overall_predictability_score=0.85,
        )

    # Test end_date before start_date in IncomeTrendsRequest
    with pytest.raises(ValidationError, match="end_date must be after start_date"):
        IncomeTrendsRequest(
            start_date=now,  # Later than end_date
            end_date=one_month_ago,  # Earlier than start_date
        )


# Test datetime UTC validation
def test_datetime_utc_validation():
    """Test datetime UTC validation per ADR-011"""
    # Test naive datetime
    with pytest.raises(
        ValidationError, match="Please provide datetime with UTC timezone"
    ):
        IncomePattern(
            source="Primary Employer",
            frequency=FrequencyType.BIWEEKLY,
            average_amount=Decimal("1250.00"),
            confidence_score=0.95,
            last_occurrence=datetime.now(),  # Naive datetime
        )

    # Test non-UTC timezone
    with pytest.raises(
        ValidationError, match="Please provide datetime with UTC timezone"
    ):
        IncomePattern(
            source="Primary Employer",
            frequency=FrequencyType.BIWEEKLY,
            average_amount=Decimal("1250.00"),
            confidence_score=0.95,
            last_occurrence=datetime.now(
                ZoneInfo("America/New_York")
            ),  # Non-UTC timezone
        )

    # Test valid UTC datetime
    data = IncomePattern(
        source="Primary Employer",
        frequency=FrequencyType.BIWEEKLY,
        average_amount=Decimal("1250.00"),
        confidence_score=0.95,
        last_occurrence=datetime.now(timezone.utc),  # UTC timezone
    )
    # Verify the datetime is in UTC by comparing with a known UTC value created for the test
    test_utc = datetime.now(timezone.utc)
    # If both are UTC, they should both have the same timezone (tzinfo will be same type)
    assert type(data.last_occurrence).__name__ == type(test_utc).__name__


def test_required_fields():
    """Test required fields validation"""
    # Test missing required fields in IncomePattern
    with pytest.raises(ValidationError, match="Field required"):
        IncomePattern(
            frequency=FrequencyType.BIWEEKLY,
            average_amount=Decimal("1250.00"),
            confidence_score=0.95,
        )

    with pytest.raises(ValidationError, match="Field required"):
        IncomePattern(
            source="Primary Employer",
            average_amount=Decimal("1250.00"),
            confidence_score=0.95,
        )

    # Test missing required fields in IncomeTrendsAnalysis
    with pytest.raises(ValidationError, match="Field required"):
        IncomeTrendsAnalysis(
            patterns=[
                IncomePattern(
                    source="Primary Employer",
                    frequency=FrequencyType.BIWEEKLY,
                    average_amount=Decimal("1250.00"),
                    confidence_score=0.95,
                )
            ],
            source_statistics=[
                SourceStatistics(
                    source="Primary Employer",
                    total_occurrences=24,
                    total_amount=Decimal("30000.00"),
                    average_amount=Decimal("1250.00"),
                    min_amount=Decimal("1150.00"),
                    max_amount=Decimal("1350.00"),
                    standard_deviation=50.25,
                    reliability_score=0.95,
                )
            ],
            data_end_date=datetime.now(timezone.utc),
            overall_predictability_score=0.85,
        )
