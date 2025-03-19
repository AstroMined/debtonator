from datetime import datetime, timezone, timedelta
from decimal import Decimal
from zoneinfo import ZoneInfo  # Only needed for non-UTC timezone tests

import pytest
from pydantic import ValidationError

from src.schemas.payment_patterns import (
    PatternType,
    FrequencyMetrics,
    AmountStatistics,
    SeasonalMetrics,
    PaymentPatternAnalysis,
    PaymentPatternRequest,
)


# Test valid object creation
def test_frequency_metrics_valid():
    """Test valid frequency metrics schema creation"""
    data = FrequencyMetrics(
        average_days_between=30.5,
        std_dev_days=1.2,
        min_days=29,
        max_days=32
    )

    assert data.average_days_between == 30.5
    assert data.std_dev_days == 1.2
    assert data.min_days == 29
    assert data.max_days == 32


def test_amount_statistics_valid():
    """Test valid amount statistics schema creation"""
    data = AmountStatistics(
        average_amount=Decimal("150.00"),
        std_dev_amount=Decimal("10.00"),
        min_amount=Decimal("140.00"),
        max_amount=Decimal("160.00"),
        total_amount=Decimal("1500.00")
    )

    assert data.average_amount == Decimal("150.00")
    assert data.std_dev_amount == Decimal("10.00")
    assert data.min_amount == Decimal("140.00")
    assert data.max_amount == Decimal("160.00")
    assert data.total_amount == Decimal("1500.00")


def test_seasonal_metrics_valid():
    """Test valid seasonal metrics schema creation"""
    data = SeasonalMetrics(
        avg_days_before_due=5.3,
        std_dev_days=1.8,
        sample_size=10
    )

    assert data.avg_days_before_due == 5.3
    assert data.std_dev_days == 1.8
    assert data.sample_size == 10


def test_payment_pattern_analysis_valid():
    """Test valid payment pattern analysis schema creation"""
    now = datetime.now(timezone.utc)
    six_months_ago = now - timedelta(days=180)
    
    frequency_metrics = FrequencyMetrics(
        average_days_between=30.5,
        std_dev_days=1.2,
        min_days=29,
        max_days=32
    )
    
    amount_statistics = AmountStatistics(
        average_amount=Decimal("150.00"),
        std_dev_amount=Decimal("10.00"),
        min_amount=Decimal("140.00"),
        max_amount=Decimal("160.00"),
        total_amount=Decimal("1500.00")
    )
    
    seasonal_metrics = {
        1: SeasonalMetrics(
            avg_days_before_due=5.3,
            std_dev_days=1.8,
            sample_size=5
        ),
        7: SeasonalMetrics(
            avg_days_before_due=4.8,
            std_dev_days=1.5,
            sample_size=5
        )
    }
    
    data = PaymentPatternAnalysis(
        pattern_type=PatternType.REGULAR,
        confidence_score=Decimal("0.95"),
        frequency_metrics=frequency_metrics,
        amount_statistics=amount_statistics,
        sample_size=10,
        analysis_period_start=six_months_ago,
        analysis_period_end=now,
        suggested_category="Utilities",
        notes=["Consistent monthly payments", "Slight amount variations in summer"],
        seasonal_metrics=seasonal_metrics
    )

    assert data.pattern_type == PatternType.REGULAR
    assert data.confidence_score == Decimal("0.95")
    assert data.frequency_metrics == frequency_metrics
    assert data.amount_statistics == amount_statistics
    assert data.sample_size == 10
    assert data.analysis_period_start == six_months_ago
    assert data.analysis_period_end == now
    assert data.suggested_category == "Utilities"
    assert len(data.notes) == 2
    assert len(data.seasonal_metrics) == 2
    assert data.seasonal_metrics[1].sample_size == 5
    assert data.seasonal_metrics[7].sample_size == 5


