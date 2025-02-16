from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.balance_reconciliation import BalanceReconciliation

pytestmark = pytest.mark.asyncio

@pytest.fixture(scope="function")
async def test_account(db_session: AsyncSession) -> Account:
    account = Account(
        name="Test Account",
        type="checking",
        available_balance=Decimal("1000.00"),
        created_at=datetime.now(ZoneInfo("UTC")),
        updated_at=datetime.now(ZoneInfo("UTC"))
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account

async def test_create_balance_reconciliation(
    db_session: AsyncSession,
    test_account: Account
):
    """Test creating a balance reconciliation record."""
    reconciliation = BalanceReconciliation(
        account_id=test_account.id,
        previous_balance=Decimal("1000.00"),
        new_balance=Decimal("1100.00"),
        adjustment_amount=Decimal("100.00"),
        reason="Test reconciliation",
        reconciliation_date=datetime.now(ZoneInfo("UTC"))
    )
    db_session.add(reconciliation)
    await db_session.commit()
    await db_session.refresh(reconciliation)

    assert reconciliation.id is not None
    assert reconciliation.account_id == test_account.id
    assert reconciliation.previous_balance == Decimal("1000.00")
    assert reconciliation.new_balance == Decimal("1100.00")
    assert reconciliation.adjustment_amount == Decimal("100.00")
    assert reconciliation.reason == "Test reconciliation"
    assert isinstance(reconciliation.reconciliation_date, datetime)
    assert isinstance(reconciliation.created_at, datetime)
    assert isinstance(reconciliation.updated_at, datetime)

async def test_balance_reconciliation_default_date(
    db_session: AsyncSession,
    test_account: Account
):
    """Test that reconciliation_date defaults to current UTC time if not provided."""
    reconciliation = BalanceReconciliation(
        account_id=test_account.id,
        previous_balance=Decimal("1000.00"),
        new_balance=Decimal("1100.00"),
        adjustment_amount=Decimal("100.00"),
        reason="Test reconciliation"
    )
    db_session.add(reconciliation)
    await db_session.commit()
    await db_session.refresh(reconciliation)

    assert reconciliation.reconciliation_date is not None
    assert isinstance(reconciliation.reconciliation_date, datetime)
    # Verify it's a recent timestamp (within last minute)
    now = datetime.now(ZoneInfo("UTC"))
    assert isinstance(reconciliation.reconciliation_date, datetime)
    assert reconciliation.reconciliation_date.tzinfo is not None  # Ensure timezone-aware
    diff = now - reconciliation.reconciliation_date.replace(tzinfo=ZoneInfo("UTC"))
    assert diff.total_seconds() < 60

async def test_balance_reconciliation_relationships(
    db_session: AsyncSession,
    test_account: Account
):
    """Test balance reconciliation relationships."""
    reconciliation = BalanceReconciliation(
        account_id=test_account.id,
        previous_balance=Decimal("1000.00"),
        new_balance=Decimal("1100.00"),
        adjustment_amount=Decimal("100.00"),
        reason="Test reconciliation",
        reconciliation_date=datetime.now(ZoneInfo("UTC"))
    )
    db_session.add(reconciliation)
    await db_session.commit()
    await db_session.refresh(reconciliation)

    # Refresh test_account to load specific relationship
    await db_session.refresh(test_account, ['balance_reconciliations'])

    # Test account relationship
    assert reconciliation.account is not None
    assert reconciliation.account.id == test_account.id
    assert reconciliation.account.name == test_account.name

    # Test relationship from account side
    assert reconciliation in test_account.balance_reconciliations

async def test_balance_reconciliation_string_representation(
    db_session: AsyncSession,
    test_account: Account
):
    """Test the string representation of a balance reconciliation."""
    reconciliation = BalanceReconciliation(
        account_id=test_account.id,
        previous_balance=Decimal("1000.00"),
        new_balance=Decimal("1100.00"),
        adjustment_amount=Decimal("100.00"),
        reason="Test reconciliation",
        reconciliation_date=datetime.now(ZoneInfo("UTC"))
    )
    db_session.add(reconciliation)
    await db_session.commit()

    expected_str = f"<BalanceReconciliation(id={reconciliation.id}, account_id={test_account.id}, adjustment_amount=100.00)>"
    assert str(reconciliation) == expected_str
    assert repr(reconciliation) == expected_str

async def test_balance_reconciliation_cascade_delete(
    db_session: AsyncSession,
    test_account: Account
):
    """Test that balance reconciliations are deleted when account is deleted."""
    reconciliation = BalanceReconciliation(
        account_id=test_account.id,
        previous_balance=Decimal("1000.00"),
        new_balance=Decimal("1100.00"),
        adjustment_amount=Decimal("100.00"),
        reason="Test reconciliation",
        reconciliation_date=datetime.now(ZoneInfo("UTC"))
    )
    db_session.add(reconciliation)
    await db_session.commit()

    # Delete the account
    await db_session.delete(test_account)
    await db_session.commit()

    # Verify reconciliation is also deleted
    result = await db_session.get(BalanceReconciliation, reconciliation.id)
    assert result is None
