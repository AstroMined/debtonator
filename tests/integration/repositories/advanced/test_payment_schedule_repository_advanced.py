"""
Integration tests for the PaymentScheduleRepository.

This module contains tests for the PaymentScheduleRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.

These tests verify CRUD operations and specialized methods for the
PaymentScheduleRepository, ensuring proper validation flow and relationship
loading.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Optional

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.liabilities import Liability, LiabilityStatus
from src.models.payment_schedules import PaymentSchedule
from src.repositories.accounts import AccountRepository
from src.repositories.liabilities import LiabilityRepository
from src.repositories.payment_schedules import PaymentScheduleRepository
# Import schemas and schema factories - essential part of the validation pattern
from src.schemas.payment_schedules import (PaymentScheduleCreate,
                                           PaymentScheduleUpdate)
from tests.helpers.schema_factories.accounts import create_account_schema
from tests.helpers.schema_factories.liabilities import create_liability_schema
from tests.helpers.schema_factories.payment_schedules import (
    create_payment_schedule_schema, create_payment_schedule_update_schema)

pytestmark = pytest.mark.asyncio


async def test_create_payment_schedule(
    payment_schedule_repository: PaymentScheduleRepository,
    test_liability: Liability,
    test_checking_account: Account,
):
    """Test creating a payment schedule with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. SCHEMA: Create and validate through Pydantic schema
    scheduled_date = datetime.now(timezone.utc) + timedelta(days=10)
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
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

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

    # 2. SCHEMA: Create and validate update data through Pydantic schema
    new_scheduled_date = datetime.now(timezone.utc) + timedelta(days=15)
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

    # Convert the timezone-aware date to naive for comparison with database result
    db_date = result.scheduled_date.replace(tzinfo=None)
    expected_date = new_scheduled_date.replace(tzinfo=None)
    assert abs((db_date - expected_date).total_seconds()) < 60  # Within a minute

    assert result.updated_at > test_payment_schedule.updated_at


async def test_delete_payment_schedule(
    payment_schedule_repository: PaymentScheduleRepository,
    test_payment_schedule: PaymentSchedule,
):
    """Test deleting a payment schedule."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Delete the payment schedule
    result = await payment_schedule_repository.delete(test_payment_schedule.id)

    # 4. ASSERT: Verify the operation results
    assert result is True

    # Verify it's actually deleted
    deleted_schedule = await payment_schedule_repository.get(test_payment_schedule.id)
    assert deleted_schedule is None


async def test_get_by_account(
    payment_schedule_repository: PaymentScheduleRepository,
    test_checking_account: Account,
    test_multiple_schedules: List[PaymentSchedule],
):
    """Test getting payment schedules for a specific account."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get payment schedules for the account
    results = await payment_schedule_repository.get_by_account(test_checking_account.id)

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 3  # Should get at least 3 schedules for this account
    for schedule in results:
        assert schedule.account_id == test_checking_account.id


async def test_get_by_liability(
    payment_schedule_repository: PaymentScheduleRepository,
    test_liability: Liability,
    test_multiple_schedules: List[PaymentSchedule],
):
    """Test getting payment schedules for a specific liability."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get payment schedules for the liability
    results = await payment_schedule_repository.get_by_liability(test_liability.id)

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 4  # Should get at least 4 schedules for this liability
    for schedule in results:
        assert schedule.liability_id == test_liability.id


async def test_get_with_account(
    payment_schedule_repository: PaymentScheduleRepository,
    test_payment_schedule: PaymentSchedule,
):
    """Test getting a payment schedule with account relationship loaded."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get the payment schedule with account
    result = await payment_schedule_repository.get_with_account(
        test_payment_schedule.id
    )

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_payment_schedule.id
    assert result.account is not None
    assert result.account.id == test_payment_schedule.account_id
    assert result.account.name is not None


