import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.balance_history import BalanceHistory
from src.models.base_model import naive_utc_from_date, naive_utc_now

pytestmark = pytest.mark.asyncio


async def test_datetime_handling(
    db_session: AsyncSession, test_checking_account: Account
):
    """Test proper datetime handling in BalanceHistory model"""
    # Create instance with explicit datetime values
    balance_history = BalanceHistory(
        account_id=test_checking_account.id,
        balance=1000.00,
        timestamp=naive_utc_from_date(2025, 3, 15),
        created_at=naive_utc_from_date(2025, 3, 15),
        updated_at=naive_utc_from_date(2025, 3, 15),
    )

    db_session.add(balance_history)
    await db_session.commit()
    await db_session.refresh(balance_history)

    # Verify all datetime fields are naive (no tzinfo)
    assert balance_history.timestamp.tzinfo is None
    assert balance_history.created_at.tzinfo is None
    assert balance_history.updated_at.tzinfo is None

    # Verify timestamp components
    assert balance_history.timestamp.year == 2025
    assert balance_history.timestamp.month == 3
    assert balance_history.timestamp.day == 15
    assert balance_history.timestamp.hour == 0
    assert balance_history.timestamp.minute == 0
    assert balance_history.timestamp.second == 0

    # Verify created_at components
    assert balance_history.created_at.year == 2025
    assert balance_history.created_at.month == 3
    assert balance_history.created_at.day == 15
    assert balance_history.created_at.hour == 0
    assert balance_history.created_at.minute == 0
    assert balance_history.created_at.second == 0

    # Verify updated_at components
    assert balance_history.updated_at.year == 2025
    assert balance_history.updated_at.month == 3
    assert balance_history.updated_at.day == 15
    assert balance_history.updated_at.hour == 0
    assert balance_history.updated_at.minute == 0
    assert balance_history.updated_at.second == 0


async def test_default_datetime_handling(
    db_session: AsyncSession, test_checking_account: Account
):
    """Test default datetime values are properly set"""
    balance_history = BalanceHistory(
        account_id=test_checking_account.id, balance=1000.00, timestamp=naive_utc_now()
    )

    db_session.add(balance_history)
    await db_session.commit()
    await db_session.refresh(balance_history)

    # Verify created_at and updated_at are set and naive
    assert balance_history.created_at is not None
    assert balance_history.updated_at is not None
    assert balance_history.created_at.tzinfo is None
    assert balance_history.updated_at.tzinfo is None


async def test_relationship_datetime_handling(db_session):
    """Test datetime handling with relationships"""
    balance_history = BalanceHistory(
        account_id=1, balance=1000.00, timestamp=naive_utc_now()
    )
    db_session.add(balance_history)
    await db_session.commit()

    # Refresh to load relationships
    await db_session.refresh(balance_history, ["account"])

    # Verify datetime fields remain naive after refresh
    assert balance_history.timestamp.tzinfo is None
    assert balance_history.created_at.tzinfo is None
    assert balance_history.updated_at.tzinfo is None
