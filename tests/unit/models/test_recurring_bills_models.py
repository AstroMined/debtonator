from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.recurring_bills import RecurringBill
from src.utils.datetime_utils import naive_utc_now

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


async def test_recurring_bill_str_representation(test_recurring_bill: RecurringBill):
    """Test string representation of recurring bill"""
    expected = "<RecurringBill Test Recurring Bill $50.00>"
    assert str(test_recurring_bill) == expected


async def test_datetime_handling(
    db_session: AsyncSession,
    test_checking_account: Account,
    test_recurring_category,
):
    """Test proper datetime handling in recurring bills"""
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
