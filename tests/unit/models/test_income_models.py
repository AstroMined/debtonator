from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.income import Income
from src.utils.datetime_utils import naive_utc_from_date

pytestmark = pytest.mark.asyncio


async def test_income_creation(test_income_record: Income):
    """Test basic income record creation and attributes"""
    assert isinstance(test_income_record, Income)
    assert test_income_record.source == "Salary"
    assert test_income_record.amount == Decimal("2000.00")
    assert test_income_record.deposited is False
    # Note: undeposited_amount is a calculated field maintained by the service layer
    assert test_income_record.undeposited_amount is not None


async def test_income_account_relationship(
    db_session: AsyncSession, test_income_record: Income, test_checking_account: Account
):
    """Test relationship with Account model"""
    await db_session.refresh(test_income_record, ["account"])
    await db_session.refresh(test_checking_account, ["income"])

    assert test_income_record.account == test_checking_account
    assert test_income_record in test_checking_account.income


async def test_income_str_representation(test_income_record):
    """Test string representation of income record"""
    expected = "<Income Salary 2000.00>"
    assert str(test_income_record) == expected


async def test_datetime_handling(
    db_session: AsyncSession, test_checking_account: Account
):
    """Test proper datetime handling in income records"""
    # Create income with explicit datetime values
    income = Income(
        account_id=test_checking_account.id,
        date=naive_utc_from_date(2025, 3, 15),
        source="Test Income",
        amount=Decimal("1000.00"),
        deposited=False,
    )

    db_session.add(income)
    await db_session.commit()
    await db_session.refresh(income)

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
