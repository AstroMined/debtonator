from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Dict, List, Tuple
from zoneinfo import ZoneInfo  # Only needed for non-UTC timezone tests

import pytest
from pydantic import ValidationError

from src.schemas.cashflow.account_analysis import (
    AccountCorrelation,
    AccountRiskAssessment,
    AccountUsagePattern,
    BalanceDistribution,
    CrossAccountAnalysis,
    TransferPattern,
)


# Test valid object creation
def test_account_correlation_valid():
    """Test valid account correlation schema creation"""
    correlation = AccountCorrelation(
        correlation_score=Decimal("0.75"),
        transfer_frequency=5,
        common_categories=["Groceries", "Utilities", "Entertainment"],
        relationship_type="complementary",
    )

    assert correlation.correlation_score == Decimal("0.75")
    assert correlation.transfer_frequency == 5
    assert correlation.common_categories == ["Groceries", "Utilities", "Entertainment"]
    assert correlation.relationship_type == "complementary"


def test_transfer_pattern_valid():
    """Test valid transfer pattern schema creation"""
    pattern = TransferPattern(
        source_account_id=1,
        target_account_id=2,
        average_amount=Decimal("500.00"),
        frequency=3,
        typical_day_of_month=15,
        category_distribution={"Bills": Decimal("0.7"), "Savings": Decimal("0.3")},
    )

    assert pattern.source_account_id == 1
    assert pattern.target_account_id == 2
    assert pattern.average_amount == Decimal("500.00")
    assert pattern.frequency == 3
    assert pattern.typical_day_of_month == 15
    assert pattern.category_distribution == {
        "Bills": Decimal("0.7"),
        "Savings": Decimal("0.3"),
    }


def test_account_usage_pattern_valid():
    """Test valid account usage pattern schema creation"""
    usage = AccountUsagePattern(
        account_id=1,
        primary_use="Daily Expenses",
        average_transaction_size=Decimal("75.50"),
        common_merchants=["Walmart", "Amazon", "Target"],
        peak_usage_days=[1, 15, 30],
        category_preferences={
            "Groceries": Decimal("0.4"),
            "Shopping": Decimal("0.3"),
            "Bills": Decimal("0.3"),
        },
        utilization_rate=Decimal("0.65"),
    )

    assert usage.account_id == 1
    assert usage.primary_use == "Daily Expenses"
    assert usage.average_transaction_size == Decimal("75.50")
    assert usage.common_merchants == ["Walmart", "Amazon", "Target"]
    assert usage.peak_usage_days == [1, 15, 30]
    assert usage.category_preferences == {
        "Groceries": Decimal("0.4"),
        "Shopping": Decimal("0.3"),
        "Bills": Decimal("0.3"),
    }
    assert usage.utilization_rate == Decimal("0.65")


def test_balance_distribution_valid():
    """Test valid balance distribution schema creation"""
    distribution = BalanceDistribution(
        account_id=1,
        average_balance=Decimal("2500.00"),
        balance_volatility=Decimal("350.75"),
        min_balance_30d=Decimal("1800.00"),
        max_balance_30d=Decimal("3200.00"),
        typical_balance_range=(Decimal("2000.00"), Decimal("3000.00")),
        percentage_of_total=Decimal("0.35"),
    )

    assert distribution.account_id == 1
    assert distribution.average_balance == Decimal("2500.00")
    assert distribution.balance_volatility == Decimal("350.75")
    assert distribution.min_balance_30d == Decimal("1800.00")
    assert distribution.max_balance_30d == Decimal("3200.00")
    assert distribution.typical_balance_range == (
        Decimal("2000.00"),
        Decimal("3000.00"),
    )
    assert distribution.percentage_of_total == Decimal("0.35")


def test_account_risk_assessment_valid():
    """Test valid account risk assessment schema creation"""
    risk = AccountRiskAssessment(
        account_id=1,
        overdraft_risk=Decimal("0.15"),
        credit_utilization_risk=Decimal("0.25"),
        payment_failure_risk=Decimal("0.10"),
        volatility_score=Decimal("0.30"),
        overall_risk_score=Decimal("0.20"),
    )

    assert risk.account_id == 1
    assert risk.overdraft_risk == Decimal("0.15")
    assert risk.credit_utilization_risk == Decimal("0.25")
    assert risk.payment_failure_risk == Decimal("0.10")
    assert risk.volatility_score == Decimal("0.30")
    assert risk.overall_risk_score == Decimal("0.20")


