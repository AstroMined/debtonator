import pytest
from decimal import Decimal
from datetime import date, timedelta
from sqlalchemy import select

from src.models.accounts import Account
from src.models.liabilities import Liability
from src.models.income import Income
from src.services.cashflow import (
    calculate_forecast,
    calculate_required_funds,
    calculate_daily_deficit,
    calculate_yearly_deficit,
    calculate_required_income
)

@pytest.fixture
async def sample_account(db_session):
    account = Account(
        name="Test Checking",
        type="checking",
        available_balance=Decimal("1000.00"),
        created_at=date.today(),
        updated_at=date.today()
    )
    db_session.add(account)
    await db_session.commit()
    return account

@pytest.fixture
async def sample_liabilities(db_session, sample_account):
    today = date.today()
    liabilities = [
        Liability(
            name=f"Test Bill {i}",
            amount=Decimal("100.00"),
            due_date=today + timedelta(days=i*15),
            description=f"Test liability {i}",
            category="utilities",
            recurring=True,
            primary_account_id=sample_account.id,
            auto_pay=False,
            paid=False,
            created_at=today,
            updated_at=today
        )
        for i in range(6)  # Create 6 liabilities spread over 90 days
    ]
    db_session.add_all(liabilities)
    await db_session.commit()
    return liabilities

@pytest.fixture
async def sample_income(db_session, sample_account):
    today = date.today()
    income_entries = [
        Income(
            date=today + timedelta(days=i*30),
            source=f"Test Income {i}",
            amount=Decimal("1000.00"),
            deposited=False,
            account_id=sample_account.id,
            created_at=today,
            updated_at=today
        )
        for i in range(3)  # Create 3 income entries over 90 days
    ]
    db_session.add_all(income_entries)
    await db_session.commit()
    return income_entries

@pytest.mark.asyncio
async def test_calculate_forecast(db_session, sample_account, sample_liabilities, sample_income):
    today = date.today()
    forecast = await calculate_forecast(
        db_session,
        sample_account.id,
        today,
        today + timedelta(days=90)
    )
    
    assert len(forecast) > 0
    assert all(isinstance(f["balance"], Decimal) for f in forecast)
    assert all(isinstance(f["date"], date) for f in forecast)
    
    # Verify forecast includes all liabilities and income
    total_liabilities = sum(liability.amount for liability in sample_liabilities)
    total_income = sum(income.amount for income in sample_income)
    
    # Last forecast entry should reflect all transactions
    final_balance = forecast[-1]["balance"]
    expected_balance = sample_account.available_balance + total_income - total_liabilities
    assert final_balance == expected_balance

@pytest.mark.asyncio
async def test_calculate_required_funds(db_session, sample_account, sample_liabilities):
    today = date.today()
    
    # Test 14-day outlook
    required_14 = await calculate_required_funds(
        db_session,
        sample_account.id,
        today,
        today + timedelta(days=14)
    )
    
    # Should include only liabilities due within 14 days
    expected_14 = sum(
        liability.amount for liability in sample_liabilities
        if liability.due_date <= today + timedelta(days=14)
    )
    assert required_14 == expected_14
    
    # Test 30-day outlook
    required_30 = await calculate_required_funds(
        db_session,
        sample_account.id,
        today,
        today + timedelta(days=30)
    )
    
    # Should include more liabilities than 14-day outlook
    assert required_30 >= required_14

@pytest.mark.asyncio
async def test_calculate_daily_deficit(db_session, sample_account):
    min_amount = Decimal("-500.00")
    days = 30
    
    deficit = calculate_daily_deficit(min_amount, days)
    assert deficit == Decimal("16.67")  # 500/30 rounded to 2 decimal places
    
    # Test with positive amount (should return 0)
    min_amount = Decimal("500.00")
    deficit = calculate_daily_deficit(min_amount, days)
    assert deficit == Decimal("0.00")

@pytest.mark.asyncio
async def test_calculate_yearly_deficit(db_session):
    daily_deficit = Decimal("16.67")
    yearly = calculate_yearly_deficit(daily_deficit)
    assert yearly == daily_deficit * 365

@pytest.mark.asyncio
async def test_calculate_required_income(db_session):
    yearly_deficit = Decimal("6084.55")  # 16.67 * 365
    
    # Test with different tax rates
    income_80_tax = calculate_required_income(yearly_deficit, tax_rate=Decimal("0.80"))
    assert income_80_tax == yearly_deficit / Decimal("0.80")
    
    income_70_tax = calculate_required_income(yearly_deficit, tax_rate=Decimal("0.70"))
    assert income_70_tax == yearly_deficit / Decimal("0.70")
    
    # Verify higher tax rate requires more gross income
    assert income_70_tax > income_80_tax

@pytest.mark.asyncio
async def test_forecast_with_no_transactions(db_session, sample_account):
    today = date.today()
    forecast = await calculate_forecast(
        db_session,
        sample_account.id,
        today,
        today + timedelta(days=90)
    )
    
    # Should still return forecast entries but with unchanged balance
    assert len(forecast) > 0
    assert all(f["balance"] == sample_account.available_balance for f in forecast)
