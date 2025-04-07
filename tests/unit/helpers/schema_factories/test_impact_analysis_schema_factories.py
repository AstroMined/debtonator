"""
Unit tests for impact analysis schema factory functions.

Tests ensure that impact analysis schema factories produce valid schema instances
that pass validation.
"""

# pylint: disable=no-member

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from src.schemas.impact_analysis import (
    AccountImpact,
    CashflowImpact,
    RiskFactor,
    SplitImpactAnalysis,
    SplitImpactRequest,
)
from tests.helpers.schema_factories.impact_analysis import (
    create_account_impact_schema,
    create_cashflow_impact_schema,
    create_risk_factor_schema,
    create_split_impact_analysis_schema,
    create_split_impact_request_schema,
)


def test_create_account_impact_schema():
    """Test creating an AccountImpact schema with default values."""
    schema = create_account_impact_schema(account_id=1)
    
    assert isinstance(schema, AccountImpact)
    assert schema.account_id == 1
    assert schema.current_balance == Decimal("1000.00")
    assert schema.projected_balance == Decimal("900.00")
    assert schema.current_credit_utilization is None
    assert schema.projected_credit_utilization is None
    assert schema.risk_score == 35


def test_create_account_impact_schema_with_custom_values():
    """Test creating an AccountImpact schema with custom values."""
    schema = create_account_impact_schema(
        account_id=2,
        current_balance=Decimal("2000.00"),
        projected_balance=Decimal("1750.00"),
        current_credit_utilization=Decimal("0.30"),
        projected_credit_utilization=Decimal("0.35"),
        risk_score=40
    )
    
    assert isinstance(schema, AccountImpact)
    assert schema.account_id == 2
    assert schema.current_balance == Decimal("2000.00")
    assert schema.projected_balance == Decimal("1750.00")
    assert schema.current_credit_utilization == Decimal("0.30")
    assert schema.projected_credit_utilization == Decimal("0.35")
    assert schema.risk_score == 40


def test_create_account_impact_schema_with_partial_custom_values():
    """Test creating an AccountImpact schema with some custom values."""
    schema = create_account_impact_schema(
        account_id=3,
        current_balance=Decimal("3000.00"),
        current_credit_utilization=Decimal("0.25")
    )
    
    assert isinstance(schema, AccountImpact)
    assert schema.account_id == 3
    assert schema.current_balance == Decimal("3000.00")
    assert schema.projected_balance == Decimal("900.00")  # Default value
    assert schema.current_credit_utilization == Decimal("0.25")
    assert schema.projected_credit_utilization is None
    assert schema.risk_score == 35  # Default value


def test_create_cashflow_impact_schema():
    """Test creating a CashflowImpact schema with default values."""
    schema = create_cashflow_impact_schema()
    
    assert isinstance(schema, CashflowImpact)
    assert isinstance(schema.date, datetime)
    assert schema.date.tzinfo == timezone.utc
    assert schema.total_bills == Decimal("500.00")
    assert schema.available_funds == Decimal("1000.00")
    assert schema.projected_deficit is None


def test_create_cashflow_impact_schema_with_custom_values():
    """Test creating a CashflowImpact schema with custom values."""
    custom_date = datetime(2023, 6, 15, tzinfo=timezone.utc)
    
    schema = create_cashflow_impact_schema(
        date=custom_date,
        total_bills=Decimal("750.00"),
        available_funds=Decimal("500.00"),
        projected_deficit=Decimal("250.00")
    )
    
    assert isinstance(schema, CashflowImpact)
    assert schema.date == custom_date
    assert schema.total_bills == Decimal("750.00")
    assert schema.available_funds == Decimal("500.00")
    assert schema.projected_deficit == Decimal("250.00")


def test_create_risk_factor_schema():
    """Test creating a RiskFactor schema with default values."""
    schema = create_risk_factor_schema()
    
    assert isinstance(schema, RiskFactor)
    assert schema.name == "Insufficient Funds"
    assert schema.severity == 65
    assert schema.description == "Risk of insufficient funds to cover upcoming bills"


def test_create_risk_factor_schema_with_custom_values():
    """Test creating a RiskFactor schema with custom values."""
    schema = create_risk_factor_schema(
        name="Payment Timing Risk",
        severity=75,
        description="Risk of payment timing conflicts with income schedule"
    )
    
    assert isinstance(schema, RiskFactor)
    assert schema.name == "Payment Timing Risk"
    assert schema.severity == 75
    assert schema.description == "Risk of payment timing conflicts with income schedule"


