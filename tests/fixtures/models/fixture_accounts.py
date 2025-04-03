from decimal import Decimal
from typing import List

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.utils.datetime_utils import naive_utc_now


@pytest_asyncio.fixture
async def test_checking_account(db_session: AsyncSession) -> Account:
    """Primary Test Checking for use in various tests"""
    checking_account = Account(
        name="Primary Test Checking",
        account_type="checking",
        available_balance=Decimal("1000.00"),
        created_at=naive_utc_now(),
        updated_at=naive_utc_now(),
    )
    db_session.add(checking_account)
    await db_session.commit()
    await db_session.refresh(checking_account)
    return checking_account


@pytest_asyncio.fixture
async def test_savings_account(db_session: AsyncSession) -> Account:
    """Fixture to create a second test account for recurring income."""
    # Create model instance directly
    account = Account(
        name="Test Savings Account",
        account_type="savings",
        available_balance=Decimal("500.00"),
    )

    # Add to session manually
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)

    return account


@pytest_asyncio.fixture
async def test_second_account(db_session: AsyncSession) -> Account:
    """Create a second test account for use in split payment tests."""
    # Create model instance directly
    account = Account(
        name="Second Checking Account",
        account_type="checking",
        available_balance=Decimal("2000.00"),
    )

    # Add to session manually
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)

    return account


@pytest_asyncio.fixture
async def test_multiple_accounts(db_session: AsyncSession) -> List[Account]:
    """Create multiple test accounts of different types."""
    # Create accounts of different types
    account_types = [
        ("Checking A", "checking", Decimal("1200.00")),
        ("Savings B", "savings", Decimal("5000.00")),
        ("Credit Card C", "credit", Decimal("-700.00")),
        (
            "Investment D",
            "savings",
            Decimal("10000.00"),
        ),  # Changed from "investment" to "savings"
    ]

    accounts = []
    for name, acc_type, balance in account_types:
        # Create model instance directly
        account = Account(
            name=name,
            account_type=acc_type,
            available_balance=balance,
            total_limit=Decimal("3000.00") if acc_type == "credit" else None,
            available_credit=Decimal("2300.00") if acc_type == "credit" else None,
        )

        # Add to session manually
        db_session.add(account)
        accounts.append(account)

    # Flush to get IDs and establish database rows
    await db_session.flush()

    # Refresh all entries to make sure they reflect what's in the database
    for account in accounts:
        await db_session.refresh(account)

    return accounts


@pytest_asyncio.fixture
async def test_credit_account(db_session: AsyncSession) -> Account:
    """Test credit account for use in various tests"""
    credit_account = Account(
        name="Test Credit Card",
        account_type="credit",
        available_balance=Decimal("-500.00"),
        total_limit=Decimal("2000.00"),
        available_credit=Decimal("1500.00"),  # total_limit - abs(available_balance)
        created_at=naive_utc_now(),
        updated_at=naive_utc_now(),
    )
    db_session.add(credit_account)
    await db_session.commit()
    await db_session.refresh(credit_account)
    return credit_account
