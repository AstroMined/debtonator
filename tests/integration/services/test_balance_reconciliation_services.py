from datetime import datetime
from decimal import Decimal

import pytest
from sqlalchemy import select

from src.models.accounts import Account
from src.models.balance_reconciliation import BalanceReconciliation
from src.schemas.balance_reconciliation import (BalanceReconciliationCreate,
                                                BalanceReconciliationUpdate)
from src.services.balance_reconciliation import BalanceReconciliationService


@pytest.fixture
async def test_account(db_session):
    """Create a test account"""
    account = Account(
        name="Test Account",
        type="checking",
        available_balance=Decimal("1000.00"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account


@pytest.fixture
async def test_reconciliation(db_session, test_account):
    """Create a test reconciliation record"""
    reconciliation = BalanceReconciliation(
        account_id=test_account.id,
        previous_balance=Decimal("1000.00"),
        new_balance=Decimal("1100.00"),
        adjustment_amount=Decimal("100.00"),
        reason="Test reconciliation",
        reconciliation_date=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(reconciliation)
    await db_session.commit()
    await db_session.refresh(reconciliation)
    return reconciliation


async def test_create_reconciliation(db_session, test_account):
    """Test creating a new reconciliation record"""
    service = BalanceReconciliationService(db_session)
    reconciliation_data = BalanceReconciliationCreate(
        account_id=test_account.id,
        previous_balance=Decimal("1000.00"),
        new_balance=Decimal("1100.00"),
        reason="Test reconciliation",
    )

    result = await service.create_reconciliation(reconciliation_data)

    assert result.account_id == test_account.id
    assert result.previous_balance == Decimal("1000.00")
    assert result.new_balance == Decimal("1100.00")
    assert result.adjustment_amount == Decimal("100.00")
    assert result.reason == "Test reconciliation"

    # Verify account balance was updated
    account = await db_session.get(Account, test_account.id)
    assert account.available_balance == Decimal("1100.00")


async def test_create_reconciliation_invalid_account(db_session):
    """Test creating a reconciliation with invalid account ID"""
    service = BalanceReconciliationService(db_session)
    reconciliation_data = BalanceReconciliationCreate(
        account_id=999,
        previous_balance=Decimal("1000.00"),
        new_balance=Decimal("1100.00"),
        reason="Test reconciliation",
    )

    with pytest.raises(ValueError, match="Account with id 999 not found"):
        await service.create_reconciliation(reconciliation_data)


async def test_get_reconciliation(db_session, test_reconciliation):
    """Test retrieving a specific reconciliation record"""
    service = BalanceReconciliationService(db_session)
    result = await service.get_reconciliation(test_reconciliation.id)

    assert result is not None
    assert result.id == test_reconciliation.id
    assert result.account_id == test_reconciliation.account_id
    assert result.previous_balance == test_reconciliation.previous_balance
    assert result.new_balance == test_reconciliation.new_balance


async def test_get_account_reconciliations(
    db_session, test_account, test_reconciliation
):
    """Test retrieving reconciliation history for an account"""
    service = BalanceReconciliationService(db_session)
    results = await service.get_account_reconciliations(test_account.id)

    assert len(results) == 1
    assert results[0].id == test_reconciliation.id
    assert results[0].account_id == test_account.id


async def test_update_reconciliation(db_session, test_reconciliation):
    """Test updating a reconciliation record"""
    service = BalanceReconciliationService(db_session)
    update_data = BalanceReconciliationUpdate(reason="Updated reason")

    result = await service.update_reconciliation(test_reconciliation.id, update_data)

    assert result is not None
    assert result.id == test_reconciliation.id
    assert result.reason == "Updated reason"


async def test_update_nonexistent_reconciliation(db_session):
    """Test updating a nonexistent reconciliation record"""
    service = BalanceReconciliationService(db_session)
    update_data = BalanceReconciliationUpdate(reason="Updated reason")

    result = await service.update_reconciliation(999, update_data)
    assert result is None


async def test_delete_reconciliation(db_session, test_reconciliation):
    """Test deleting a reconciliation record"""
    service = BalanceReconciliationService(db_session)

    # Delete the record
    success = await service.delete_reconciliation(test_reconciliation.id)
    assert success is True

    # Verify it's gone
    result = await db_session.execute(
        select(BalanceReconciliation).filter_by(id=test_reconciliation.id)
    )
    assert result.scalar_one_or_none() is None


async def test_delete_nonexistent_reconciliation(db_session):
    """Test deleting a nonexistent reconciliation record"""
    service = BalanceReconciliationService(db_session)
    success = await service.delete_reconciliation(999)
    assert success is False


async def test_get_latest_reconciliation(db_session, test_account, test_reconciliation):
    """Test getting the most recent reconciliation for an account"""
    service = BalanceReconciliationService(db_session)
    result = await service.get_latest_reconciliation(test_account.id)

    assert result is not None
    assert result.id == test_reconciliation.id
    assert result.account_id == test_account.id