def test_cross_account_analysis_valid():
    """Test valid cross account analysis schema creation"""
    now = datetime.now(timezone.utc)

    # Create component schemas
    correlation = AccountCorrelation(
        correlation_score=Decimal("0.75"),
        transfer_frequency=5,
        common_categories=["Groceries", "Utilities"],
        relationship_type="complementary",
    )

    pattern = TransferPattern(
        source_account_id=1,
        target_account_id=2,
        average_amount=Decimal("500.00"),
        frequency=3,
        typical_day_of_month=15,
        category_distribution={"Bills": Decimal("0.7"), "Savings": Decimal("0.3")},
    )

    usage = AccountUsagePattern(
        account_id=1,
        primary_use="Daily Expenses",
        average_transaction_size=Decimal("75.50"),
        common_merchants=["Walmart", "Amazon"],
        peak_usage_days=[1, 15],
        category_preferences={"Groceries": Decimal("0.5"), "Bills": Decimal("0.5")},
        utilization_rate=Decimal("0.65"),
    )

    distribution = BalanceDistribution(
        account_id=1,
        average_balance=Decimal("2500.00"),
        balance_volatility=Decimal("350.75"),
        min_balance_30d=Decimal("1800.00"),
        max_balance_30d=Decimal("3200.00"),
        typical_balance_range=(Decimal("2000.00"), Decimal("3000.00")),
        percentage_of_total=Decimal("0.35"),
    )

    risk = AccountRiskAssessment(
        account_id=1,
        overdraft_risk=Decimal("0.15"),
        credit_utilization_risk=Decimal("0.25"),
        payment_failure_risk=Decimal("0.10"),
        volatility_score=Decimal("0.30"),
        overall_risk_score=Decimal("0.20"),
    )

    # Create the full analysis
    analysis = CrossAccountAnalysis(
        correlations={"1": {"2": correlation}},
        transfer_patterns=[pattern],
        usage_patterns={1: usage},
        balance_distribution={1: distribution},
        risk_assessment={1: risk},
        timestamp=now,
    )

    assert analysis.correlations["1"]["2"].correlation_score == Decimal("0.75")
    assert analysis.transfer_patterns[0].average_amount == Decimal("500.00")
    assert analysis.usage_patterns[1].primary_use == "Daily Expenses"
    assert analysis.balance_distribution[1].average_balance == Decimal("2500.00")
    assert analysis.risk_assessment[1].overall_risk_score == Decimal("0.20")
    assert analysis.timestamp == now


# Test field validations
def test_account_correlation_range_validation():
    """Test range validation in account correlation schema"""
    # Test correlation_score below minimum
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to -1"
    ):
        AccountCorrelation(
            correlation_score=Decimal("-1.5"),  # Below minimum
            transfer_frequency=5,
            common_categories=["Groceries", "Utilities"],
            relationship_type="complementary",
        )

    # Test correlation_score above maximum
    with pytest.raises(
        ValidationError, match="Input should be less than or equal to 1"
    ):
        AccountCorrelation(
            correlation_score=Decimal("1.5"),  # Above maximum
            transfer_frequency=5,
            common_categories=["Groceries", "Utilities"],
            relationship_type="complementary",
        )

    # Test negative transfer_frequency
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        AccountCorrelation(
            correlation_score=Decimal("0.75"),
            transfer_frequency=-1,  # Negative
            common_categories=["Groceries", "Utilities"],
            relationship_type="complementary",
        )


def test_account_correlation_pattern_validation():
    """Test pattern validation in account correlation schema"""
    # Test invalid relationship_type
    with pytest.raises(ValidationError, match="String should match pattern"):
        AccountCorrelation(
            correlation_score=Decimal("0.75"),
            transfer_frequency=5,
            common_categories=["Groceries", "Utilities"],
            relationship_type="invalid",  # Invalid value
        )


