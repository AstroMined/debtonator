"""
Integration tests for StatementHistoryRepository.

This module contains tests that validate the behavior of the StatementHistoryRepository
against a real database.
"""

import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.statement_history import StatementHistory
from src.models.accounts import Account
from src.repositories.statement_history import StatementHistoryRepository
from src.repositories.accounts import AccountRepository


@pytest.mark.asyncio
async def test_create_statement_history(db_session: AsyncSession):
    """Test creating a statement history record."""
    # Create account first
    account_repo = AccountRepository(db_session)
    
    account = await account_repo.create({
        "name": "Statement Test Account",
        "type": "credit",
        "available_balance": Decimal("-500.00"),
        "total_limit": Decimal("2000.00"),
        "available_credit": Decimal("1500.00")
    })
    
    # Create repository
    repo = StatementHistoryRepository(db_session)
    
    # Create statement history record
    statement_date = datetime.now().replace(day=1)  # First of current month
    due_date = statement_date + timedelta(days=21)  # 21 days after statement date
    
    statement = await repo.create({
        "account_id": account.id,
        "statement_date": statement_date,
        "statement_balance": Decimal("500.00"),
        "minimum_payment": Decimal("25.00"),
        "due_date": due_date
    })
    
    # Assert created statement
    assert statement.id is not None
    assert statement.account_id == account.id
    assert statement.statement_date == statement_date
    assert statement.statement_balance == Decimal("500.00")
    assert statement.minimum_payment == Decimal("25.00")
    assert statement.due_date == due_date


@pytest.mark.asyncio
async def test_get_by_account(db_session: AsyncSession):
    """Test retrieving statement history for an account."""
    # Create account
    account_repo = AccountRepository(db_session)
    
    account = await account_repo.create({
        "name": "Statement History Account",
        "type": "credit",
        "available_balance": Decimal("-800.00"),
        "total_limit": Decimal("3000.00"),
        "available_credit": Decimal("2200.00")
    })
    
    # Create repository
    repo = StatementHistoryRepository(db_session)
    
    # Create multiple statement history records
    now = datetime.now()
    
    statement1 = await repo.create({
        "account_id": account.id,
        "statement_date": now - timedelta(days=60),
        "statement_balance": Decimal("400.00"),
        "minimum_payment": Decimal("20.00"),
        "due_date": now - timedelta(days=39)
    })
    
    statement2 = await repo.create({
        "account_id": account.id,
        "statement_date": now - timedelta(days=30),
        "statement_balance": Decimal("600.00"),
        "minimum_payment": Decimal("30.00"),
        "due_date": now - timedelta(days=9)
    })
    
    statement3 = await repo.create({
        "account_id": account.id,
        "statement_date": now,
        "statement_balance": Decimal("800.00"),
        "minimum_payment": Decimal("40.00"),
        "due_date": now + timedelta(days=21)
    })
    
    # Test get_by_account (default limit is 12)
    statements = await repo.get_by_account(account.id)
    
    # Test get_by_account with limit
    statements_limited = await repo.get_by_account(account.id, limit=2)
    
    # Assert
    assert len(statements) >= 3  # Could be more if other tests added statements
    assert any(stmt.id == statement1.id for stmt in statements)
    assert any(stmt.id == statement2.id for stmt in statements)
    assert any(stmt.id == statement3.id for stmt in statements)
    
    assert len(statements_limited) == 2
    # Should return the most recent statements first
    assert statements_limited[0].id == statement3.id
    assert statements_limited[1].id == statement2.id


