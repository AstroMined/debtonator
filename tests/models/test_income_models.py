import pytest
from datetime import datetime, timedelta
from decimal import Decimal

from src.models.income import Income
from src.models.accounts import Account
from src.models.base_model import naive_utc_now, naive_utc_from_date

pytestmark = pytest.mark.asyncio

@pytest.fixture
def checking_account():
    """Create a test checking account"""
    return Account(
        name="Test Checking",
        type="checking",
        available_balance=Decimal('1000.00'),
        created_at=naive_utc_now(),
        updated_at=naive_utc_now()
    )

@pytest.fixture
def income_record(checking_account):
    """Create a test income record"""
    income = Income(
        date=naive_utc_now(),
        source="Salary",
        amount=Decimal('2000.00'),
        deposited=False,
        account=checking_account
    )
    income.calculate_undeposited()
    return income

@pytest.mark.asyncio
async def test_income_creation(income_record):
    """Test basic income record creation and attributes"""
    assert isinstance(income_record, Income)
    assert income_record.source == "Salary"
    assert income_record.amount == Decimal('2000.00')
    assert income_record.deposited is False
    assert income_record.undeposited_amount == Decimal('2000.00')  # Should match amount when not deposited

@pytest.mark.asyncio
async def test_income_account_relationship(income_record, checking_account):
    """Test relationship with Account model"""
    assert income_record.account == checking_account
    assert income_record in checking_account.income

@pytest.mark.asyncio
async def test_calculate_undeposited_when_not_deposited(income_record):
    """Test undeposited amount calculation when income is not deposited"""
    income_record.calculate_undeposited()
    assert income_record.undeposited_amount == income_record.amount

@pytest.mark.asyncio
async def test_calculate_undeposited_when_deposited(income_record):
    """Test undeposited amount calculation when income is deposited"""
    income_record.deposited = True
    income_record.calculate_undeposited()
    assert income_record.undeposited_amount == Decimal('0')

@pytest.mark.asyncio
async def test_income_str_representation(income_record):
    """Test string representation of income record"""
    expected = "<Income Salary 2000.00>"
    assert str(income_record) == expected

@pytest.mark.asyncio
async def test_datetime_handling():
    """Test proper datetime handling in income records"""
    # Create income with explicit datetime values
    income = Income(
        date=naive_utc_from_date(2025, 3, 15),
        source="Test Income",
        amount=Decimal('1000.00'),
        deposited=False
    )

    # Verify all datetime fields are naive (no tzinfo)
    assert income.date.tzinfo is None
    assert income.created_at.tzinfo is None
    assert income.updated_at.tzinfo is None

    # Verify date components
    assert income.date.year == 2025
    assert income.date.month == 3
    assert income.date.day == 15
    assert income.date.hour == 0
    assert income.date.minute == 0
    assert income.date.second == 0
