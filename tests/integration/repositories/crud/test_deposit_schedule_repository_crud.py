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
from src.schemas.deposit_schedules import DepositScheduleCreate, DepositScheduleUpdate
from tests.helpers.schema_factories.accounts import create_account_schema
from tests.helpers.schema_factories.deposit_schedules import (
    create_deposit_schedule_schema,
)
from tests.helpers.schema_factories.income import create_income_schema

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def deposit_schedule_repository(
    db_session: AsyncSession,
) -> DepositScheduleRepository:
    """Fixture for DepositScheduleRepository with test database session."""
    return DepositScheduleRepository(db_session)


@pytest_asyncio.fixture
async def income_repository(db_session: AsyncSession) -> IncomeRepository:
    """Fixture for IncomeRepository with test database session."""
    return IncomeRepository(db_session)


@pytest_asyncio.fixture
async def test_income(
    income_repository: IncomeRepository,
    test_checking_account: Account,
) -> Income:
    """Fixture to create a test income entry."""
    # Create and validate through Pydantic schema
    income_schema = create_income_schema(
        source="Monthly Salary",
        amount=Decimal("3000.00"),
        account_id=test_checking_account.id,
        date=datetime.now(timezone.utc),
        deposited=False,
    )

    # Convert validated schema to dict for repository
    validated_data = income_schema.model_dump()

    # Create income through repository
    return await income_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_additional_income(
    income_repository: IncomeRepository,
    test_second_account: Account,
) -> Income:
    """Fixture to create a second test income entry."""
    # Create and validate through Pydantic schema
    income_schema = create_income_schema(
        source="Freelance Payment",
        amount=Decimal("1500.00"),
        account_id=test_second_account.id,
        date=datetime.now(timezone.utc),
        deposited=False,
    )

    # Convert validated schema to dict for repository
    validated_data = income_schema.model_dump()

    # Create income through repository
    return await income_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_deposit_schedule(
    deposit_schedule_repository: DepositScheduleRepository,
    test_income: Income,
    test_checking_account: Account,
) -> DepositSchedule:
    """Fixture to create a test deposit schedule."""
    # Create and validate through Pydantic schema
    schedule_schema = create_deposit_schedule_schema(
        income_id=test_income.id,
        account_id=test_checking_account.id,
        schedule_date=datetime.now(timezone.utc) + timedelta(days=7),
        amount=Decimal("3000.00"),
        recurring=False,
        status="pending",
    )

    # Convert validated schema to dict for repository
    validated_data = schedule_schema.model_dump()

    # Create deposit schedule through repository
    return await deposit_schedule_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_multiple_schedules(
    deposit_schedule_repository: DepositScheduleRepository,
    test_income: Income,
    test_additional_income: Income,
    test_checking_account: Account,
    test_second_account: Account,
) -> List[DepositSchedule]:
    """Fixture to create multiple deposit schedules for testing."""
    now = datetime.now(timezone.utc)

    # Create multiple deposit schedules with various attributes
    schedule_data = [
        {
            "income_id": test_income.id,
            "account_id": test_checking_account.id,
            "schedule_date": now + timedelta(days=3),
            "amount": Decimal("3000.00"),
            "recurring": False,
            "status": "pending",
        },
        {
            "income_id": test_additional_income.id,
            "account_id": test_second_account.id,
            "schedule_date": now + timedelta(days=14),
            "amount": Decimal("1500.00"),
            "recurring": True,
            "recurrence_pattern": {"frequency": "monthly", "day": 15},
            "status": "pending",
        },
        {
            "income_id": test_income.id,
            "account_id": test_checking_account.id,
            "schedule_date": now - timedelta(days=5),  # Past date
            "amount": Decimal("1000.00"),
            "recurring": False,
            "status": "pending",  # Overdue
        },
        {
            "income_id": test_additional_income.id,
            "account_id": test_second_account.id,
            "schedule_date": now - timedelta(days=10),  # Past date
            "amount": Decimal("500.00"),
            "recurring": False,
            "status": "processed",  # Already processed
        },
    ]

    # Create the deposit schedules using the repository
    created_schedules = []
    for data in schedule_data:
        # Create and validate through Pydantic schema
        schedule_schema = create_deposit_schedule_schema(**data)

        # Convert validated schema to dict for repository
        validated_data = schedule_schema.model_dump()

        # Create deposit schedule through repository
        schedule = await deposit_schedule_repository.create(validated_data)
        created_schedules.append(schedule)

    return created_schedules


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

    assert result.updated_at > test_deposit_schedule.updated_at


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


