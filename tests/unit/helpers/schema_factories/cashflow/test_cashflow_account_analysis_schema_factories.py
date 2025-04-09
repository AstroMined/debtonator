"""
Unit tests for account analysis schema factory functions.

Tests ensure that account analysis schema factories produce valid schema instances
that pass validation.
"""

# pylint: disable=no-member

from datetime import datetime, timezone
from decimal import Decimal

from src.schemas.cashflow.cashflow_account_analysis import (
    AccountCorrelation,
    AccountRiskAssessment,
    AccountUsagePattern,
    BalanceDistribution,
    CrossAccountAnalysis,
    TransferPattern,
)
from tests.helpers.schema_factories.cashflow.cashflow_account_analysis_schema_factories import (
    create_account_correlation_schema,
    create_account_risk_assessment_schema,
    create_account_usage_pattern_schema,
    create_balance_distribution_schema,
    create_cross_account_analysis_schema,
    create_transfer_pattern_schema,
)


def test_create_account_correlation_schema():
    """Test creating an AccountCorrelation schema with default values."""
    schema = create_account_correlation_schema()

    assert isinstance(schema, AccountCorrelation)
    assert schema.correlation_score == Decimal("0.75")
    assert schema.transfer_frequency == 3
    assert schema.common_categories == ["Bills", "Groceries", "Utilities"]
    assert schema.relationship_type == "complementary"


def test_create_account_correlation_schema_with_custom_values():
    """Test creating an AccountCorrelation schema with custom values."""
    custom_categories = ["Rent", "Entertainment", "Travel"]

    schema = create_account_correlation_schema(
        correlation_score=Decimal("-0.25"),
        transfer_frequency=5,
        common_categories=custom_categories,
        relationship_type="supplementary",
    )

    assert isinstance(schema, AccountCorrelation)
    assert schema.correlation_score == Decimal("-0.25")
    assert schema.transfer_frequency == 5
    assert schema.common_categories == custom_categories
    assert schema.relationship_type == "supplementary"


def test_create_transfer_pattern_schema():
    """Test creating a TransferPattern schema with default values."""
    schema = create_transfer_pattern_schema(source_account_id=1, target_account_id=2)

    assert isinstance(schema, TransferPattern)
    assert schema.source_account_id == 1
    assert schema.target_account_id == 2
    assert schema.average_amount == Decimal("500.00")
    assert schema.frequency == 2
    assert schema.typical_day_of_month is None
    assert "Bills" in schema.category_distribution
    assert schema.category_distribution["Bills"] == Decimal("0.5")
    assert "Savings" in schema.category_distribution
    assert schema.category_distribution["Savings"] == Decimal("0.3")
    assert "Discretionary" in schema.category_distribution
    assert schema.category_distribution["Discretionary"] == Decimal("0.2")


def test_create_transfer_pattern_schema_with_custom_values():
    """Test creating a TransferPattern schema with custom values."""
    custom_categories = {
        "Rent": Decimal("0.7"),
        "Utilities": Decimal("0.3"),
    }

    schema = create_transfer_pattern_schema(
        source_account_id=3,
        target_account_id=4,
        average_amount=Decimal("750.00"),
        frequency=3,
        typical_day_of_month=15,
        category_distribution=custom_categories,
    )

    assert isinstance(schema, TransferPattern)
    assert schema.source_account_id == 3
    assert schema.target_account_id == 4
    assert schema.average_amount == Decimal("750.00")
    assert schema.frequency == 3
    assert schema.typical_day_of_month == 15
    assert schema.category_distribution == custom_categories


def test_create_account_usage_pattern_schema():
    """Test creating an AccountUsagePattern schema with default values."""
    schema = create_account_usage_pattern_schema(account_id=1)

    assert isinstance(schema, AccountUsagePattern)
    assert schema.account_id == 1
    assert schema.primary_use == "Daily Expenses"
    assert schema.average_transaction_size == Decimal("100.00")
    assert "Grocery Store" in schema.common_merchants
    assert 1 in schema.peak_usage_days
    assert 15 in schema.peak_usage_days
    assert 28 in schema.peak_usage_days
    assert "Groceries" in schema.category_preferences
    assert schema.category_preferences["Groceries"] == Decimal("0.3")
    assert schema.utilization_rate is None


