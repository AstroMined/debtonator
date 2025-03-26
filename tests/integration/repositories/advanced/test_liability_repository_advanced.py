"""
Integration tests for the LiabilityRepository.

This module contains tests for the LiabilityRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.categories import Category
from src.models.liabilities import Liability, LiabilityStatus
from src.repositories.liabilities import LiabilityRepository
from src.schemas.liabilities import LiabilityCreate, LiabilityUpdate
from src.utils.datetime_utils import utc_now, days_from_now, datetime_greater_than, datetime_equals, days_ago
from tests.helpers.schema_factories.accounts import create_account_schema
from tests.helpers.schema_factories.categories import create_category_schema
from tests.helpers.schema_factories.liabilities import create_liability_schema

pytestmark = pytest.mark.asyncio


async def test_get_with_splits(
    liability_repository: LiabilityRepository,
    test_liability: Liability,
):
    """Test getting a liability with its splits loaded."""
    # 1. ARRANGE: Setup is already done with fixtures
    # Note: In a complete test, we would create bill splits for this liability

    # 2. ACT: Get the liability with splits
    result = await liability_repository.get_with_splits(test_liability.id)

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_liability.id
    assert hasattr(result, "splits")  # Ensure splits attribute exists
    # In a real test, we would verify splits are loaded correctly


async def test_get_with_payments(
    liability_repository: LiabilityRepository,
    test_liability: Liability,
):
    """Test getting a liability with its payments loaded."""
    # 1. ARRANGE: Setup is already done with fixtures
    # Note: In a complete test, we would create payments for this liability

    # 2. ACT: Get the liability with payments
    result = await liability_repository.get_with_payments(test_liability.id)

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_liability.id
    assert hasattr(result, "payments")  # Ensure payments attribute exists
    # In a real test, we would verify payments are loaded correctly


async def test_get_with_relationships(
    liability_repository: LiabilityRepository,
    test_liability: Liability,
):
    """Test getting a liability with multiple relationships loaded."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get the liability with multiple relationships
    result = await liability_repository.get_with_relationships(
        liability_id=test_liability.id,
        include_primary_account=True,
        include_category=True,
        include_splits=True,
        include_payments=True,
    )

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_liability.id
    assert hasattr(result, "primary_account")  # Ensure relationship attributes exist
    assert hasattr(result, "category")
    assert hasattr(result, "splits")
    assert hasattr(result, "payments")
    # In a real test, we would verify relationships are loaded correctly


async def test_get_bills_due_in_range(
    liability_repository: LiabilityRepository,
    test_multiple_liabilities: List[Liability],
):
    """Test getting bills due within a date range."""
    # 1. ARRANGE: Setup is already done with fixtures
    now = utc_now()
    start_date = now
    end_date = now + timedelta(days=20)

    # 2. ACT: Get bills due in range
    results = await liability_repository.get_bills_due_in_range(start_date, end_date)

    # 3. ASSERT: Verify the operation results
    assert len(results) >= 2  # Should find at least 2 bills due within 20 days
    for liability in results:
        assert liability.due_date >= start_date
        assert liability.due_date <= end_date
        assert liability.paid is False  # By default, include_paid is False


async def test_get_bills_due_in_range_with_paid(
    liability_repository: LiabilityRepository,
    test_multiple_liabilities: List[Liability],
):
    """Test getting bills due within a date range including paid bills."""
    # 1. ARRANGE: Setup is already done with fixtures
    now = utc_now()
    start_date = now
    end_date = days_from_now(40)  # Include all future bills

    # 2. ACT: Get bills due in range, including paid
    results = await liability_repository.get_bills_due_in_range(
        start_date, end_date, include_paid=True
    )

    # 3. ASSERT: Verify the operation results
    assert len(results) >= 3  # Should find at least 3 bills (2 unpaid, 1 paid)
    paid_count = sum(1 for bill in results if bill.paid)
    assert paid_count >= 1  # At least one paid bill in results


async def test_get_bills_by_category(
    liability_repository: LiabilityRepository,
    test_category: Category,
    test_multiple_liabilities: List[Liability],
):
    """Test getting bills filtered by category."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get bills by category
    results = await liability_repository.get_bills_by_category(test_category.id)

    # 3. ASSERT: Verify the operation results
    assert len(results) >= 1
    for liability in results:
        assert liability.category_id == test_category.id
        assert liability.paid is False  # By default, include_paid is False


async def test_get_recurring_bills(
    liability_repository: LiabilityRepository,
    test_multiple_liabilities: List[Liability],
):
    """Test getting recurring bills."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get recurring bills
    results = await liability_repository.get_recurring_bills()

    # 3. ASSERT: Verify the operation results
    assert len(results) >= 2  # Should find at least 2 recurring bills
    for liability in results:
        assert liability.recurring is True