async def test_get_with_liability(
    payment_schedule_repository: PaymentScheduleRepository,
    test_payment_schedule: PaymentSchedule,
):
    """Test getting a payment schedule with liability relationship loaded."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get the payment schedule with liability
    result = await payment_schedule_repository.get_with_liability(
        test_payment_schedule.id
    )

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_payment_schedule.id
    assert result.liability is not None
    assert result.liability.id == test_payment_schedule.liability_id
    assert result.liability.name is not None


async def test_get_by_date_range(
    payment_schedule_repository: PaymentScheduleRepository,
    test_multiple_schedules: List[PaymentSchedule],
):
    """Test getting payment schedules within a date range."""
    # 1. ARRANGE: Setup date range
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=1)
    end_date = now + timedelta(days=10)

    # 2. SCHEMA: Not needed for this query-only operation

    # 3. ACT: Get payment schedules within date range
    results = await payment_schedule_repository.get_by_date_range(start_date, end_date)

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 2  # Should get at least 2 schedules in this range
    for schedule in results:
        # Convert the timezone-aware dates to naive for comparison with database values
        naive_start_date = start_date.replace(tzinfo=None)
        naive_end_date = end_date.replace(tzinfo=None)
        naive_schedule_date = schedule.scheduled_date

        assert naive_schedule_date >= naive_start_date
        assert naive_schedule_date <= naive_end_date


async def test_get_pending_schedules(
    payment_schedule_repository: PaymentScheduleRepository,
    test_multiple_schedules: List[PaymentSchedule],
):
    """Test getting pending payment schedules."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get pending payment schedules
    results = await payment_schedule_repository.get_pending_schedules()

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 4  # Should get at least 4 pending schedules
    for schedule in results:
        assert schedule.processed is False
        assert schedule.processed_date is None


async def test_get_processed_schedules(
    payment_schedule_repository: PaymentScheduleRepository,
    test_multiple_schedules: List[PaymentSchedule],
):
    """Test getting processed payment schedules."""
    # 1. ARRANGE: Mark one schedule as processed
    test_schedule = test_multiple_schedules[0]
    process_time = datetime.now(timezone.utc)

    # Use the repository method to mark as processed
    update_schema = create_payment_schedule_update_schema(
        processed=True,
        # Note: processed_date will be set by the mark_as_processed method
    )

    await payment_schedule_repository.mark_as_processed(test_schedule.id, process_time)

    # 3. ACT: Get processed payment schedules
    results = await payment_schedule_repository.get_processed_schedules()

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 1  # Should get at least 1 processed schedule
    assert any(s.id == test_schedule.id for s in results)
    for schedule in results:
        assert schedule.processed is True
        assert schedule.processed_date is not None


async def test_mark_as_processed(
    payment_schedule_repository: PaymentScheduleRepository,
    test_payment_schedule: PaymentSchedule,
):
    """Test marking a payment schedule as processed."""
    # 1. ARRANGE: Set up processing date
    process_time = datetime.now(timezone.utc)

    # 2. SCHEMA: Not needed for this method as it uses ID and optional datetime

    # 3. ACT: Mark the payment schedule as processed
    result = await payment_schedule_repository.mark_as_processed(
        test_payment_schedule.id, process_time
    )

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_payment_schedule.id
    assert result.processed is True
    assert result.processed_date is not None

    # Convert to naive datetime for comparison
    db_processed_date = result.processed_date.replace(tzinfo=None)
    expected_processed_date = process_time.replace(tzinfo=None)
    assert abs((db_processed_date - expected_processed_date).total_seconds()) < 60


async def test_get_schedules_with_relationships(
    payment_schedule_repository: PaymentScheduleRepository,
    test_multiple_schedules: List[PaymentSchedule],
):
    """Test getting payment schedules with all relationships loaded."""
    # 1. ARRANGE: Set up date range
    now = datetime.now(timezone.utc)
    date_range = (now - timedelta(days=10), now + timedelta(days=20))

    # 2. SCHEMA: Not needed for this query-only operation

    # 3. ACT: Get payment schedules with relationships
    results = await payment_schedule_repository.get_schedules_with_relationships(
        date_range
    )

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 3  # Should get at least 3 schedules in this range
    for schedule in results:
        assert schedule.account is not None
        assert schedule.liability is not None
        assert schedule.account.id == schedule.account_id
        assert schedule.liability.id == schedule.liability_id


