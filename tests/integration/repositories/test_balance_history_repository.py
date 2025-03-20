"""
Integration tests for BalanceHistoryRepository.

This module contains tests that validate the behavior of the BalanceHistoryRepository
against a real database.
"""

import pytest
from datetime import datetime, date, timedelta
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.balance_history import BalanceHistory
from src.models.accounts import Account
from src.repositories.balance_history import BalanceHistoryRepository
from src.repositories.accounts import AccountRepository


@pytest.mark.asyncio
async def test_create_balance_history(db_session: AsyncSession):
    """Test creating a balance history record."""
    # Create account first
    account_repo = AccountRepository(db_session)
    
    account = await account_repo.create({
        "name": "Balance Test Account",
        "type": "checking",
        "available_balance": Decimal("1000.00")
    })
    
    # Create repository
    repo = BalanceHistoryRepository(db_session)
    
    # Create balance history record
    timestamp = datetime.now()
    
    balance_history = await repo.create({
        "account_id": account.id,
        "balance": Decimal("1000.00"),
        "available_credit": None,
        "is_reconciled": False,
        "notes": "Initial balance",
        "timestamp": timestamp
    })
    
    # Assert created balance history
    assert balance_history.id is not None
    assert balance_history.account_id == account.id
    assert balance_history.balance == Decimal("1000.00")
    assert balance_history.available_credit is None
    assert balance_history.is_reconciled is False
    assert balance_history.notes == "Initial balance"
    assert balance_history.timestamp == timestamp


@pytest.mark.asyncio
async def test_get_by_account(db_session: AsyncSession):
    """Test retrieving balance history for an account."""
    # Create account
    account_repo = AccountRepository(db_session)
    
    account = await account_repo.create({
        "name": "Balance History Account",
        "type": "checking",
        "available_balance": Decimal("1500.00")
    })
    
    # Create repository
    repo = BalanceHistoryRepository(db_session)
    
    # Create multiple balance history records
    now = datetime.now()
    
    balance1 = await repo.create({
        "account_id": account.id,
        "balance": Decimal("1000.00"),
        "is_reconciled": False,
        "timestamp": now - timedelta(days=3)
    })
    
    balance2 = await repo.create({
        "account_id": account.id,
        "balance": Decimal("1200.00"),
        "is_reconciled": False,
        "timestamp": now - timedelta(days=2)
    })
    
    balance3 = await repo.create({
        "account_id": account.id,
        "balance": Decimal("1500.00"),
        "is_reconciled": True,
        "timestamp": now - timedelta(days=1)
    })
    
    # Test get_by_account (default limit is 30)
    balances = await repo.get_by_account(account.id)
    
    # Test get_by_account with limit
    balances_limited = await repo.get_by_account(account.id, limit=2)
    
    # Assert
    assert len(balances) == 3
    assert any(bal.id == balance1.id for bal in balances)
    assert any(bal.id == balance2.id for bal in balances)
    assert any(bal.id == balance3.id for bal in balances)
    
    assert len(balances_limited) == 2
    # Should return the most recent balances first
    assert balances_limited[0].id == balance3.id
    assert balances_limited[1].id == balance2.id


@pytest.mark.asyncio
async def test_get_latest_balance(db_session: AsyncSession):
    """Test retrieving the latest balance for an account."""
    # Create account
    account_repo = AccountRepository(db_session)
    
    account = await account_repo.create({
        "name": "Latest Balance Account",
        "type": "checking",
        "available_balance": Decimal("2000.00")
    })
    
    # Create repository
    repo = BalanceHistoryRepository(db_session)
    
    # Create balance history records
    now = datetime.now()
    
    old_balance = await repo.create({
        "account_id": account.id,
        "balance": Decimal("1800.00"),
        "is_reconciled": False,
        "timestamp": now - timedelta(days=2)
    })
    
    latest_balance = await repo.create({
        "account_id": account.id,
        "balance": Decimal("2000.00"),
        "is_reconciled": True,
        "timestamp": now - timedelta(hours=2)
    })
    
    # Test get_latest_balance
    balance = await repo.get_latest_balance(account.id)
    
    # Assert
    assert balance is not None
    assert balance.id == latest_balance.id
    assert balance.timestamp == latest_balance.timestamp
    assert balance.balance == latest_balance.balance


