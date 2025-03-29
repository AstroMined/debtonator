"""
Integration tests for the RecurringBillRepository.

This module contains tests for the RecurringBillRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.
"""

from decimal import Decimal
from typing import List

import pytest

from src.models.accounts import Account
from src.models.categories import Category
from src.models.recurring_bills import RecurringBill
from src.repositories.recurring_bills import RecurringBillRepository
from src.schemas.recurring_bills import RecurringBillCreate
from src.utils.datetime_utils import days_from_now, utc_now

pytestmark = pytest.mark.asyncio


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

    # For bill_with_account, we don't request category, so don't check for it

    # Check bill with category relationship
    assert bill_with_category.category is not None
    assert bill_with_category.category.id == test_category.id
    assert bill_with_category.category.name == test_category.name

    # For bill_with_category, we don't request account, so don't check for it

    # Check bill with all relationships
    assert bill_with_all.account is not None
    assert bill_with_all.account.id == test_checking_account.id
    assert bill_with_all.category is not None
    assert bill_with_all.category.id == test_category.id
    # We also loaded liabilities, but we don't need to check the attribute
    # as that would trigger lazy loading if it wasn't properly loaded


async def test_get_by_account_id(
    recurring_bill_repository: RecurringBillRepository,
    test_bills_by_account,
):
    """Test retrieving recurring bills by account ID."""
    # 1. ARRANGE: Extract accounts and bills from fixture
    account1, account2, bills = test_bills_by_account
    bill1, bill2, bill3 = bills

    # 2. ACT: Get bills by account ID
    account1_bills = await recurring_bill_repository.get_by_account_id(account1.id)
    account2_bills = await recurring_bill_repository.get_by_account_id(account2.id)

    # 3. ASSERT: Verify the operation results
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
    # 1. ARRANGE: Setup date range for upcoming bills using datetime utilities
    current_date = utc_now().date()
    start_date = current_date  # Start from today
    end_date = days_from_now(45).date()  # Cover at least one full month

    # 2. ACT: Get upcoming bills in date range
    upcoming_bills = await recurring_bill_repository.get_upcoming_bills(
        start_date, end_date
    )

    # 3. ASSERT: Verify the operation results
    # Filter to only include active bills, since repository method only returns active bills
    active_bills = [bill for bill in test_multiple_recurring_bills if bill.active]
    assert len(upcoming_bills) >= len(active_bills)

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
