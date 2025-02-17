import pytest
from datetime import datetime
from decimal import Decimal

from src.models.recurring_bills import RecurringBill
from src.models.accounts import Account
from src.models.categories import Category
from src.models.base_model import naive_utc_now, naive_utc_from_date

@pytest.fixture(scope="function")
async def recurring_category(db_session):
    """Create a test category for recurring bills"""
    category = Category(
        name="Recurring",
        description="Recurring monthly bills",
        created_at=naive_utc_now(),
        updated_at=naive_utc_now()
    )
    db_session.add(category)
    await db_session.flush()
    await db_session.refresh(category)
    return category

@pytest.fixture(scope="function")
async def checking_account(db_session):
    """Create a test checking account"""
    account = Account(
        name="Test Checking",
        type="checking",
        available_balance=Decimal('1000.00'),
        created_at=naive_utc_now(),
        updated_at=naive_utc_now()
    )
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)
    return account

@pytest.fixture(scope="function")
async def recurring_bill(db_session, checking_account, recurring_category):
    """Create a test recurring bill instance"""
    bill = RecurringBill(
        bill_name="Netflix",
        amount=Decimal('19.99'),
        day_of_month=15,
        account=checking_account,
        category=recurring_category,
        auto_pay=True,
        active=True,
        created_at=naive_utc_now(),
        updated_at=naive_utc_now()
    )
    db_session.add(bill)
    await db_session.flush()
    await db_session.refresh(bill)
    return bill

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
async def test_recurring_bill_account_relationship(db_session, recurring_bill, checking_account):
    """Test relationship with Account model"""
    # Refresh the objects to ensure relationships are loaded
    await db_session.refresh(recurring_bill, ['account'])
    await db_session.refresh(checking_account, ['recurring_bills'])
    
    assert recurring_bill.account == checking_account
    assert any(bill.id == recurring_bill.id for bill in checking_account.recurring_bills)

@pytest.mark.asyncio
async def test_recurring_bill_create_liability(db_session, recurring_bill):
    """Test creating a new Liability from recurring bill template"""
    # Create the liability
    liability = recurring_bill.create_liability("03", 2025)
    db_session.add(liability)
    await db_session.flush()
    await db_session.refresh(liability)
    
    # Verify the liability
    assert liability.name == "Netflix"
    assert liability.amount == Decimal('19.99')
    assert liability.due_date == naive_utc_from_date(2025, 3, 15)
    assert liability.auto_pay is True
    assert liability.primary_account_id == recurring_bill.account_id
    assert liability.category_id == recurring_bill.category_id
    assert liability.category.name == "Recurring"

@pytest.mark.asyncio
async def test_recurring_bill_str_representation(recurring_bill):
    """Test string representation of recurring bill"""
    expected = "<RecurringBill Netflix $19.99>"
    assert str(recurring_bill) == expected

@pytest.mark.asyncio
async def test_datetime_handling(db_session, checking_account, recurring_category):
    """Test proper datetime handling in recurring bills and generated liabilities"""
    # Create recurring bill
    bill = RecurringBill(
        bill_name="Test Bill",
        amount=Decimal('19.99'),
        day_of_month=15,
        account=checking_account,
        category=recurring_category,
        auto_pay=True,
        active=True,
        created_at=naive_utc_now(),
        updated_at=naive_utc_now()
    )
    db_session.add(bill)
    await db_session.flush()
    await db_session.refresh(bill)

    # Verify recurring bill datetime fields are naive
    assert bill.created_at.tzinfo is None
    assert bill.updated_at.tzinfo is None

    # Create and verify liability datetime handling
    liability = bill.create_liability("03", 2025)
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