def test_payment_pattern_analysis_minimal():
    """Test payment pattern analysis with minimal required fields"""
    now = datetime.now(timezone.utc)
    six_months_ago = now - timedelta(days=180)
    
    frequency_metrics = FrequencyMetrics(
        average_days_between=30.5,
        std_dev_days=1.2,
        min_days=29,
        max_days=32
    )
    
    amount_statistics = AmountStatistics(
        average_amount=Decimal("150.00"),
        std_dev_amount=Decimal("10.00"),
        min_amount=Decimal("140.00"),
        max_amount=Decimal("160.00"),
        total_amount=Decimal("1500.00")
    )
    
    data = PaymentPatternAnalysis(
        pattern_type=PatternType.REGULAR,
        confidence_score=Decimal("0.95"),
        frequency_metrics=frequency_metrics,
        amount_statistics=amount_statistics,
        sample_size=10,
        analysis_period_start=six_months_ago,
        analysis_period_end=now
    )

    assert data.pattern_type == PatternType.REGULAR
    assert data.confidence_score == Decimal("0.95")
    assert data.frequency_metrics == frequency_metrics
    assert data.amount_statistics == amount_statistics
    assert data.sample_size == 10
    assert data.analysis_period_start == six_months_ago
    assert data.analysis_period_end == now
    assert data.suggested_category is None
    assert data.notes is None
    assert data.seasonal_metrics is None


def test_payment_pattern_request_valid():
    """Test valid payment pattern request schema creation"""
    start_date = datetime.now(timezone.utc) - timedelta(days=180)
    end_date = datetime.now(timezone.utc)
    
    data = PaymentPatternRequest(
        account_id=1,
        category_id="utilities",
        start_date=start_date,
        end_date=end_date,
        min_sample_size=5,
        liability_id=2
    )

    assert data.account_id == 1
    assert data.category_id == "utilities"
    assert data.start_date == start_date
    assert data.end_date == end_date
    assert data.min_sample_size == 5
    assert data.liability_id == 2


def test_payment_pattern_request_default_fields():
    """Test payment pattern request with default values"""
    data = PaymentPatternRequest()

    assert data.account_id is None
    assert data.category_id is None
    assert data.start_date is None
    assert data.end_date is None
    assert data.min_sample_size == 3  # Default value
    assert data.liability_id is None


# Test field validations
def test_enum_validation():
    """Test pattern type enum validation"""
    # Test invalid pattern type
    with pytest.raises(ValidationError, match="Input should be 'regular', 'irregular', 'seasonal' or 'unknown'"):
        PaymentPatternAnalysis(
            pattern_type="monthly",  # Invalid value
            confidence_score=0.95,
            frequency_metrics=FrequencyMetrics(
                average_days_between=30.5,
                std_dev_days=1.2,
                min_days=29,
                max_days=32
            ),
            amount_statistics=AmountStatistics(
                average_amount=Decimal("150.00"),
                std_dev_amount=Decimal("10.00"),
                min_amount=Decimal("140.00"),
                max_amount=Decimal("160.00"),
                total_amount=Decimal("1500.00")
            ),
            sample_size=10,
            analysis_period_start=datetime.now(timezone.utc) - timedelta(days=180),
            analysis_period_end=datetime.now(timezone.utc)
        )


def test_confidence_score_range():
    """Test confidence score range validation"""
    frequency_metrics = FrequencyMetrics(
        average_days_between=30.5,
        std_dev_days=1.2,
        min_days=29,
        max_days=32
    )
    
    amount_statistics = AmountStatistics(
        average_amount=Decimal("150.00"),
        std_dev_amount=Decimal("10.00"),
        min_amount=Decimal("140.00"),
        max_amount=Decimal("160.00"),
        total_amount=Decimal("1500.00")
    )
    
    # Test below minimum (0)
    with pytest.raises(ValidationError, match="Input should be greater than or equal to 0"):
        PaymentPatternAnalysis(
            pattern_type=PatternType.REGULAR,
            confidence_score=Decimal("-0.1"),  # Invalid value
            frequency_metrics=frequency_metrics,
            amount_statistics=amount_statistics,
            sample_size=10,
            analysis_period_start=datetime.now(timezone.utc) - timedelta(days=180),
            analysis_period_end=datetime.now(timezone.utc)
        )
    
    # Test above maximum (1)
    with pytest.raises(ValidationError, match="Input should be less than or equal to 1"):
        PaymentPatternAnalysis(
            pattern_type=PatternType.REGULAR,
            confidence_score=Decimal("1.1"),  # Invalid value
            frequency_metrics=frequency_metrics,
            amount_statistics=amount_statistics,
            sample_size=10,
            analysis_period_start=datetime.now(timezone.utc) - timedelta(days=180),
            analysis_period_end=datetime.now(timezone.utc)
        )