def test_create_account_usage_pattern_schema_with_custom_values():
    """Test creating an AccountUsagePattern schema with custom values."""
    custom_merchants = ["Amazon", "Starbucks", "Target"]
    custom_peak_days = [5, 20]
    custom_categories = {"Coffee": Decimal("0.4"), "Shopping": Decimal("0.6")}

    schema = create_account_usage_pattern_schema(
        account_id=2,
        primary_use="Online Shopping",
        average_transaction_size=Decimal("50.00"),
        common_merchants=custom_merchants,
        peak_usage_days=custom_peak_days,
        category_preferences=custom_categories,
        utilization_rate=Decimal("0.65"),
    )

    assert isinstance(schema, AccountUsagePattern)
    assert schema.account_id == 2
    assert schema.primary_use == "Online Shopping"
    assert schema.average_transaction_size == Decimal("50.00")
    assert schema.common_merchants == custom_merchants
    assert schema.peak_usage_days == custom_peak_days
    assert schema.category_preferences == custom_categories
    assert schema.utilization_rate == Decimal("0.65")


def test_create_balance_distribution_schema():
    """Test creating a BalanceDistribution schema with default values."""
    schema = create_balance_distribution_schema(account_id=1)

    assert isinstance(schema, BalanceDistribution)
    assert schema.account_id == 1
    assert schema.average_balance == Decimal("1500.00")
    assert schema.balance_volatility == Decimal("300.00")
    assert schema.min_balance_30d == Decimal("1000.00")
    assert schema.max_balance_30d == Decimal("2000.00")
    assert schema.typical_balance_range[0] == Decimal("800.00")
    assert schema.typical_balance_range[1] == Decimal("2200.00")
    assert schema.percentage_of_total == Decimal("0.35")


def test_create_balance_distribution_schema_with_custom_values():
    """Test creating a BalanceDistribution schema with custom values."""
    custom_range = (Decimal("500.00"), Decimal("3000.00"))

    schema = create_balance_distribution_schema(
        account_id=2,
        average_balance=Decimal("2500.00"),
        balance_volatility=Decimal("500.00"),
        min_balance_30d=Decimal("1500.00"),
        max_balance_30d=Decimal("3500.00"),
        typical_balance_range=custom_range,
        percentage_of_total=Decimal("0.45"),
    )

    assert isinstance(schema, BalanceDistribution)
    assert schema.account_id == 2
    assert schema.average_balance == Decimal("2500.00")
    assert schema.balance_volatility == Decimal("500.00")
    assert schema.min_balance_30d == Decimal("1500.00")
    assert schema.max_balance_30d == Decimal("3500.00")
    assert schema.typical_balance_range == custom_range
    assert schema.percentage_of_total == Decimal("0.45")


def test_create_account_risk_assessment_schema():
    """Test creating an AccountRiskAssessment schema with default values."""
    schema = create_account_risk_assessment_schema(account_id=1)

    assert isinstance(schema, AccountRiskAssessment)
    assert schema.account_id == 1
    assert schema.overdraft_risk == Decimal("0.25")
    assert schema.credit_utilization_risk is None
    assert schema.payment_failure_risk == Decimal("0.15")
    assert schema.volatility_score == Decimal("0.30")
    assert schema.overall_risk_score == Decimal("0.23")


def test_create_account_risk_assessment_schema_with_custom_values():
    """Test creating an AccountRiskAssessment schema with custom values."""
    schema = create_account_risk_assessment_schema(
        account_id=2,
        overdraft_risk=Decimal("0.10"),
        credit_utilization_risk=Decimal("0.35"),
        payment_failure_risk=Decimal("0.05"),
        volatility_score=Decimal("0.15"),
        overall_risk_score=Decimal("0.15"),
    )

    assert isinstance(schema, AccountRiskAssessment)
    assert schema.account_id == 2
    assert schema.overdraft_risk == Decimal("0.10")
    assert schema.credit_utilization_risk == Decimal("0.35")
    assert schema.payment_failure_risk == Decimal("0.05")
    assert schema.volatility_score == Decimal("0.15")
    assert schema.overall_risk_score == Decimal("0.15")


