from datetime import datetime, timedelta
from decimal import Decimal
from typing import AsyncGenerator

import pytest

from src.models.accounts import Account
from src.models.deposit_schedules import DepositSchedule
from src.models.income import Income
from src.schemas.deposit_schedules import (DepositScheduleCreate,
                                           DepositScheduleUpdate)
from src.services.deposit_schedules import DepositScheduleService


@pytest.fixture(scope="function")
async def deposit_schedule_service(
    db_session,
) -> AsyncGenerator[DepositScheduleService, None]:
    yield DepositScheduleService(db_session)


@pytest.fixture(scope="function")
async def test_account(db_session) -> AsyncGenerator[Account, None]:
    account = Account(
        name="Test Checking", type="checking", available_balance=Decimal("1000.00")
    )
    db_session.add(account)
    await db_session.commit()
    yield account


@pytest.fixture(scope="function")
async def test_income(db_session, test_account) -> AsyncGenerator[Income, None]:
    income = Income(
        date=datetime.utcnow(),
        source="Test Income",
        amount=Decimal("2000.00"),
        deposited=False,
        account_id=test_account.id,
    )
    db_session.add(income)
    await db_session.commit()
    yield income


@pytest.fixture(scope="function")
async def test_deposit_schedule(
    db_session, test_income, test_account
) -> AsyncGenerator[DepositSchedule, None]:
    schedule = DepositSchedule(
        income_id=test_income.id,
        account_id=test_account.id,
        schedule_date=datetime.utcnow() + timedelta(days=1),
        amount=Decimal("1000.00"),
        recurring=False,
        status="pending",
    )
    db_session.add(schedule)
    await db_session.commit()
    yield schedule


async def test_create_deposit_schedule(
    deposit_schedule_service: DepositScheduleService,
    test_income: Income,
    test_account: Account,
):
    schedule_data = DepositScheduleCreate(
        income_id=test_income.id,
        account_id=test_account.id,
        schedule_date=datetime.utcnow() + timedelta(days=1),
        amount=Decimal("1000.00"),
        recurring=False,
        status="pending",
    )
    success, error, schedule = await deposit_schedule_service.create_deposit_schedule(
        schedule_data
    )

    assert success is True
    assert error is None
    assert schedule is not None
    assert schedule.income_id == test_income.id
    assert schedule.account_id == test_account.id
    assert schedule.amount == Decimal("1000.00")


async def test_create_deposit_schedule_invalid_amount(
    deposit_schedule_service: DepositScheduleService,
    test_income: Income,
    test_account: Account,
):
    schedule_data = DepositScheduleCreate(
        income_id=test_income.id,
        account_id=test_account.id,
        schedule_date=datetime.utcnow() + timedelta(days=1),
        amount=Decimal("3000.00"),  # More than income amount
        recurring=False,
        status="pending",
    )
    success, error, schedule = await deposit_schedule_service.create_deposit_schedule(
        schedule_data
    )

    assert success is False
    assert error == "Schedule amount cannot exceed income amount"
    assert schedule is None


async def test_get_deposit_schedule(
    deposit_schedule_service: DepositScheduleService,
    test_deposit_schedule: DepositSchedule,
):
    schedule = await deposit_schedule_service.get_deposit_schedule(
        test_deposit_schedule.id
    )
    assert schedule is not None
    assert schedule.id == test_deposit_schedule.id


async def test_update_deposit_schedule(
    deposit_schedule_service: DepositScheduleService,
    test_deposit_schedule: DepositSchedule,
):
    update_data = DepositScheduleUpdate(amount=Decimal("500.00"), status="completed")
    success, error, updated_schedule = (
        await deposit_schedule_service.update_deposit_schedule(
            test_deposit_schedule.id, update_data
        )
    )

    assert success is True
    assert error is None
    assert updated_schedule is not None
    assert updated_schedule.amount == Decimal("500.00")
    assert updated_schedule.status == "completed"


async def test_delete_deposit_schedule(
    deposit_schedule_service: DepositScheduleService,
    test_deposit_schedule: DepositSchedule,
):
    success, error = await deposit_schedule_service.delete_deposit_schedule(
        test_deposit_schedule.id
    )
    assert success is True
    assert error is None

    # Verify deletion
    deleted_schedule = await deposit_schedule_service.get_deposit_schedule(
        test_deposit_schedule.id
    )
    assert deleted_schedule is None


async def test_list_deposit_schedules(
    deposit_schedule_service: DepositScheduleService,
    test_deposit_schedule: DepositSchedule,
):
    schedules = await deposit_schedule_service.list_deposit_schedules()
    assert len(schedules) > 0
    assert any(s.id == test_deposit_schedule.id for s in schedules)


async def test_get_pending_deposits(
    deposit_schedule_service: DepositScheduleService,
    test_deposit_schedule: DepositSchedule,
    test_account: Account,
):
    pending_deposits = await deposit_schedule_service.get_pending_deposits(
        test_account.id
    )
    assert len(pending_deposits) > 0
    assert any(d.id == test_deposit_schedule.id for d in pending_deposits)
