import pytest
from decimal import Decimal
from datetime import date, timedelta
from sqlalchemy import select, exc
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.income import Income
from src.models.accounts import Account
from src.services.income import (
    calculate_undeposited_amount,
    update_account_balance_from_income,
    get_income_by_account,
    get_total_undeposited_income
)

@pytest.fixture
async def sample_accounts(db_session: AsyncSession):
    accounts = [
        Account(
            name="Test Checking",
            type="checking",
            available_balance=Decimal("1000.00"),
            created_at=date.today(),
            updated_at=date.today()
        ),
        Account(
            name="Second Checking",
            type="checking",
            available_balance=Decimal("500.00"),
            created_at=date.today(),
            updated_at=date.today()
        )
    ]
    
    db_session.add_all(accounts)
    await db_session.commit()
    return accounts

@pytest.fixture
async def sample_incomes(db_session: AsyncSession, sample_accounts):
    incomes = [
        Income(
            date=date.today(),
            source="Test Paycheck",
            amount=Decimal("2000.00"),
            deposited=False,
            account_id=sample_accounts[0].id,
            created_at=date.today(),
            updated_at=date.today()
        ),
        Income(
            date=date.today() + timedelta(days=1),
            source="Second Paycheck",
            amount=Decimal("1500.00"),
            deposited=False,
            account_id=sample_accounts[0].id,
            created_at=date.today(),
            updated_at=date.today()
        ),
        Income(
            date=date.today(),
            source="Other Income",
            amount=Decimal("1000.00"),
            deposited=False,
            account_id=sample_accounts[1].id,
            created_at=date.today(),
            updated_at=date.today()
        )
    ]
    
    db_session.add_all(incomes)
    await db_session.commit()
    return incomes

@pytest.mark.asyncio
async def test_create_income(db_session: AsyncSession, sample_accounts):
    income = Income(
        date=date.today(),
        source="Test Income",
        amount=Decimal("1500.00"),
        deposited=False,
        account_id=sample_accounts[0].id,
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
    assert db_income.account_id == sample_accounts[0].id
    
    # Verify relationship with account
    assert db_income.account.name == "Test Checking"

@pytest.mark.asyncio
async def test_calculate_undeposited_amount(db_session: AsyncSession, sample_incomes):
    # Test undeposited amount calculation
    undeposited = await calculate_undeposited_amount(db_session, sample_incomes[0].id)
    assert undeposited == sample_incomes[0].amount
    
    # Mark as deposited and test again
    sample_incomes[0].deposited = True
    await db_session.commit()
    
    undeposited = await calculate_undeposited_amount(db_session, sample_incomes[0].id)
    assert undeposited == Decimal("0.00")
    
    # Test total undeposited income for an account
    total_undeposited = await get_total_undeposited_income(db_session, sample_incomes[0].account_id)
    assert total_undeposited == sample_incomes[1].amount  # Only the second income is still undeposited

@pytest.mark.asyncio
async def test_update_account_balance_from_income(db_session: AsyncSession, sample_incomes, sample_accounts):
    initial_balance = sample_accounts[0].available_balance
    
    # Update account balance from income
    await update_account_balance_from_income(db_session, sample_incomes[0].id)
    
    # Verify account balance was updated
    result = await db_session.execute(
        select(Account).where(Account.id == sample_accounts[0].id)
    )
    updated_account = result.scalar_one()
    assert updated_account.available_balance == initial_balance + sample_incomes[0].amount
    
    # Verify income was marked as deposited
    result = await db_session.execute(
        select(Income).where(Income.id == sample_incomes[0].id)
    )
    updated_income = result.scalar_one()
    assert updated_income.deposited is True
    
    # Test updating multiple incomes
    await update_account_balance_from_income(db_session, sample_incomes[1].id)
    result = await db_session.execute(
        select(Account).where(Account.id == sample_accounts[0].id)
    )
    final_account = result.scalar_one()
    assert final_account.available_balance == initial_balance + sample_incomes[0].amount + sample_incomes[1].amount

@pytest.mark.asyncio
async def test_multiple_income_deposits(db_session: AsyncSession, sample_accounts):
    # Create multiple income entries
    incomes = [
        Income(
            date=date.today(),
            source=f"Test Income {i}",
            amount=Decimal("1000.00"),
            deposited=False,
            account_id=sample_accounts[0].id,
            created_at=date.today(),
            updated_at=date.today()
        )
        for i in range(3)
    ]
    
    db_session.add_all(incomes)
    await db_session.commit()
    
    initial_balance = sample_accounts[0].available_balance
    expected_total = initial_balance + sum(income.amount for income in incomes)
    
    # Deposit all income
    for income in incomes:
        await update_account_balance_from_income(db_session, income.id)
    
    # Verify final balance
    result = await db_session.execute(
        select(Account).where(Account.id == sample_accounts[0].id)
    )
    final_account = result.scalar_one()
    assert final_account.available_balance == expected_total

@pytest.mark.asyncio
async def test_deposit_already_deposited_income(db_session: AsyncSession, sample_incomes, sample_accounts):
    # First deposit
    await update_account_balance_from_income(db_session, sample_incomes[0].id)
    initial_balance = sample_accounts[0].available_balance
    
    # Try to deposit again
    await update_account_balance_from_income(db_session, sample_incomes[0].id)
    
    # Verify balance hasn't changed
    result = await db_session.execute(
        select(Account).where(Account.id == sample_accounts[0].id)
    )
    final_account = result.scalar_one()
    assert final_account.available_balance == initial_balance

@pytest.mark.asyncio
async def test_get_income_by_account(db_session: AsyncSession, sample_incomes, sample_accounts):
    # Get income for first account
    income_list = await get_income_by_account(db_session, sample_accounts[0].id)
    assert len(income_list) == 2
    assert all(income.account_id == sample_accounts[0].id for income in income_list)
    
    # Get income for second account
    income_list = await get_income_by_account(db_session, sample_accounts[1].id)
    assert len(income_list) == 1
    assert income_list[0].source == "Other Income"

@pytest.mark.asyncio
async def test_income_constraints(db_session: AsyncSession):
    # Test creating income with non-existent account
    invalid_income = Income(
        date=date.today(),
        source="Invalid Income",
        amount=Decimal("1000.00"),
        deposited=False,
        account_id=999,  # Non-existent account
        created_at=date.today(),
        updated_at=date.today()
    )
    
    db_session.add(invalid_income)
    with pytest.raises(exc.IntegrityError):
        await db_session.commit()
    await db_session.rollback()

@pytest.mark.asyncio
async def test_negative_amount_validation(db_session: AsyncSession, sample_accounts):
    # Test creating income with negative amount
    negative_income = Income(
        date=date.today(),
        source="Negative Income",
        amount=Decimal("-1000.00"),
        deposited=False,
        account_id=sample_accounts[0].id,
        created_at=date.today(),
        updated_at=date.today()
    )
    
    db_session.add(negative_income)
    with pytest.raises(exc.IntegrityError):
        await db_session.commit()
    await db_session.rollback()
