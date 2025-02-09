import pytest
from decimal import Decimal
from datetime import date
from sqlalchemy import select

from src.models.accounts import Account
from src.schemas.accounts import AccountCreate

@pytest.fixture
async def sample_account_data():
    return {
        "name": "Test Checking",
        "type": "checking",
        "available_balance": Decimal("1000.00"),
        "created_at": date.today(),
        "updated_at": date.today()
    }

@pytest.fixture
async def sample_credit_account_data():
    return {
        "name": "Test Credit Card",
        "type": "credit",
        "available_balance": Decimal("-500.00"),
        "total_limit": Decimal("2000.00"),
        "available_credit": Decimal("1500.00"),
        "last_statement_balance": Decimal("500.00"),
        "last_statement_date": date.today(),
        "created_at": date.today(),
        "updated_at": date.today()
    }

@pytest.mark.asyncio
async def test_create_checking_account(db_session, sample_account_data):
    # Create account
    account = Account(**sample_account_data)
    db_session.add(account)
    await db_session.commit()
    
    # Fetch the account
    result = await db_session.execute(select(Account).where(Account.name == "Test Checking"))
    db_account = result.scalar_one()
    
    assert db_account.name == sample_account_data["name"]
    assert db_account.type == sample_account_data["type"]
    assert db_account.available_balance == sample_account_data["available_balance"]
    assert db_account.available_credit is None
    assert db_account.total_limit is None

@pytest.mark.asyncio
async def test_create_credit_account(db_session, sample_credit_account_data):
    # Create account
    account = Account(**sample_credit_account_data)
    db_session.add(account)
    await db_session.commit()
    
    # Fetch the account
    result = await db_session.execute(select(Account).where(Account.name == "Test Credit Card"))
    db_account = result.scalar_one()
    
    assert db_account.name == sample_credit_account_data["name"]
    assert db_account.type == sample_credit_account_data["type"]
    assert db_account.available_balance == sample_credit_account_data["available_balance"]
    assert db_account.total_limit == sample_credit_account_data["total_limit"]
    assert db_account.available_credit == sample_credit_account_data["available_credit"]
    assert db_account.last_statement_balance == sample_credit_account_data["last_statement_balance"]

@pytest.mark.asyncio
async def test_calculate_available_credit(db_session, sample_credit_account_data):
    account = Account(**sample_credit_account_data)
    
    # Verify initial available credit
    assert account.available_credit == Decimal("1500.00")
    
    # Test credit calculation after balance change
    account.available_balance = Decimal("-1000.00")
    expected_available_credit = account.total_limit - abs(account.available_balance)
    assert account.available_credit == expected_available_credit
    assert account.available_credit == Decimal("1000.00")

@pytest.mark.asyncio
async def test_checking_account_balance_update(db_session, sample_account_data):
    account = Account(**sample_account_data)
    db_session.add(account)
    await db_session.commit()
    
    # Test deposit
    initial_balance = account.available_balance
    deposit_amount = Decimal("500.00")
    account.available_balance += deposit_amount
    await db_session.commit()
    
    result = await db_session.execute(select(Account).where(Account.id == account.id))
    updated_account = result.scalar_one()
    assert updated_account.available_balance == initial_balance + deposit_amount
    
    # Test withdrawal
    withdrawal_amount = Decimal("200.00")
    updated_account.available_balance -= withdrawal_amount
    await db_session.commit()
    
    result = await db_session.execute(select(Account).where(Account.id == account.id))
    final_account = result.scalar_one()
    assert final_account.available_balance == initial_balance + deposit_amount - withdrawal_amount

@pytest.mark.asyncio
async def test_credit_limit_validation(db_session, sample_credit_account_data):
    account = Account(**sample_credit_account_data)
    db_session.add(account)
    await db_session.commit()
    
    # Verify credit limit enforcement
    assert abs(account.available_balance) <= account.total_limit
    
    # Test approaching credit limit
    account.available_balance = Decimal("-1990.00")  # Just under limit
    await db_session.commit()
    
    result = await db_session.execute(select(Account).where(Account.id == account.id))
    updated_account = result.scalar_one()
    assert updated_account.available_credit == Decimal("10.00")
    assert abs(updated_account.available_balance) <= updated_account.total_limit
