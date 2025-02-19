from decimal import Decimal
from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.base_model import naive_utc_from_date, naive_utc_now

pytestmark = pytest.mark.asyncio


async def test_datetime_handling(db_session: AsyncSession):
    """Test proper datetime handling in Account model"""
    # Create checking_account with explicit datetime values
    checking_account = Account(
        name="Test Account",
        type="checking",
        available_balance=Decimal("1000.00"),
        created_at=naive_utc_from_date(2025, 3, 15),
        updated_at=naive_utc_from_date(2025, 3, 15)
    )

    db_session.add(checking_account)
    await db_session.commit()
    await db_session.refresh(checking_account)

    # Verify all datetime fields are naive (no tzinfo)
    assert checking_account.created_at.tzinfo is None
    assert checking_account.updated_at.tzinfo is None

    # Verify created_at components
    assert checking_account.created_at.year == 2025
    assert checking_account.created_at.month == 3
    assert checking_account.created_at.day == 15
    assert checking_account.created_at.hour == 0
    assert checking_account.created_at.minute == 0
    assert checking_account.created_at.second == 0

    # Verify updated_at components
    assert checking_account.updated_at.year == 2025
    assert checking_account.updated_at.month == 3
    assert checking_account.updated_at.day == 15
    assert checking_account.updated_at.hour == 0
    assert checking_account.updated_at.minute == 0
    assert checking_account.updated_at.second == 0

async def test_default_datetime_handling(db_session: AsyncSession):
    """Test default datetime values are properly set"""
    checking_account = Account(
        name="Test Account",
        type="checking",
        available_balance=Decimal("1000.00")
    )

    db_session.add(checking_account)
    await db_session.commit()
    await db_session.refresh(checking_account)

    # Verify created_at and updated_at are set and naive
    assert checking_account.created_at is not None
    assert checking_account.updated_at is not None
    assert checking_account.created_at.tzinfo is None
    assert checking_account.updated_at.tzinfo is None

async def test_create_checking_account(db_session: AsyncSession):
    """Test creating a checking account"""
    account = Account(
        name="Basic Checking Account",
        type="checking",
        available_balance=Decimal("1000.00")
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    assert account.id is not None
    assert account.name == "Basic Checking Account"
    assert account.type == "checking"
    assert account.available_balance == Decimal("1000.00")
    assert account.available_credit is None
    assert account.total_limit is None
    assert account.created_at.tzinfo is None
    assert account.updated_at.tzinfo is None

async def test_create_credit_account(db_session: AsyncSession):
    """Test creating a credit account with limit"""
    account = Account(
        name="Basic Credit Card",
        type="credit",
        total_limit=Decimal("2000.00"),
        available_balance=Decimal("-500.00"),
        available_credit=Decimal("1500.00")  # Set directly as this is now managed by service
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    assert account.id is not None
    assert account.name == "Basic Credit Card"
    assert account.type == "credit"
    assert account.available_balance == Decimal("-500.00")
    assert account.total_limit == Decimal("2000.00")
    assert account.available_credit == Decimal("1500.00")
    assert account.created_at.tzinfo is None
    assert account.updated_at.tzinfo is None

async def test_create_savings_account(db_session: AsyncSession):
    """Test creating a savings account"""
    account = Account(
        name="Basic Savings Account",
        type="savings",
        available_balance=Decimal("5000.00")
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    assert account.id is not None
    assert account.name == "Basic Savings Account"
    assert account.type == "savings"
    assert account.available_balance == Decimal("5000.00")
    assert account.available_credit is None
    assert account.total_limit is None
    assert account.created_at.tzinfo is None
    assert account.updated_at.tzinfo is None

async def test_update_account_balance(db_session: AsyncSession, base_account: Account):
    """Test updating an account's balance"""
    # Add $500 to the balance
    base_account.available_balance += Decimal("500.00")
    await db_session.commit()
    await db_session.refresh(base_account)

    assert base_account.available_balance == Decimal("1500.00")
    assert base_account.created_at.tzinfo is None
    assert base_account.updated_at.tzinfo is None
