from datetime import datetime, timedelta, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo  # Only needed for non-UTC timezone tests

import pytest
from pydantic import ValidationError

from src.schemas.impact_analysis import (
    AccountImpact,
    CashflowImpact,
    RiskFactor,
    SplitImpactAnalysis,
    SplitImpactRequest,
)


# Test valid object creation
def test_account_impact_valid():
    """Test valid account impact schema creation"""
    data = AccountImpact(
        account_id=1,
        current_balance=Decimal("500.00"),
        projected_balance=Decimal("400.00"),
        current_credit_utilization=Decimal("0.30"),
        projected_credit_utilization=Decimal("0.40"),
        risk_score=25,
    )

    assert data.account_id == 1
    assert data.current_balance == Decimal("500.00")
    assert data.projected_balance == Decimal("400.00")
    assert data.current_credit_utilization == Decimal("0.30")
    assert data.projected_credit_utilization == Decimal("0.40")
    assert data.risk_score == 25


def test_account_impact_optional_fields():
    """Test account impact with optional fields omitted"""
    data = AccountImpact(
        account_id=1,
        current_balance=Decimal("500.00"),
        projected_balance=Decimal("400.00"),
        risk_score=25,
    )

    assert data.account_id == 1
    assert data.current_balance == Decimal("500.00")
    assert data.projected_balance == Decimal("400.00")
    assert data.current_credit_utilization is None
    assert data.projected_credit_utilization is None
    assert data.risk_score == 25


def test_cashflow_impact_valid():
    """Test valid cashflow impact schema creation"""
    now = datetime.now(timezone.utc)

    data = CashflowImpact(
        date=now,
        total_bills=Decimal("250.00"),
        available_funds=Decimal("300.00"),
        projected_deficit=Decimal("-50.00"),
    )

    assert data.date == now
    assert data.total_bills == Decimal("250.00")
    assert data.available_funds == Decimal("300.00")
    assert data.projected_deficit == Decimal("-50.00")


def test_cashflow_impact_default_date():
    """Test cashflow impact with default date"""
    before = datetime.now(timezone.utc)
    data = CashflowImpact(
        total_bills=Decimal("250.00"), available_funds=Decimal("300.00")
    )
    after = datetime.now(timezone.utc)

    assert data.date is not None
    assert before <= data.date <= after
    assert isinstance(data.date, datetime)
    assert data.date.tzinfo == timezone.utc
    assert data.total_bills == Decimal("250.00")
    assert data.available_funds == Decimal("300.00")
    assert data.projected_deficit is None


def test_risk_factor_valid():
    """Test valid risk factor schema creation"""
    data = RiskFactor(
        name="Insufficient funds",
        severity=75,
        description="Account may have insufficient funds for upcoming bills",
    )

    assert data.name == "Insufficient funds"
    assert data.severity == 75
    assert data.description == "Account may have insufficient funds for upcoming bills"


def test_split_impact_analysis_valid():
    """Test valid split impact analysis schema creation"""
    account_impacts = [
        AccountImpact(
            account_id=1,
            current_balance=Decimal("500.00"),
            projected_balance=Decimal("400.00"),
            risk_score=25,
        ),
        AccountImpact(
            account_id=2,
            current_balance=Decimal("300.00"),
            projected_balance=Decimal("200.00"),
            risk_score=40,
        ),
    ]

    now = datetime.now(timezone.utc)
    cashflow_impacts = [
        CashflowImpact(
            date=now, total_bills=Decimal("250.00"), available_funds=Decimal("300.00")
        ),
        CashflowImpact(
            date=now + timedelta(days=30),
            total_bills=Decimal("300.00"),
            available_funds=Decimal("250.00"),
            projected_deficit=Decimal("-50.00"),
        ),
    ]

    risk_factors = [
        RiskFactor(
            name="Insufficient funds",
            severity=75,
            description="Account may have insufficient funds for upcoming bills",
        ),
        RiskFactor(
            name="High utilization",
            severity=60,
            description="Credit utilization may exceed recommended limits",
        ),
    ]

    recommendations = [
        "Consider delaying payment until after next deposit",
        "Split bill across multiple accounts to reduce impact",
    ]

    data = SplitImpactAnalysis(
        total_amount=Decimal("600.00"),
        account_impacts=account_impacts,
        cashflow_impacts=cashflow_impacts,
        risk_factors=risk_factors,
        overall_risk_score=65,
        recommendations=recommendations,
    )

    assert data.total_amount == Decimal("600.00")
    assert len(data.account_impacts) == 2
    assert len(data.cashflow_impacts) == 2
    assert len(data.risk_factors) == 2
    assert data.overall_risk_score == 65
    assert len(data.recommendations) == 2


