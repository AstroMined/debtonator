import pytest
from datetime import date, timedelta
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from src.models.accounts import Account
from src.models.liabilities import Liability
from src.models.income import Income
from src.schemas.cashflow import AccountForecastRequest
from src.services.cashflow import CashflowService

@pytest.fixture
async def test_account(db_session: AsyncSession):
    account = Account(
        name="Test Account",
        type="checking",
        available_balance=Decimal("1000.00")
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account

@pytest.fixture
async def test_credit_account(db_session: AsyncSession):
    account = Account(
        name="Test Credit",
        type="credit",
        available_balance=Decimal("-500.00"),
        total_limit=Decimal("2000.00")
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account

@pytest.fixture
async def test_category(db_session: AsyncSession):
    from src.models.categories import Category
    category = Category(
        name="Test Category",
        description="Test Description"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category

@pytest.fixture
async def test_bills(db_session: AsyncSession, test_account: Account, test_category):
    today = date.today()
    bills = [
        Liability(
            name="Rent",
            amount=Decimal("800.00"),
            due_date=today + timedelta(days=5),
            primary_account_id=test_account.id,
            category_id=test_category.id,
            status="pending"
        ),
        Liability(
            name="Utilities",
            amount=Decimal("100.00"),
            due_date=today + timedelta(days=10),
            primary_account_id=test_account.id,
            category_id=test_category.id,
            status="pending",
            recurring=True
        )
    ]
    for bill in bills:
        db_session.add(bill)
    await db_session.commit()
    return bills

@pytest.fixture
async def test_income(db_session: AsyncSession, test_account: Account):
    today = date.today()
    income_entries = [
        Income(
            source="Salary",
            amount=Decimal("2000.00"),
            date=today + timedelta(days=15),
            account_id=test_account.id,
            deposited=False
        ),
        Income(
            source="Freelance",
            amount=Decimal("500.00"),
            date=today + timedelta(days=20),
            account_id=test_account.id,
            deposited=False
        )
    ]
    for income in income_entries:
        db_session.add(income)
    await db_session.commit()
    return income_entries

async def test_get_account_forecast_basic(
    db_session: AsyncSession,
    test_account: Account,
    test_bills,
    test_income
):
    service = CashflowService(db_session)
    today = date.today()
    
    request = AccountForecastRequest(
        account_id=test_account.id,
        start_date=today,
        end_date=today + timedelta(days=30),
        include_pending=True,
        include_recurring=True,
        include_transfers=True
    )
    
    response = await service.get_account_forecast(request)
    
    assert response.account_id == test_account.id
    assert response.forecast_period == (today, today + timedelta(days=30))
    assert len(response.daily_forecasts) == 31  # 30 days + today
    assert response.overall_confidence >= Decimal("0.1")
    assert response.overall_confidence <= Decimal("1.0")
    
    # Verify metrics
    assert response.metrics.average_daily_balance is not None
    assert response.metrics.minimum_projected_balance is not None
    assert response.metrics.maximum_projected_balance is not None
    assert response.metrics.average_inflow is not None
    assert response.metrics.average_outflow is not None
    assert isinstance(response.metrics.projected_low_balance_dates, list)
    assert response.metrics.balance_volatility >= Decimal("0")

async def test_get_account_forecast_credit_account(
    db_session: AsyncSession,
    test_credit_account: Account
):
    service = CashflowService(db_session)
    today = date.today()
    
    request = AccountForecastRequest(
        account_id=test_credit_account.id,
        start_date=today,
        end_date=today + timedelta(days=30),
        include_pending=True,
        include_recurring=True,
        include_transfers=True
    )
    
    response = await service.get_account_forecast(request)
    
    assert response.account_id == test_credit_account.id
    assert response.metrics.credit_utilization is not None
    assert response.metrics.credit_utilization >= Decimal("0")
    assert response.metrics.credit_utilization <= Decimal("1")

async def test_get_account_forecast_warning_flags(
    db_session: AsyncSession,
    test_account: Account,
    test_bills
):
    service = CashflowService(db_session)
    today = date.today()
    
    # Set low balance to trigger warnings
    test_account.available_balance = Decimal("50.00")
    await db_session.commit()
    
    request = AccountForecastRequest(
        account_id=test_account.id,
        start_date=today,
        end_date=today + timedelta(days=30),
        include_pending=True,
        include_recurring=True,
        include_transfers=True
    )
    
    response = await service.get_account_forecast(request)
    
    # Should have low balance warnings
    low_balance_forecasts = [
        f for f in response.daily_forecasts
        if "low_balance" in f.warning_flags
    ]
    assert len(low_balance_forecasts) > 0
    
    # Confidence should be lower due to warnings
    assert response.overall_confidence < Decimal("0.9")

async def test_get_account_forecast_recurring_bills(
    db_session: AsyncSession,
    test_account: Account,
    test_bills
):
    service = CashflowService(db_session)
    today = date.today()
    
    request = AccountForecastRequest(
        account_id=test_account.id,
        start_date=today,
        end_date=today + timedelta(days=60),  # Longer period to catch recurring bills
        include_pending=True,
        include_recurring=True,
        include_transfers=True
    )
    
    response = await service.get_account_forecast(request)
    
    # Find forecasts with recurring bills
    recurring_transactions = []
    for forecast in response.daily_forecasts:
        for trans in forecast.contributing_transactions:
            if "Recurring Bill:" in trans["description"]:
                recurring_transactions.append(trans)
    
    # Should have at least one recurring transaction
    assert len(recurring_transactions) > 0

async def test_get_account_forecast_invalid_account(db_session: AsyncSession):
    service = CashflowService(db_session)
    today = date.today()
    
    request = AccountForecastRequest(
        account_id=999999,  # Non-existent account
        start_date=today,
        end_date=today + timedelta(days=30),
        include_pending=True,
        include_recurring=True,
        include_transfers=True
    )
    
    with pytest.raises(ValueError, match="Account with id .* not found"):
        await service.get_account_forecast(request)