@pytest.mark.asyncio
async def test_get_latest_statement(db_session: AsyncSession):
    """Test retrieving the latest statement for an account."""
    # Create account
    account_repo = AccountRepository(db_session)
    
    account = await account_repo.create({
        "name": "Latest Statement Account",
        "type": "credit",
        "available_balance": Decimal("-700.00"),
        "total_limit": Decimal("2500.00"),
        "available_credit": Decimal("1800.00")
    })
    
    # Create repository
    repo = StatementHistoryRepository(db_session)
    
    # Create statement history records
    now = datetime.now()
    
    old_statement = await repo.create({
        "account_id": account.id,
        "statement_date": now - timedelta(days=30),
        "statement_balance": Decimal("500.00"),
        "minimum_payment": Decimal("25.00"),
        "due_date": now - timedelta(days=9)
    })
    
    latest_statement = await repo.create({
        "account_id": account.id,
        "statement_date": now - timedelta(days=1),
        "statement_balance": Decimal("700.00"),
        "minimum_payment": Decimal("35.00"),
        "due_date": now + timedelta(days=20)
    })
    
    # Test get_latest_statement
    statement = await repo.get_latest_statement(account.id)
    
    # Assert
    assert statement is not None
    assert statement.id == latest_statement.id
    assert statement.statement_date == latest_statement.statement_date
    assert statement.statement_balance == latest_statement.statement_balance


@pytest.mark.asyncio
async def test_get_with_account(db_session: AsyncSession):
    """Test retrieving a statement with its associated account."""
    # Create account
    account_repo = AccountRepository(db_session)
    
    account = await account_repo.create({
        "name": "Statement With Account",
        "type": "credit",
        "available_balance": Decimal("-600.00"),
        "total_limit": Decimal("2000.00"),
        "available_credit": Decimal("1400.00")
    })
    
    # Create repository
    repo = StatementHistoryRepository(db_session)
    
    # Create statement
    statement = await repo.create({
        "account_id": account.id,
        "statement_date": datetime.now(),
        "statement_balance": Decimal("600.00"),
        "minimum_payment": Decimal("30.00"),
        "due_date": datetime.now() + timedelta(days=21)
    })
    
    # Test get_with_account
    stmt_with_account = await repo.get_with_account(statement.id)
    
    # Assert
    assert stmt_with_account is not None
    assert stmt_with_account.account is not None
    assert stmt_with_account.account.id == account.id
    assert stmt_with_account.account.name == "Statement With Account"


@pytest.mark.asyncio
async def test_get_by_date_range(db_session: AsyncSession):
    """Test retrieving statements within a date range."""
    # Create account
    account_repo = AccountRepository(db_session)
    
    account = await account_repo.create({
        "name": "Date Range Account",
        "type": "credit",
        "available_balance": Decimal("-900.00"),
        "total_limit": Decimal("5000.00"),
        "available_credit": Decimal("4100.00")
    })
    
    # Create repository
    repo = StatementHistoryRepository(db_session)
    
    # Create statement history records
    now = datetime.now()
    
    old_statement = await repo.create({
        "account_id": account.id,
        "statement_date": now - timedelta(days=90),
        "statement_balance": Decimal("300.00"),
        "due_date": now - timedelta(days=69)
    })
    
    mid_statement1 = await repo.create({
        "account_id": account.id,
        "statement_date": now - timedelta(days=60),
        "statement_balance": Decimal("500.00"),
        "due_date": now - timedelta(days=39)
    })
    
    mid_statement2 = await repo.create({
        "account_id": account.id,
        "statement_date": now - timedelta(days=30),
        "statement_balance": Decimal("700.00"),
        "due_date": now - timedelta(days=9)
    })
    
    recent_statement = await repo.create({
        "account_id": account.id,
        "statement_date": now,
        "statement_balance": Decimal("900.00"),
        "due_date": now + timedelta(days=21)
    })
    
    # Define date range
    start_date = now - timedelta(days=70)
    end_date = now - timedelta(days=20)
    
    # Test get_by_date_range
    statements = await repo.get_by_date_range(account.id, start_date, end_date)
    
    # Assert
    assert len(statements) == 2
    assert any(stmt.id == mid_statement1.id for stmt in statements)
    assert any(stmt.id == mid_statement2.id for stmt in statements)
    assert not any(stmt.id == old_statement.id for stmt in statements)
    assert not any(stmt.id == recent_statement.id for stmt in statements)


