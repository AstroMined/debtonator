"""
Integration tests for RecurringBillRepository.

This module contains tests that validate the behavior of the RecurringBillRepository
against a real database.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.categories import Category
from src.models.recurring_bills import RecurringBill
from src.repositories.accounts import AccountRepository
from src.repositories.categories import CategoryRepository
from src.repositories.recurring_bills import RecurringBillRepository


@pytest.mark.asyncio
async def test_create_recurring_bill(db_session: AsyncSession):
    """Test creating a recurring bill."""
    # Create dependencies first (account, category)
    account_repo = AccountRepository(db_session)
    category_repo = CategoryRepository(db_session)

    # Create test account
    account = await account_repo.create(
        {
            "name": "Test Account",
            "type": "checking",
            "available_balance": Decimal("1000.00"),
        }
    )

    # Create test category
    category = await category_repo.create({"name": "Test Category"})

    # Create repository
    repo = RecurringBillRepository(db_session)

    # Create recurring bill
    recurring_bill = await repo.create(
        {
            "bill_name": "Test Recurring Bill",
            "amount": Decimal("50.00"),
            "day_of_month": 15,
            "account_id": account.id,
            "category_id": category.id,
            "auto_pay": True,
        }
    )

    # Assert created bill
    assert recurring_bill.id is not None
    assert recurring_bill.bill_name == "Test Recurring Bill"
    assert recurring_bill.amount == Decimal("50.00")
    assert recurring_bill.day_of_month == 15
    assert recurring_bill.account_id == account.id
    assert recurring_bill.category_id == category.id
    assert recurring_bill.auto_pay is True
    assert recurring_bill.active is True


@pytest.mark.asyncio
async def test_get_by_name(db_session: AsyncSession):
    """Test retrieving a recurring bill by name."""
    # Setup dependencies
    account_repo = AccountRepository(db_session)
    category_repo = CategoryRepository(db_session)

    account = await account_repo.create(
        {
            "name": "Test Account 2",
            "type": "checking",
            "available_balance": Decimal("1000.00"),
        }
    )

    category = await category_repo.create({"name": "Test Category 2"})

    # Create repository and recurring bill
    repo = RecurringBillRepository(db_session)

    await repo.create(
        {
            "bill_name": "Unique Bill Name",
            "amount": Decimal("75.00"),
            "day_of_month": 20,
            "account_id": account.id,
            "category_id": category.id,
        }
    )

    # Test get_by_name
    bill = await repo.get_by_name("Unique Bill Name")

    # Assert
    assert bill is not None
    assert bill.bill_name == "Unique Bill Name"
    assert bill.amount == Decimal("75.00")

    # Test non-existent bill
    non_existent = await repo.get_by_name("Non Existent Bill")
    assert non_existent is None


@pytest.mark.asyncio
async def test_get_active_bills(db_session: AsyncSession):
    """Test retrieving all active recurring bills."""
    # Setup dependencies
    account_repo = AccountRepository(db_session)
    category_repo = CategoryRepository(db_session)

    account = await account_repo.create(
        {
            "name": "Test Account 3",
            "type": "checking",
            "available_balance": Decimal("1000.00"),
        }
    )

    category = await category_repo.create({"name": "Test Category 3"})

    # Create repository and recurring bills
    repo = RecurringBillRepository(db_session)

    bill1 = await repo.create(
        {
            "bill_name": "Active Bill 1",
            "amount": Decimal("100.00"),
            "day_of_month": 1,
            "account_id": account.id,
            "category_id": category.id,
            "active": True,
        }
    )

    bill2 = await repo.create(
        {
            "bill_name": "Active Bill 2",
            "amount": Decimal("200.00"),
            "day_of_month": 15,
            "account_id": account.id,
            "category_id": category.id,
            "active": True,
        }
    )

    inactive_bill = await repo.create(
        {
            "bill_name": "Inactive Bill",
            "amount": Decimal("300.00"),
            "day_of_month": 20,
            "account_id": account.id,
            "category_id": category.id,
            "active": False,
        }
    )

    # Test get_active_bills
    active_bills = await repo.get_active_bills()

    # Assert
    assert len(active_bills) >= 2  # May include bills from other tests
    assert any(bill.id == bill1.id for bill in active_bills)
    assert any(bill.id == bill2.id for bill in active_bills)
    assert not any(bill.id == inactive_bill.id for bill in active_bills)


@pytest.mark.asyncio
async def test_get_by_day_of_month(db_session: AsyncSession):
    """Test retrieving recurring bills by day of month."""
    # Setup dependencies
    account_repo = AccountRepository(db_session)
    category_repo = CategoryRepository(db_session)

    account = await account_repo.create(
        {
            "name": "Test Account 4",
            "type": "checking",
            "available_balance": Decimal("1000.00"),
        }
    )

    category = await category_repo.create({"name": "Test Category 4"})

    # Create repository and recurring bills
    repo = RecurringBillRepository(db_session)

    day10_bill1 = await repo.create(
        {
            "bill_name": "Day 10 Bill 1",
            "amount": Decimal("50.00"),
            "day_of_month": 10,
            "account_id": account.id,
            "category_id": category.id,
        }
    )

    day10_bill2 = await repo.create(
        {
            "bill_name": "Day 10 Bill 2",
            "amount": Decimal("75.00"),
            "day_of_month": 10,
            "account_id": account.id,
            "category_id": category.id,
        }
    )

    day15_bill = await repo.create(
        {
            "bill_name": "Day 15 Bill",
            "amount": Decimal("100.00"),
            "day_of_month": 15,
            "account_id": account.id,
            "category_id": category.id,
        }
    )

    # Test get_by_day_of_month
    day10_bills = await repo.get_by_day_of_month(10)
    day15_bills = await repo.get_by_day_of_month(15)
    day20_bills = await repo.get_by_day_of_month(20)

    # Assert
    assert len(day10_bills) >= 2  # May include bills from other tests
    assert any(bill.id == day10_bill1.id for bill in day10_bills)
    assert any(bill.id == day10_bill2.id for bill in day10_bills)

    assert len(day15_bills) >= 1  # May include bills from other tests
    assert any(bill.id == day15_bill.id for bill in day15_bills)

    # Day 20 shouldn't include any of our test bills
    assert not any(
        bill.id in [day10_bill1.id, day10_bill2.id, day15_bill.id]
        for bill in day20_bills
    )


@pytest.mark.asyncio
async def test_get_with_relationships(db_session: AsyncSession):
    """Test retrieving a recurring bill with relationships."""
    # Setup dependencies
    account_repo = AccountRepository(db_session)
    category_repo = CategoryRepository(db_session)

    account = await account_repo.create(
        {
            "name": "Test Account 5",
            "type": "checking",
            "available_balance": Decimal("1000.00"),
        }
    )

    category = await category_repo.create({"name": "Test Category 5"})

    # Create repository and recurring bill
    repo = RecurringBillRepository(db_session)

    bill = await repo.create(
        {
            "bill_name": "Relationship Test Bill",
            "amount": Decimal("150.00"),
            "day_of_month": 25,
            "account_id": account.id,
            "category_id": category.id,
        }
    )

    # Test get_with_relationships with different combinations
    bill_with_account = await repo.get_with_relationships(bill.id, include_account=True)

    bill_with_category = await repo.get_with_relationships(
        bill.id, include_category=True
    )

    bill_with_all = await repo.get_with_relationships(
        bill.id, include_account=True, include_category=True, include_liabilities=True
    )

    # Assert
    assert bill_with_account.account is not None
    assert bill_with_account.account.id == account.id
    assert bill_with_account.account.name == "Test Account 5"

    assert bill_with_category.category is not None
    assert bill_with_category.category.id == category.id
    assert bill_with_category.category.name == "Test Category 5"

    assert bill_with_all.account is not None
    assert bill_with_all.category is not None
    assert hasattr(bill_with_all, "liabilities")


@pytest.mark.asyncio
async def test_get_by_account_id(db_session: AsyncSession):
    """Test retrieving recurring bills by account ID."""
    # Setup dependencies
    account_repo = AccountRepository(db_session)
    category_repo = CategoryRepository(db_session)

    account1 = await account_repo.create(
        {
            "name": "Test Account 6A",
            "type": "checking",
            "available_balance": Decimal("1000.00"),
        }
    )

    account2 = await account_repo.create(
        {
            "name": "Test Account 6B",
            "type": "checking",
            "available_balance": Decimal("2000.00"),
        }
    )

    category = await category_repo.create({"name": "Test Category 6"})

    # Create repository and recurring bills
    repo = RecurringBillRepository(db_session)

    bill1_account1 = await repo.create(
        {
            "bill_name": "Account 1 Bill 1",
            "amount": Decimal("50.00"),
            "day_of_month": 5,
            "account_id": account1.id,
            "category_id": category.id,
        }
    )

    bill2_account1 = await repo.create(
        {
            "bill_name": "Account 1 Bill 2",
            "amount": Decimal("75.00"),
            "day_of_month": 10,
            "account_id": account1.id,
            "category_id": category.id,
        }
    )

    bill_account2 = await repo.create(
        {
            "bill_name": "Account 2 Bill",
            "amount": Decimal("100.00"),
            "day_of_month": 15,
            "account_id": account2.id,
            "category_id": category.id,
        }
    )

    # Test get_by_account_id
    account1_bills = await repo.get_by_account_id(account1.id)
    account2_bills = await repo.get_by_account_id(account2.id)

    # Assert
    assert len(account1_bills) >= 2  # May include bills from other tests
    assert any(bill.id == bill1_account1.id for bill in account1_bills)
    assert any(bill.id == bill2_account1.id for bill in account1_bills)

    assert len(account2_bills) >= 1  # May include bills from other tests
    assert any(bill.id == bill_account2.id for bill in account2_bills)


@pytest.mark.asyncio
async def test_toggle_functions(db_session: AsyncSession):
    """Test toggle_active and toggle_auto_pay functions."""
    # Setup dependencies
    account_repo = AccountRepository(db_session)
    category_repo = CategoryRepository(db_session)

    account = await account_repo.create(
        {
            "name": "Test Account 7",
            "type": "checking",
            "available_balance": Decimal("1000.00"),
        }
    )

    category = await category_repo.create({"name": "Test Category 7"})

    # Create repository and recurring bill
    repo = RecurringBillRepository(db_session)

    bill = await repo.create(
        {
            "bill_name": "Toggle Test Bill",
            "amount": Decimal("125.00"),
            "day_of_month": 20,
            "account_id": account.id,
            "category_id": category.id,
            "active": True,
            "auto_pay": False,
        }
    )

    # Test toggle_active
    toggled_bill = await repo.toggle_active(bill.id)
    assert toggled_bill.active is False

    # Toggle again
    toggled_bill = await repo.toggle_active(bill.id)
    assert toggled_bill.active is True

    # Test toggle_auto_pay
    toggled_bill = await repo.toggle_auto_pay(bill.id)
    assert toggled_bill.auto_pay is True

    # Toggle again
    toggled_bill = await repo.toggle_auto_pay(bill.id)
    assert toggled_bill.auto_pay is False


@pytest.mark.asyncio
async def test_get_monthly_total(db_session: AsyncSession):
    """Test calculating total amount of all active recurring bills."""
    # Setup dependencies
    account_repo = AccountRepository(db_session)
    category_repo = CategoryRepository(db_session)

    account = await account_repo.create(
        {
            "name": "Test Account 8",
            "type": "checking",
            "available_balance": Decimal("1000.00"),
        }
    )

    category = await category_repo.create({"name": "Test Category 8"})

    # Create repository and recurring bills
    repo = RecurringBillRepository(db_session)

    # Get initial total (may include bills from other tests)
    initial_total = await repo.get_monthly_total()

    # Create test bills
    active_bill1 = await repo.create(
        {
            "bill_name": "Active Total Bill 1",
            "amount": Decimal("100.00"),
            "day_of_month": 5,
            "account_id": account.id,
            "category_id": category.id,
            "active": True,
        }
    )

    active_bill2 = await repo.create(
        {
            "bill_name": "Active Total Bill 2",
            "amount": Decimal("200.00"),
            "day_of_month": 15,
            "account_id": account.id,
            "category_id": category.id,
            "active": True,
        }
    )

    inactive_bill = await repo.create(
        {
            "bill_name": "Inactive Total Bill",
            "amount": Decimal("500.00"),
            "day_of_month": 25,
            "account_id": account.id,
            "category_id": category.id,
            "active": False,
        }
    )

    # Test get_monthly_total
    new_total = await repo.get_monthly_total()

    # Assert
    assert new_total >= initial_total + Decimal(
        "300.00"
    )  # Active bills should be included

    # Verify by toggling active status
    await repo.toggle_active(active_bill1.id)  # Now inactive
    adjusted_total = await repo.get_monthly_total()
    assert adjusted_total >= initial_total + Decimal("200.00")
    assert adjusted_total < new_total


@pytest.mark.asyncio
async def test_get_upcoming_bills(db_session: AsyncSession):
    """Test retrieving upcoming bills within a date range."""
    # Setup dependencies
    account_repo = AccountRepository(db_session)
    category_repo = CategoryRepository(db_session)

    account = await account_repo.create(
        {
            "name": "Test Account 9",
            "type": "checking",
            "available_balance": Decimal("1000.00"),
        }
    )

    category = await category_repo.create({"name": "Test Category 9"})

    # Create repository and recurring bills
    repo = RecurringBillRepository(db_session)

    day5_bill = await repo.create(
        {
            "bill_name": "Day 5 Bill",
            "amount": Decimal("50.00"),
            "day_of_month": 5,
            "account_id": account.id,
            "category_id": category.id,
        }
    )

    day15_bill = await repo.create(
        {
            "bill_name": "Day 15 Bill",
            "amount": Decimal("100.00"),
            "day_of_month": 15,
            "account_id": account.id,
            "category_id": category.id,
        }
    )

    day25_bill = await repo.create(
        {
            "bill_name": "Day 25 Bill",
            "amount": Decimal("150.00"),
            "day_of_month": 25,
            "account_id": account.id,
            "category_id": category.id,
        }
    )

    # Define date range that includes next month (to ensure we get multiple occurrences)
    today = date.today()
    start_date = today
    end_date = today + timedelta(days=45)  # Ensure we cover at least one full month

    # Test get_upcoming_bills
    upcoming_bills = await repo.get_upcoming_bills(start_date, end_date)

    # Assert
    assert len(upcoming_bills) >= 3  # At least our 3 bills, maybe more from other tests

    # Verify dates are within range
    for bill, due_date in upcoming_bills:
        assert start_date <= due_date <= end_date

    # Verify bills are included (at least one occurrence of each)
    day5_bill_found = False
    day15_bill_found = False
    day25_bill_found = False

    for bill, due_date in upcoming_bills:
        if bill.id == day5_bill.id:
            day5_bill_found = True
        elif bill.id == day15_bill.id:
            day15_bill_found = True
        elif bill.id == day25_bill.id:
            day25_bill_found = True

    assert day5_bill_found
    assert day15_bill_found
    assert day25_bill_found
