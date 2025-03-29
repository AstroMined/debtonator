from datetime import datetime
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.credit_limit_history import CreditLimitHistory
from src.utils.datetime_utils import naive_utc_from_date, naive_utc_now

pytestmark = pytest.mark.asyncio


async def test_create_credit_limit_history(
    db_session: AsyncSession, test_credit_account: Account
):
    """Test creating a credit limit history record."""
    history = CreditLimitHistory(
        account_id=test_credit_account.id,
        credit_limit=Decimal("2000.00"),
        effective_date=naive_utc_now(),
        reason="Initial credit limit",
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
    db_session: AsyncSession, test_credit_account: Account
):
    """Test credit limit history relationships."""
    history = CreditLimitHistory(
        account_id=test_credit_account.id,
        credit_limit=Decimal("2000.00"),
        effective_date=naive_utc_now(),
        reason="Initial credit limit",
    )
    db_session.add(history)
    await db_session.commit()
    await db_session.refresh(history)

    # Refresh test_credit_account to load specific relationship
    await db_session.refresh(test_credit_account, ["credit_limit_history"])

    # Test account relationship
    assert history.account is not None
    assert history.account.id == test_credit_account.id
    assert history.account.name == test_credit_account.name

    # Test relationship from account side
    assert history in test_credit_account.credit_limit_history


async def test_credit_limit_history_string_representation(
    db_session: AsyncSession, test_credit_account: Account
):
    """Test the string representation of a credit limit history record."""
    history = CreditLimitHistory(
        account_id=test_credit_account.id,
        credit_limit=Decimal("2000.00"),
        effective_date=naive_utc_now(),
        reason="Initial credit limit",
    )
    db_session.add(history)
    await db_session.commit()

    expected_str = (
        f"<CreditLimitHistory account_id={test_credit_account.id} limit=2000.00>"
    )
    assert str(history) == expected_str
    assert repr(history) == expected_str


async def test_credit_limit_history_cascade_delete(
    db_session: AsyncSession, test_credit_account: Account
):
    """Test that credit limit history records are deleted when account is deleted."""
    history = CreditLimitHistory(
        account_id=test_credit_account.id,
        credit_limit=Decimal("2000.00"),
        effective_date=naive_utc_now(),
        reason="Initial credit limit",
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
    db_session: AsyncSession, test_credit_account: Account
):
    """Test recording multiple credit limit changes for an account."""
    # Initial limit
    history1 = CreditLimitHistory(
        account_id=test_credit_account.id,
        credit_limit=Decimal("2000.00"),
        effective_date=naive_utc_now(),
        reason="Initial credit limit",
    )
    db_session.add(history1)
    await db_session.commit()

    # Increase limit
    history2 = CreditLimitHistory(
        account_id=test_credit_account.id,
        credit_limit=Decimal("3000.00"),
        effective_date=naive_utc_now(),
        reason="Credit limit increase",
    )
    db_session.add(history2)
    await db_session.commit()

    # Refresh test_credit_account to load specific relationship
    await db_session.refresh(test_credit_account, ["credit_limit_history"])

    # Verify both records exist and are correctly ordered
    assert len(test_credit_account.credit_limit_history) == 2
    assert test_credit_account.credit_limit_history[0].credit_limit == Decimal(
        "2000.00"
    )
    assert test_credit_account.credit_limit_history[1].credit_limit == Decimal(
        "3000.00"
    )


async def test_credit_limit_history_creation(
    db_session: AsyncSession, test_checking_account: Account
):
    """Test that credit limit history can be created without model-level validation."""

    # Without the SQLAlchemy event listener, we can create a history record
    # for a non-credit account at the model level (service layer will handle validation)
    history = CreditLimitHistory(
        account_id=test_checking_account.id,
        credit_limit=Decimal("2000.00"),
        effective_date=naive_utc_now(),
        reason="Test credit limit",
    )
    db_session.add(history)
    await db_session.commit()
    await db_session.refresh(history)

    # Verify the record was created
    assert history.id is not None
    assert history.account_id == test_checking_account.id

    # This confirms that model layer doesn't enforce validation anymore
    # The validation is now handled by the AccountService.validate_credit_limit_history method


async def test_datetime_handling(
    db_session: AsyncSession, test_credit_account: Account
):
    """Test proper datetime handling in credit limit history"""
    # Create history with explicit datetime values
    history = CreditLimitHistory(
        account_id=test_credit_account.id,
        credit_limit=Decimal("2000.00"),
        effective_date=naive_utc_from_date(2025, 3, 15),
        reason="Test credit limit",
    )
    db_session.add(history)
    await db_session.commit()
    await db_session.refresh(history)

    # Verify all datetime fields are naive (no tzinfo)
    assert history.effective_date.tzinfo is None
    assert history.created_at.tzinfo is None
    assert history.updated_at.tzinfo is None

    # Verify effective_date components
    assert history.effective_date.year == 2025
    assert history.effective_date.month == 3
    assert history.effective_date.day == 15
    assert history.effective_date.hour == 0
    assert history.effective_date.minute == 0
    assert history.effective_date.second == 0