def test_transfer_pattern_field_validation():
    """Test field validation in transfer pattern schema"""
    # Test typical_day_of_month below minimum
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 1"
    ):
        TransferPattern(
            source_account_id=1,
            target_account_id=2,
            average_amount=Decimal("500.00"),
            frequency=3,
            typical_day_of_month=0,  # Below minimum
            category_distribution={"Bills": Decimal("0.7"), "Savings": Decimal("0.3")},
        )

    # Test typical_day_of_month above maximum
    with pytest.raises(
        ValidationError, match="Input should be less than or equal to 31"
    ):
        TransferPattern(
            source_account_id=1,
            target_account_id=2,
            average_amount=Decimal("500.00"),
            frequency=3,
            typical_day_of_month=32,  # Above maximum
            category_distribution={"Bills": Decimal("0.7"), "Savings": Decimal("0.3")},
        )

    # Test negative frequency
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        TransferPattern(
            source_account_id=1,
            target_account_id=2,
            average_amount=Decimal("500.00"),
            frequency=-1,  # Negative
            typical_day_of_month=15,
            category_distribution={"Bills": Decimal("0.7"), "Savings": Decimal("0.3")},
        )


def test_balance_distribution_range_validation():
    """Test range validation in balance distribution schema"""
    # Test percentage_of_total below minimum
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        BalanceDistribution(
            account_id=1,
            average_balance=Decimal("2500.00"),
            balance_volatility=Decimal("350.75"),
            min_balance_30d=Decimal("1800.00"),
            max_balance_30d=Decimal("3200.00"),
            typical_balance_range=(Decimal("2000.00"), Decimal("3000.00")),
            percentage_of_total=Decimal("-0.1"),  # Below minimum
        )

    # Test percentage_of_total above maximum
    with pytest.raises(
        ValidationError, match="Input should be less than or equal to 1"
    ):
        BalanceDistribution(
            account_id=1,
            average_balance=Decimal("2500.00"),
            balance_volatility=Decimal("350.75"),
            min_balance_30d=Decimal("1800.00"),
            max_balance_30d=Decimal("3200.00"),
            typical_balance_range=(Decimal("2000.00"), Decimal("3000.00")),
            percentage_of_total=Decimal("1.1"),  # Above maximum
        )

    # Test percentage_of_total with valid 4 decimal places (special case field)
    distribution = BalanceDistribution(
        account_id=1,
        average_balance=Decimal("2500.00"),
        balance_volatility=Decimal("350.75"),
        min_balance_30d=Decimal("1800.00"),
        max_balance_30d=Decimal("3200.00"),
        typical_balance_range=(Decimal("2000.00"), Decimal("3000.00")),
        percentage_of_total=Decimal("0.3333"),
    )
    assert distribution.percentage_of_total == Decimal("0.3333")

    # Test percentage_of_total with too many decimal places (5 decimal places)
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.0001"):
        BalanceDistribution(
            account_id=1,
            average_balance=Decimal("2500.00"),
            balance_volatility=Decimal("350.75"),
            min_balance_30d=Decimal("1800.00"),
            max_balance_30d=Decimal("3200.00"),
            typical_balance_range=(Decimal("2000.00"), Decimal("3000.00")),
            percentage_of_total=Decimal("0.33333"),  # 5 decimal places
        )


