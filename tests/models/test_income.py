import pytest
from datetime import date
from decimal import Decimal

from src.models.income import Income
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
def income_record(checking_account):
    """Create a test income record"""
    income = Income(
        date=date.today(),
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
