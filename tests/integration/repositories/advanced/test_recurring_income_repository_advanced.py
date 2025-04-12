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
from typing import List

import pytest

from src.models.accounts import Account
from src.models.recurring_income import RecurringIncome
from src.repositories.recurring_income import RecurringIncomeRepository

# Import schema and schema factories - essential part of the validation pattern
from src.utils.datetime_utils import datetime_equals, datetime_greater_than, utc_now

pytestmark = pytest.mark.asyncio


async def test_get_by_source(
    recurring_income_repository: RecurringIncomeRepository,
    test_multiple_recurring_incomes: List[RecurringIncome],
):
    """Test getting recurring income by source name."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get recurring income by source
    results = await recurring_income_repository.get_by_source("Salary")

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 1  # Should get at least 1 income with "Salary" in source
    for income in results:
        assert "salary" in income.source.lower()


async def test_get_by_account(
    recurring_income_repository: RecurringIncomeRepository,
    test_checking_account: Account,
    test_multiple_recurring_incomes: List[RecurringIncome],
):
    """Test getting recurring income for a specific account."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get recurring income for the account
    results = await recurring_income_repository.get_by_account(test_checking_account.id)

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 2  # Should get at least 2 incomes for this account
    for income in results:
        assert income.account_id == test_checking_account.id
        # Relationship should be loaded
        assert income.account is not None
        assert income.account.id == test_checking_account.id


async def test_get_active_income(
    recurring_income_repository: RecurringIncomeRepository,
    test_multiple_recurring_incomes: List[RecurringIncome],
):
    """Test getting active recurring income records."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get active recurring income
    results = await recurring_income_repository.get_active_income()

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 3  # Should get at least 3 active incomes
    for income in results:
        assert income.active is True
        # Relationship should be loaded
        assert income.account is not None


async def test_get_by_day_of_month(
    recurring_income_repository: RecurringIncomeRepository,
    test_multiple_recurring_incomes: List[RecurringIncome],
):
    """Test getting recurring income for a specific day of the month."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get recurring income for day 15
    results = await recurring_income_repository.get_by_day_of_month(15)

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 1  # Should get at least 1 income for day 15
    for income in results:
        assert income.day_of_month == 15
        # Relationship should be loaded
        assert income.account is not None


async def test_get_with_income_entries(
    recurring_income_repository: RecurringIncomeRepository,
    test_recurring_income: RecurringIncome,
):
    """Test getting a recurring income with its income entries."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get the recurring income with income entries
    result = await recurring_income_repository.get_with_income_entries(
        test_recurring_income.id
    )

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_recurring_income.id
    assert hasattr(result, "income_entries")
    # May be empty list if no income entries have been created yet


async def test_get_with_account(
    recurring_income_repository: RecurringIncomeRepository,
    test_recurring_income: RecurringIncome,
):
    """Test getting a recurring income with its account."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get the recurring income with account
    result = await recurring_income_repository.get_with_account(
        test_recurring_income.id
    )

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_recurring_income.id
    assert result.account is not None
    assert result.account.id == test_recurring_income.account_id
    assert result.account.name is not None


async def test_get_with_relationships(
    recurring_income_repository: RecurringIncomeRepository,
    test_recurring_income: RecurringIncome,
):
    """Test getting a recurring income with all relationships loaded."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get the recurring income with relationships
    result = await recurring_income_repository.get_with_relationships(
        test_recurring_income.id
    )

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_recurring_income.id
    assert result.account is not None
    assert result.account.id == test_recurring_income.account_id
    assert hasattr(result, "income_entries")
    # Category might be None if not set


async def test_toggle_active(
    recurring_income_repository: RecurringIncomeRepository,
    test_recurring_income: RecurringIncome,
):
    """Test toggling the active status of a recurring income."""
    # 1. ARRANGE: Get current status
    initial_active = test_recurring_income.active

    # 2. SCHEMA: Not needed for this method as it uses ID only

    # 3. ACT: Toggle active status
    result = await recurring_income_repository.toggle_active(test_recurring_income.id)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_recurring_income.id
    assert result.active is not initial_active  # Should be toggled

    # Toggle back to verify
    result = await recurring_income_repository.toggle_active(test_recurring_income.id)
    assert result.active is initial_active  # Should be back to original


async def test_toggle_auto_deposit(
    recurring_income_repository: RecurringIncomeRepository,
    test_recurring_income: RecurringIncome,
):
    """Test toggling the auto_deposit status of a recurring income."""
    # 1. ARRANGE: Get current status
    initial_auto_deposit = test_recurring_income.auto_deposit

    # 2. SCHEMA: Not needed for this method as it uses ID only

    # 3. ACT: Toggle auto_deposit status
    result = await recurring_income_repository.toggle_auto_deposit(
        test_recurring_income.id
    )

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_recurring_income.id
    assert result.auto_deposit is not initial_auto_deposit  # Should be toggled

    # Toggle back to verify
    result = await recurring_income_repository.toggle_auto_deposit(
        test_recurring_income.id
    )
    assert result.auto_deposit is initial_auto_deposit  # Should be back to original


async def test_update_day_of_month(
    recurring_income_repository: RecurringIncomeRepository,
    test_recurring_income: RecurringIncome,
):
    """Test updating the day_of_month for a recurring income."""
    # 1. ARRANGE: Choose a new day
    new_day = 25 if test_recurring_income.day_of_month != 25 else 20

    # 2. SCHEMA: Not needed for this method as it uses ID and int only

    # 3. ACT: Update day_of_month
    result = await recurring_income_repository.update_day_of_month(
        test_recurring_income.id, new_day
    )

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_recurring_income.id
    assert result.day_of_month == new_day


async def test_get_monthly_total(
    recurring_income_repository: RecurringIncomeRepository,
    test_checking_account: Account,
    test_multiple_recurring_incomes: List[RecurringIncome],
):
    """Test calculating the total monthly amount of recurring income."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get monthly total for account
    total = await recurring_income_repository.get_monthly_total(
        test_checking_account.id
    )

    # 4. ASSERT: Verify the operation results
    assert total > 0

    # Calculate expected total manually for verification
    expected_total = sum(
        income.amount
        for income in test_multiple_recurring_incomes
        if income.account_id == test_checking_account.id and income.active
    )
    assert total == expected_total


