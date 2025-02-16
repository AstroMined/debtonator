from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo
import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import event

from src.models.accounts import Account
from src.models.credit_limit_history import CreditLimitHistory

pytestmark = pytest.mark.asyncio

@pytest.fixture(scope="function")
async def test_credit_account(db_session: AsyncSession) -> Account:
    account = Account(
        name="Test Credit Card",
        type="credit",
        available_balance=Decimal("-500.00"),
        total_limit=Decimal("2000.00"),
        created_at=datetime.now(ZoneInfo("UTC")),
        updated_at=datetime.now(ZoneInfo("UTC"))
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account

async def test_create_credit_limit_history(
    db_session: AsyncSession,
    test_credit_account: Account
):
    """Test creating a credit limit history record."""
    history = CreditLimitHistory(
        account_id=test_credit_account.id,
        credit_limit=Decimal("2000.00"),
        effective_date=datetime.now(ZoneInfo("UTC")),
        reason="Initial credit limit"
    )
    db_session.add(history)
    await db_session.commit()
    await db_session.refresh(history)

    assert history.id is not None
    assert history.account_id == test_credit_account.id
    assert history.credit_limit == Decimal("2000.00")
    assert isinstance(history.effective_date, datetime)
    assert history.reason == "Initial credit limit"
    assert isinstance(history.created_at, datetime)
    assert isinstance(history.updated_at, datetime)

async def test_credit_limit_history_relationships(
    db_session: AsyncSession,
    test_credit_account: Account
):
    """Test credit limit history relationships."""
    history = CreditLimitHistory(
        account_id=test_credit_account.id,
        credit_limit=Decimal("2000.00"),
        effective_date=datetime.now(ZoneInfo("UTC")),
        reason="Initial credit limit"
    )
    db_session.add(history)
    await db_session.commit()
    await db_session.refresh(history)

    # Refresh test_credit_account to load specific relationship
    await db_session.refresh(test_credit_account, ['credit_limit_history'])

    # Test account relationship
    assert history.account is not None
    assert history.account.id == test_credit_account.id
    assert history.account.name == test_credit_account.name

    # Test relationship from account side
    assert history in test_credit_account.credit_limit_history

async def test_credit_limit_history_string_representation(
    db_session: AsyncSession,
    test_credit_account: Account
):
    """Test the string representation of a credit limit history record."""
    history = CreditLimitHistory(
        account_id=test_credit_account.id,
        credit_limit=Decimal("2000.00"),
        effective_date=datetime.now(ZoneInfo("UTC")),
        reason="Initial credit limit"
    )
    db_session.add(history)
    await db_session.commit()

    expected_str = f"<CreditLimitHistory account_id={test_credit_account.id} limit=2000.00>"
    assert str(history) == expected_str
    assert repr(history) == expected_str

async def test_credit_limit_history_cascade_delete(
    db_session: AsyncSession,
    test_credit_account: Account
):
    """Test that credit limit history records are deleted when account is deleted."""
    history = CreditLimitHistory(
        account_id=test_credit_account.id,
        credit_limit=Decimal("2000.00"),
        effective_date=datetime.now(ZoneInfo("UTC")),
        reason="Initial credit limit"
    )
    db_session.add(history)
    await db_session.commit()

    # Delete the account
    await db_session.delete(test_credit_account)
    await db_session.commit()

    # Verify history record is also deleted
    result = await db_session.get(CreditLimitHistory, history.id)
    assert result is None

async def test_multiple_credit_limit_changes(
    db_session: AsyncSession,
    test_credit_account: Account
):
    """Test recording multiple credit limit changes for an account."""
    # Initial limit
    history1 = CreditLimitHistory(
        account_id=test_credit_account.id,
        credit_limit=Decimal("2000.00"),
        effective_date=datetime.now(ZoneInfo("UTC")),
        reason="Initial credit limit"
    )
    db_session.add(history1)
    await db_session.commit()

    # Increase limit
    history2 = CreditLimitHistory(
        account_id=test_credit_account.id,
        credit_limit=Decimal("3000.00"),
        effective_date=datetime.now(ZoneInfo("UTC")),
        reason="Credit limit increase"
    )
    db_session.add(history2)
    await db_session.commit()

    # Refresh test_credit_account to load specific relationship
    await db_session.refresh(test_credit_account, ['credit_limit_history'])

    # Verify both records exist and are correctly ordered
    assert len(test_credit_account.credit_limit_history) == 2
    assert test_credit_account.credit_limit_history[0].credit_limit == Decimal("2000.00")
    assert test_credit_account.credit_limit_history[1].credit_limit == Decimal("3000.00")

async def test_credit_limit_history_non_credit_account(
    db_session: AsyncSession
):
    """Test that credit limit history can't be created for non-credit accounts."""
    checking_account = Account(
        name="Test Checking",
        type="checking",
        available_balance=Decimal("1000.00"),
        created_at=datetime.now(ZoneInfo("UTC")),
        updated_at=datetime.now(ZoneInfo("UTC"))
    )
    db_session.add(checking_account)
    await db_session.commit()

    history = CreditLimitHistory(
        account_id=checking_account.id,
        credit_limit=Decimal("2000.00"),
        effective_date=datetime.now(ZoneInfo("UTC")),
        reason="Invalid credit limit"
    )
    db_session.add(history)
    
    # This should raise an error since checking accounts shouldn't have credit limits
    with pytest.raises(ValueError, match="Credit limit history can only be created for credit accounts"):
        await db_session.commit()
