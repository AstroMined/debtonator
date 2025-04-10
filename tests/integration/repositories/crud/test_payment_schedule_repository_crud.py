"""
Integration tests for the PaymentScheduleRepository.

This module contains tests for the PaymentScheduleRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.
"""

# pylint: disable=no-member

from decimal import Decimal

import pytest

from src.models.accounts import Account
from src.models.liabilities import Liability
from src.models.payment_schedules import PaymentSchedule
from src.repositories.payment_schedules import PaymentScheduleRepository
from src.utils.datetime_utils import datetime_greater_than, days_from_now
from tests.helpers.schema_factories.payment_schedules_schema_factories import (
    create_payment_schedule_schema,
    create_payment_schedule_update_schema,
)

pytestmark = pytest.mark.asyncio


async def test_create_payment_schedule(
    payment_schedule_repository: PaymentScheduleRepository,
    test_liability: Liability,
    test_checking_account: Account,
):
    """Test creating a payment schedule with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures
    scheduled_date = days_from_now(10)

    # 2. SCHEMA: Create and validate through Pydantic schema
    schedule_schema = create_payment_schedule_schema(
        liability_id=test_liability.id,
        account_id=test_checking_account.id,
        amount=Decimal("250.00"),
        scheduled_date=scheduled_date,
        description="Test payment creation",
        auto_process=True,
    )

    # Convert validated schema to dict for repository
    validated_data = schedule_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await payment_schedule_repository.create(validated_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id is not None
    assert result.liability_id == test_liability.id
    assert result.account_id == test_checking_account.id
    assert result.amount == Decimal("250.00")
    assert result.description == "Test payment creation"
    assert result.auto_process is True
    assert result.processed is False
    assert result.processed_date is None
    assert result.created_at is not None
    assert result.updated_at is not None


async def test_get_payment_schedule(
    payment_schedule_repository: PaymentScheduleRepository,
    test_payment_schedule: PaymentSchedule,
):
    """Test retrieving a payment schedule by ID."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. SCHEMA: No schema needed for get operation

    # 3. ACT: Get the payment schedule
    result = await payment_schedule_repository.get(test_payment_schedule.id)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_payment_schedule.id
    assert result.liability_id == test_payment_schedule.liability_id
    assert result.account_id == test_payment_schedule.account_id
    assert result.amount == test_payment_schedule.amount
    assert result.description == test_payment_schedule.description
    assert result.scheduled_date is not None


async def test_update_payment_schedule(
    payment_schedule_repository: PaymentScheduleRepository,
    test_payment_schedule: PaymentSchedule,
):
    """Test updating a payment schedule with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures
    # Store original timestamp before update
    original_updated_at = test_payment_schedule.updated_at
    new_scheduled_date = days_from_now(15)

    # 2. SCHEMA: Create and validate update data through Pydantic schema
    update_schema = create_payment_schedule_update_schema(
        scheduled_date=new_scheduled_date,
        amount=Decimal("225.00"),
        description="Updated payment description",
    )

    # Convert validated schema to dict for repository
    update_data = update_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await payment_schedule_repository.update(
        test_payment_schedule.id, update_data
    )

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_payment_schedule.id
    assert result.amount == Decimal("225.00")
    assert result.description == "Updated payment description"

    # Compare dates with proper timezone handling
    db_date = result.scheduled_date.replace(tzinfo=None)
    expected_date = new_scheduled_date.replace(tzinfo=None)
    assert abs((db_date - expected_date).total_seconds()) < 60  # Within a minute

    assert datetime_greater_than(
        result.updated_at, original_updated_at, ignore_timezone=True
    )


async def test_delete_payment_schedule(
    payment_schedule_repository: PaymentScheduleRepository,
    test_payment_schedule: PaymentSchedule,
):
    """Test deleting a payment schedule."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. SCHEMA: No schema needed for delete operation

    # 3. ACT: Delete the payment schedule
    result = await payment_schedule_repository.delete(test_payment_schedule.id)

    # 4. ASSERT: Verify the operation results
    assert result is True

    # Verify it's actually deleted
    deleted_schedule = await payment_schedule_repository.get(test_payment_schedule.id)
    assert deleted_schedule is None
