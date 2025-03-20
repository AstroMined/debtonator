from datetime import date, timedelta
from decimal import Decimal

import pytest

from src.models.accounts import Account
from src.models.categories import Category
from src.models.liabilities import Liability
from src.schemas.impact_analysis import SplitImpactRequest
from src.services.impact_analysis import ImpactAnalysisService


@pytest.fixture
async def impact_analysis_service(db_session):
    return ImpactAnalysisService(db_session)


@pytest.fixture
async def test_category(db_session):
    category = Category(
        name="Test Category",
        description="Test category for impact analysis",
        created_at=date.today(),
        updated_at=date.today(),
    )
    db_session.add(category)
    await db_session.commit()
    return category


@pytest.fixture
async def test_accounts(db_session):
    # Create test accounts
    checking = Account(
        name="Test Checking",
        type="checking",
        available_balance=Decimal("2000.00"),
        created_at=date.today(),
        updated_at=date.today(),
    )
    credit = Account(
        name="Test Credit",
        type="credit",
        available_balance=Decimal("-500.00"),
        total_limit=Decimal("5000.00"),
        available_credit=Decimal("4500.00"),
        created_at=date.today(),
        updated_at=date.today(),
    )
    db_session.add_all([checking, credit])
    await db_session.commit()

    return [checking, credit]


@pytest.fixture
async def test_liability(db_session, test_category, test_accounts):
    liability = Liability(
        name="Test Bill",
        amount=Decimal("1000.00"),
        due_date=date.today() + timedelta(days=15),
        description="Test liability",
        recurring=False,
        category_id=test_category.id,
        primary_account_id=test_accounts[0].id,
        auto_pay=False,
        auto_pay_enabled=False,
        paid=False,
        created_at=date.today(),
        updated_at=date.today(),
    )
    db_session.add(liability)
    await db_session.commit()
    return liability


async def test_analyze_split_impact(
    impact_analysis_service, test_accounts, test_liability
):
    """Test the analyze_split_impact method with a basic split scenario."""
    # Create a split request
    request = SplitImpactRequest(
        liability_id=test_liability.id,
        splits=[
            {"account_id": test_accounts[0].id, "amount": 600},  # Checking
            {"account_id": test_accounts[1].id, "amount": 400},  # Credit
        ],
        analysis_period_days=30,
    )

    # Analyze the impact
    result = await impact_analysis_service.analyze_split_impact(request)

    # Verify the result structure
    assert result.total_amount == Decimal("1000.00")
    assert len(result.account_impacts) == 2
    assert len(result.cashflow_impacts) > 0

    # Verify account impacts
    checking_impact = next(
        impact
        for impact in result.account_impacts
        if impact.account_id == test_accounts[0].id
    )
    credit_impact = next(
        impact
        for impact in result.account_impacts
        if impact.account_id == test_accounts[1].id
    )

    # Check projected balances
    assert checking_impact.projected_balance == Decimal("1400.00")  # 2000 - 600
    assert credit_impact.projected_balance == Decimal("-900.00")  # -500 - 400

    # Verify credit utilization for credit account
    assert credit_impact.current_credit_utilization == Decimal(
        "10.00"
    )  # (500/5000) * 100
    assert credit_impact.projected_credit_utilization == Decimal(
        "18.00"
    )  # (900/5000) * 100

    # Verify risk scores are calculated
    assert 0 <= checking_impact.risk_score <= 100
    assert 0 <= credit_impact.risk_score <= 100

    # Verify overall risk score
    assert 0 <= result.overall_risk_score <= 100

    # Verify recommendations are generated
    assert isinstance(result.recommendations, list)


async def test_high_risk_scenario(
    impact_analysis_service, test_accounts, test_liability
):
    """Test the analysis with a high-risk split scenario."""
    # Create a split request that would drain the checking account
    request = SplitImpactRequest(
        liability_id=test_liability.id,
        splits=[
            {"account_id": test_accounts[0].id, "amount": 1900},  # Checking (dangerous)
            {"account_id": test_accounts[1].id, "amount": 100},  # Credit
        ],
        analysis_period_days=30,
    )

    # Analyze the impact
    result = await impact_analysis_service.analyze_split_impact(request)

    # Verify high risk is detected
    checking_impact = next(
        impact
        for impact in result.account_impacts
        if impact.account_id == test_accounts[0].id
    )

    # Should have high risk score due to low projected balance
    assert checking_impact.risk_score > 70

    # Should have relevant risk factors
    low_balance_risk = next(
        (
            factor
            for factor in result.risk_factors
            if factor.name == "Low Account Balance"
        ),
        None,
    )
    assert low_balance_risk is not None
    assert low_balance_risk.severity > 70

    # Should have specific recommendations
    assert any("reducing the split amount" in rec for rec in result.recommendations)


async def test_cashflow_impact_calculation(
    impact_analysis_service, test_accounts, test_liability, db_session, test_category
):
    """Test cashflow impact calculations with multiple upcoming bills."""
    # Create additional future liabilities
    future_bills = [
        Liability(
            name=f"Future Bill {i}",
            amount=Decimal("500.00"),
            due_date=date.today() + timedelta(days=15 + i * 10),
            description="Future test liability",
            recurring=False,
            category_id=test_category.id,
            primary_account_id=test_accounts[0].id,
            auto_pay=False,
            auto_pay_enabled=False,
            paid=False,
            created_at=date.today(),
            updated_at=date.today(),
        )
        for i in range(3)
    ]
    db_session.add_all(future_bills)
    await db_session.commit()

    # Create a split request
    request = SplitImpactRequest(
        liability_id=test_liability.id,
        splits=[
            {"account_id": test_accounts[0].id, "amount": 800},
            {"account_id": test_accounts[1].id, "amount": 200},
        ],
        analysis_period_days=60,
    )

    # Analyze the impact
    result = await impact_analysis_service.analyze_split_impact(request)

    # Verify cashflow impacts are calculated correctly
    assert len(result.cashflow_impacts) > 0

    # Should detect future cashflow issues
    assert any(impact.projected_deficit for impact in result.cashflow_impacts)

    # Should have cashflow-related recommendations
    assert any("deficit" in rec.lower() for rec in result.recommendations)


async def test_credit_utilization_risk(
    impact_analysis_service, test_accounts, test_liability
):
    """Test detection of high credit utilization risk."""
    # Create a split that would result in high credit utilization
    request = SplitImpactRequest(
        liability_id=test_liability.id,
        splits=[
            {"account_id": test_accounts[0].id, "amount": 100},
            {
                "account_id": test_accounts[1].id,
                "amount": 4000,
            },  # Would use 90% of credit
        ],
        analysis_period_days=30,
    )

    # Analyze the impact
    result = await impact_analysis_service.analyze_split_impact(request)

    # Verify high credit utilization is detected
    credit_impact = next(
        impact
        for impact in result.account_impacts
        if impact.account_id == test_accounts[1].id
    )

    assert credit_impact.projected_credit_utilization > 80

    # Should have credit utilization risk factor
    high_utilization_risk = next(
        (
            factor
            for factor in result.risk_factors
            if factor.name == "High Credit Utilization"
        ),
        None,
    )
    assert high_utilization_risk is not None
    assert high_utilization_risk.severity > 70

    # Should have credit-specific recommendations
    assert any("credit utilization" in rec.lower() for rec in result.recommendations)
