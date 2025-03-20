from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.base_model import naive_utc_from_date, naive_utc_now
from src.models.deposit_schedules import DepositSchedule
from src.models.income import Income

pytestmark = pytest.mark.asyncio


async def test_datetime_handling(
    db_session: AsyncSession, test_income_record: Income, test_checking_account: Account
):
    """Test proper datetime handling in DepositSchedule model"""
    # Create deposit_schedule with explicit datetime values
    deposit_schedule = DepositSchedule(
        income_id=test_income_record.id,
        account_id=test_checking_account.id,
        schedule_date=naive_utc_from_date(2025, 3, 15),
        amount=1000.00,
        recurring=True,
        created_at=naive_utc_from_date(2025, 3, 15),
        updated_at=naive_utc_from_date(2025, 3, 15),
    )

    db_session.add(deposit_schedule)
    await db_session.commit()
    await db_session.refresh(deposit_schedule)

    # Verify all datetime fields are naive (no tzinfo)
    assert deposit_schedule.schedule_date.tzinfo is None
    assert deposit_schedule.created_at.tzinfo is None
    assert deposit_schedule.updated_at.tzinfo is None

    # Verify schedule_date components
    assert deposit_schedule.schedule_date.year == 2025
    assert deposit_schedule.schedule_date.month == 3
    assert deposit_schedule.schedule_date.day == 15
    assert deposit_schedule.schedule_date.hour == 0
    assert deposit_schedule.schedule_date.minute == 0
    assert deposit_schedule.schedule_date.second == 0

    # Verify created_at components
    assert deposit_schedule.created_at.year == 2025
    assert deposit_schedule.created_at.month == 3
    assert deposit_schedule.created_at.day == 15
    assert deposit_schedule.created_at.hour == 0
    assert deposit_schedule.created_at.minute == 0
    assert deposit_schedule.created_at.second == 0

    # Verify updated_at components
    assert deposit_schedule.updated_at.year == 2025
    assert deposit_schedule.updated_at.month == 3
    assert deposit_schedule.updated_at.day == 15
    assert deposit_schedule.updated_at.hour == 0
    assert deposit_schedule.updated_at.minute == 0
    assert deposit_schedule.updated_at.second == 0


async def test_default_datetime_handling(
    db_session: AsyncSession, test_income_record: Income, test_checking_account: Account
):
    """Test default datetime values are properly set"""
    deposit_schedule = DepositSchedule(
        income_id=test_income_record.id,
        account_id=test_checking_account.id,
        schedule_date=naive_utc_now(),
        amount=1000.00,
        recurring=True,
    )

    db_session.add(deposit_schedule)
    await db_session.commit()
    await db_session.refresh(deposit_schedule)

    # Verify created_at and updated_at are set and naive
    assert deposit_schedule.created_at is not None
    assert deposit_schedule.updated_at is not None
    assert deposit_schedule.created_at.tzinfo is None
    assert deposit_schedule.updated_at.tzinfo is None


async def test_model_relationships(
    db_session: AsyncSession, test_income_record: Income, test_checking_account: Account
):
    """Test relationships between models"""
    deposit_schedule = DepositSchedule(
        income_id=test_income_record.id,
        account_id=test_checking_account.id,
        schedule_date=naive_utc_now(),
        amount=1000.00,
        recurring=True,
    )
    db_session.add(deposit_schedule)
    await db_session.commit()

    # Refresh to load relationships
    await db_session.refresh(deposit_schedule, ["income", "account"])

    # Verify relationships are properly loaded
    assert deposit_schedule.income is not None
    assert deposit_schedule.income.id == test_income_record.id
    assert deposit_schedule.account is not None
    assert deposit_schedule.account.id == test_checking_account.id

    # Verify datetime fields remain naive after refresh
    assert deposit_schedule.schedule_date.tzinfo is None
    assert deposit_schedule.created_at.tzinfo is None
    assert deposit_schedule.updated_at.tzinfo is None
