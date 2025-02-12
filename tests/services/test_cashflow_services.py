import pytest
from decimal import Decimal
from datetime import date, timedelta
from sqlalchemy import select
from src.services.cashflow import CashflowService
from src.models.accounts import Account
from src.models.liabilities import Liability
from src.models.payments import Payment
from src.models.income import Income

@pytest.fixture
async def test_account(db_session):
    account = Account(
        name="Test Checking",
        type="checking",
        available_balance=Decimal("1000.00")
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account

@pytest.fixture
async def test_liabilities(db_session, test_account):
    today = date.today()
    liabilities = [
            Liability(
                name="Rent",
                amount=Decimal("800.00"),
                due_date=today + timedelta(days=5),
                category="Housing",
                primary_account_id=test_account.id
            ),
            Liability(
                name="Utilities",
                amount=Decimal("100.00"),
                due_date=today + timedelta(days=10),
                category="Utilities",
                primary_account_id=test_account.id
            ),
            Liability(
                name="Internet",
                amount=Decimal("50.00"),
                due_date=today + timedelta(days=15),
                category="Utilities",
                primary_account_id=test_account.id
            )
    ]
    for liability in liabilities:
        db_session.add(liability)
    await db_session.commit()
    for liability in liabilities:
        await db_session.refresh(liability)
    return liabilities

@pytest.fixture
async def test_income(db_session, test_account):
    today = date.today()
    income_entries = [
        Income(
            date=today + timedelta(days=3),
            source="Salary",
            amount=Decimal("2000.00"),
            deposited=False,
            account_id=test_account.id
        ),
        Income(
            date=today + timedelta(days=17),
            source="Freelance",
            amount=Decimal("500.00"),
            deposited=False,
            account_id=test_account.id
        )
    ]
    for income in income_entries:
        db_session.add(income)
    await db_session.commit()
    for income in income_entries:
        await db_session.refresh(income)
    return income_entries

@pytest.mark.asyncio
async def test_get_forecast(db_session, test_account, test_liabilities, test_income):
    """Test getting cashflow forecast for a date range."""
    service = CashflowService(db_session)
    today = date.today()
    start_date = today
    end_date = today + timedelta(days=20)
    
    forecast = await service.get_forecast(
        test_account.id,
        start_date,
        end_date
    )
    
    assert len(forecast) == 21  # 21 days including start and end date
    assert forecast[0]["date"] == start_date
    assert forecast[0]["balance"] == Decimal("1000.00")  # Initial balance
    
    # Check balance after first income
    assert forecast[3]["balance"] == Decimal("3000.00")  # 1000 + 2000
    
    # Check balance after first liability
    assert forecast[5]["balance"] == Decimal("2200.00")  # 3000 - 800
    
    # Check balance after second liability
    assert forecast[10]["balance"] == Decimal("2100.00")  # 2200 - 100
    
    # Check balance after third liability and second income
    assert forecast[17]["balance"] == Decimal("2550.00")  # 2050 + 500

@pytest.mark.asyncio
async def test_get_required_funds(db_session, test_account, test_liabilities):
    """Test calculating required funds for a date range."""
    service = CashflowService(db_session)
    today = date.today()
    start_date = today
    end_date = today + timedelta(days=20)
    
    required_funds = await service.get_required_funds(
        test_account.id,
        start_date,
        end_date
    )
    
    # Sum of all liabilities in range
    assert required_funds == Decimal("950.00")  # 800 + 100 + 50

def test_get_daily_deficit():
    """Test calculating daily deficit."""
    service = CashflowService(None)  # No DB needed for this calculation
    
    # Test positive amount (should return 0)
    assert service.get_daily_deficit(Decimal("100.00"), 30) == Decimal("0.00")
    
    # Test negative amount
    assert service.get_daily_deficit(Decimal("-300.00"), 30) == Decimal("10.00")
    
    # Test zero amount
    assert service.get_daily_deficit(Decimal("0.00"), 30) == Decimal("0.00")
    
    # Test rounding
    assert service.get_daily_deficit(Decimal("-100.00"), 3) == Decimal("33.33")

def test_get_yearly_deficit():
    """Test calculating yearly deficit."""
    service = CashflowService(None)  # No DB needed for this calculation
    
    # Test with daily deficit
    assert service.get_yearly_deficit(Decimal("10.00")) == Decimal("3650.00")
    
    # Test with zero
    assert service.get_yearly_deficit(Decimal("0.00")) == Decimal("0.00")

def test_get_required_income():
    """Test calculating required income with tax consideration."""
    service = CashflowService(None)  # No DB needed for this calculation
    
    # Test with default tax rate (0.80)
    assert service.get_required_income(Decimal("1000.00")) == Decimal("1250.00")
    
    # Test with custom tax rate
    # Round to 2 decimal places for consistency
    result = service.get_required_income(
        Decimal("1000.00"),
        Decimal("0.70")
    ).quantize(Decimal("0.01"))
    assert result == Decimal("1428.57")
    
    # Test with zero deficit
    assert service.get_required_income(Decimal("0.00")) == Decimal("0.00")

@pytest.mark.asyncio
async def test_get_forecast_empty_range(db_session, test_account):
    """Test getting forecast with no liabilities or income in range."""
    service = CashflowService(db_session)
    today = date.today()
    start_date = today + timedelta(days=100)  # Future date with no entries
    end_date = start_date + timedelta(days=5)
    
    forecast = await service.get_forecast(
        test_account.id,
        start_date,
        end_date
    )
    
    assert len(forecast) == 6  # 6 days including start and end date
    for entry in forecast:
        assert entry["balance"] == test_account.available_balance

@pytest.mark.asyncio
async def test_get_required_funds_empty_range(db_session, test_account):
    """Test getting required funds with no liabilities in range."""
    service = CashflowService(db_session)
    today = date.today()
    start_date = today + timedelta(days=100)  # Future date with no entries
    end_date = start_date + timedelta(days=5)
    
    required_funds = await service.get_required_funds(
        test_account.id,
        start_date,
        end_date
    )
    
    assert required_funds == Decimal("0.00")