def test_decimal_precision():
    """Test decimal precision validation"""
    # Test too many decimal places
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        AmountStatistics(
            average_amount=Decimal("150.123"),  # Invalid precision
            std_dev_amount=Decimal("10.00"),
            min_amount=Decimal("140.00"),
            max_amount=Decimal("160.00"),
            total_amount=Decimal("1500.00")
        )
    
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        AmountStatistics(
            average_amount=Decimal("150.00"),
            std_dev_amount=Decimal("10.123"),  # Invalid precision
            min_amount=Decimal("140.00"),
            max_amount=Decimal("160.00"),
            total_amount=Decimal("1500.00")
        )


def test_non_negative_values():
    """Test non-negative value validation"""
    # Test negative values for FrequencyMetrics
    with pytest.raises(ValidationError, match="Input should be greater than or equal to 0"):
        FrequencyMetrics(
            average_days_between=-1.0,  # Invalid negative value
            std_dev_days=1.2,
            min_days=29,
            max_days=32
        )
    
    with pytest.raises(ValidationError, match="Input should be greater than or equal to 0"):
        FrequencyMetrics(
            average_days_between=30.5,
            std_dev_days=-1.2,  # Invalid negative value
            min_days=29,
            max_days=32
        )
    
    with pytest.raises(ValidationError, match="Input should be greater than or equal to 0"):
        FrequencyMetrics(
            average_days_between=30.5,
            std_dev_days=1.2,
            min_days=-1,  # Invalid negative value
            max_days=32
        )
    
    # Test negative values for AmountStatistics (std_dev_amount)
    with pytest.raises(ValidationError, match="Input should be greater than or equal to 0"):
        AmountStatistics(
            average_amount=Decimal("150.00"),
            std_dev_amount=Decimal("-10.00"),  # Invalid negative value
            min_amount=Decimal("140.00"),
            max_amount=Decimal("160.00"),
            total_amount=Decimal("1500.00")
        )


def test_positive_sample_size():
    """Test positive sample size validation"""
    # Test zero or negative sample size in SeasonalMetrics
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        SeasonalMetrics(
            avg_days_before_due=5.3,
            std_dev_days=1.8,
            sample_size=0  # Invalid zero value
        )
    
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        SeasonalMetrics(
            avg_days_before_due=5.3,
            std_dev_days=1.8,
            sample_size=-1  # Invalid negative value
        )
    
    # Test zero or negative sample size in PaymentPatternAnalysis
    frequency_metrics = FrequencyMetrics(
        average_days_between=30.5,
        std_dev_days=1.2,
        min_days=29,
        max_days=32
    )
    
    amount_statistics = AmountStatistics(
        average_amount=Decimal("150.00"),
        std_dev_amount=Decimal("10.00"),
        min_amount=Decimal("140.00"),
        max_amount=Decimal("160.00"),
        total_amount=Decimal("1500.00")
    )
    
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        PaymentPatternAnalysis(
            pattern_type=PatternType.REGULAR,
            confidence_score=0.95,
            frequency_metrics=frequency_metrics,
            amount_statistics=amount_statistics,
            sample_size=0,  # Invalid zero value
            analysis_period_start=datetime.now(timezone.utc) - timedelta(days=180),
            analysis_period_end=datetime.now(timezone.utc)
        )


def test_min_sample_size_validation():
    """Test min_sample_size validation in PaymentPatternRequest"""
    # Test below minimum (2)
    with pytest.raises(ValidationError, match="Input should be greater than or equal to 2"):
        PaymentPatternRequest(min_sample_size=1)  # Invalid value
    
    # Test valid values
    data1 = PaymentPatternRequest(min_sample_size=2)  # Minimum valid value
    assert data1.min_sample_size == 2
    
    data2 = PaymentPatternRequest(min_sample_size=10)  # Higher valid value
    assert data2.min_sample_size == 10


def test_string_length_validation():
    """Test string length validation"""
    frequency_metrics = FrequencyMetrics(
        average_days_between=30.5,
        std_dev_days=1.2,
        min_days=29,
        max_days=32
    )
    
    amount_statistics = AmountStatistics(
        average_amount=Decimal("150.00"),
        std_dev_amount=Decimal("10.00"),
        min_amount=Decimal("140.00"),
        max_amount=Decimal("160.00"),
        total_amount=Decimal("1500.00")
    )
    
    # Test suggested category too long
    with pytest.raises(ValidationError, match="String should have at most 100 characters"):
        PaymentPatternAnalysis(
            pattern_type=PatternType.REGULAR,
            confidence_score=0.95,
            frequency_metrics=frequency_metrics,
            amount_statistics=amount_statistics,
            sample_size=10,
            analysis_period_start=datetime.now(timezone.utc) - timedelta(days=180),
            analysis_period_end=datetime.now(timezone.utc),
            suggested_category="X" * 101  # Too long
        )
    
    # Test category_id too long
    with pytest.raises(ValidationError, match="String should have at most 100 characters"):
        PaymentPatternRequest(
            category_id="X" * 101  # Too long
        )