async def test_get_upcoming_deposits(
    recurring_income_repository: RecurringIncomeRepository,
    test_multiple_recurring_incomes: List[RecurringIncome],
):
    """Test getting estimated upcoming deposits."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get upcoming deposits for next 30 days
    results = await recurring_income_repository.get_upcoming_deposits(days=30)

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 3  # Should get at least 3 upcoming deposits (active incomes)

    # First deposit projection should have expected fields
    first_deposit = results[0]
    assert "source" in first_deposit
    assert "amount" in first_deposit
    assert "projected_date" in first_deposit
    assert "account_id" in first_deposit
    assert "recurring_id" in first_deposit

    # Verify projected dates are in the future using proper timezone-aware comparison
    now = utc_now()
    for deposit in results:
        assert datetime_greater_than(deposit["projected_date"], now) or datetime_equals(
            deposit["projected_date"], now
        )


async def test_find_by_pattern(
    recurring_income_repository: RecurringIncomeRepository,
    test_multiple_recurring_incomes: List[RecurringIncome],
):
    """Test finding recurring income by pattern in source name."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Find recurring income by pattern
    results = await recurring_income_repository.find_by_pattern("free")

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 1  # Should get at least 1 income with "free" in source
    for income in results:
        assert "free" in income.source.lower()
        # Relationship should be loaded
        assert income.account is not None


async def test_get_total_by_source(
    recurring_income_repository: RecurringIncomeRepository,
    test_multiple_recurring_incomes: List[RecurringIncome],
):
    """Test calculating total amount for recurring incomes by source pattern."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get total by source pattern
    total = await recurring_income_repository.get_total_by_source("salary")

    # 4. ASSERT: Verify the operation results
    assert total > 0

    # Calculate expected total manually for verification
    expected_total = sum(
        income.amount
        for income in test_multiple_recurring_incomes
        if "salary" in income.source.lower() and income.active
    )
    assert total == expected_total


async def test_validation_error_handling(
    test_checking_account: Account,
):
    """Test handling invalid data that would normally be caught by schema validation."""
    # Import the schema factory
    from tests.helpers.schema_factories.recurring_income_schema_factories import (
        create_recurring_income_schema,
    )

    # Try creating a schema with invalid data and expect it to fail validation
    try:
        invalid_schema = create_recurring_income_schema(
            source="Invalid Income",
            amount=Decimal("-50.00"),  # Invalid negative amount
            day_of_month=15,
            account_id=test_checking_account.id,
            auto_deposit=False,
        )
        assert False, "Schema should have raised a validation error for negative amount"
    except ValueError as e:
        # This is expected - schema validation should catch the error
        assert "amount" in str(e).lower() and "greater than" in str(e).lower()

    # Try with invalid day_of_month
    try:
        invalid_schema = create_recurring_income_schema(
            source="Invalid Income",
            amount=Decimal("50.00"),
            day_of_month=32,  # Invalid day
            account_id=test_checking_account.id,
            auto_deposit=False,
        )
        assert False, "Schema should have raised a validation error for invalid day"
    except ValueError as e:
        # This is expected - schema validation should catch the error
        assert "day_of_month" in str(e).lower()