@pytest.mark.asyncio
async def test_get_statements_with_due_dates(db_session: AsyncSession):
    """Test retrieving statements with due dates in a specified range."""
    # Create accounts
    account_repo = AccountRepository(db_session)
    
    account1 = await account_repo.create({
        "name": "Due Date Account 1",
        "type": "credit",
        "available_balance": Decimal("-400.00"),
        "total_limit": Decimal("1000.00"),
        "available_credit": Decimal("600.00")
    })
    
    account2 = await account_repo.create({
        "name": "Due Date Account 2",
        "type": "credit",
        "available_balance": Decimal("-600.00"),
        "total_limit": Decimal("2000.00"),
        "available_credit": Decimal("1400.00")
    })
    
    # Create repository
    repo = StatementHistoryRepository(db_session)
    
    # Create statement history records
    now = datetime.now()
    
    # Due dates in the past
    past_statement = await repo.create({
        "account_id": account1.id,
        "statement_date": now - timedelta(days=40),
        "statement_balance": Decimal("200.00"),
        "minimum_payment": Decimal("10.00"),
        "due_date": now - timedelta(days=19)
    })
    
    # Due dates in the target range
    upcoming_statement1 = await repo.create({
        "account_id": account1.id,
        "statement_date": now - timedelta(days=20),
        "statement_balance": Decimal("400.00"),
        "minimum_payment": Decimal("20.00"),
        "due_date": now + timedelta(days=1)
    })
    
    upcoming_statement2 = await repo.create({
        "account_id": account2.id,
        "statement_date": now - timedelta(days=15),
        "statement_balance": Decimal("600.00"),
        "minimum_payment": Decimal("30.00"),
        "due_date": now + timedelta(days=6)
    })
    
    # Due dates beyond the range
    future_statement = await repo.create({
        "account_id": account2.id,
        "statement_date": now,
        "statement_balance": Decimal("800.00"),
        "minimum_payment": Decimal("40.00"),
        "due_date": now + timedelta(days=21)
    })
    
    # Define date range for due dates
    start_date = now
    end_date = now + timedelta(days=10)
    
    # Test get_statements_with_due_dates
    statements = await repo.get_statements_with_due_dates(start_date, end_date)
    
    # Assert
    assert len(statements) == 2
    assert any(stmt.id == upcoming_statement1.id for stmt in statements)
    assert any(stmt.id == upcoming_statement2.id for stmt in statements)
    assert not any(stmt.id == past_statement.id for stmt in statements)
    assert not any(stmt.id == future_statement.id for stmt in statements)


@pytest.mark.asyncio
async def test_get_upcoming_statements_with_accounts(db_session: AsyncSession):
    """Test retrieving upcoming statements with their accounts."""
    # Create accounts
    account_repo = AccountRepository(db_session)
    
    account1 = await account_repo.create({
        "name": "Upcoming Account 1",
        "type": "credit",
        "available_balance": Decimal("-500.00"),
        "total_limit": Decimal("1500.00"),
        "available_credit": Decimal("1000.00")
    })
    
    account2 = await account_repo.create({
        "name": "Upcoming Account 2",
        "type": "credit",
        "available_balance": Decimal("-700.00"),
        "total_limit": Decimal("2500.00"),
        "available_credit": Decimal("1800.00")
    })
    
    # Create repository
    repo = StatementHistoryRepository(db_session)
    
    # Create statement history records
    now = datetime.now()
    
    # Past due
    past_statement = await repo.create({
        "account_id": account1.id,
        "statement_date": now - timedelta(days=30),
        "statement_balance": Decimal("300.00"),
        "minimum_payment": Decimal("15.00"),
        "due_date": now - timedelta(days=9)
    })
    
    # Upcoming due dates
    upcoming_statement1 = await repo.create({
        "account_id": account1.id,
        "statement_date": now - timedelta(days=15),
        "statement_balance": Decimal("500.00"),
        "minimum_payment": Decimal("25.00"),
        "due_date": now + timedelta(days=6)
    })
    
    upcoming_statement2 = await repo.create({
        "account_id": account2.id,
        "statement_date": now - timedelta(days=10),
        "statement_balance": Decimal("700.00"),
        "minimum_payment": Decimal("35.00"),
        "due_date": now + timedelta(days=11)
    })
    
    # Far future due date (beyond the 30-day default window)
    future_statement = await repo.create({
        "account_id": account2.id,
        "statement_date": now,
        "statement_balance": Decimal("900.00"),
        "minimum_payment": Decimal("45.00"),
        "due_date": now + timedelta(days=40)
    })
    
    # Test get_upcoming_statements_with_accounts (default days=30)
    statements_with_accounts = await repo.get_upcoming_statements_with_accounts()
    
    # Test with custom days parameter
    statements_with_accounts_10days = await repo.get_upcoming_statements_with_accounts(days=10)
    
    # Assert default behavior (30 days)
    assert len(statements_with_accounts) == 2
    
    statement_ids = [stmt[0].id for stmt in statements_with_accounts]
    account_ids = [acct[1].id for acct in statements_with_accounts]
    
    assert upcoming_statement1.id in statement_ids
    assert upcoming_statement2.id in statement_ids
    assert account1.id in account_ids
    assert account2.id in account_ids
    
    # Assert custom days behavior (10 days)
    assert len(statements_with_accounts_10days) == 1
    assert statements_with_accounts_10days[0][0].id == upcoming_statement1.id
    assert statements_with_accounts_10days[0][1].id == account1.id