def test_account_risk_assessment_range_validation():
    """Test range validation in account risk assessment schema"""
    # Test overdraft_risk below minimum
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        AccountRiskAssessment(
            account_id=1,
            overdraft_risk=Decimal("-0.1"),  # Below minimum
            payment_failure_risk=Decimal("0.10"),
            volatility_score=Decimal("0.30"),
            overall_risk_score=Decimal("0.20"),
        )

    # Test overdraft_risk above maximum
    with pytest.raises(
        ValidationError, match="Input should be less than or equal to 1"
    ):
        AccountRiskAssessment(
            account_id=1,
            overdraft_risk=Decimal("1.1"),  # Above maximum
            payment_failure_risk=Decimal("0.10"),
            volatility_score=Decimal("0.30"),
            overall_risk_score=Decimal("0.20"),
        )

    # Test credit_utilization_risk below minimum
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        AccountRiskAssessment(
            account_id=1,
            overdraft_risk=Decimal("0.15"),
            credit_utilization_risk=Decimal("-0.1"),  # Below minimum
            payment_failure_risk=Decimal("0.10"),
            volatility_score=Decimal("0.30"),
            overall_risk_score=Decimal("0.20"),
        )

    # Test credit_utilization_risk above maximum
    with pytest.raises(
        ValidationError, match="Input should be less than or equal to 1"
    ):
        AccountRiskAssessment(
            account_id=1,
            overdraft_risk=Decimal("0.15"),
            credit_utilization_risk=Decimal("1.1"),  # Above maximum
            payment_failure_risk=Decimal("0.10"),
            volatility_score=Decimal("0.30"),
            overall_risk_score=Decimal("0.20"),
        )


def test_account_usage_pattern_validation():
    """Test validation in account usage pattern schema"""
    # Test peak_usage_days max length
    with pytest.raises(ValidationError, match="List should have at most 31 items"):
        AccountUsagePattern(
            account_id=1,
            primary_use="Daily Expenses",
            average_transaction_size=Decimal("75.50"),
            common_merchants=["Walmart", "Amazon"],
            peak_usage_days=list(range(1, 33)),  # 32 items, exceeds max length
            category_preferences={"Groceries": Decimal("0.5"), "Bills": Decimal("0.5")},
            utilization_rate=Decimal("0.65"),
        )

    # Test common_merchants max length
    with pytest.raises(ValidationError, match="List should have at most 100 items"):
        AccountUsagePattern(
            account_id=1,
            primary_use="Daily Expenses",
            average_transaction_size=Decimal("75.50"),
            common_merchants=[
                "Merchant" + str(i) for i in range(101)
            ],  # 101 items, exceeds max length
            peak_usage_days=[1, 15],
            category_preferences={"Groceries": Decimal("0.5"), "Bills": Decimal("0.5")},
            utilization_rate=Decimal("0.65"),
        )

    # Test utilization_rate below minimum
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        AccountUsagePattern(
            account_id=1,
            primary_use="Daily Expenses",
            average_transaction_size=Decimal("75.50"),
            common_merchants=["Walmart", "Amazon"],
            peak_usage_days=[1, 15],
            category_preferences={"Groceries": Decimal("0.5"), "Bills": Decimal("0.5")},
            utilization_rate=Decimal("-0.1"),  # Below minimum
        )

    # Test utilization_rate above maximum
    with pytest.raises(
        ValidationError, match="Input should be less than or equal to 1"
    ):
        AccountUsagePattern(
            account_id=1,
            primary_use="Daily Expenses",
            average_transaction_size=Decimal("75.50"),
            common_merchants=["Walmart", "Amazon"],
            peak_usage_days=[1, 15],
            category_preferences={"Groceries": Decimal("0.5"), "Bills": Decimal("0.5")},
            utilization_rate=Decimal("1.1"),  # Above maximum
        )


