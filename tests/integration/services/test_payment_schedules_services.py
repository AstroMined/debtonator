from datetime import datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy import select

from src.models.accounts import Account
from src.models.liabilities import Liability
from src.models.payment_schedules import PaymentSchedule
from src.schemas.payment_schedules import PaymentScheduleCreate
from src.services.payment_schedules import PaymentScheduleService


@pytest.fixture(scope="function")
async def test_account(db_session):
    account = Account(
        name="Test Account",
        type="checking",
        available_balance=Decimal("1000.00"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(account)
    await db_session.commit()
    return account


@pytest.fixture(scope="function")
async def test_liability(db_session, test_account, test_category):
    liability = Liability(
        name="Test Bill",
        amount=Decimal("100.00"),
        due_date=datetime.utcnow() + timedelta(days=7),
        category_id=test_category.id,
        primary_account_id=test_account.id,
        auto_pay=False,
        auto_pay_enabled=False,
        paid=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(liability)
    await db_session.commit()
    return liability


@pytest.fixture(scope="function")
async def test_schedule(db_session, test_liability, test_account):
    schedule = PaymentSchedule(
        liability_id=test_liability.id,
        account_id=test_account.id,
        scheduled_date=datetime.utcnow() + timedelta(days=5),
        amount=Decimal("100.00"),
        description="Test schedule",
        auto_process=False,
        processed=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(schedule)
    await db_session.commit()
    return schedule


async def test_create_schedule(db_session, test_liability, test_account):
    service = PaymentScheduleService(db_session)
    schedule_data = PaymentScheduleCreate(
        liability_id=test_liability.id,
        account_id=test_account.id,
        scheduled_date=datetime.utcnow() + timedelta(days=5),
        amount=100.00,
        description="Test schedule",
    )

    schedule = await service.create_schedule(schedule_data)
    assert schedule.liability_id == test_liability.id
    assert schedule.account_id == test_account.id
    assert schedule.amount == Decimal("100.00")
    assert not schedule.processed


async def test_create_schedule_paid_liability(db_session, test_liability, test_account):
    # Mark liability as paid
    test_liability.paid = True
    await db_session.commit()

    service = PaymentScheduleService(db_session)
    schedule_data = PaymentScheduleCreate(
        liability_id=test_liability.id,
        account_id=test_account.id,
        scheduled_date=datetime.utcnow() + timedelta(days=5),
        amount=100.00,
    )

    with pytest.raises(
        ValueError, match="Cannot schedule payment for already paid liability"
    ):
        await service.create_schedule(schedule_data)


async def test_get_schedule(db_session, test_schedule):
    service = PaymentScheduleService(db_session)
    schedule = await service.get_schedule(test_schedule.id)
    assert schedule is not None
    assert schedule.id == test_schedule.id


async def test_get_schedules_by_date_range(db_session, test_schedule):
    service = PaymentScheduleService(db_session)
    start_date = datetime.utcnow()
    end_date = datetime.utcnow() + timedelta(days=7)

    schedules = await service.get_schedules_by_date_range(start_date, end_date)
    assert len(schedules) == 1
    assert schedules[0].id == test_schedule.id


async def test_get_schedules_by_liability(db_session, test_schedule, test_liability):
    service = PaymentScheduleService(db_session)
    schedules = await service.get_schedules_by_liability(test_liability.id)
    assert len(schedules) == 1
    assert schedules[0].id == test_schedule.id


async def test_process_schedule(db_session, test_schedule):
    service = PaymentScheduleService(db_session)
    processed_schedule = await service.process_schedule(test_schedule.id)

    assert processed_schedule.processed
    assert processed_schedule.processed_date is not None

    # Verify payment was created
    result = await db_session.execute(
        select(PaymentSchedule).where(PaymentSchedule.id == test_schedule.id)
    )
    schedule = result.scalar_one()
    assert schedule.processed


async def test_process_already_processed_schedule(db_session, test_schedule):
    # Mark schedule as processed
    test_schedule.processed = True
    test_schedule.processed_date = datetime.utcnow()
    await db_session.commit()

    service = PaymentScheduleService(db_session)
    with pytest.raises(ValueError, match="Schedule already processed"):
        await service.process_schedule(test_schedule.id)


async def test_delete_schedule(db_session, test_schedule):
    service = PaymentScheduleService(db_session)
    success = await service.delete_schedule(test_schedule.id)
    assert success

    result = await db_session.execute(
        select(PaymentSchedule).where(PaymentSchedule.id == test_schedule.id)
    )
    assert result.scalar_one_or_none() is None


async def test_delete_processed_schedule(db_session, test_schedule):
    # Mark schedule as processed
    test_schedule.processed = True
    test_schedule.processed_date = datetime.utcnow()
    await db_session.commit()

    service = PaymentScheduleService(db_session)
    with pytest.raises(ValueError, match="Cannot delete processed schedule"):
        await service.delete_schedule(test_schedule.id)


async def test_process_due_schedules(db_session, test_schedule):
    # Set schedule to auto-process and due today
    test_schedule.auto_process = True
    test_schedule.scheduled_date = datetime.utcnow()
    await db_session.commit()

    service = PaymentScheduleService(db_session)
    processed_schedules = await service.process_due_schedules()

    assert len(processed_schedules) == 1
    assert processed_schedules[0].id == test_schedule.id
    assert processed_schedules[0].processed