@pytest.mark.asyncio
async def test_get_with_account(db_session: AsyncSession):
    """Test retrieving a balance with its associated account."""
    # Create account
    account_repo = AccountRepository(db_session)
    
    account = await account_repo.create({
        "name": "Balance With Account",
        "type": "checking",
        "available_balance": Decimal("2500.00")
    })
    
    # Create repository
    repo = BalanceHistoryRepository(db_session)
    
    # Create balance
    balance = await repo.create({
        "account_id": account.id,
        "balance": Decimal("2500.00"),
        "is_reconciled": True,
        "timestamp": datetime.now()
    })
    
    # Test get_with_account
    bal_with_account = await repo.get_with_account(balance.id)
    
    # Assert
    assert bal_with_account is not None
    assert bal_with_account.account is not None
    assert bal_with_account.account.id == account.id
    assert bal_with_account.account.name == "Balance With Account"


@pytest.mark.asyncio
async def test_get_by_date_range(db_session: AsyncSession):
    """Test retrieving balance history within a date range."""
    # Create account
    account_repo = AccountRepository(db_session)
    
    account = await account_repo.create({
        "name": "Date Range Account",
        "type": "checking",
        "available_balance": Decimal("3000.00")
    })
    
    # Create repository
    repo = BalanceHistoryRepository(db_session)
    
    # Create balance history records
    now = datetime.now()
    
    old_balance = await repo.create({
        "account_id": account.id,
        "balance": Decimal("2000.00"),
        "is_reconciled": False,
        "timestamp": now - timedelta(days=30)
    })
    
    mid_balance1 = await repo.create({
        "account_id": account.id,
        "balance": Decimal("2200.00"),
        "is_reconciled": False,
        "timestamp": now - timedelta(days=20)
    })
    
    mid_balance2 = await repo.create({
        "account_id": account.id,
        "balance": Decimal("2500.00"),
        "is_reconciled": True,
        "timestamp": now - timedelta(days=10)
    })
    
    recent_balance = await repo.create({
        "account_id": account.id,
        "balance": Decimal("3000.00"),
        "is_reconciled": True,
        "timestamp": now
    })
    
    # Define date range
    start_date = now - timedelta(days=25)
    end_date = now - timedelta(days=5)
    
    # Test get_by_date_range
    balances = await repo.get_by_date_range(account.id, start_date, end_date)
    
    # Assert
    assert len(balances) == 2
    assert any(bal.id == mid_balance1.id for bal in balances)
    assert any(bal.id == mid_balance2.id for bal in balances)
    assert not any(bal.id == old_balance.id for bal in balances)
    assert not any(bal.id == recent_balance.id for bal in balances)


@pytest.mark.asyncio
async def test_get_reconciled_balances(db_session: AsyncSession):
    """Test retrieving reconciled balance records."""
    # Create account
    account_repo = AccountRepository(db_session)
    
    account = await account_repo.create({
        "name": "Reconciled Balance Account",
        "type": "checking",
        "available_balance": Decimal("2800.00")
    })
    
    # Create repository
    repo = BalanceHistoryRepository(db_session)
    
    # Create balance history records
    now = datetime.now()
    
    unreconciled1 = await repo.create({
        "account_id": account.id,
        "balance": Decimal("2400.00"),
        "is_reconciled": False,
        "timestamp": now - timedelta(days=3)
    })
    
    reconciled1 = await repo.create({
        "account_id": account.id,
        "balance": Decimal("2500.00"),
        "is_reconciled": True,
        "timestamp": now - timedelta(days=2)
    })
    
    unreconciled2 = await repo.create({
        "account_id": account.id,
        "balance": Decimal("2600.00"),
        "is_reconciled": False,
        "timestamp": now - timedelta(days=1)
    })
    
    reconciled2 = await repo.create({
        "account_id": account.id,
        "balance": Decimal("2800.00"),
        "is_reconciled": True,
        "timestamp": now
    })
    
    # Test get_reconciled_balances
    reconciled_balances = await repo.get_reconciled_balances(account.id)
    
    # Assert
    assert len(reconciled_balances) == 2
    assert any(bal.id == reconciled1.id for bal in reconciled_balances)
    assert any(bal.id == reconciled2.id for bal in reconciled_balances)
    assert not any(bal.id == unreconciled1.id for bal in reconciled_balances)
    assert not any(bal.id == unreconciled2.id for bal in reconciled_balances)