def test_positive_id_validation():
    """Test positive ID validation"""
    # Test zero or negative account_id
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        PaymentPatternRequest(account_id=0)  # Invalid zero value
    
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        PaymentPatternRequest(account_id=-1)  # Invalid negative value
    
    # Test zero or negative liability_id
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        PaymentPatternRequest(liability_id=0)  # Invalid zero value
    
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        PaymentPatternRequest(liability_id=-1)  # Invalid negative value


# Test datetime UTC validation
def test_datetime_utc_validation():
    """Test datetime UTC validation per ADR-011"""
    frequency_metrics = FrequencyMetrics(
        average_days_between=30.5,
        std_dev_days=1.2,
        min_days=29,
        max_days=32
    )
    
    amount_statistics = AmountStatistics(
        average_amount=Decimal("150.00"),
        std_dev_amount=Decimal("10.00"),
        min_amount=Decimal("140.00"),
        max_amount=Decimal("160.00"),
        total_amount=Decimal("1500.00")
    )
    
    now = datetime.now(timezone.utc)
    
    # Test naive datetime
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        PaymentPatternAnalysis(
            pattern_type=PatternType.REGULAR,
            confidence_score=0.95,
            frequency_metrics=frequency_metrics,
            amount_statistics=amount_statistics,
            sample_size=10,
            analysis_period_start=datetime.now(),  # Naive datetime
            analysis_period_end=now
        )
    
    # Test non-UTC timezone
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        PaymentPatternAnalysis(
            pattern_type=PatternType.REGULAR,
            confidence_score=0.95,
            frequency_metrics=frequency_metrics,
            amount_statistics=amount_statistics,
            sample_size=10,
            analysis_period_start=now,
            analysis_period_end=datetime.now(ZoneInfo("America/New_York"))  # Non-UTC timezone
        )
    
    # Test naive datetime in request
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        PaymentPatternRequest(
            start_date=datetime.now()  # Naive datetime
        )
    
    # Test non-UTC timezone in request
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        PaymentPatternRequest(
            start_date=datetime.now(ZoneInfo("America/New_York"))  # Non-UTC timezone
        )


def test_required_fields():
    """Test required fields validation"""
    # Missing in FrequencyMetrics
    with pytest.raises(ValidationError, match="Field required"):
        FrequencyMetrics(
            std_dev_days=1.2,
            min_days=29,
            max_days=32
        )
    
    # Missing in AmountStatistics
    with pytest.raises(ValidationError, match="Field required"):
        AmountStatistics(
            std_dev_amount=Decimal("10.00"),
            min_amount=Decimal("140.00"),
            max_amount=Decimal("160.00"),
            total_amount=Decimal("1500.00")
        )
    
    # Missing in SeasonalMetrics
    with pytest.raises(ValidationError, match="Field required"):
        SeasonalMetrics(
            std_dev_days=1.8,
            sample_size=10
        )
    
    # Missing in PaymentPatternAnalysis
    frequency_metrics = FrequencyMetrics(
        average_days_between=30.5,
        std_dev_days=1.2,
        min_days=29,
        max_days=32
    )
    
    amount_statistics = AmountStatistics(
        average_amount=Decimal("150.00"),
        std_dev_amount=Decimal("10.00"),
        min_amount=Decimal("140.00"),
        max_amount=Decimal("160.00"),
        total_amount=Decimal("1500.00")
    )
    
    with pytest.raises(ValidationError, match="Field required"):
        PaymentPatternAnalysis(
            confidence_score=0.95,  # Missing pattern_type
            frequency_metrics=frequency_metrics,
            amount_statistics=amount_statistics,
            sample_size=10,
            analysis_period_start=datetime.now(timezone.utc) - timedelta(days=180),
            analysis_period_end=datetime.now(timezone.utc)
        )