async def test_get_upcoming_schedules(
    payment_schedule_repository: PaymentScheduleRepository,
    test_multiple_schedules: List[PaymentSchedule],
    test_checking_account: Account,
):
    """Test getting upcoming payment schedules."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get upcoming payment schedules for next 7 days
    results = await payment_schedule_repository.get_upcoming_schedules(
        days=7, account_id=test_checking_account.id
    )

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 1  # Should get at least 1 upcoming schedule
    for schedule in results:
        assert schedule.account_id == test_checking_account.id
        assert schedule.processed is False

        # Schedule date should be in the future and within 7 days
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        assert schedule.scheduled_date >= now
        assert schedule.scheduled_date <= (now + timedelta(days=7))

        # Relationships should be loaded
        assert schedule.account is not None
        assert schedule.liability is not None


async def test_find_overdue_schedules(
    payment_schedule_repository: PaymentScheduleRepository,
    test_multiple_schedules: List[PaymentSchedule],
):
    """Test finding overdue payment schedules."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Find overdue payment schedules
    results = await payment_schedule_repository.find_overdue_schedules()

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 1  # Should get at least 1 overdue schedule
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    for schedule in results:
        assert schedule.processed is False
        assert schedule.scheduled_date < now

        # Relationships should be loaded
        assert schedule.account is not None
        assert schedule.liability is not None


async def test_get_auto_process_schedules(
    payment_schedule_repository: PaymentScheduleRepository,
    test_multiple_schedules: List[PaymentSchedule],
):
    """Test getting payment schedules set for auto-processing."""
    # 1. ARRANGE: Set up date range
    now = datetime.now(timezone.utc)
    date_range = (now - timedelta(days=1), now + timedelta(days=30))

    # 2. SCHEMA: Not needed for this query-only operation

    # 3. ACT: Get auto-process payment schedules
    results = await payment_schedule_repository.get_auto_process_schedules(date_range)

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 2  # Should get at least 2 auto-process schedules
    for schedule in results:
        assert schedule.auto_process is True
        assert schedule.processed is False

        # Relationships should be loaded
        assert schedule.account is not None
        assert schedule.liability is not None


async def test_get_total_scheduled_payments(
    payment_schedule_repository: PaymentScheduleRepository,
    test_multiple_schedules: List[PaymentSchedule],
    test_checking_account: Account,
):
    """Test calculating total amount of scheduled payments."""
    # 1. ARRANGE: Set up date range
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=10)
    end_date = now + timedelta(days=20)

    # 2. SCHEMA: Not needed for this calculation operation

    # 3. ACT: Get total scheduled payments for account
    total = await payment_schedule_repository.get_total_scheduled_payments(
        start_date, end_date, test_checking_account.id
    )

    # 4. ASSERT: Verify the operation results
    assert total > 0  # Should have at least some scheduled payments

    # Calculate expected total manually for verification
    expected_total = sum(
        float(s.amount)
        for s in test_multiple_schedules
        if (
            s.account_id == test_checking_account.id
            and s.scheduled_date >= start_date.replace(tzinfo=None)
            and s.scheduled_date <= end_date.replace(tzinfo=None)
        )
    )
    assert total == pytest.approx(expected_total, abs=0.01)


async def test_cancel_schedule(
    payment_schedule_repository: PaymentScheduleRepository,
    test_payment_schedule: PaymentSchedule,
):
    """Test cancelling a payment schedule."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Cancel the payment schedule
    result = await payment_schedule_repository.cancel_schedule(test_payment_schedule.id)

    # 4. ASSERT: Verify the operation results
    assert result is True

    # Verify it's actually deleted
    cancelled_schedule = await payment_schedule_repository.get(test_payment_schedule.id)
    assert cancelled_schedule is None


async def test_validation_error_handling(
    payment_schedule_repository: PaymentScheduleRepository,
    test_liability: Liability,
    test_checking_account: Account,
):
    """Test handling invalid data that would normally be caught by schema validation."""
    # Try creating a schema with invalid data and expect it to fail validation
    try:
        invalid_schema = PaymentScheduleCreate(
            liability_id=test_liability.id,
            account_id=test_checking_account.id,
            scheduled_date=datetime.now(timezone.utc),
            amount=Decimal("-50.00"),  # Invalid negative amount
            description="Test validation",
        )
        assert False, "Schema should have raised a validation error for negative amount"
    except ValueError as e:
        # This is expected - schema validation should catch the error
        assert "amount" in str(e).lower() and "greater than" in str(e).lower()
