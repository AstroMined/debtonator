"""
Unit tests for the base Account model.

Tests the Account model fields, constraints, and behavior
as part of ADR-016 Account Type Expansion.

Note: Specific account type tests are in their respective test files.
"""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.utils.datetime_utils import naive_utc_from_date

pytestmark = pytest.mark.asyncio


async def test_datetime_handling(db_session: AsyncSession):
    """Test proper datetime handling in Account model"""
    # Create account with explicit datetime values
    account = Account(
        name="Test Account",
        account_type="checking",  # Updated from type to account_type
        current_balance=Decimal("1000.00"),  # Updated from available_balance
        available_balance=Decimal("1000.00"),
        created_at=naive_utc_from_date(2025, 3, 15),
        updated_at=naive_utc_from_date(2025, 3, 15),
    )

    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    # Verify all datetime fields are naive (no tzinfo)
    assert account.created_at.tzinfo is None
    assert account.updated_at.tzinfo is None

    # Verify created_at components
    assert account.created_at.year == 2025
    assert account.created_at.month == 3
    assert account.created_at.day == 15
    assert account.created_at.hour == 0
    assert account.created_at.minute == 0
    assert account.created_at.second == 0

    # Verify updated_at components
    assert account.updated_at.year == 2025
    assert account.updated_at.month == 3
    assert account.updated_at.day == 15
    assert account.updated_at.hour == 0
    assert account.updated_at.minute == 0
    assert account.updated_at.second == 0


async def test_default_datetime_handling(db_session: AsyncSession):
    """Test default datetime values are properly set"""
    account = Account(
        name="Test Account",
        account_type="checking",  # Updated from type
        current_balance=Decimal("1000.00"),  # Added current_balance
        available_balance=Decimal("1000.00"),
    )

    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    # Verify created_at and updated_at are set and naive
    assert account.created_at is not None
    assert account.updated_at is not None
    assert account.created_at.tzinfo is None
    assert account.updated_at.tzinfo is None


async def test_create_test_checking_account(db_session: AsyncSession):
    """Test creating a base account with new fields from ADR-016"""
    account = Account(
        name="Basic Account",
        account_type="account",  # Using base polymorphic identity
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
        institution="Test Bank",
        currency="USD",
        account_number="12345678",
        url="https://test-bank.com",
        logo_path="/images/test-bank.png",
        is_closed=False,
        description="Test account description",
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    assert account.id is not None
    assert account.name == "Basic Account"
    assert account.account_type == "account"
    assert account.current_balance == Decimal("1000.00")
    assert account.available_balance == Decimal("1000.00")
    assert account.institution == "Test Bank"
    assert account.currency == "USD"
    assert account.account_number == "12345678"
    assert account.url == "https://test-bank.com"
    assert account.logo_path == "/images/test-bank.png"
    assert account.is_closed is False
    assert account.description == "Test account description"
    assert account.created_at.tzinfo is None
    assert account.updated_at.tzinfo is None


async def test_polymorphic_identity(db_session: AsyncSession):
    """Test account polymorphic identity behavior"""
    # Create a base account
    account = Account(
        name="Polymorphic Test",
        account_type="account",  # Base polymorphic identity
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    # Verify it was created as the base Account type
    retrieved_account = await db_session.get(Account, account.id)
    assert retrieved_account is not None
    assert (
        type(retrieved_account) is Account
    )  # Should be exactly Account, not a subclass
    assert retrieved_account.account_type == "account"


async def test_next_action_fields(db_session: AsyncSession):
    """Test the next action tracking fields"""
    next_date = naive_utc_from_date(2025, 5, 10)
    account = Account(
        name="Action Test",
        account_type="account",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
        next_action_date=next_date,
        next_action_amount=Decimal("150.00"),
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    assert account.next_action_date == next_date
    assert account.next_action_amount == Decimal("150.00")


async def test_update_account_balance(db_session: AsyncSession):
    """Test updating an account's balance"""
    # Create the account first
    account = Account(
        name="Balance Test",
        account_type="checking",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)

    # Add $500 to the balance
    account.current_balance += Decimal("500.00")
    account.available_balance += Decimal("500.00")
    await db_session.commit()
    await db_session.refresh(account)

    assert account.current_balance == Decimal("1500.00")
    assert account.available_balance == Decimal("1500.00")
    assert account.created_at.tzinfo is None
    assert account.updated_at.tzinfo is None


async def test_account_repr(db_session: AsyncSession):
    """Test the __repr__ method of Account model"""
    account = Account(name="Repr Test", account_type="checking")
    db_session.add(account)
    await db_session.commit()

    # Test the __repr__ method - updated format includes id and account_type
    assert (
        f"<Account(id={account.id}, name={account.name}, type={account.account_type})>"
        in repr(account)
    )


async def test_decimal_precision_storage(db_session: AsyncSession):
    """Test four decimal place precision storage for account balances and limits."""
    # Test with 4 decimal places in money fields
    account = Account(
        name="Four Decimal Account",
        account_type="checking",
        current_balance=Decimal("1000.1234"),
        available_balance=Decimal("1000.5678"),
        next_action_amount=Decimal("500.9876"),
    )
    db_session.add(account)
    await db_session.commit()

    # Verify storage with 4 decimal places
    await db_session.refresh(account)
    assert account.current_balance == Decimal("1000.1234")
    assert account.available_balance == Decimal("1000.5678")
    assert account.next_action_amount == Decimal("500.9876")

    # Verify decimal precision for each field
    assert account.current_balance.as_tuple().exponent == -4
    assert account.available_balance.as_tuple().exponent == -4
    assert account.next_action_amount.as_tuple().exponent == -4