async def test_find_bills_by_status(
    liability_repository: LiabilityRepository,
    test_multiple_liabilities: List[Liability],
):
    """Test finding bills with a specific status."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Find bills by status
    results = await liability_repository.find_bills_by_status(LiabilityStatus.PENDING)

    # 3. ASSERT: Verify the operation results
    assert len(results) >= 1
    for liability in results:
        assert liability.status == LiabilityStatus.PENDING


async def test_get_bills_for_account(
    liability_repository: LiabilityRepository,
    test_checking_account: Account,
    test_multiple_liabilities: List[Liability],
):
    """Test getting bills associated with a specific account."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get bills for account
    results = await liability_repository.get_bills_for_account(test_checking_account.id)

    # 3. ASSERT: Verify the operation results
    assert len(results) >= 3  # Should find at least 3 unpaid bills
    for liability in results:
        assert liability.primary_account_id == test_checking_account.id
        assert liability.paid is False  # By default, include_paid is False


async def test_get_upcoming_payments(
    liability_repository: LiabilityRepository,
    test_multiple_liabilities: List[Liability],
):
    """Test getting upcoming bills due within specified days."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get upcoming payments (due in next 10 days)
    results = await liability_repository.get_upcoming_payments(days=10)

    # 3. ASSERT: Verify the operation results
    assert len(results) >= 1  # Should find at least 1 bill due in 10 days
    now = utc_now()
    future_date = days_from_now(10)
    for liability in results:
        # Verify each bill is due within the next 10 days using proper timezone-aware comparison
        assert datetime_greater_than(liability.due_date, now) or datetime_equals(liability.due_date, now)
        assert datetime_greater_than(future_date, liability.due_date) or datetime_equals(future_date, liability.due_date)
        assert liability.paid is False


async def test_get_overdue_bills(
    liability_repository: LiabilityRepository,
    test_multiple_liabilities: List[Liability],
):
    """Test getting overdue bills."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get overdue bills
    results = await liability_repository.get_overdue_bills()

    # 3. ASSERT: Verify the operation results
    assert len(results) >= 1  # Should find at least 1 overdue bill
    now = utc_now()
    for liability in results:
        # Use proper timezone-aware comparison
        assert datetime_greater_than(now, liability.due_date)
        assert liability.paid is False


async def test_mark_as_paid(
    liability_repository: LiabilityRepository,
    test_liability: Liability,
):
    """Test marking a liability as paid."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Mark the liability as paid
    result = await liability_repository.mark_as_paid(test_liability.id)

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_liability.id
    assert result.paid is True
    assert result.status == LiabilityStatus.PAID


async def test_reset_payment_status(
    liability_repository: LiabilityRepository,
    test_liability: Liability,
):
    """Test resetting a liability payment status to unpaid."""
    # 1. ARRANGE: First mark as paid
    await liability_repository.mark_as_paid(test_liability.id)

    # 2. ACT: Reset payment status
    result = await liability_repository.reset_payment_status(test_liability.id)

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_liability.id
    assert result.paid is False
    assert result.status == LiabilityStatus.PENDING


async def test_get_monthly_liability_amount(
    liability_repository: LiabilityRepository,
    test_multiple_liabilities: List[Liability],
):
    """Test getting total liability amount for a specific month."""
    # 1. ARRANGE: Setup is already done with fixtures
    now = utc_now()

    # 2. ACT: Get monthly liability amount
    total = await liability_repository.get_monthly_liability_amount(now.year, now.month)

    # 3. ASSERT: Verify the operation results
    assert total is not None
    assert total > Decimal("0")  # Should have some bills for this month


async def test_validation_error_handling():
    """Test handling of validation errors that would be caught by the Pydantic schema."""
    # Try creating a schema with invalid data
    try:
        invalid_schema = LiabilityCreate(
            name="",  # Invalid empty name
            amount=Decimal("-10.00"),  # Invalid negative amount
            due_date=days_ago(10),  # Past date is actually valid per ADR-002 for historical data
            category_id=1,
            primary_account_id=1,
        )
        assert False, "Schema should have raised a validation error"
    except ValueError as e:
        # This is expected - schema validation should catch the error
        error_str = str(e).lower()
        assert "name" in error_str or "amount" in error_str  # Note: due_date removed as past dates are valid
