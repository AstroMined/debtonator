from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.categories import Category
from src.models.recurring_bills import RecurringBill
from src.utils.datetime_utils import naive_utc_from_date, naive_utc_now

pytestmark = pytest.mark.asyncio


async def test_recurring_bill_creation(test_recurring_bill: RecurringBill):
    """Test basic recurring bill creation and attributes"""
    assert isinstance(test_recurring_bill, RecurringBill)
    assert test_recurring_bill.bill_name == "Test Recurring Bill"
    assert test_recurring_bill.amount == Decimal("50.00")
    assert test_recurring_bill.day_of_month == 15
    assert test_recurring_bill.auto_pay is True
    assert test_recurring_bill.active is True


async def test_recurring_bill_account_relationship(
    db_session: AsyncSession,
    test_recurring_bill: RecurringBill,
    test_checking_account: Account,
):
    """Test relationship with Account model"""
    # Refresh the objects to ensure relationships are loaded
    await db_session.refresh(test_recurring_bill, ["account"])
    await db_session.refresh(test_checking_account, ["recurring_bills"])

    assert test_recurring_bill.account == test_checking_account
    assert any(
        bill.id == test_recurring_bill.id
        for bill in test_checking_account.recurring_bills
    )


async def test_liability_creation_from_recurring_bill(
    db_session: AsyncSession, test_recurring_bill: RecurringBill
):
    """Test proper creation of liability model from recurring bill template"""
    # Import here to avoid circular imports
    from src.services.recurring_bills import RecurringBillService

    # Create service and use service method instead of model method
    service = RecurringBillService(db_session)
    liability = service.create_liability_from_recurring(test_recurring_bill, "03", 2025)
    db_session.add(liability)
    await db_session.flush()
    await db_session.refresh(liability)

    # Verify the liability has all the right properties
    assert liability.name == "Test Recurring Bill"
    assert liability.amount == Decimal("50.00")
    assert liability.due_date == naive_utc_from_date(2025, 3, 15)
    assert liability.auto_pay is True
    assert liability.primary_account_id == test_recurring_bill.account_id
    assert liability.category_id == test_recurring_bill.category_id
    assert liability.category.name == "Recurring"

    # This test confirms that the service method correctly sets all fields
    # previously set by the model method, in accordance with ADR-012


async def test_recurring_bill_str_representation(test_recurring_bill: RecurringBill):
    """Test string representation of recurring bill"""
    expected = "<RecurringBill Test Recurring Bill $50.00>"
    assert str(test_recurring_bill) == expected


async def test_datetime_handling(
    db_session: AsyncSession,
    test_checking_account: Account,
    test_recurring_category: Category,
):
    """Test proper datetime handling in recurring bills and generated liabilities"""
    # Create recurring bill
    bill = RecurringBill(
        bill_name="Test Bill",
        amount=Decimal("19.99"),
        day_of_month=15,
        account=test_checking_account,
        category=test_recurring_category,
        auto_pay=True,
        active=True,
        created_at=naive_utc_now(),
        updated_at=naive_utc_now(),
    )
    db_session.add(bill)
    await db_session.flush()
    await db_session.refresh(bill)

    # Verify recurring bill datetime fields are naive
    assert bill.created_at.tzinfo is None
    assert bill.updated_at.tzinfo is None

    # Create and verify liability datetime handling
    # Use service method instead of model method
    from src.services.recurring_bills import RecurringBillService

    service = RecurringBillService(db_session)
    liability = service.create_liability_from_recurring(bill, "03", 2025)
    db_session.add(liability)
    await db_session.flush()
    await db_session.refresh(liability)

    # Verify liability datetime fields are naive and correct
    assert liability.due_date.tzinfo is None
    assert liability.created_at.tzinfo is None
    assert liability.updated_at.tzinfo is None

    # Verify due_date components
    assert liability.due_date.year == 2025
    assert liability.due_date.month == 3
    assert liability.due_date.day == 15
    assert liability.due_date.hour == 0
    assert liability.due_date.minute == 0
    assert liability.due_date.second == 0