@pytest.mark.asyncio
async def test_get_statements_with_minimum_payment(db_session: AsyncSession):
    """Test retrieving statements with minimum payment information."""
    # Create account
    account_repo = AccountRepository(db_session)
    
    account = await account_repo.create({
        "name": "Minimum Payment Account",
        "type": "credit",
        "available_balance": Decimal("-800.00"),
        "total_limit": Decimal("3000.00"),
        "available_credit": Decimal("2200.00")
    })
    
    # Create repository
    repo = StatementHistoryRepository(db_session)
    
    # Create statement history records
    now = datetime.now()
    
    # Statement with minimum payment
    statement1 = await repo.create({
        "account_id": account.id,
        "statement_date": now - timedelta(days=60),
        "statement_balance": Decimal("400.00"),
        "minimum_payment": Decimal("20.00"),
        "due_date": now - timedelta(days=39)
    })
    
    # Statement with minimum payment
    statement2 = await repo.create({
        "account_id": account.id,
        "statement_date": now - timedelta(days=30),
        "statement_balance": Decimal("600.00"),
        "minimum_payment": Decimal("30.00"),
        "due_date": now - timedelta(days=9)
    })
    
    # Statement without minimum payment
    statement3 = await repo.create({
        "account_id": account.id,
        "statement_date": now,
        "statement_balance": Decimal("800.00"),
        "minimum_payment": None,
        "due_date": now + timedelta(days=21)
    })
    
    # Test get_statements_with_minimum_payment
    statements = await repo.get_statements_with_minimum_payment(account.id)
    
    # Assert
    assert len(statements) == 2
    assert any(stmt.id == statement1.id for stmt in statements)
    assert any(stmt.id == statement2.id for stmt in statements)
    assert not any(stmt.id == statement3.id for stmt in statements)


@pytest.mark.asyncio
async def test_get_average_statement_balance(db_session: AsyncSession):
    """Test calculating average statement balance."""
    # Create account
    account_repo = AccountRepository(db_session)
    
    account = await account_repo.create({
        "name": "Average Balance Account",
        "type": "credit",
        "available_balance": Decimal("-500.00"),
        "total_limit": Decimal("2000.00"),
        "available_credit": Decimal("1500.00")
    })
    
    # Create repository
    repo = StatementHistoryRepository(db_session)
    
    # Create statement history records
    now = datetime.now()
    
    await repo.create({
        "account_id": account.id,
        "statement_date": now - timedelta(days=90),
        "statement_balance": Decimal("300.00")
    })
    
    await repo.create({
        "account_id": account.id,
        "statement_date": now - timedelta(days=60),
        "statement_balance": Decimal("600.00")
    })
    
    await repo.create({
        "account_id": account.id,
        "statement_date": now - timedelta(days=30),
        "statement_balance": Decimal("900.00")
    })
    
    # Test get_average_statement_balance (default months=6)
    average = await repo.get_average_statement_balance(account.id)
    
    # Test with custom months parameter
    average_2months = await repo.get_average_statement_balance(account.id, months=2)
    
    # Assert
    assert average == Decimal("600.00")  # (300 + 600 + 900) / 3
    assert average_2months == Decimal("750.00")  # (600 + 900) / 2