@pytest.mark.asyncio
async def test_min_max_balance(db_session: AsyncSession):
    """Test retrieving minimum and maximum balance records."""
    # Create account
    account_repo = AccountRepository(db_session)
    
    account = await account_repo.create({
        "name": "Min-Max Balance Account",
        "type": "checking",
        "available_balance": Decimal("2000.00")
    })
    
    # Create repository
    repo = BalanceHistoryRepository(db_session)
    
    # Create balance history records
    now = datetime.now()
    
    # Old balance outside the default date range (30 days)
    await repo.create({
        "account_id": account.id,
        "balance": Decimal("500.00"),  # Would be min if in range
        "timestamp": now - timedelta(days=40)
    })
    
    # Balances within the default date range
    mid_balance = await repo.create({
        "account_id": account.id,
        "balance": Decimal("1500.00"),
        "timestamp": now - timedelta(days=20)
    })
    
    min_balance = await repo.create({
        "account_id": account.id,
        "balance": Decimal("1000.00"),  # Minimum in range
        "timestamp": now - timedelta(days=10)
    })
    
    max_balance = await repo.create({
        "account_id": account.id,
        "balance": Decimal("2000.00"),  # Maximum in range
        "timestamp": now
    })
    
    # Test get_min_max_balance with default days (30)
    min_bal, max_bal = await repo.get_min_max_balance(account.id)
    
    # Assert
    assert min_bal.id == min_balance.id
    assert min_bal.balance == Decimal("1000.00")
    
    assert max_bal.id == max_balance.id
    assert max_bal.balance == Decimal("2000.00")


@pytest.mark.asyncio
async def test_get_balance_trend(db_session: AsyncSession):
    """Test retrieving balance trend data."""
    # Create account
    account_repo = AccountRepository(db_session)
    
    account = await account_repo.create({
        "name": "Trend Balance Account",
        "type": "checking",
        "available_balance": Decimal("2500.00")
    })
    
    # Create repository
    repo = BalanceHistoryRepository(db_session)
    
    # Create balance history records
    now = datetime.now()
    
    timestamp1 = now - timedelta(days=20)
    balance1 = await repo.create({
        "account_id": account.id,
        "balance": Decimal("1000.00"),
        "timestamp": timestamp1
    })
    
    timestamp2 = now - timedelta(days=10)
    balance2 = await repo.create({
        "account_id": account.id,
        "balance": Decimal("1800.00"),
        "timestamp": timestamp2
    })
    
    timestamp3 = now
    balance3 = await repo.create({
        "account_id": account.id,
        "balance": Decimal("2500.00"),
        "timestamp": timestamp3
    })
    
    # Test get_balance_trend
    trend = await repo.get_balance_trend(account.id)
    
    # Assert
    assert len(trend) == 3
    
    # Check that timestamps and balances match
    timestamps = [ts for ts, _ in trend]
    balances = [bal for _, bal in trend]
    
    assert timestamp1 in timestamps
    assert timestamp2 in timestamps
    assert timestamp3 in timestamps
    
    assert Decimal("1000.00") in balances
    assert Decimal("1800.00") in balances
    assert Decimal("2500.00") in balances


@pytest.mark.asyncio
async def test_get_average_balance(db_session: AsyncSession):
    """Test calculating average balance."""
    # Create account
    account_repo = AccountRepository(db_session)
    
    account = await account_repo.create({
        "name": "Average Balance Account",
        "type": "checking",
        "available_balance": Decimal("2400.00")
    })
    
    # Create repository
    repo = BalanceHistoryRepository(db_session)
    
    # Create balance history records
    now = datetime.now()
    
    # Balance outside the default date range (30 days)
    await repo.create({
        "account_id": account.id,
        "balance": Decimal("500.00"),
        "timestamp": now - timedelta(days=40)
    })
    
    # Balances within the default date range
    await repo.create({
        "account_id": account.id,
        "balance": Decimal("1200.00"),
        "timestamp": now - timedelta(days=20)
    })
    
    await repo.create({
        "account_id": account.id,
        "balance": Decimal("1800.00"),
        "timestamp": now - timedelta(days=10)
    })
    
    await repo.create({
        "account_id": account.id,
        "balance": Decimal("2400.00"),
        "timestamp": now
    })
    
    # Test get_average_balance with default days (30)
    average = await repo.get_average_balance(account.id)
    
    # Test with custom days parameter
    average_15days = await repo.get_average_balance(account.id, days=15)
    
    # Assert
    # Average of 1200 + 1800 + 2400 = 5400 / 3 = 1800
    assert average == Decimal("1800")
    
    # Average of 1800 + 2400 = 4200 / 2 = 2100
    assert average_15days == Decimal("2100")