def test_split_impact_request_valid():
    """Test valid split impact request schema creation"""
    now = datetime.now(timezone.utc)
    splits = [
        {"account_id": 1, "amount": Decimal("300.00")},
        {"account_id": 2, "amount": Decimal("200.00")},
    ]

    data = SplitImpactRequest(
        liability_id=5, splits=splits, analysis_period_days=60, start_date=now
    )

    assert data.liability_id == 5
    assert len(data.splits) == 2
    assert data.analysis_period_days == 60
    assert data.start_date == now


def test_split_impact_request_defaults():
    """Test split impact request with default values"""
    before = datetime.now(timezone.utc)
    splits = [
        {"account_id": 1, "amount": Decimal("300.00")},
        {"account_id": 2, "amount": Decimal("200.00")},
    ]

    data = SplitImpactRequest(liability_id=5, splits=splits)
    after = datetime.now(timezone.utc)

    assert data.liability_id == 5
    assert len(data.splits) == 2
    assert data.analysis_period_days == 90  # default value
    assert data.start_date is not None
    assert before <= data.start_date <= after
    assert data.start_date.tzinfo == timezone.utc


# Test field validations
def test_account_id_validation():
    """Test account_id validation"""
    # Test invalid account_id (less than or equal to 0)
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        AccountImpact(
            account_id=0,
            current_balance=Decimal("500.00"),
            projected_balance=Decimal("400.00"),
            risk_score=25,
        )

    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        AccountImpact(
            account_id=-1,
            current_balance=Decimal("500.00"),
            projected_balance=Decimal("400.00"),
            risk_score=25,
        )


def test_decimal_precision():
    """Test decimal precision validation"""
    # Test too many decimal places for money fields
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        AccountImpact(
            account_id=1,
            current_balance=Decimal("500.123"),
            projected_balance=Decimal("400.00"),
            risk_score=25,
        )

    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        AccountImpact(
            account_id=1,
            current_balance=Decimal("500.00"),
            projected_balance=Decimal("400.123"),
            risk_score=25,
        )

    # Test too many decimal places for percentage fields
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.0001"):
        AccountImpact(
            account_id=1,
            current_balance=Decimal("500.00"),
            projected_balance=Decimal("400.00"),
            current_credit_utilization=Decimal("0.30001"),
            risk_score=25,
        )


def test_credit_utilization_range():
    """Test credit utilization range validation"""
    # Test below minimum (0)
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        AccountImpact(
            account_id=1,
            current_balance=Decimal("500.00"),
            projected_balance=Decimal("400.00"),
            current_credit_utilization=Decimal("-0.01"),
            risk_score=25,
        )

    # Test above maximum (1)
    with pytest.raises(
        ValidationError, match="Input should be less than or equal to 1"
    ):
        AccountImpact(
            account_id=1,
            current_balance=Decimal("500.00"),
            projected_balance=Decimal("400.00"),
            current_credit_utilization=Decimal("1.01"),
            risk_score=25,
        )

    # Test valid boundary values
    data1 = AccountImpact(
        account_id=1,
        current_balance=Decimal("500.00"),
        projected_balance=Decimal("400.00"),
        current_credit_utilization=Decimal("0.00"),
        risk_score=25,
    )
    assert data1.current_credit_utilization == Decimal("0.00")

    data2 = AccountImpact(
        account_id=1,
        current_balance=Decimal("500.00"),
        projected_balance=Decimal("400.00"),
        current_credit_utilization=Decimal("1.00"),
        risk_score=25,
    )
    assert data2.current_credit_utilization == Decimal("1.00")


def test_risk_score_range():
    """Test risk score range validation"""
    # Test below minimum (0)
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        AccountImpact(
            account_id=1,
            current_balance=Decimal("500.00"),
            projected_balance=Decimal("400.00"),
            risk_score=-1,
        )

    # Test above maximum (100)
    with pytest.raises(
        ValidationError, match="Input should be less than or equal to 100"
    ):
        AccountImpact(
            account_id=1,
            current_balance=Decimal("500.00"),
            projected_balance=Decimal("400.00"),
            risk_score=101,
        )

    # Test valid boundary values
    data1 = AccountImpact(
        account_id=1,
        current_balance=Decimal("500.00"),
        projected_balance=Decimal("400.00"),
        risk_score=0,
    )
    assert data1.risk_score == 0

    data2 = AccountImpact(
        account_id=1,
        current_balance=Decimal("500.00"),
        projected_balance=Decimal("400.00"),
        risk_score=100,
    )
    assert data2.risk_score == 100


