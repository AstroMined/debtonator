"""
Integration tests for the DepositScheduleRepository.

This module contains tests for the DepositScheduleRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.

These tests verify CRUD operations and specialized methods for the
DepositScheduleRepository, ensuring proper validation flow and data integrity.
"""

from datetime import timedelta
from decimal import Decimal
from typing import List

import pytest

from src.models.accounts import Account
from src.models.deposit_schedules import DepositSchedule
from src.models.income import Income
from src.repositories.deposit_schedules import DepositScheduleRepository
from src.utils.datetime_utils import (
    datetime_equals,
    datetime_greater_than,
    days_ago,
    days_from_now,
    utc_now,
)

pytestmark = pytest.mark.asyncio


async def test_get_by_account(
    deposit_schedule_repository: DepositScheduleRepository,
    test_checking_account: Account,
    test_multiple_deposit_schedules: List[DepositSchedule],
):
    """Test getting deposit schedules for a specific account."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get deposit schedules for the account
    results = await deposit_schedule_repository.get_by_account(test_checking_account.id)

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 2  # Should get at least 2 schedules for this account
    for schedule in results:
        assert schedule.account_id == test_checking_account.id


async def test_get_by_income(
    deposit_schedule_repository: DepositScheduleRepository,
    test_income: Income,
    test_multiple_deposit_schedules: List[DepositSchedule],
):
    """Test getting deposit schedules for a specific income."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get deposit schedules for the income
    results = await deposit_schedule_repository.get_by_income(test_income.id)

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 2  # Should get at least 2 schedules for this income
    for schedule in results:
        assert schedule.income_id == test_income.id


async def test_get_with_account(
    deposit_schedule_repository: DepositScheduleRepository,
    test_deposit_schedule: DepositSchedule,
):
    """Test getting a deposit schedule with account relationship loaded."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get the deposit schedule with account
    result = await deposit_schedule_repository.get_with_account(
        test_deposit_schedule.id
    )

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_deposit_schedule.id
    assert result.account is not None
    assert result.account.id == test_deposit_schedule.account_id
    assert result.account.name is not None


async def test_get_with_income(
    deposit_schedule_repository: DepositScheduleRepository,
    test_deposit_schedule: DepositSchedule,
):
    """Test getting a deposit schedule with income relationship loaded."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get the deposit schedule with income
    result = await deposit_schedule_repository.get_with_income(test_deposit_schedule.id)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_deposit_schedule.id
    assert result.income is not None
    assert result.income.id == test_deposit_schedule.income_id
    assert result.income.source is not None


async def test_get_by_date_range(
    deposit_schedule_repository: DepositScheduleRepository,
    test_multiple_deposit_schedules: List[DepositSchedule],
):
    """Test getting deposit schedules within a date range."""
    # 1. ARRANGE: Setup date range
    start_date = utc_now() - timedelta(days=14)
    end_date = utc_now() + timedelta(days=7)

    # 2. SCHEMA: Not needed for this query-only operation

    # 3. ACT: Get deposit schedules within date range
    results = await deposit_schedule_repository.get_by_date_range(start_date, end_date)

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 3  # Should get at least 3 schedules in this range

    # Verify dates are within the range
    for schedule in results:
        # Use proper timezone-aware comparison
        assert datetime_greater_than(
            schedule.schedule_date, start_date, ignore_timezone=True
        ) or datetime_equals(schedule.schedule_date, start_date, ignore_timezone=True)
        assert datetime_greater_than(
            end_date, schedule.schedule_date, ignore_timezone=True
        ) or datetime_equals(end_date, schedule.schedule_date, ignore_timezone=True)


async def test_get_pending_schedules(
    deposit_schedule_repository: DepositScheduleRepository,
    test_multiple_deposit_schedules: List[DepositSchedule],
):
    """Test getting pending deposit schedules."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get pending deposit schedules
    results = await deposit_schedule_repository.get_pending_schedules()

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 3  # Should get at least 3 pending schedules
    for schedule in results:
        assert schedule.status == "pending"


async def test_get_processed_schedules(
    deposit_schedule_repository: DepositScheduleRepository,
    test_multiple_deposit_schedules: List[DepositSchedule],
):
    """Test getting processed deposit schedules."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get processed deposit schedules
    results = await deposit_schedule_repository.get_processed_schedules()

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 1  # Should get at least 1 processed schedule
    for schedule in results:
        assert schedule.status == "processed"


