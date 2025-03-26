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
from src.schemas.payment_schedules import (PaymentScheduleCreate,
                                           PaymentScheduleUpdate)
from tests.helpers.schema_factories.accounts import create_account_schema
from tests.helpers.schema_factories.liabilities import create_liability_schema
from tests.helpers.schema_factories.payment_schedules import (
    create_payment_schedule_schema, create_payment_schedule_update_schema)
from src.utils.datetime_utils import (utc_now, days_from_now, days_ago,
                                          datetime_equals, datetime_greater_than)

pytestmark = pytest.mark.asyncio


async def test_get_by_account(
    payment_schedule_repository: PaymentScheduleRepository,
    test_checking_account: Account,
    test_multiple_payment_schedules: List[PaymentSchedule],
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
    test_multiple_payment_schedules: List[PaymentSchedule],
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
    test_multiple_payment_schedules: List[PaymentSchedule],
):
    """Test getting payment schedules within a date range."""
    # 1. ARRANGE: Setup date range
    now = utc_now()
    start_date = now - timedelta(days=5)  # Expanded range to catch more test data
    end_date = now + timedelta(days=15)   # Expanded range to catch more test data

    # 2. SCHEMA: Not needed for this query-only operation

    # 3. ACT: Get payment schedules within date range
    results = await payment_schedule_repository.get_by_date_range(start_date, end_date)

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 2  # Should get at least 2 schedules in this range
    for schedule in results:
        # Use proper timezone-aware comparison
        assert (datetime_greater_than(schedule.scheduled_date, start_date, ignore_timezone=True) or 
                datetime_equals(schedule.scheduled_date, start_date, ignore_timezone=True))
        assert (datetime_greater_than(end_date, schedule.scheduled_date, ignore_timezone=True) or 
                datetime_equals(end_date, schedule.scheduled_date, ignore_timezone=True))


async def test_get_pending_schedules(
    payment_schedule_repository: PaymentScheduleRepository,
    test_multiple_payment_schedules: List[PaymentSchedule],
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
    test_multiple_payment_schedules: List[PaymentSchedule],
):
    """Test getting processed payment schedules."""
    # 1. ARRANGE: Mark one schedule as processed
    test_schedule = test_multiple_payment_schedules[0]
    process_time = utc_now()

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
    process_time = utc_now()

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

    # Use proper timezone-aware comparison for dates
    assert datetime_equals(result.processed_date, process_time, ignore_microseconds=True)


async def test_get_schedules_with_relationships(
    payment_schedule_repository: PaymentScheduleRepository,
    test_multiple_payment_schedules: List[PaymentSchedule],
):
    """Test getting payment schedules with all relationships loaded."""
    # 1. ARRANGE: Set up date range
    now = utc_now()
    date_range = (days_ago(10), days_from_now(20))

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
    test_multiple_payment_schedules: List[PaymentSchedule],
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
    now = utc_now()
    future_date = days_from_now(7)
    
    for schedule in results:
        assert schedule.account_id == test_checking_account.id
        assert schedule.processed is False

        # Schedule date should be in the future and within 7 days using proper timezone-aware comparison
        assert datetime_greater_than(schedule.scheduled_date, now) or datetime_equals(schedule.scheduled_date, now)
        assert datetime_greater_than(future_date, schedule.scheduled_date) or datetime_equals(future_date, schedule.scheduled_date)

        # Relationships should be loaded
        assert schedule.account is not None
        assert schedule.liability is not None


async def test_find_overdue_schedules(
    payment_schedule_repository: PaymentScheduleRepository,
    test_multiple_payment_schedules: List[PaymentSchedule],
):
    """Test finding overdue payment schedules."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Find overdue payment schedules
    results = await payment_schedule_repository.find_overdue_schedules()

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 1  # Should get at least 1 overdue schedule
    now = utc_now()
    
    for schedule in results:
        assert schedule.processed is False
        # Use proper timezone-aware comparison
        assert datetime_greater_than(now, schedule.scheduled_date, ignore_timezone=True)

        # Relationships should be loaded
        assert schedule.account is not None
        assert schedule.liability is not None


async def test_get_auto_process_schedules(
    payment_schedule_repository: PaymentScheduleRepository,
    test_multiple_payment_schedules: List[PaymentSchedule],
):
    """Test getting payment schedules set for auto-processing."""
    # 1. ARRANGE: Set up date range
    now = utc_now()
    date_range = (days_ago(1), days_from_now(30))

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
    test_multiple_payment_schedules: List[PaymentSchedule],
    test_checking_account: Account,
):
    """Test calculating total amount of scheduled payments."""
    # 1. ARRANGE: Set up date range
    now = utc_now()
    start_date = days_ago(10)
    end_date = days_from_now(20)

    # 2. SCHEMA: Not needed for this calculation operation

    # 3. ACT: Get total scheduled payments for account
    total = await payment_schedule_repository.get_total_scheduled_payments(
        start_date, end_date, test_checking_account.id
    )

    # 4. ASSERT: Verify the operation results
    assert total > 0  # Should have at least some scheduled payments


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
            scheduled_date=utc_now(),
            amount=Decimal("-50.00"),  # Invalid negative amount
            description="Test validation",
        )
        assert False, "Schema should have raised a validation error for negative amount"
    except ValueError as e:
        # This is expected - schema validation should catch the error
        assert "amount" in str(e).lower() and "greater than" in str(e).lower()