async def test_get_by_account(
    deposit_schedule_repository: DepositScheduleRepository,
    test_checking_account: Account,
    test_multiple_schedules: List[DepositSchedule],
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
    test_multiple_schedules: List[DepositSchedule],
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
    test_multiple_schedules: List[DepositSchedule],
):
    """Test getting deposit schedules within a date range."""
    # 1. ARRANGE: Setup date range
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=14)
    end_date = now + timedelta(days=7)

    # 2. SCHEMA: Not needed for this query-only operation

    # 3. ACT: Get deposit schedules within date range
    results = await deposit_schedule_repository.get_by_date_range(start_date, end_date)

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 3  # Should get at least 3 schedules in this range

    # Verify dates are within the range
    for schedule in results:
        # Make naive comparison for dates
        schedule_date = schedule.schedule_date.replace(tzinfo=None)
        naive_start = start_date.replace(tzinfo=None)
        naive_end = end_date.replace(tzinfo=None)

        assert schedule_date >= naive_start
        assert schedule_date <= naive_end


async def test_get_pending_schedules(
    deposit_schedule_repository: DepositScheduleRepository,
    test_multiple_schedules: List[DepositSchedule],
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
    test_multiple_schedules: List[DepositSchedule],
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
    test_multiple_schedules: List[DepositSchedule],
):
    """Test getting deposit schedules with all relationships loaded."""
    # 1. ARRANGE: Setup date range
    now = datetime.now(timezone.utc)
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
    test_multiple_schedules: List[DepositSchedule],
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
        now = datetime.now(timezone.utc).replace(tzinfo=None)
        schedule_date = schedule.schedule_date.replace(tzinfo=None)
        assert schedule_date >= now
        assert schedule_date <= (now + timedelta(days=7))

        # Relationships should be loaded
        assert schedule.account is not None
        assert schedule.income is not None


async def test_find_overdue_schedules(
    deposit_schedule_repository: DepositScheduleRepository,
    test_multiple_schedules: List[DepositSchedule],
):
    """Test finding overdue deposit schedules."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Find overdue deposit schedules
    results = await deposit_schedule_repository.find_overdue_schedules()

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 1  # Should get at least 1 overdue schedule
    now = datetime.now(timezone.utc).replace(tzinfo=None)
    for schedule in results:
        assert schedule.status == "pending"
        schedule_date = schedule.schedule_date.replace(tzinfo=None)
        assert schedule_date < now

        # Relationships should be loaded
        assert schedule.account is not None
        assert schedule.income is not None


async def test_get_recurring_schedules(
    deposit_schedule_repository: DepositScheduleRepository,
    test_multiple_schedules: List[DepositSchedule],
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
    test_multiple_schedules: List[DepositSchedule],
    test_checking_account: Account,
):
    """Test calculating total amount of scheduled deposits."""
    # 1. ARRANGE: Setup date range
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=14)
    end_date = now + timedelta(days=14)

    # 2. SCHEMA: Not needed for this calculation operation

    # 3. ACT: Get total scheduled deposits for account
    total = await deposit_schedule_repository.get_total_scheduled_deposits(
        start_date, end_date, test_checking_account.id
    )

    # 4. ASSERT: Verify the operation results
    assert total > 0  # Should have at least some scheduled deposits

    # Calculate expected total manually for verification
    expected_total = 0.0
    for schedule in test_multiple_schedules:
        if (
            schedule.account_id == test_checking_account.id
            and schedule.status == "pending"
            and schedule.schedule_date >= start_date.replace(tzinfo=None)
            and schedule.schedule_date <= end_date.replace(tzinfo=None)
        ):
            expected_total += float(schedule.amount)

    assert total == pytest.approx(expected_total, abs=0.01)


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
    # Try creating a schema with invalid data and expect it to fail validation
    try:
        invalid_schema = DepositScheduleCreate(
            income_id=test_income.id,
            account_id=test_checking_account.id,
            schedule_date=datetime.now(timezone.utc),
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
        invalid_schema = DepositScheduleCreate(
            income_id=test_income.id,
            account_id=test_checking_account.id,
            schedule_date=datetime.now(timezone.utc),
            amount=Decimal("50.00"),
            recurring=False,
            status="invalid_status",  # Invalid status
        )
        assert False, "Schema should have raised a validation error for invalid status"
    except ValueError as e:
        # This is expected - schema validation should catch the error
        assert "status" in str(e).lower()