def test_create_cross_account_analysis_schema():
    """Test creating a CrossAccountAnalysis schema with default values."""
    schema = create_cross_account_analysis_schema()

    assert isinstance(schema, CrossAccountAnalysis)
    assert isinstance(schema.timestamp, datetime)
    assert schema.timestamp.tzinfo == timezone.utc

    # Check correlations
    assert "1-2" in schema.correlations
    assert "correlation" in schema.correlations["1-2"]
    assert isinstance(schema.correlations["1-2"]["correlation"], AccountCorrelation)
    assert schema.correlations["1-2"]["correlation"].correlation_score == Decimal(
        "0.75"
    )

    # Check transfer patterns
    assert len(schema.transfer_patterns) == 2
    assert schema.transfer_patterns[0].source_account_id == 1
    assert schema.transfer_patterns[0].target_account_id == 2
    assert schema.transfer_patterns[1].source_account_id == 2
    assert schema.transfer_patterns[1].target_account_id == 1

    # Check usage patterns
    assert 1 in schema.usage_patterns
    assert 2 in schema.usage_patterns
    assert schema.usage_patterns[1].primary_use == "Daily Expenses"

    # Check balance distribution
    assert 1 in schema.balance_distribution
    assert 2 in schema.balance_distribution
    assert schema.balance_distribution[1].average_balance == Decimal("1500.00")

    # Check risk assessment
    assert 1 in schema.risk_assessment
    assert 2 in schema.risk_assessment
    assert schema.risk_assessment[1].overdraft_risk == Decimal("0.25")


def test_create_cross_account_analysis_schema_with_custom_timestamp():
    """Test creating a CrossAccountAnalysis schema with a custom timestamp."""
    custom_timestamp = datetime(2023, 6, 15, tzinfo=timezone.utc)

    schema = create_cross_account_analysis_schema(timestamp=custom_timestamp)

    assert isinstance(schema, CrossAccountAnalysis)
    assert schema.timestamp == custom_timestamp


def test_create_cross_account_analysis_schema_with_custom_values():
    """Test creating a CrossAccountAnalysis schema with custom nested schemas."""
    # Create custom correlation data
    correlation_obj = create_account_correlation_schema(
        correlation_score=Decimal("0.9"), relationship_type="independent"
    )

    correlations = {"3-4": {"correlation": correlation_obj}}

    # Create custom transfer patterns
    transfer_pattern = create_transfer_pattern_schema(
        source_account_id=3, target_account_id=4, average_amount=Decimal("1000.00")
    ).model_dump()

    transfer_patterns = [transfer_pattern]

    # Create custom usage patterns
    usage_pattern = create_account_usage_pattern_schema(
        account_id=3, primary_use="Savings"
    ).model_dump()

    usage_patterns = {3: usage_pattern}

    # Create custom balance distribution
    balance_dist = create_balance_distribution_schema(
        account_id=3, average_balance=Decimal("5000.00")
    ).model_dump()

    balance_distribution = {3: balance_dist}

    # Create custom risk assessment
    risk_assessment_data = create_account_risk_assessment_schema(
        account_id=3, overall_risk_score=Decimal("0.05")
    ).model_dump()

    risk_assessment = {3: risk_assessment_data}

    # Create schema with all custom components
    schema = create_cross_account_analysis_schema(
        correlations=correlations,
        transfer_patterns=transfer_patterns,
        usage_patterns=usage_patterns,
        balance_distribution=balance_distribution,
        risk_assessment=risk_assessment,
    )

    assert isinstance(schema, CrossAccountAnalysis)
    assert "3-4" in schema.correlations
    assert "correlation" in schema.correlations["3-4"]
    assert schema.correlations["3-4"]["correlation"].correlation_score == Decimal("0.9")
    assert schema.correlations["3-4"]["correlation"].relationship_type == "independent"

    assert len(schema.transfer_patterns) == 1
    assert schema.transfer_patterns[0].source_account_id == 3
    assert schema.transfer_patterns[0].target_account_id == 4

    assert 3 in schema.usage_patterns
    assert schema.usage_patterns[3].primary_use == "Savings"

    assert 3 in schema.balance_distribution
    assert schema.balance_distribution[3].average_balance == Decimal("5000.00")

    assert 3 in schema.risk_assessment
    assert schema.risk_assessment[3].overall_risk_score == Decimal("0.05")