def test_create_split_impact_analysis_schema():
    """Test creating a SplitImpactAnalysis schema with default values."""
    schema = create_split_impact_analysis_schema()
    
    assert isinstance(schema, SplitImpactAnalysis)
    assert schema.total_amount == Decimal("1000.00")
    assert schema.overall_risk_score == 45
    
    # Check account impacts
    assert len(schema.account_impacts) == 2
    assert schema.account_impacts[0].account_id == 1
    assert schema.account_impacts[0].current_balance == Decimal("1000.00")
    assert schema.account_impacts[1].account_id == 2
    assert schema.account_impacts[1].current_balance == Decimal("2000.00")
    
    # Check cashflow impacts
    assert len(schema.cashflow_impacts) == 2
    assert isinstance(schema.cashflow_impacts[0].date, datetime)
    assert schema.cashflow_impacts[0].total_bills == Decimal("500.00")
    assert schema.cashflow_impacts[1].projected_deficit == Decimal("100.00")
    
    # Check risk factors
    assert len(schema.risk_factors) == 2
    assert schema.risk_factors[0].name == "Insufficient Funds"
    assert schema.risk_factors[1].name == "Credit Utilization"
    
    # Check recommendations
    assert len(schema.recommendations) == 3
    assert "Split bill payment across multiple pay periods" in schema.recommendations


def test_create_split_impact_analysis_schema_with_custom_values():
    """Test creating a SplitImpactAnalysis schema with custom values."""
    custom_account_impacts = [
        create_account_impact_schema(
            account_id=3,
            current_balance=Decimal("1500.00"),
            projected_balance=Decimal("1200.00")
        ).model_dump()
    ]
    
    custom_cashflow_impacts = [
        create_cashflow_impact_schema(
            total_bills=Decimal("300.00"),
            available_funds=Decimal("1200.00")
        ).model_dump()
    ]
    
    custom_risk_factors = [
        create_risk_factor_schema(
            name="Custom Risk",
            severity=50,
            description="Custom risk description"
        ).model_dump()
    ]
    
    custom_recommendations = ["Custom recommendation"]
    
    schema = create_split_impact_analysis_schema(
        total_amount=Decimal("1500.00"),
        account_impacts=custom_account_impacts,
        cashflow_impacts=custom_cashflow_impacts,
        risk_factors=custom_risk_factors,
        overall_risk_score=60,
        recommendations=custom_recommendations
    )
    
    assert isinstance(schema, SplitImpactAnalysis)
    assert schema.total_amount == Decimal("1500.00")
    assert schema.overall_risk_score == 60
    assert len(schema.account_impacts) == 1
    assert schema.account_impacts[0].account_id == 3
    assert schema.account_impacts[0].current_balance == Decimal("1500.00")
    assert len(schema.cashflow_impacts) == 1
    assert schema.cashflow_impacts[0].total_bills == Decimal("300.00")
    assert len(schema.risk_factors) == 1
    assert schema.risk_factors[0].name == "Custom Risk"
    assert schema.recommendations == custom_recommendations


def test_create_split_impact_request_schema():
    """Test creating a SplitImpactRequest schema with default values."""
    schema = create_split_impact_request_schema(liability_id=1)
    
    assert isinstance(schema, SplitImpactRequest)
    assert schema.liability_id == 1
    assert schema.analysis_period_days == 90
    assert isinstance(schema.start_date, datetime)
    assert schema.start_date.tzinfo == timezone.utc
    
    # Check splits
    assert len(schema.splits) == 2
    assert schema.splits[0]["account_id"] == 1
    assert schema.splits[0]["amount"] == Decimal("300.00")
    assert schema.splits[1]["account_id"] == 2
    assert schema.splits[1]["amount"] == Decimal("700.00")


def test_create_split_impact_request_schema_with_custom_values():
    """Test creating a SplitImpactRequest schema with custom values."""
    custom_date = datetime(2023, 6, 15, tzinfo=timezone.utc)
    custom_splits = [
        {"account_id": 3, "amount": Decimal("400.00")},
        {"account_id": 4, "amount": Decimal("600.00")},
    ]
    
    schema = create_split_impact_request_schema(
        liability_id=2,
        splits=custom_splits,
        analysis_period_days=180,
        start_date=custom_date
    )
    
    assert isinstance(schema, SplitImpactRequest)
    assert schema.liability_id == 2
    assert schema.splits == custom_splits
    assert schema.analysis_period_days == 180
    assert schema.start_date == custom_date


def test_create_split_impact_request_schema_with_valid_analysis_period_bounds():
    """Test creating a SplitImpactRequest schema with minimum and maximum analysis periods."""
    # Test minimum allowed analysis period (14 days)
    min_schema = create_split_impact_request_schema(
        liability_id=1,
        analysis_period_days=14
    )
    assert min_schema.analysis_period_days == 14
    
    # Test maximum allowed analysis period (365 days)
    max_schema = create_split_impact_request_schema(
        liability_id=1,
        analysis_period_days=365
    )
    assert max_schema.analysis_period_days == 365
