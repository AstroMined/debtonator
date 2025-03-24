"""
Integration tests for the RecurringBillRepository.

This module contains tests for the RecurringBillRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import List

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.categories import Category
from src.models.recurring_bills import RecurringBill
from src.repositories.accounts import AccountRepository
from src.repositories.categories import CategoryRepository
from src.repositories.recurring_bills import RecurringBillRepository
from src.schemas.recurring_bills import (RecurringBillCreate,
                                         RecurringBillUpdate)
from tests.helpers.schema_factories.accounts import create_account_schema
from tests.helpers.schema_factories.categories import create_category_schema
from tests.helpers.schema_factories.recurring_bills import \
    create_recurring_bill_schema

pytestmark = pytest.mark.asyncio


async def test_create_recurring_bill(
    recurring_bill_repository: RecurringBillRepository,
    test_checking_account: Account,
    test_category: Category,
):
    """Test creating a recurring bill with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. SCHEMA: Create and validate through Pydantic schema
    bill_schema = create_recurring_bill_schema(
        bill_name="New Test Bill",
        amount=Decimal("75.00"),
        day_of_month=10,
        account_id=test_checking_account.id,
        category_id=test_category.id,
        auto_pay=True,
    )

    # Convert validated schema to dict for repository
    validated_data = bill_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await recurring_bill_repository.create(validated_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id is not None
    assert result.bill_name == "New Test Bill"
    assert result.amount == Decimal("75.00")
    assert result.day_of_month == 10
    assert result.account_id == test_checking_account.id
    assert result.category_id == test_category.id
    assert result.auto_pay is True
    assert result.active is True  # Default when created
    assert result.created_at is not None
    assert result.updated_at is not None


async def test_get_recurring_bill(
    recurring_bill_repository: RecurringBillRepository,
    test_recurring_bill: RecurringBill,
):
    """Test retrieving a recurring bill by ID."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get the recurring bill by ID
    result = await recurring_bill_repository.get(test_recurring_bill.id)

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_recurring_bill.id
    assert result.bill_name == test_recurring_bill.bill_name
    assert result.amount == test_recurring_bill.amount
    assert result.day_of_month == test_recurring_bill.day_of_month
    assert result.account_id == test_recurring_bill.account_id
    assert result.category_id == test_recurring_bill.category_id
    assert result.auto_pay == test_recurring_bill.auto_pay
    assert result.active == test_recurring_bill.active


async def test_update_recurring_bill(
    recurring_bill_repository: RecurringBillRepository,
    test_recurring_bill: RecurringBill,
):
    """Test updating a recurring bill with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. SCHEMA: Create and validate update data through Pydantic schema
    update_schema = RecurringBillUpdate(
        bill_name="Updated Bill Name",
        amount=Decimal("125.00"),
        day_of_month=20,
    )

    # Convert validated schema to dict for repository
    update_data = update_schema.model_dump(exclude_unset=True)

    # 3. ACT: Pass validated data to repository
    result = await recurring_bill_repository.update(test_recurring_bill.id, update_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_recurring_bill.id
    assert result.bill_name == "Updated Bill Name"
    assert result.amount == Decimal("125.00")
    assert result.day_of_month == 20
    # Fields not in update_data should remain unchanged
    assert result.account_id == test_recurring_bill.account_id
    assert result.category_id == test_recurring_bill.category_id
    assert result.auto_pay == test_recurring_bill.auto_pay
    assert result.active == test_recurring_bill.active
    assert result.updated_at > test_recurring_bill.updated_at


async def test_delete_recurring_bill(
    recurring_bill_repository: RecurringBillRepository,
    test_recurring_bill: RecurringBill,
):
    """Test deleting a recurring bill."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Delete the recurring bill
    result = await recurring_bill_repository.delete(test_recurring_bill.id)

    # 3. ASSERT: Verify the operation results
    assert result is True

    # Verify the bill is actually deleted
    deleted_check = await recurring_bill_repository.get(test_recurring_bill.id)
    assert deleted_check is None


async def test_get_by_name(
    recurring_bill_repository: RecurringBillRepository,
    test_recurring_bill: RecurringBill,
):
    """Test getting a recurring bill by name."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get recurring bill by name
    result = await recurring_bill_repository.get_by_name(test_recurring_bill.bill_name)

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_recurring_bill.id
    assert result.bill_name == test_recurring_bill.bill_name

    # Test non-existent bill
    non_existent = await recurring_bill_repository.get_by_name("Non Existent Bill")
    assert non_existent is None


async def test_get_active_bills(
    recurring_bill_repository: RecurringBillRepository,
    test_multiple_recurring_bills: List[RecurringBill],
):
    """Test retrieving all active recurring bills."""
    # 1. ARRANGE: Setup is already done with fixtures
    active_bill_ids = [bill.id for bill in test_multiple_recurring_bills if bill.active]
    inactive_bill_ids = [
        bill.id for bill in test_multiple_recurring_bills if not bill.active
    ]

    # 2. ACT: Get active bills
    active_bills = await recurring_bill_repository.get_active_bills()

    # 3. ASSERT: Verify the operation results
    assert len(active_bills) >= len(active_bill_ids)

    # Check that all active bills are returned
    for bill_id in active_bill_ids:
        assert any(bill.id == bill_id for bill in active_bills)

    # Check that no inactive bills are returned
    for bill_id in inactive_bill_ids:
        assert not any(bill.id == bill_id for bill in active_bills)


async def test_get_by_day_of_month(
    recurring_bill_repository: RecurringBillRepository,
    test_multiple_recurring_bills: List[RecurringBill],
):
    """Test retrieving recurring bills by day of month."""
    # 1. ARRANGE: Setup is already done with fixtures
    day_10_bill_ids = [
        bill.id for bill in test_multiple_recurring_bills if bill.day_of_month == 10
    ]
    day_15_bill_ids = [
        bill.id for bill in test_multiple_recurring_bills if bill.day_of_month == 15
    ]

    # 2. ACT: Get bills by day of month
    day_10_bills = await recurring_bill_repository.get_by_day_of_month(10)
    day_15_bills = await recurring_bill_repository.get_by_day_of_month(15)
    day_5_bills = await recurring_bill_repository.get_by_day_of_month(5)

    # 3. ASSERT: Verify the operation results
    assert len(day_10_bills) >= len(day_10_bill_ids)
    assert len(day_15_bills) >= len(day_15_bill_ids)

    # Check that all day 10 bills are returned
    for bill_id in day_10_bill_ids:
        assert any(bill.id == bill_id for bill in day_10_bills)

    # Check that all day 15 bills are returned
    for bill_id in day_15_bill_ids:
        assert any(bill.id == bill_id for bill in day_15_bills)

    # We didn't create any day 5 bills in our fixtures
    # There might be some from other tests, but none of ours
    for bill in day_5_bills:
        assert bill.id not in [b.id for b in test_multiple_recurring_bills]


async def test_get_with_relationships(
    recurring_bill_repository: RecurringBillRepository,
    test_recurring_bill: RecurringBill,
    test_checking_account: Account,
    test_category: Category,
):
    """Test retrieving a recurring bill with relationships."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get recurring bill with different relationship combinations
    bill_with_account = await recurring_bill_repository.get_with_relationships(
        test_recurring_bill.id, include_account=True
    )

    bill_with_category = await recurring_bill_repository.get_with_relationships(
        test_recurring_bill.id, include_category=True
    )

    bill_with_all = await recurring_bill_repository.get_with_relationships(
        test_recurring_bill.id,
        include_account=True,
        include_category=True,
        include_liabilities=True,
    )

    # 3. ASSERT: Verify the operation results
    # Check bill with account relationship
    assert bill_with_account.account is not None
    assert bill_with_account.account.id == test_checking_account.id
    assert bill_with_account.account.name == test_checking_account.name
    assert (
        not hasattr(bill_with_account, "category") or bill_with_account.category is None
    )

    # Check bill with category relationship
    assert bill_with_category.category is not None
    assert bill_with_category.category.id == test_category.id
    assert bill_with_category.category.name == test_category.name
    assert (
        not hasattr(bill_with_category, "account") or bill_with_category.account is None
    )

    # Check bill with all relationships
    assert bill_with_all.account is not None
    assert bill_with_all.account.id == test_checking_account.id
    assert bill_with_all.category is not None
    assert bill_with_all.category.id == test_category.id
    assert hasattr(bill_with_all, "liabilities")


async def test_get_by_account_id(
    recurring_bill_repository: RecurringBillRepository,
    account_repository: AccountRepository,
    test_category: Category,
):
    """Test retrieving recurring bills by account ID."""
    # 1. ARRANGE: Create two accounts and bills for each

    # 2. SCHEMA: Create accounts through schema validation
    account1_schema = create_account_schema(
        name="Account A for Bill Test",
        account_type="checking",
        available_balance=Decimal("1000.00"),
    )

    account2_schema = create_account_schema(
        name="Account B for Bill Test",
        account_type="savings",
        available_balance=Decimal("2000.00"),
    )

    # Convert and create accounts
    account1 = await account_repository.create(account1_schema.model_dump())
    account2 = await account_repository.create(account2_schema.model_dump())

    # Create bills for account 1
    bill1_schema = create_recurring_bill_schema(
        bill_name="Account 1 Bill 1",
        amount=Decimal("50.00"),
        day_of_month=5,
        account_id=account1.id,
        category_id=test_category.id,
    )

    bill2_schema = create_recurring_bill_schema(
        bill_name="Account 1 Bill 2",
        amount=Decimal("75.00"),
        day_of_month=10,
        account_id=account1.id,
        category_id=test_category.id,
    )

    # Create bill for account 2
    bill3_schema = create_recurring_bill_schema(
        bill_name="Account 2 Bill",
        amount=Decimal("100.00"),
        day_of_month=15,
        account_id=account2.id,
        category_id=test_category.id,
    )

    # Convert and create bills
    bill1 = await recurring_bill_repository.create(bill1_schema.model_dump())
    bill2 = await recurring_bill_repository.create(bill2_schema.model_dump())
    bill3 = await recurring_bill_repository.create(bill3_schema.model_dump())

    # 3. ACT: Get bills by account ID
    account1_bills = await recurring_bill_repository.get_by_account_id(account1.id)
    account2_bills = await recurring_bill_repository.get_by_account_id(account2.id)

    # 4. ASSERT: Verify the operation results
    assert len(account1_bills) >= 2
    assert any(bill.id == bill1.id for bill in account1_bills)
    assert any(bill.id == bill2.id for bill in account1_bills)
    assert not any(bill.id == bill3.id for bill in account1_bills)

    assert len(account2_bills) >= 1
    assert any(bill.id == bill3.id for bill in account2_bills)
    assert not any(bill.id == bill1.id for bill in account2_bills)
    assert not any(bill.id == bill2.id for bill in account2_bills)


async def test_toggle_active(
    recurring_bill_repository: RecurringBillRepository,
    test_recurring_bill: RecurringBill,
):
    """Test toggling the active status of a recurring bill."""
    # 1. ARRANGE: Setup is already done with fixtures
    initial_active_status = test_recurring_bill.active

    # 2. ACT: Toggle active status
    toggled_bill = await recurring_bill_repository.toggle_active(test_recurring_bill.id)

    # 3. ASSERT: Verify the operation results
    assert toggled_bill.active is not initial_active_status

    # 4. ACT: Toggle again
    toggled_again = await recurring_bill_repository.toggle_active(
        test_recurring_bill.id
    )

    # 5. ASSERT: Verify the operation results
    assert toggled_again.active is initial_active_status


async def test_toggle_auto_pay(
    recurring_bill_repository: RecurringBillRepository,
    test_recurring_bill: RecurringBill,
):
    """Test toggling the auto-pay status of a recurring bill."""
    # 1. ARRANGE: Setup is already done with fixtures
    initial_auto_pay_status = test_recurring_bill.auto_pay

    # 2. ACT: Toggle auto-pay status
    toggled_bill = await recurring_bill_repository.toggle_auto_pay(
        test_recurring_bill.id
    )

    # 3. ASSERT: Verify the operation results
    assert toggled_bill.auto_pay is not initial_auto_pay_status

    # 4. ACT: Toggle again
    toggled_again = await recurring_bill_repository.toggle_auto_pay(
        test_recurring_bill.id
    )

    # 5. ASSERT: Verify the operation results
    assert toggled_again.auto_pay is initial_auto_pay_status


async def test_get_monthly_total(
    recurring_bill_repository: RecurringBillRepository,
    test_multiple_recurring_bills: List[RecurringBill],
):
    """Test calculating total amount of all active recurring bills."""
    # 1. ARRANGE: Calculate expected total from active bills in fixtures
    active_bills = [bill for bill in test_multiple_recurring_bills if bill.active]
    expected_active_total = sum(bill.amount for bill in active_bills)

    # 2. ACT: Get monthly total
    total = await recurring_bill_repository.get_monthly_total()

    # 3. ASSERT: Verify the operation results
    assert total >= expected_active_total

    # 4. ARRANGE: Deactivate one bill
    first_active_bill = next(
        bill for bill in test_multiple_recurring_bills if bill.active
    )
    await recurring_bill_repository.toggle_active(first_active_bill.id)
    new_expected_total = expected_active_total - first_active_bill.amount

    # 5. ACT: Get updated monthly total
    new_total = await recurring_bill_repository.get_monthly_total()

    # 6. ASSERT: Verify the operation results
    assert new_total >= new_expected_total
    assert new_total < total


async def test_get_upcoming_bills(
    recurring_bill_repository: RecurringBillRepository,
    test_multiple_recurring_bills: List[RecurringBill],
):
    """Test retrieving upcoming bills within a date range."""
    # 1. ARRANGE: Setup date range for upcoming bills
    today = date.today()
    start_date = today
    end_date = today + timedelta(days=45)  # Cover at least one full month

    # 2. ACT: Get upcoming bills in date range
    upcoming_bills = await recurring_bill_repository.get_upcoming_bills(
        start_date, end_date
    )

    # 3. ASSERT: Verify the operation results
    assert len(upcoming_bills) >= len(test_multiple_recurring_bills)

    # Verify dates are within range
    for bill, due_date in upcoming_bills:
        assert start_date <= due_date <= end_date

    # Check that all our test bills are included at least once
    for test_bill in test_multiple_recurring_bills:
        if test_bill.active:  # Only active bills are returned
            bill_found = False
            for bill, _ in upcoming_bills:
                if bill.id == test_bill.id:
                    bill_found = True
                    break
            assert bill_found, f"Bill {test_bill.id} not found in upcoming bills"


async def test_validation_error_handling():
    """Test handling of validation errors that would be caught by the Pydantic schema."""
    # Try creating a schema with invalid data
    try:
        invalid_schema = RecurringBillCreate(
            bill_name="",  # Invalid empty name
            amount=Decimal("-50.00"),  # Invalid negative amount
            day_of_month=32,  # Invalid day of month
            account_id=999,  # Non-existent account ID
            category_id=999,  # Non-existent category ID
        )
        assert False, "Schema should have raised a validation error"
    except ValueError as e:
        # This is expected - schema validation should catch the error
        error_str = str(e).lower()
        assert (
            "bill_name" in error_str
            or "amount" in error_str
            or "day_of_month" in error_str
        )
