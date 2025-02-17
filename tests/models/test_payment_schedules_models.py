import pytest
from datetime import datetime
from src.models.payment_schedules import PaymentSchedule
from src.models.base_model import naive_utc_from_date, naive_utc_now

async def test_datetime_handling():
    """Test proper datetime handling in PaymentSchedule model"""
    # Create instance with explicit datetime values
    instance = PaymentSchedule(
        liability_id=1,
        account_id=1,
        scheduled_date=naive_utc_from_date(2025, 3, 15),
        amount=1000.00,
        auto_process=True,
        created_at=naive_utc_from_date(2025, 3, 15),
        updated_at=naive_utc_from_date(2025, 3, 15)
    )

    # Verify all datetime fields are naive (no tzinfo)
    assert instance.scheduled_date.tzinfo is None
    assert instance.created_at.tzinfo is None
    assert instance.updated_at.tzinfo is None

    # Verify scheduled_date components
    assert instance.scheduled_date.year == 2025
    assert instance.scheduled_date.month == 3
    assert instance.scheduled_date.day == 15
    assert instance.scheduled_date.hour == 0
    assert instance.scheduled_date.minute == 0
    assert instance.scheduled_date.second == 0

    # Verify created_at components
    assert instance.created_at.year == 2025
    assert instance.created_at.month == 3
    assert instance.created_at.day == 15
    assert instance.created_at.hour == 0
    assert instance.created_at.minute == 0
    assert instance.created_at.second == 0

    # Verify updated_at components
    assert instance.updated_at.year == 2025
    assert instance.updated_at.month == 3
    assert instance.updated_at.day == 15
    assert instance.updated_at.hour == 0
    assert instance.updated_at.minute == 0
    assert instance.updated_at.second == 0

async def test_default_datetime_handling():
    """Test default datetime values are properly set"""
    instance = PaymentSchedule(
        liability_id=1,
        account_id=1,
        scheduled_date=naive_utc_now(),
        amount=1000.00,
        auto_process=True
    )

    # Verify created_at and updated_at are set and naive
    assert instance.created_at is not None
    assert instance.updated_at is not None
    assert instance.created_at.tzinfo is None
    assert instance.updated_at.tzinfo is None

async def test_relationship_datetime_handling(db_session):
    """Test datetime handling with relationships"""
    instance = PaymentSchedule(
        liability_id=1,
        account_id=1,
        scheduled_date=naive_utc_now(),
        amount=1000.00,
        auto_process=True
    )
    db_session.add(instance)
    await db_session.commit()

    # Refresh to load relationships
    await db_session.refresh(instance, ['liability', 'account'])

    # Verify datetime fields remain naive after refresh
    assert instance.scheduled_date.tzinfo is None
    assert instance.created_at.tzinfo is None
    assert instance.updated_at.tzinfo is None
