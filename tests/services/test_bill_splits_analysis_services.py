from decimal import Decimal
from datetime import date, timedelta
import pytest
from sqlalchemy import select
from src.models.accounts import Account
from src.models.liabilities import Liability
from src.models.bill_splits import BillSplit
from src.schemas.bill_splits import BillSplitCreate, OptimizationSuggestion
from src.services.bill_splits import BillSplitService

@pytest.mark.asyncio
async def test_calculate_optimization_metrics(db_session):
    # Create test accounts
    checking = Account(
        name="Test Checking",
        type="checking",
        available_balance=Decimal("1000.00"),
        created_at=date.today(),
        updated_at=date.today()
    )
    credit = Account(
        name="Test Credit",
        type="credit",
        available_balance=Decimal("-500.00"),
        total_limit=Decimal("2000.00"),
        created_at=date.today(),
        updated_at=date.today()
    )
    db_session.add_all([checking, credit])
    await db_session.commit()

    # Create test splits
    splits = [
        BillSplitCreate(
            liability_id=1,
            account_id=checking.id,
            amount=Decimal("300.00")
        ),
        BillSplitCreate(
            liability_id=1,
            account_id=credit.id,
            amount=Decimal("700.00")
        )
    ]

    service = BillSplitService(db_session)
    accounts = {checking.id: checking, credit.id: credit}
    metrics = await service.calculate_optimization_metrics(splits, accounts)

    assert metrics.credit_utilization[credit.id] == pytest.approx(60.0)  # (500 + 700) / 2000 * 100
    assert metrics.balance_impact[checking.id] == Decimal("-300.00")
    assert metrics.balance_impact[credit.id] == Decimal("-700.00")
    assert 0 <= metrics.risk_score <= 1
    assert 0 <= metrics.optimization_score <= 1

@pytest.mark.asyncio
async def test_analyze_split_impact(db_session):
    # Create test accounts
    checking = Account(
        name="Test Checking",
        type="checking",
        available_balance=Decimal("1000.00"),
        created_at=date.today(),
        updated_at=date.today()
    )
    credit = Account(
        name="Test Credit",
        type="credit",
        available_balance=Decimal("-500.00"),
        total_limit=Decimal("2000.00"),
        created_at=date.today(),
        updated_at=date.today()
    )
    db_session.add_all([checking, credit])
    await db_session.commit()

    # Create test liability
    liability = Liability(
        name="Test Bill",
        amount=Decimal("1000.00"),
        due_date=date.today() + timedelta(days=15),
        category_id=1,
        primary_account_id=checking.id,
        auto_pay=False,
        auto_pay_enabled=False,
        status="pending",
        paid=False,
        recurring=False,
        created_at=date.today(),
        updated_at=date.today()
    )
    db_session.add(liability)
    await db_session.commit()

    # Create test splits
    splits = [
        BillSplitCreate(
            liability_id=liability.id,
            account_id=checking.id,
            amount=Decimal("300.00")
        ),
        BillSplitCreate(
            liability_id=liability.id,
            account_id=credit.id,
            amount=Decimal("700.00")
        )
    ]

    service = BillSplitService(db_session)
    impact = await service.analyze_split_impact(splits)

    assert impact.split_configuration == splits
    assert impact.metrics.credit_utilization[credit.id] == pytest.approx(60.0)
    assert impact.short_term_impact[checking.id] == Decimal("-300.00")
    assert impact.short_term_impact[credit.id] == Decimal("-700.00")
    assert impact.long_term_impact[checking.id] == Decimal("-300.00")
    assert impact.long_term_impact[credit.id] == Decimal("-700.00")
    assert isinstance(impact.risk_factors, list)
    assert isinstance(impact.recommendations, list)

@pytest.mark.asyncio
async def test_generate_optimization_suggestions(db_session):
    # Create test accounts
    checking = Account(
        name="Test Checking",
        type="checking",
        available_balance=Decimal("1000.00"),
        created_at=date.today(),
        updated_at=date.today()
    )
    credit1 = Account(
        name="Credit Card 1",
        type="credit",
        available_balance=Decimal("-1500.00"),
        total_limit=Decimal("2000.00"),
        created_at=date.today(),
        updated_at=date.today()
    )
    credit2 = Account(
        name="Credit Card 2",
        type="credit",
        available_balance=Decimal("-200.00"),
        total_limit=Decimal("2000.00"),
        created_at=date.today(),
        updated_at=date.today()
    )
    db_session.add_all([checking, credit1, credit2])
    await db_session.commit()

    # Create test liability
    liability = Liability(
        name="Test Bill",
        amount=Decimal("1200.00"),
        due_date=date.today() + timedelta(days=15),
        category_id=1,
        primary_account_id=credit1.id,
        auto_pay=False,
        auto_pay_enabled=False,
        status="pending",
        paid=False,
        recurring=False,
        created_at=date.today(),
        updated_at=date.today()
    )
    db_session.add(liability)
    await db_session.commit()

    # Create initial split
    split = BillSplit(
        liability_id=liability.id,
        account_id=credit1.id,
        amount=Decimal("1200.00"),
        created_at=date.today(),
        updated_at=date.today()
    )
    db_session.add(split)
    await db_session.commit()

    service = BillSplitService(db_session)
    suggestions = await service.generate_optimization_suggestions(liability.id)

    assert len(suggestions) > 0
    for suggestion in suggestions:
        assert isinstance(suggestion, OptimizationSuggestion)
        assert len(suggestion.original_splits) > 0
        assert len(suggestion.suggested_splits) > 0
        assert suggestion.priority >= 1 and suggestion.priority <= 5
        assert len(suggestion.reasoning) > 0

        # Verify total amount matches liability
        original_total = sum(split.amount for split in suggestion.original_splits)
        suggested_total = sum(split.amount for split in suggestion.suggested_splits)
        assert abs(original_total - liability.amount) < Decimal("0.01")
        assert abs(suggested_total - liability.amount) < Decimal("0.01")

        # Verify improvement
        assert suggestion.improvement_metrics.optimization_score > 0