def test_decimal_precision():
    """Test decimal precision validation"""
    # Test too many decimal places in correlation_score
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.0001"):
        AccountCorrelation(
            correlation_score=Decimal("0.75321"),  # Too many decimal places
            transfer_frequency=5,
            common_categories=["Groceries", "Utilities"],
            relationship_type="complementary",
        )

    # Test too many decimal places in average_amount
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        TransferPattern(
            source_account_id=1,
            target_account_id=2,
            average_amount=Decimal("500.123"),  # Too many decimal places
            frequency=3,
            typical_day_of_month=15,
            category_distribution={"Bills": Decimal("0.7"), "Savings": Decimal("0.3")},
        )

    # Test too many decimal places in average_balance
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        BalanceDistribution(
            account_id=1,
            average_balance=Decimal("2500.123"),  # Too many decimal places
            balance_volatility=Decimal("350.75"),
            min_balance_30d=Decimal("1800.00"),
            max_balance_30d=Decimal("3200.00"),
            typical_balance_range=(Decimal("2000.00"), Decimal("3000.00")),
            percentage_of_total=Decimal("0.35"),
        )

    # Test different decimal precision for money vs percentage fields
    # Money fields should have at most 2 decimal places
    balance_dist = BalanceDistribution(
        account_id=1,
        average_balance=Decimal("2500.00"),
        balance_volatility=Decimal("350.75"),
        min_balance_30d=Decimal("1800.00"),
        max_balance_30d=Decimal("3200.00"),
        typical_balance_range=(Decimal("2000.00"), Decimal("3000.00")),
        percentage_of_total=Decimal("0.3333"),  # Percentage field (4 decimal places)
    )

    assert balance_dist.average_balance == Decimal("2500.00")
    assert balance_dist.percentage_of_total == Decimal("0.3333")  # 4 decimal places

    # Test all risk assessment fields with 4 decimal places (percentage fields)
    risk = AccountRiskAssessment(
        account_id=1,
        overdraft_risk=Decimal("0.1234"),
        credit_utilization_risk=Decimal("0.2345"),
        payment_failure_risk=Decimal("0.3456"),
        volatility_score=Decimal("0.4567"),
        overall_risk_score=Decimal("0.5678"),
    )

    # Verify all risk fields accept 4 decimal places (percentage fields)
    assert risk.overdraft_risk == Decimal("0.1234")
    assert risk.credit_utilization_risk == Decimal("0.2345")
    assert risk.payment_failure_risk == Decimal("0.3456")
    assert risk.volatility_score == Decimal("0.4567")
    assert risk.overall_risk_score == Decimal("0.5678")

    # Test AccountUsagePattern percentage fields with 4 decimal places
    usage = AccountUsagePattern(
        account_id=1,
        primary_use="Daily Expenses",
        average_transaction_size=Decimal("75.50"),
        common_merchants=["Walmart", "Amazon"],
        peak_usage_days=[1, 15],
        category_preferences={
            "Groceries": Decimal("0.1234"),
            "Shopping": Decimal("0.2345"),
            "Bills": Decimal("0.6421"),
        },
        utilization_rate=Decimal("0.7654"),
    )

    # Verify percentage fields accept 4 decimal places
    assert usage.category_preferences["Groceries"] == Decimal("0.1234")
    assert usage.category_preferences["Shopping"] == Decimal("0.2345")
    assert usage.category_preferences["Bills"] == Decimal("0.6421")
    assert usage.utilization_rate == Decimal("0.7654")

    # Test validation error with too many decimal places in percentage field
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.0001"):
        AccountRiskAssessment(
            account_id=1,
            overdraft_risk=Decimal("0.12345"),  # 5 decimal places
            payment_failure_risk=Decimal("0.3456"),
            volatility_score=Decimal("0.4567"),
            overall_risk_score=Decimal("0.5678"),
        )


def test_datetime_utc_validation():
    """Test datetime UTC validation per ADR-011"""
    now = datetime.now(timezone.utc)

    # Create component schemas for cross account analysis
    correlation = AccountCorrelation(
        correlation_score=Decimal("0.75"),
        transfer_frequency=5,
        common_categories=["Groceries"],
        relationship_type="complementary",
    )

    pattern = TransferPattern(
        source_account_id=1,
        target_account_id=2,
        average_amount=Decimal("500.00"),
        frequency=3,
        category_distribution={"Bills": Decimal("1.0")},
    )

    usage = AccountUsagePattern(
        account_id=1,
        primary_use="Daily Expenses",
        average_transaction_size=Decimal("75.50"),
        common_merchants=["Walmart"],
        peak_usage_days=[1],
        category_preferences={"Groceries": Decimal("1.0")},
    )

    distribution = BalanceDistribution(
        account_id=1,
        average_balance=Decimal("2500.00"),
        balance_volatility=Decimal("350.75"),
        min_balance_30d=Decimal("1800.00"),
        max_balance_30d=Decimal("3200.00"),
        typical_balance_range=(Decimal("2000.00"), Decimal("3000.00")),
        percentage_of_total=Decimal("0.35"),
    )

    risk = AccountRiskAssessment(
        account_id=1,
        overdraft_risk=Decimal("0.15"),
        payment_failure_risk=Decimal("0.10"),
        volatility_score=Decimal("0.30"),
        overall_risk_score=Decimal("0.20"),
    )

    # Test naive datetime in timestamp
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        CrossAccountAnalysis(
            correlations={"1": {"2": correlation}},
            transfer_patterns=[pattern],
            usage_patterns={1: usage},
            balance_distribution={1: distribution},
            risk_assessment={1: risk},
            timestamp=datetime.now(),  # Naive datetime
        )

    # Test non-UTC timezone in timestamp
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        CrossAccountAnalysis(
            correlations={"1": {"2": correlation}},
            transfer_patterns=[pattern],
            usage_patterns={1: usage},
            balance_distribution={1: distribution},
            risk_assessment={1: risk},
            timestamp=datetime.now(ZoneInfo("America/New_York")),  # Non-UTC timezone
        )


