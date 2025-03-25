"""
Integration tests for the DepositScheduleRepository.

This module contains tests for the DepositScheduleRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.

These tests verify CRUD operations and specialized methods for the
DepositScheduleRepository, ensuring proper validation flow and data integrity.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Dict, List, Optional, Tuple

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.deposit_schedules import DepositSchedule
from src.models.income import Income
from src.repositories.accounts import AccountRepository
from src.repositories.deposit_schedules import DepositScheduleRepository
from src.repositories.income import IncomeRepository
# Import schemas and schema factories - essential part of the validation pattern
from src.schemas.deposit_schedules import (DepositScheduleCreate,
                                           DepositScheduleUpdate)
from tests.helpers.datetime_utils import (datetime_equals,
                                          datetime_greater_than, utc_now)
from tests.helpers.schema_factories.accounts import create_account_schema
from tests.helpers.schema_factories.deposit_schedules import \
    create_deposit_schedule_schema
from tests.helpers.schema_factories.income import create_income_schema

pytestmark = pytest.mark.asyncio


async def test_create_deposit_schedule(
    deposit_schedule_repository: DepositScheduleRepository,
    test_income: Income,
    test_checking_account: Account,
):
    """Test creating a deposit schedule with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. SCHEMA: Create and validate through Pydantic schema
    schedule_date = datetime.now(timezone.utc) + timedelta(days=5)
    schedule_schema = create_deposit_schedule_schema(
        income_id=test_income.id,
        account_id=test_checking_account.id,
        schedule_date=schedule_date,
        amount=Decimal("2500.00"),
        recurring=True,
        recurrence_pattern={"frequency": "weekly", "day": "friday"},
        status="pending",
    )

    # Convert validated schema to dict for repository
    validated_data = schedule_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await deposit_schedule_repository.create(validated_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id is not None
    assert result.income_id == test_income.id
    assert result.account_id == test_checking_account.id
    assert result.amount == Decimal("2500.00")
    assert result.recurring is True
    assert result.recurrence_pattern == {"frequency": "weekly", "day": "friday"}
    assert result.status == "pending"
    assert result.created_at is not None
    assert result.updated_at is not None

    # Verify date is correct (accounting for potential timezone issues)
    result_date = result.schedule_date.replace(tzinfo=None)
    expected_date = schedule_date.replace(tzinfo=None)
    assert abs((result_date - expected_date).total_seconds()) < 60  # Within a minute


async def test_get_deposit_schedule(
    deposit_schedule_repository: DepositScheduleRepository,
    test_deposit_schedule: DepositSchedule,
):
    """Test retrieving a deposit schedule by ID."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get the deposit schedule
    result = await deposit_schedule_repository.get(test_deposit_schedule.id)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_deposit_schedule.id
    assert result.income_id == test_deposit_schedule.income_id
    assert result.account_id == test_deposit_schedule.account_id
    assert result.amount == test_deposit_schedule.amount
    assert result.status == test_deposit_schedule.status


async def test_update_deposit_schedule(
    deposit_schedule_repository: DepositScheduleRepository,
    test_deposit_schedule: DepositSchedule,
):
    """Test updating a deposit schedule with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures

    # Store original timestamp before update
    original_updated_at = test_deposit_schedule.updated_at

    # 2. SCHEMA: Create and validate update data through Pydantic schema
    new_schedule_date = datetime.now(timezone.utc) + timedelta(days=10)
    update_schema = DepositScheduleUpdate(
        schedule_date=new_schedule_date,
        amount=Decimal("3500.00"),
        recurring=True,
        recurrence_pattern={"frequency": "monthly", "day": 1},
    )

    # Convert validated schema to dict for repository
    update_data = update_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await deposit_schedule_repository.update(
        test_deposit_schedule.id, update_data
    )

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_deposit_schedule.id
    assert result.amount == Decimal("3500.00")
    assert result.recurring is True
    assert result.recurrence_pattern == {"frequency": "monthly", "day": 1}

    # Verify date is updated correctly
    result_date = result.schedule_date.replace(tzinfo=None)
    expected_date = new_schedule_date.replace(tzinfo=None)
    assert abs((result_date - expected_date).total_seconds()) < 60  # Within a minute

    assert datetime_greater_than(
        result.updated_at, original_updated_at, ignore_timezone=True
    )


async def test_delete_deposit_schedule(
    deposit_schedule_repository: DepositScheduleRepository,
    test_deposit_schedule: DepositSchedule,
):
    """Test deleting a deposit schedule."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Delete the deposit schedule
    result = await deposit_schedule_repository.delete(test_deposit_schedule.id)

    # 4. ASSERT: Verify the operation results
    assert result is True

    # Verify it's actually deleted
    deleted_schedule = await deposit_schedule_repository.get(test_deposit_schedule.id)
    assert deleted_schedule is None