def test_total_bills_non_negative():
    """Test total_bills must be non-negative"""
    now = datetime.now(timezone.utc)

    # Test negative value
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        CashflowImpact(
            date=now, total_bills=Decimal("-0.01"), available_funds=Decimal("300.00")
        )

    # Test zero (valid)
    data = CashflowImpact(
        date=now, total_bills=Decimal("0.00"), available_funds=Decimal("300.00")
    )
    assert data.total_bills == Decimal("0.00")


def test_string_length_validation():
    """Test string length validation"""
    # Test name too long (max 100)
    with pytest.raises(
        ValidationError, match="String should have at most 100 characters"
    ):
        RiskFactor(name="X" * 101, severity=75, description="Valid description")

    # Test description too long (max 500)
    with pytest.raises(
        ValidationError, match="String should have at most 500 characters"
    ):
        RiskFactor(name="Valid name", severity=75, description="X" * 501)

    # Test valid boundary values
    data = RiskFactor(name="X" * 100, severity=75, description="X" * 500)
    assert len(data.name) == 100
    assert len(data.description) == 500


def test_positive_amount_validation():
    """Test positive amount validation"""
    account_impacts = [
        AccountImpact(
            account_id=1,
            current_balance=Decimal("500.00"),
            projected_balance=Decimal("400.00"),
            risk_score=25,
        )
    ]

    now = datetime.now(timezone.utc)
    cashflow_impacts = [
        CashflowImpact(
            date=now, total_bills=Decimal("250.00"), available_funds=Decimal("300.00")
        )
    ]

    risk_factors = [RiskFactor(name="Risk", severity=75, description="Description")]

    # Test zero amount
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        SplitImpactAnalysis(
            total_amount=Decimal("0.00"),
            account_impacts=account_impacts,
            cashflow_impacts=cashflow_impacts,
            risk_factors=risk_factors,
            overall_risk_score=65,
            recommendations=["Recommendation"],
        )

    # Test negative amount
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        SplitImpactAnalysis(
            total_amount=Decimal("-1.00"),
            account_impacts=account_impacts,
            cashflow_impacts=cashflow_impacts,
            risk_factors=risk_factors,
            overall_risk_score=65,
            recommendations=["Recommendation"],
        )


def test_analysis_period_range():
    """Test analysis period range validation"""
    splits = [{"account_id": 1, "amount": Decimal("100.00")}]

    # Test below minimum (14 days)
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 14"
    ):
        SplitImpactRequest(liability_id=5, splits=splits, analysis_period_days=13)

    # Test above maximum (365 days)
    with pytest.raises(
        ValidationError, match="Input should be less than or equal to 365"
    ):
        SplitImpactRequest(liability_id=5, splits=splits, analysis_period_days=366)

    # Test valid boundary values
    data1 = SplitImpactRequest(liability_id=5, splits=splits, analysis_period_days=14)
    assert data1.analysis_period_days == 14

    data2 = SplitImpactRequest(liability_id=5, splits=splits, analysis_period_days=365)
    assert data2.analysis_period_days == 365


# Test datetime UTC validation
def test_datetime_utc_validation():
    """Test datetime UTC validation per ADR-011"""
    splits = [{"account_id": 1, "amount": Decimal("100.00")}]

    # Test naive datetime
    with pytest.raises(
        ValidationError, match="Please provide datetime with UTC timezone"
    ):
        SplitImpactRequest(
            liability_id=5, splits=splits, start_date=datetime.now()  # Naive datetime
        )

    # Test non-UTC timezone
    with pytest.raises(
        ValidationError, match="Please provide datetime with UTC timezone"
    ):
        SplitImpactRequest(
            liability_id=5,
            splits=splits,
            start_date=datetime.now(ZoneInfo("America/New_York")),  # Non-UTC timezone
        )

    # Test valid UTC datetime
    data = SplitImpactRequest(
        liability_id=5, splits=splits, start_date=datetime.now(timezone.utc)
    )
    assert data.start_date.tzinfo == timezone.utc


def test_required_fields():
    """Test required fields validation"""
    # Test missing account_id
    with pytest.raises(ValidationError, match="Field required"):
        AccountImpact(
            current_balance=Decimal("500.00"),
            projected_balance=Decimal("400.00"),
            risk_score=25,
        )

    # Test missing current_balance
    with pytest.raises(ValidationError, match="Field required"):
        AccountImpact(account_id=1, projected_balance=Decimal("400.00"), risk_score=25)

    # Test missing projected_balance
    with pytest.raises(ValidationError, match="Field required"):
        AccountImpact(account_id=1, current_balance=Decimal("500.00"), risk_score=25)

    # Test missing risk_score
    with pytest.raises(ValidationError, match="Field required"):
        AccountImpact(
            account_id=1,
            current_balance=Decimal("500.00"),
            projected_balance=Decimal("400.00"),
        )