@pytest.mark.asyncio
async def test_get_statement_trend(db_session: AsyncSession):
    """Test retrieving statement balance trend."""
    # Create account
    account_repo = AccountRepository(db_session)
    
    account = await account_repo.create({
        "name": "Trend Account",
        "type": "credit",
        "available_balance": Decimal("-700.00"),
        "total_limit": Decimal("2500.00"),
        "available_credit": Decimal("1800.00")
    })
    
    # Create repository
    repo = StatementHistoryRepository(db_session)
    
    # Create statement history records
    now = datetime.now()
    
    statement1_date = now - timedelta(days=90)
    statement1 = await repo.create({
        "account_id": account.id,
        "statement_date": statement1_date,
        "statement_balance": Decimal("300.00")
    })
    
    statement2_date = now - timedelta(days=60)
    statement2 = await repo.create({
        "account_id": account.id,
        "statement_date": statement2_date,
        "statement_balance": Decimal("500.00")
    })
    
    statement3_date = now - timedelta(days=30)
    statement3 = await repo.create({
        "account_id": account.id,
        "statement_date": statement3_date,
        "statement_balance": Decimal("700.00")
    })
    
    # Test get_statement_trend
    trend = await repo.get_statement_trend(account.id)
    
    # Assert
    assert len(trend) == 3
    
    # Check that dates and balances match
    dates = [date for date, _ in trend]
    balances = [balance for _, balance in trend]
    
    assert statement1_date in dates
    assert statement2_date in dates
    assert statement3_date in dates
    
    assert Decimal("300.00") in balances
    assert Decimal("500.00") in balances
    assert Decimal("700.00") in balances


@pytest.mark.asyncio
async def test_get_total_minimum_payments_due(db_session: AsyncSession):
    """Test calculating total minimum payments due."""
    # Create accounts
    account_repo = AccountRepository(db_session)
    
    account1 = await account_repo.create({
        "name": "Min Payment Account 1",
        "type": "credit",
        "available_balance": Decimal("-400.00"),
        "total_limit": Decimal("1000.00"),
        "available_credit": Decimal("600.00")
    })
    
    account2 = await account_repo.create({
        "name": "Min Payment Account 2",
        "type": "credit",
        "available_balance": Decimal("-600.00"),
        "total_limit": Decimal("2000.00"),
        "available_credit": Decimal("1400.00")
    })
    
    # Create repository
    repo = StatementHistoryRepository(db_session)
    
    # Create statement history records
    now = datetime.now()
    
    # Due dates outside the target range
    await repo.create({
        "account_id": account1.id,
        "statement_date": now - timedelta(days=40),
        "statement_balance": Decimal("200.00"),
        "minimum_payment": Decimal("10.00"),
        "due_date": now - timedelta(days=19)  # Past due
    })
    
    await repo.create({
        "account_id": account2.id,
        "statement_date": now,
        "statement_balance": Decimal("800.00"),
        "minimum_payment": Decimal("40.00"),
        "due_date": now + timedelta(days=31)  # Future due
    })
    
    # Due dates in the target range
    await repo.create({
        "account_id": account1.id,
        "statement_date": now - timedelta(days=20),
        "statement_balance": Decimal("400.00"),
        "minimum_payment": Decimal("20.00"),
        "due_date": now + timedelta(days=1)
    })
    
    await repo.create({
        "account_id": account2.id,
        "statement_date": now - timedelta(days=15),
        "statement_balance": Decimal("600.00"),
        "minimum_payment": Decimal("30.00"),
        "due_date": now + timedelta(days=6)
    })
    
    # Define date range for due dates
    start_date = now
    end_date = now + timedelta(days=10)
    
    # Test get_total_minimum_payments_due
    total = await repo.get_total_minimum_payments_due(start_date, end_date)
    
    # Assert
    assert total == Decimal("50.00")  # 20.00 + 30.00
