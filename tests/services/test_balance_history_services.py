from datetime import datetime, timedelta
from decimal import Decimal
import pytest
from sqlalchemy import select

from src.models.accounts import Account
from src.models.balance_history import BalanceHistory
from src.schemas.balance_history import BalanceHistoryCreate
from src.services.balance_history import BalanceHistoryService


@pytest.fixture(scope="function")
async def test_account(db_session):
    account = Account(
        name="Test Account",
        type="checking",
        available_balance=Decimal("1000.00"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)
    return account


@pytest.fixture(scope="function")
def balance_history_service(db_session):
    return BalanceHistoryService(db_session)


async def test_record_balance_change(balance_history_service, test_account):
    balance_data = BalanceHistoryCreate(
        account_id=test_account.id,
        balance=Decimal("1500.00"),
        notes="Initial balance record"
    )
    
    entry = await balance_history_service.record_balance_change(balance_data)
    
    assert entry.id is not None
    assert entry.account_id == test_account.id
    assert entry.balance == Decimal("1500.00")
    assert entry.notes == "Initial balance record"
    assert entry.is_reconciled is False
    assert isinstance(entry.timestamp, datetime)


async def test_get_balance_history(balance_history_service, test_account):
    # Create multiple balance history entries
    timestamps = [
        datetime.utcnow() - timedelta(days=2),
        datetime.utcnow() - timedelta(days=1),
        datetime.utcnow()
    ]
    balances = [Decimal("1000.00"), Decimal("1500.00"), Decimal("1200.00")]
    
    for timestamp, balance in zip(timestamps, balances):
        balance_data = BalanceHistoryCreate(
            account_id=test_account.id,
            balance=balance
        )
        await balance_history_service.record_balance_change(balance_data, timestamp)
    
    # Test retrieval with date range
    history = await balance_history_service.get_balance_history(
        test_account.id,
        timestamps[0],
        timestamps[-1]
    )
    
    assert len(history) == 3
    assert [entry.balance for entry in history] == balances


async def test_get_balance_trend(balance_history_service, test_account):
    # Create balance history entries over time
    start_date = datetime.utcnow() - timedelta(days=2)
    end_date = datetime.utcnow()
    
    balances = [Decimal("1000.00"), Decimal("1500.00"), Decimal("2000.00")]
    timestamps = [
        start_date,
        start_date + timedelta(days=1),
        end_date
    ]
    
    for timestamp, balance in zip(timestamps, balances):
        balance_data = BalanceHistoryCreate(
            account_id=test_account.id,
            balance=balance
        )
        await balance_history_service.record_balance_change(balance_data, timestamp)
    
    trend = await balance_history_service.get_balance_trend(
        test_account.id,
        start_date,
        end_date
    )
    
    assert trend.account_id == test_account.id
    assert trend.start_balance == Decimal("1000.00")
    assert trend.end_balance == Decimal("2000.00")
    assert trend.net_change == Decimal("1000.00")
    assert trend.trend_direction == "increasing"
    assert trend.min_balance == Decimal("1000.00")
    assert trend.max_balance == Decimal("2000.00")
    assert trend.volatility > Decimal("0")


async def test_mark_reconciled(balance_history_service, test_account):
    # Create a balance history entry
    balance_data = BalanceHistoryCreate(
        account_id=test_account.id,
        balance=Decimal("1500.00")
    )
    entry = await balance_history_service.record_balance_change(balance_data)
    
    # Mark as reconciled
    updated_entry = await balance_history_service.mark_reconciled(
        entry.id,
        notes="Reconciled with bank statement"
    )
    
    assert updated_entry.is_reconciled is True
    assert updated_entry.notes == "Reconciled with bank statement"


async def test_get_unreconciled_entries(balance_history_service, test_account):
    # Create multiple entries with different reconciliation status
    timestamps = [
        datetime.utcnow() - timedelta(days=2),
        datetime.utcnow() - timedelta(days=1),
        datetime.utcnow()
    ]
    
    for timestamp in timestamps:
        balance_data = BalanceHistoryCreate(
            account_id=test_account.id,
            balance=Decimal("1500.00")
        )
        entry = await balance_history_service.record_balance_change(balance_data, timestamp)
        
        # Mark every other entry as reconciled
        if timestamps.index(timestamp) % 2 == 0:
            await balance_history_service.mark_reconciled(entry.id)
    
    unreconciled = await balance_history_service.get_unreconciled_entries(test_account.id)
    
    assert len(unreconciled) == 1  # Only one entry should be unreconciled
    assert all(not entry.is_reconciled for entry in unreconciled)


async def test_invalid_account_id(balance_history_service):
    invalid_id = 999
    balance_data = BalanceHistoryCreate(
        account_id=invalid_id,
        balance=Decimal("1500.00")
    )
    
    # Should raise a ValueError for non-existent account
    with pytest.raises(ValueError, match=f"Account {invalid_id} not found"):
        await balance_history_service.record_balance_change(balance_data)


async def test_get_balance_trend_no_history(balance_history_service, test_account):
    start_date = datetime.utcnow() - timedelta(days=1)
    end_date = datetime.utcnow()
    
    with pytest.raises(ValueError, match=f"No balance history found for account {test_account.id}"):
        await balance_history_service.get_balance_trend(test_account.id, start_date, end_date)
