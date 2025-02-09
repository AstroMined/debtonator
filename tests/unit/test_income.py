import pytest
from decimal import Decimal
from datetime import date
from sqlalchemy import select

from src.models.income import Income
from src.models.accounts import Account
from src.services.income import calculate_undeposited_amount, update_account_balance_from_income

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
async def sample_income(db_session, sample_account):
    income = Income(
        date=date.today(),
        source="Test Paycheck",
        amount=Decimal("2000.00"),
        deposited=False,
        account_id=sample_account.id,
        created_at=date.today(),
        updated_at=date.today()
    )
    
    db_session.add(income)
    await db_session.commit()
    return income

@pytest.mark.asyncio
async def test_create_income(db_session, sample_account):
    income = Income(
        date=date.today(),
        source="Test Income",
        amount=Decimal("1500.00"),
        deposited=False,
        account_id=sample_account.id,
        created_at=date.today(),
        updated_at=date.today()
    )
    
    db_session.add(income)
    await db_session.commit()
    
    # Fetch and verify the income
    result = await db_session.execute(
        select(Income).where(Income.source == "Test Income")
    )
    db_income = result.scalar_one()
    
    assert db_income.amount == Decimal("1500.00")
    assert db_income.deposited is False
    assert db_income.account_id == sample_account.id

@pytest.mark.asyncio
async def test_calculate_undeposited_amount(db_session, sample_income):
    # Test undeposited amount calculation
    undeposited = await calculate_undeposited_amount(db_session, sample_income.id)
    assert undeposited == sample_income.amount
    
    # Mark as deposited and test again
    sample_income.deposited = True
    await db_session.commit()
    
    undeposited = await calculate_undeposited_amount(db_session, sample_income.id)
    assert undeposited == Decimal("0.00")

@pytest.mark.asyncio
async def test_update_account_balance_from_income(db_session, sample_income, sample_account):
    initial_balance = sample_account.available_balance
    
    # Update account balance from income
    await update_account_balance_from_income(db_session, sample_income.id)
    
    # Verify account balance was updated
    result = await db_session.execute(
        select(Account).where(Account.id == sample_account.id)
    )
    updated_account = result.scalar_one()
    assert updated_account.available_balance == initial_balance + sample_income.amount
    
    # Verify income was marked as deposited
    result = await db_session.execute(
        select(Income).where(Income.id == sample_income.id)
    )
    updated_income = result.scalar_one()
    assert updated_income.deposited is True

@pytest.mark.asyncio
async def test_multiple_income_deposits(db_session, sample_account):
    # Create multiple income entries
    incomes = [
        Income(
            date=date.today(),
            source=f"Test Income {i}",
            amount=Decimal("1000.00"),
            deposited=False,
            account_id=sample_account.id,
            created_at=date.today(),
            updated_at=date.today()
        )
        for i in range(3)
    ]
    
    db_session.add_all(incomes)
    await db_session.commit()
    
    initial_balance = sample_account.available_balance
    expected_total = initial_balance + sum(income.amount for income in incomes)
    
    # Deposit all income
    for income in incomes:
        await update_account_balance_from_income(db_session, income.id)
    
    # Verify final balance
    result = await db_session.execute(
        select(Account).where(Account.id == sample_account.id)
    )
    final_account = result.scalar_one()
    assert final_account.available_balance == expected_total

@pytest.mark.asyncio
async def test_deposit_already_deposited_income(db_session, sample_income, sample_account):
    # First deposit
    await update_account_balance_from_income(db_session, sample_income.id)
    initial_balance = sample_account.available_balance
    
    # Try to deposit again
    await update_account_balance_from_income(db_session, sample_income.id)
    
    # Verify balance hasn't changed
    result = await db_session.execute(
        select(Account).where(Account.id == sample_account.id)
    )
    final_account = result.scalar_one()
    assert final_account.available_balance == initial_balance
