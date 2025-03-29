from datetime import date
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.categories import Category
from src.models.liabilities import Liability
from src.models.recurring_bills import RecurringBill
from src.schemas.recurring_bills import RecurringBillCreate, RecurringBillUpdate
from src.services.recurring_bills import RecurringBillService


@pytest.fixture
async def account(db_session: AsyncSession) -> Account:
    """Create a test account"""
    account = Account(
        name="Test Account",
        type="checking",
        available_balance=Decimal("1000.00"),
        created_at=date.today(),
        updated_at=date.today(),
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account


@pytest.fixture
async def test_category(db_session: AsyncSession) -> Category:
    """Create a test category"""
    category = Category(
        name="Test Category",
        description="Test Description",
        created_at=date.today(),
        updated_at=date.today(),
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


@pytest.fixture
async def recurring_bill(
    db_session: AsyncSession, account: Account, test_category: Category
) -> RecurringBill:
    """Create a test recurring bill"""
    bill = RecurringBill(
        bill_name="Test Bill",
        amount=Decimal("100.00"),
        day_of_month=15,
        account_id=account.id,
        category_id=test_category.id,
        auto_pay=False,
        active=True,
        created_at=date.today(),
        updated_at=date.today(),
    )
    db_session.add(bill)
    await db_session.commit()
    await db_session.refresh(bill)
    return bill


@pytest.mark.asyncio
async def test_create_recurring_bill(
    db_session: AsyncSession, account: Account, test_category: Category
):
    """Test creating a recurring bill"""
    service = RecurringBillService(db_session)
    bill_create = RecurringBillCreate(
        bill_name="New Bill",
        amount=Decimal("150.00"),
        day_of_month=20,
        account_id=account.id,
        category_id=test_category.id,
        auto_pay=True,
    )

    bill = await service.create_recurring_bill(bill_create)
    assert bill.bill_name == "New Bill"
    assert bill.amount == Decimal("150.00")
    assert bill.day_of_month == 20
    assert bill.account_id == account.id
    assert bill.category_id == test_category.id
    assert bill.auto_pay is True
    assert bill.active is True


@pytest.mark.asyncio
async def test_get_recurring_bill(
    db_session: AsyncSession, recurring_bill: RecurringBill
):
    """Test retrieving a specific recurring bill"""
    service = RecurringBillService(db_session)

    bill = await service.get_recurring_bill(recurring_bill.id)
    assert bill is not None
    assert bill.id == recurring_bill.id
    assert bill.bill_name == recurring_bill.bill_name


@pytest.mark.asyncio
async def test_get_recurring_bills(
    db_session: AsyncSession, recurring_bill: RecurringBill
):
    """Test retrieving all recurring bills"""
    service = RecurringBillService(db_session)

    bills = await service.get_recurring_bills()
    assert len(bills) == 1
    assert bills[0].id == recurring_bill.id


@pytest.mark.asyncio
async def test_get_recurring_bills_active_only(
    db_session: AsyncSession, recurring_bill: RecurringBill
):
    """Test retrieving only active recurring bills"""
    service = RecurringBillService(db_session)

    # Create an inactive bill
    inactive_bill = RecurringBill(
        bill_name="Inactive Bill",
        amount=Decimal("75.00"),
        day_of_month=10,
        account_id=recurring_bill.account_id,
        category_id=recurring_bill.category_id,
        active=False,
    )
    db_session.add(inactive_bill)
    await db_session.commit()

    # Test active_only=True (default)
    active_bills = await service.get_recurring_bills()
    assert len(active_bills) == 1
    assert active_bills[0].id == recurring_bill.id

    # Test active_only=False
    all_bills = await service.get_recurring_bills(active_only=False)
    assert len(all_bills) == 2


@pytest.mark.asyncio
async def test_update_recurring_bill(
    db_session: AsyncSession, recurring_bill: RecurringBill
):
    """Test updating a recurring bill"""
    service = RecurringBillService(db_session)

    update_data = RecurringBillUpdate(
        bill_name="Updated Bill", amount=Decimal("200.00"), auto_pay=True
    )

    updated_bill = await service.update_recurring_bill(recurring_bill.id, update_data)
    assert updated_bill is not None
    assert updated_bill.bill_name == "Updated Bill"
    assert updated_bill.amount == Decimal("200.00")
    assert updated_bill.auto_pay is True
    # Fields not in update should remain unchanged
    assert updated_bill.day_of_month == recurring_bill.day_of_month


@pytest.mark.asyncio
async def test_update_nonexistent_recurring_bill(db_session: AsyncSession):
    """Test updating a non-existent recurring bill"""
    service = RecurringBillService(db_session)

    update_data = RecurringBillUpdate(
        bill_name="Updated Bill", amount=Decimal("200.00")
    )

    result = await service.update_recurring_bill(999, update_data)
    assert result is None


@pytest.mark.asyncio
async def test_delete_recurring_bill(
    db_session: AsyncSession, recurring_bill: RecurringBill
):
    """Test deleting a recurring bill"""
    service = RecurringBillService(db_session)

    # Delete the bill
    result = await service.delete_recurring_bill(recurring_bill.id)
    assert result is True

    # Verify it's deleted
    deleted_bill = await service.get_recurring_bill(recurring_bill.id)
    assert deleted_bill is None


@pytest.mark.asyncio
async def test_delete_nonexistent_recurring_bill(db_session: AsyncSession):
    """Test deleting a non-existent recurring bill"""
    service = RecurringBillService(db_session)
    result = await service.delete_recurring_bill(999)
    assert result is False


@pytest.mark.asyncio
async def test_generate_bills(db_session: AsyncSession, recurring_bill: RecurringBill):
    """Test generating liabilities from a recurring bill"""
    service = RecurringBillService(db_session)

    # Generate bills for next month
    today = date.today()
    next_month = today.month + 1 if today.month < 12 else 1
    next_year = today.year + 1 if today.month == 12 else today.year

    generated = await service.generate_bills(recurring_bill.id, next_month, next_year)
    assert len(generated) == 1

    liability = generated[0]
    assert isinstance(liability, Liability)
    assert liability.name == recurring_bill.bill_name
    assert liability.amount == recurring_bill.amount
    # Compare the date part of the datetime to a date object
    assert liability.due_date.date() == date(
        next_year, next_month, recurring_bill.day_of_month
    )
    assert liability.recurring_bill_id == recurring_bill.id
    assert liability.category_id == recurring_bill.category_id


@pytest.mark.asyncio
async def test_generate_bills_duplicate_prevention(
    db_session: AsyncSession, recurring_bill: RecurringBill
):
    """Test that bills aren't generated twice for the same period"""
    service = RecurringBillService(db_session)

    # Generate bills for next month
    today = date.today()
    next_month = today.month + 1 if today.month < 12 else 1
    next_year = today.year + 1 if today.month == 12 else today.year

    # First generation should succeed
    first_gen = await service.generate_bills(recurring_bill.id, next_month, next_year)
    assert len(first_gen) == 1

    # Second generation for same period should return empty list
    second_gen = await service.generate_bills(recurring_bill.id, next_month, next_year)
    assert len(second_gen) == 0


@pytest.mark.asyncio
async def test_generate_bills_inactive_bill(
    db_session: AsyncSession, recurring_bill: RecurringBill
):
    """Test that inactive bills don't generate liabilities"""
    service = RecurringBillService(db_session)

    # Deactivate the bill
    recurring_bill.active = False
    await db_session.commit()

    # Try to generate bills
    today = date.today()
    next_month = today.month + 1 if today.month < 12 else 1
    next_year = today.year + 1 if today.month == 12 else today.year

    generated = await service.generate_bills(recurring_bill.id, next_month, next_year)
    assert len(generated) == 0


@pytest.mark.asyncio
async def test_generate_bills_for_month(
    db_session: AsyncSession, recurring_bill: RecurringBill, account: Account
):
    """Test generating bills for all recurring bills in a month"""
    service = RecurringBillService(db_session)

    # Create another recurring bill
    second_bill = RecurringBill(
        bill_name="Second Bill",
        amount=Decimal("75.00"),
        day_of_month=20,
        account_id=account.id,
        category_id=recurring_bill.category_id,
        auto_pay=False,
        active=True,
    )
    db_session.add(second_bill)
    await db_session.commit()

    # Generate bills for next month
    today = date.today()
    next_month = today.month + 1 if today.month < 12 else 1
    next_year = today.year + 1 if today.month == 12 else today.year

    generated = await service.generate_bills_for_month(next_month, next_year)
    assert len(generated) == 2

    # Verify both bills were generated
    bill_names = {bill.name for bill in generated}
    assert "Test Bill" in bill_names
    assert "Second Bill" in bill_names