@pytest.mark.asyncio
async def test_balance_history_with_notes(db_session: AsyncSession):
    """Test retrieving balance history records with notes."""
    # Create account
    account_repo = AccountRepository(db_session)
    
    account = await account_repo.create({
        "name": "Notes Balance Account",
        "type": "checking",
        "available_balance": Decimal("3000.00")
    })
    
    # Create repository
    repo = BalanceHistoryRepository(db_session)
    
    # Create balance history records
    now = datetime.now()
    
    with_note1 = await repo.create({
        "account_id": account.id,
        "balance": Decimal("2000.00"),
        "notes": "Initial balance check",
        "timestamp": now - timedelta(days=3)
    })
    
    no_note = await repo.create({
        "account_id": account.id,
        "balance": Decimal("2500.00"),
        "notes": None,
        "timestamp": now - timedelta(days=2)
    })
    
    empty_note = await repo.create({
        "account_id": account.id,
        "balance": Decimal("2700.00"),
        "notes": "",
        "timestamp": now - timedelta(days=1)
    })
    
    with_note2 = await repo.create({
        "account_id": account.id,
        "balance": Decimal("3000.00"),
        "notes": "Deposit added",
        "timestamp": now
    })
    
    # Test get_balance_history_with_notes
    balances_with_notes = await repo.get_balance_history_with_notes(account.id)
    
    # Assert
    assert len(balances_with_notes) == 2
    assert any(bal.id == with_note1.id for bal in balances_with_notes)
    assert any(bal.id == with_note2.id for bal in balances_with_notes)
    assert not any(bal.id == no_note.id for bal in balances_with_notes)
    assert not any(bal.id == empty_note.id for bal in balances_with_notes)


@pytest.mark.asyncio
async def test_mark_as_reconciled(db_session: AsyncSession):
    """Test marking a balance record as reconciled."""
    # Create account
    account_repo = AccountRepository(db_session)
    
    account = await account_repo.create({
        "name": "Reconcile Test Account",
        "type": "checking",
        "available_balance": Decimal("1500.00")
    })
    
    # Create repository
    repo = BalanceHistoryRepository(db_session)
    
    # Create balance history record
    balance = await repo.create({
        "account_id": account.id,
        "balance": Decimal("1500.00"),
        "is_reconciled": False,
        "timestamp": datetime.now()
    })
    
    # Test mark_as_reconciled
    updated_balance = await repo.mark_as_reconciled(balance.id)
    
    # Assert
    assert updated_balance is not None
    assert updated_balance.is_reconciled is True
    
    # Test unmarking as reconciled
    unmarked_balance = await repo.mark_as_reconciled(balance.id, reconciled=False)
    assert unmarked_balance.is_reconciled is False


@pytest.mark.asyncio
async def test_add_balance_note(db_session: AsyncSession):
    """Test adding a note to a balance record."""
    # Create account
    account_repo = AccountRepository(db_session)
    
    account = await account_repo.create({
        "name": "Note Test Account",
        "type": "checking",
        "available_balance": Decimal("2200.00")
    })
    
    # Create repository
    repo = BalanceHistoryRepository(db_session)
    
    # Create balance history record
    balance = await repo.create({
        "account_id": account.id,
        "balance": Decimal("2200.00"),
        "notes": None,
        "timestamp": datetime.now()
    })
    
    # Test add_balance_note
    updated_balance = await repo.add_balance_note(balance.id, "Reconciled with bank statement")
    
    # Assert
    assert updated_balance is not None
    assert updated_balance.notes == "Reconciled with bank statement"
    
    # Test updating an existing note
    updated_note = await repo.add_balance_note(balance.id, "Updated after reconciliation")
    assert updated_note.notes == "Updated after reconciliation"


@pytest.mark.asyncio
async def test_get_missing_days(db_session: AsyncSession):
    """Test finding days with no balance records."""
    # Create account
    account_repo = AccountRepository(db_session)
    
    account = await account_repo.create({
        "name": "Missing Days Account",
        "type": "checking",
        "available_balance": Decimal("3000.00")
    })
    
    # Create repository
    repo = BalanceHistoryRepository(db_session)
    
    # Create balance history records with specific dates
    now = datetime.now()
    today = now.replace(hour=0, minute=0, second=0, microsecond=0)
    
    day1 = today - timedelta(days=10)
    await repo.create({
        "account_id": account.id,
        "balance": Decimal("2000.00"),
        "timestamp": day1
    })
    
    day2 = today - timedelta(days=5)
    await repo.create({
        "account_id": account.id,
        "balance": Decimal("2500.00"),
        "timestamp": day2
    })
    
    day3 = today
    await repo.create({
        "account_id": account.id,
        "balance": Decimal("3000.00"),
        "timestamp": day3
    })
    
    # Test get_missing_days with a smaller range to simplify validation
    missing_days = await repo.get_missing_days(account.id, days=10)
    
    # Assert
    # We should have records for days 0, 5, and 10, so missing days are 1-4 and 6-9
    assert len(missing_days) == 8
    
    # Check a few specific days
    day_minus_1 = (today - timedelta(days=1)).date()
    day_minus_6 = (today - timedelta(days=6)).date()
    day_minus_9 = (today - timedelta(days=9)).date()
    
    assert day_minus_1 in missing_days
    assert day_minus_6 in missing_days
    assert day_minus_9 in missing_days
