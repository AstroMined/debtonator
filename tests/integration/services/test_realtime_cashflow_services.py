from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import select

from src.models.accounts import Account
from src.models.liabilities import Liability
from src.services.realtime_cashflow import RealtimeCashflowService


@pytest.fixture(scope="function")
async def sample_accounts(db_session):
    """Create sample accounts for testing."""
    accounts = [
        Account(
            name="Checking",
            type="checking",
            available_balance=Decimal("1000.00"),
            created_at=datetime.now().date(),
            updated_at=datetime.now().date(),
        ),
        Account(
            name="Credit Card",
            type="credit",
            available_balance=Decimal("-500.00"),
            available_credit=Decimal("4500.00"),
            total_limit=Decimal("5000.00"),
            created_at=datetime.now().date(),
            updated_at=datetime.now().date(),
        ),
        Account(
            name="Savings",
            type="savings",
            available_balance=Decimal("2000.00"),
            created_at=datetime.now().date(),
            updated_at=datetime.now().date(),
        ),
    ]

    for account in accounts:
        db_session.add(account)
    await db_session.commit()

    return accounts


@pytest.fixture(scope="function")
async def sample_bills(db_session, sample_accounts):
    """Create sample bills for testing."""
    today = datetime.now().date()
    bills = [
        Liability(
            name="Rent",
            amount=Decimal("1200.00"),
            due_date=today + timedelta(days=7),
            description="Monthly rent",
            recurring=True,
            category_id=1,
            primary_account_id=sample_accounts[0].id,
            auto_pay=False,
            auto_pay_enabled=False,
            paid=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
        Liability(
            name="Utilities",
            amount=Decimal("150.00"),
            due_date=today + timedelta(days=14),
            description="Monthly utilities",
            recurring=True,
            category_id=1,
            primary_account_id=sample_accounts[0].id,
            auto_pay=False,
            auto_pay_enabled=False,
            paid=False,
            created_at=datetime.now(),
            updated_at=datetime.now(),
        ),
    ]

    for bill in bills:
        db_session.add(bill)
    await db_session.commit()

    return bills


async def test_get_account_balances(db_session, sample_accounts):
    """Test fetching account balances."""
    service = RealtimeCashflowService(db_session)
    balances = await service.get_account_balances()

    assert len(balances) == 3
    checking = next(b for b in balances if b.type == "checking")
    credit = next(b for b in balances if b.type == "credit")
    savings = next(b for b in balances if b.type == "savings")

    assert checking.current_balance == Decimal("1000.00")
    assert credit.available_credit == Decimal("4500.00")
    assert savings.current_balance == Decimal("2000.00")


async def test_get_upcoming_bill(db_session, sample_bills):
    """Test fetching the next upcoming bill."""
    service = RealtimeCashflowService(db_session)
    next_date, days_until = await service.get_upcoming_bill()

    assert next_date == sample_bills[0].due_date
    assert days_until == 7


async def test_calculate_minimum_balance(db_session, sample_bills):
    """Test calculating minimum balance required."""
    service = RealtimeCashflowService(db_session)
    min_balance = await service.calculate_minimum_balance()

    # Both bills are within 14 days
    assert min_balance == Decimal("1350.00")


async def test_get_realtime_cashflow(db_session, sample_accounts, sample_bills):
    """Test getting complete realtime cashflow data."""
    service = RealtimeCashflowService(db_session)
    cashflow = await service.get_realtime_cashflow()

    assert len(cashflow.account_balances) == 3
    assert cashflow.total_available_funds == Decimal("3000.00")  # Checking + Savings
    assert cashflow.total_available_credit == Decimal("4500.00")
    assert cashflow.total_liabilities_due == Decimal("1350.00")  # Both bills
    assert cashflow.net_position == Decimal("1650.00")  # 3000 - 1350
    assert cashflow.days_until_next_bill == 7
    assert cashflow.minimum_balance_required == Decimal("1350.00")
    assert cashflow.projected_deficit is None  # We have enough funds


async def test_get_realtime_cashflow_with_deficit(
    db_session, sample_accounts, sample_bills
):
    """Test realtime cashflow with insufficient funds."""
    # Modify account balances to create a deficit
    query = select(Account).where(Account.type != "credit")
    result = await db_session.execute(query)
    for account in result.scalars():
        account.available_balance = Decimal("100.00")
    await db_session.commit()

    service = RealtimeCashflowService(db_session)
    cashflow = await service.get_realtime_cashflow()

    assert cashflow.total_available_funds == Decimal(
        "200.00"
    )  # Two accounts with 100 each
    assert cashflow.minimum_balance_required == Decimal("1350.00")
    assert cashflow.projected_deficit == Decimal("1150.00")  # 1350 - 200