async def test_mark_as_processed(
    deposit_schedule_repository: DepositScheduleRepository,
    test_deposit_schedule: DepositSchedule,
):
    """Test marking a deposit schedule as processed."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Mark the deposit schedule as processed
    result = await deposit_schedule_repository.mark_as_processed(
        test_deposit_schedule.id
    )

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_deposit_schedule.id
    assert result.status == "processed"


async def test_get_schedules_with_relationships(
    deposit_schedule_repository: DepositScheduleRepository,
    test_multiple_deposit_schedules: List[DepositSchedule],
):
    """Test getting deposit schedules with all relationships loaded."""
    # 1. ARRANGE: Setup date range
    now = utc_now()
    date_range = (now - timedelta(days=14), now + timedelta(days=14))

    # 2. SCHEMA: Not needed for this query-only operation

    # 3. ACT: Get deposit schedules with relationships
    results = await deposit_schedule_repository.get_schedules_with_relationships(
        date_range
    )

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 3  # Should get at least 3 schedules in this range
    for schedule in results:
        assert schedule.account is not None
        assert schedule.income is not None
        assert schedule.account.id == schedule.account_id
        assert schedule.income.id == schedule.income_id


async def test_get_upcoming_schedules(
    deposit_schedule_repository: DepositScheduleRepository,
    test_multiple_deposit_schedules: List[DepositSchedule],
    test_checking_account: Account,
):
    """Test getting upcoming deposit schedules."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get upcoming deposit schedules for next 7 days
    results = await deposit_schedule_repository.get_upcoming_schedules(
        days=7, account_id=test_checking_account.id
    )

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 1  # Should get at least 1 upcoming schedule
    for schedule in results:
        assert schedule.account_id == test_checking_account.id
        assert schedule.status == "pending"

        # Schedule date should be in the future and within 7 days
        now = utc_now()

        # Use proper timezone-aware comparison
        assert datetime_greater_than(
            schedule.schedule_date, now, ignore_timezone=True
        ) or datetime_equals(schedule.schedule_date, now, ignore_timezone=True)

        future_limit = now + timedelta(days=7)
        assert datetime_greater_than(
            future_limit, schedule.schedule_date, ignore_timezone=True
        ) or datetime_equals(future_limit, schedule.schedule_date, ignore_timezone=True)

        # Relationships should be loaded
        assert schedule.account is not None
        assert schedule.income is not None


async def test_find_overdue_schedules(
    deposit_schedule_repository: DepositScheduleRepository,
    test_multiple_deposit_schedules: List[DepositSchedule],
):
    """Test finding overdue deposit schedules."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Find overdue deposit schedules
    results = await deposit_schedule_repository.find_overdue_schedules()

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 1  # Should get at least 1 overdue schedule
    now = utc_now()

    for schedule in results:
        assert schedule.status == "pending"
        # Use proper timezone-aware comparison
        assert datetime_greater_than(now, schedule.schedule_date)

        # Relationships should be loaded
        assert schedule.account is not None
        assert schedule.income is not None


async def test_get_recurring_schedules(
    deposit_schedule_repository: DepositScheduleRepository,
    test_multiple_deposit_schedules: List[DepositSchedule],
):
    """Test getting recurring deposit schedules."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get recurring deposit schedules
    results = await deposit_schedule_repository.get_recurring_schedules()

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 1  # Should get at least 1 recurring schedule
    for schedule in results:
        assert schedule.recurring is True


async def test_get_total_scheduled_deposits(
    deposit_schedule_repository: DepositScheduleRepository,
    test_multiple_deposit_schedules: List[DepositSchedule],
    test_checking_account: Account,
):
    """Test calculating total amount of scheduled deposits."""
    # 1. ARRANGE: Setup date range
    start_date = days_ago(14)
    end_date = days_from_now(14)

    # 2. SCHEMA: Not needed for this calculation operation

    # 3. ACT: Get total scheduled deposits for account
    total = await deposit_schedule_repository.get_total_scheduled_deposits(
        start_date, end_date, test_checking_account.id
    )

    # 4. ASSERT: Verify the operation results
    assert total > 0  # Should have at least some scheduled deposits


async def test_cancel_schedule(
    deposit_schedule_repository: DepositScheduleRepository,
    test_deposit_schedule: DepositSchedule,
):
    """Test cancelling a deposit schedule."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Cancel the deposit schedule
    result = await deposit_schedule_repository.cancel_schedule(test_deposit_schedule.id)

    # 4. ASSERT: Verify the operation results
    assert result is True

    # Verify it's actually deleted
    cancelled_schedule = await deposit_schedule_repository.get(test_deposit_schedule.id)
    assert cancelled_schedule is None


async def test_update_status(
    deposit_schedule_repository: DepositScheduleRepository,
    test_deposit_schedule: DepositSchedule,
):
    """Test updating the status of a deposit schedule."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Update status to cancelled
    result = await deposit_schedule_repository.update_status(
        test_deposit_schedule.id, "cancelled"
    )

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_deposit_schedule.id
    assert result.status == "cancelled"

    # Test with invalid status should raise ValueError
    with pytest.raises(ValueError):
        await deposit_schedule_repository.update_status(
            test_deposit_schedule.id, "invalid_status"
        )


async def test_validation_error_handling(
    test_income: Income,
    test_checking_account: Account,
):
    """Test handling invalid data that would normally be caught by schema validation."""
    # Import the schema factory
    from tests.helpers.schema_factories.deposit_schedules_schema_factories import (
        create_deposit_schedule_schema,
    )

    # Try creating a schema with invalid data and expect it to fail validation
    try:
        invalid_schema = create_deposit_schedule_schema(
            income_id=test_income.id,
            account_id=test_checking_account.id,
            schedule_date=utc_now(),
            amount=Decimal("-50.00"),  # Invalid negative amount
            recurring=False,
            status="pending",
        )
        assert False, "Schema should have raised a validation error for negative amount"
    except ValueError as e:
        # This is expected - schema validation should catch the error
        assert "amount" in str(e).lower() and "greater than" in str(e).lower()

    # Try with invalid status
    try:
        invalid_schema = create_deposit_schedule_schema(
            income_id=test_income.id,
            account_id=test_checking_account.id,
            schedule_date=utc_now(),
            amount=Decimal("50.00"),
            recurring=False,
            status="invalid_status",  # Invalid status
        )
        assert False, "Schema should have raised a validation error for invalid status"
    except ValueError as e:
        # This is expected - schema validation should catch the error
        assert "status" in str(e).lower()
