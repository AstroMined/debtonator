"""
Integration tests for the RecurringIncomeRepository.

This module contains tests for the RecurringIncomeRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.

These tests verify CRUD operations and specialized methods for the
RecurringIncomeRepository, ensuring proper validation flow and relationship
loading.
"""

from decimal import Decimal

import pytest

from src.models.accounts import Account
from src.models.recurring_income import RecurringIncome
from src.repositories.recurring_income import RecurringIncomeRepository

# Import schema and schema factories - essential part of the validation pattern
from src.utils.datetime_utils import datetime_greater_than
from tests.helpers.schema_factories.recurring_income import (
    create_recurring_income_schema,
    create_recurring_income_update_schema,
)

pytestmark = pytest.mark.asyncio


async def test_create_recurring_income(
    recurring_income_repository: RecurringIncomeRepository,
    test_checking_account: Account,
):
    """Test creating a recurring income with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. SCHEMA: Create and validate through Pydantic schema
    income_schema = create_recurring_income_schema(
        source="Side Gig Income",
        amount=Decimal("750.00"),
        day_of_month=10,
        account_id=test_checking_account.id,
        auto_deposit=False,
    )

    # Convert validated schema to dict for repository
    validated_data = income_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await recurring_income_repository.create(validated_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id is not None
    assert result.source == "Side Gig Income"
    assert result.amount == Decimal("750.00")
    assert result.day_of_month == 10
    assert result.account_id == test_checking_account.id
    assert result.auto_deposit is False
    assert result.active is True  # Default value
    assert result.created_at is not None
    assert result.updated_at is not None


async def test_get_recurring_income(
    recurring_income_repository: RecurringIncomeRepository,
    test_recurring_income: RecurringIncome,
):
    """Test retrieving a recurring income by ID."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get the recurring income
    result = await recurring_income_repository.get(test_recurring_income.id)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_recurring_income.id
    assert result.source == test_recurring_income.source
    assert result.amount == test_recurring_income.amount
    assert result.day_of_month == test_recurring_income.day_of_month
    assert result.account_id == test_recurring_income.account_id
    assert result.auto_deposit == test_recurring_income.auto_deposit
    assert result.active == test_recurring_income.active


async def test_update_recurring_income(
    recurring_income_repository: RecurringIncomeRepository,
    test_recurring_income: RecurringIncome,
):
    """Test updating a recurring income with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures

    # Store original timestamp before update
    original_updated_at = test_recurring_income.updated_at

    # 2. SCHEMA: Create and validate update data through Pydantic schema
    update_schema = create_recurring_income_update_schema(
        source="Updated Salary",
        amount=Decimal("2500.00"),
        auto_deposit=False,
    )

    # Convert validated schema to dict for repository
    update_data = update_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await recurring_income_repository.update(
        test_recurring_income.id, update_data
    )

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_recurring_income.id
    assert result.source == "Updated Salary"
    assert result.amount == Decimal("2500.00")
    assert result.auto_deposit is False
    assert result.day_of_month == test_recurring_income.day_of_month  # Unchanged
    assert result.account_id == test_recurring_income.account_id  # Unchanged
    assert datetime_greater_than(
        result.updated_at, original_updated_at, ignore_timezone=True
    )


async def test_delete_recurring_income(
    recurring_income_repository: RecurringIncomeRepository,
    test_recurring_income: RecurringIncome,
):
    """Test deleting a recurring income."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Delete the recurring income
    result = await recurring_income_repository.delete(test_recurring_income.id)

    # 4. ASSERT: Verify the operation results
    assert result is True

    # Verify it's actually deleted
    deleted_income = await recurring_income_repository.get(test_recurring_income.id)
    assert deleted_income is None
