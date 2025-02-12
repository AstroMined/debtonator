import pytest
from datetime import date
from decimal import Decimal

from src.models.recurring_bills import RecurringBill
from src.models.accounts import Account

@pytest.fixture
def checking_account():
    """Create a test checking account"""
    return Account(
        name="Test Checking",
        type="checking",
        available_balance=Decimal('1000.00')
    )

@pytest.fixture
def recurring_bill(checking_account):
    """Create a test recurring bill instance"""
    return RecurringBill(
        bill_name="Netflix",
        amount=Decimal('19.99'),
        day_of_month=15,
        account=checking_account,
        auto_pay=True,
        active=True
    )

@pytest.mark.asyncio
async def test_recurring_bill_creation(recurring_bill):
    """Test basic recurring bill creation and attributes"""
    assert isinstance(recurring_bill, RecurringBill)
    assert recurring_bill.bill_name == "Netflix"
    assert recurring_bill.amount == Decimal('19.99')
    assert recurring_bill.day_of_month == 15
    assert recurring_bill.auto_pay is True
    assert recurring_bill.active is True

@pytest.mark.asyncio
async def test_recurring_bill_account_relationship(recurring_bill, checking_account):
    """Test relationship with Account model"""
    assert recurring_bill.account == checking_account
    assert recurring_bill in checking_account.recurring_bills

@pytest.mark.asyncio
async def test_recurring_bill_create_liability(recurring_bill):
    """Test creating a new Liability from recurring bill template"""
    liability = recurring_bill.create_liability("03", 2025)
    assert liability.name == "Netflix"
    assert liability.amount == Decimal('19.99')
    assert liability.due_date == date(2025, 3, 15)
    assert liability.auto_pay is True
    assert liability.primary_account_id == recurring_bill.account_id
    assert liability.category == "Recurring"

@pytest.mark.asyncio
async def test_recurring_bill_str_representation(recurring_bill):
    """Test string representation of recurring bill"""
    expected = "<RecurringBill Netflix $19.99>"
    assert str(recurring_bill) == expected