def test_required_fields():
    """Test required fields validation"""
    # Test missing fields in AccountCorrelation
    with pytest.raises(ValidationError, match="Field required"):
        AccountCorrelation(
            transfer_frequency=5,
            common_categories=["Groceries"],
            relationship_type="complementary",
        )

    # Test missing fields in TransferPattern
    with pytest.raises(ValidationError, match="Field required"):
        TransferPattern(
            source_account_id=1,
            average_amount=Decimal("500.00"),
            frequency=3,
            category_distribution={"Bills": Decimal("1.0")},
        )

    # Test missing fields in AccountUsagePattern
    with pytest.raises(ValidationError, match="Field required"):
        AccountUsagePattern(
            primary_use="Daily Expenses",
            average_transaction_size=Decimal("75.50"),
            common_merchants=["Walmart"],
            peak_usage_days=[1],
            category_preferences={"Groceries": Decimal("1.0")},
        )

    # Test missing fields in BalanceDistribution
    with pytest.raises(ValidationError, match="Field required"):
        BalanceDistribution(
            account_id=1,
            balance_volatility=Decimal("350.75"),
            min_balance_30d=Decimal("1800.00"),
            max_balance_30d=Decimal("3200.00"),
            typical_balance_range=(Decimal("2000.00"), Decimal("3000.00")),
            percentage_of_total=Decimal("0.35"),
        )

    # Test missing fields in AccountRiskAssessment
    with pytest.raises(ValidationError, match="Field required"):
        AccountRiskAssessment(
            account_id=1,
            payment_failure_risk=Decimal("0.10"),
            volatility_score=Decimal("0.30"),
            overall_risk_score=Decimal("0.20"),
        )

    # Test missing fields in CrossAccountAnalysis
    now = datetime.now(timezone.utc)
    correlation = AccountCorrelation(
        correlation_score=Decimal("0.75"),
        transfer_frequency=5,
        common_categories=["Groceries"],
        relationship_type="complementary",
    )

    with pytest.raises(ValidationError, match="Field required"):
        CrossAccountAnalysis(
            correlations={"1": {"2": correlation}},
            transfer_patterns=[],
            usage_patterns={},
            risk_assessment={},
            timestamp=now,
        )


def test_optional_fields():
    """Test optional fields validation"""
    # Test optional typical_day_of_month in TransferPattern
    pattern = TransferPattern(
        source_account_id=1,
        target_account_id=2,
        average_amount=Decimal("500.00"),
        frequency=3,
        category_distribution={"Bills": Decimal("1.0")},
    )
    assert pattern.typical_day_of_month is None

    # Test optional utilization_rate in AccountUsagePattern
    usage = AccountUsagePattern(
        account_id=1,
        primary_use="Daily Expenses",
        average_transaction_size=Decimal("75.50"),
        common_merchants=["Walmart"],
        peak_usage_days=[1],
        category_preferences={"Groceries": Decimal("1.0")},
    )
    assert usage.utilization_rate is None

    # Test optional credit_utilization_risk in AccountRiskAssessment
    risk = AccountRiskAssessment(
        account_id=1,
        overdraft_risk=Decimal("0.15"),
        payment_failure_risk=Decimal("0.10"),
        volatility_score=Decimal("0.30"),
        overall_risk_score=Decimal("0.20"),
    )
    assert risk.credit_utilization_risk is None
