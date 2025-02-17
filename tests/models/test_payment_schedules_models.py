import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.base_model import naive_utc_from_date, naive_utc_now
from src.models.liabilities import Liability
from src.models.payment_schedules import PaymentSchedule

pytestmark = pytest.mark.asyncio


async def test_datetime_handling(
    db_session: AsyncSession,
    test_checking_account: Account,
    test_liability: Liability
):
    """Test proper datetime handling in PaymentSchedule model"""
    # Create payment_schedule with explicit datetime values
    payment_schedule = PaymentSchedule(
        liability_id=test_liability.id,
        account_id=test_checking_account.id,
        scheduled_date=naive_utc_from_date(2025, 3, 15),
        amount=1000.00,
        auto_process=True,
        created_at=naive_utc_from_date(2025, 3, 15),
        updated_at=naive_utc_from_date(2025, 3, 15)
    )

    db_session.add(payment_schedule)
    await db_session.commit()
    await db_session.refresh(payment_schedule)

    # Verify all datetime fields are naive (no tzinfo)
    assert payment_schedule.scheduled_date.tzinfo is None
    assert payment_schedule.created_at.tzinfo is None
    assert payment_schedule.updated_at.tzinfo is None

    # Verify scheduled_date components
    assert payment_schedule.scheduled_date.year == 2025
    assert payment_schedule.scheduled_date.month == 3
    assert payment_schedule.scheduled_date.day == 15
    assert payment_schedule.scheduled_date.hour == 0
    assert payment_schedule.scheduled_date.minute == 0
    assert payment_schedule.scheduled_date.second == 0

    # Verify created_at components
    assert payment_schedule.created_at.year == 2025
    assert payment_schedule.created_at.month == 3
    assert payment_schedule.created_at.day == 15
    assert payment_schedule.created_at.hour == 0
    assert payment_schedule.created_at.minute == 0
    assert payment_schedule.created_at.second == 0

    # Verify updated_at components
    assert payment_schedule.updated_at.year == 2025
    assert payment_schedule.updated_at.month == 3
    assert payment_schedule.updated_at.day == 15
    assert payment_schedule.updated_at.hour == 0
    assert payment_schedule.updated_at.minute == 0
    assert payment_schedule.updated_at.second == 0

async def test_default_datetime_handling(
    db_session: AsyncSession,
    test_checking_account: Account,
    test_liability: Liability
):
    """Test default datetime values are properly set"""
    payment_schedule = PaymentSchedule(
        liability_id=1,
        account_id=1,
        scheduled_date=naive_utc_now(),
        amount=1000.00,
        auto_process=True
    )

    db_session.add(payment_schedule)
    await db_session.commit()
    await db_session.refresh(payment_schedule)

    # Verify created_at and updated_at are set and naive
    assert payment_schedule.created_at is not None
    assert payment_schedule.updated_at is not None
    assert payment_schedule.created_at.tzinfo is None
    assert payment_schedule.updated_at.tzinfo is None

async def test_relationship_datetime_handling(
    db_session: AsyncSession,
    test_checking_account: Account,
    test_liability: Liability
):
    """Test datetime handling with relationships"""
    payment_schedule = PaymentSchedule(
        liability_id=test_liability.id,
        account_id=test_checking_account.id,
        scheduled_date=naive_utc_now(),
        amount=1000.00,
        auto_process=True
    )

    db_session.add(payment_schedule)
    await db_session.commit()

    # Refresh to load relationships
    await db_session.refresh(payment_schedule, ['liability', 'account'])

    # Verify datetime fields remain naive after refresh
    assert payment_schedule.scheduled_date.tzinfo is None
    assert payment_schedule.created_at.tzinfo is None
    assert payment_schedule.updated_at.tzinfo is None
