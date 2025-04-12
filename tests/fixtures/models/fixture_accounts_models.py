from decimal import Decimal
from typing import List

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.checking import CheckingAccount
from src.models.account_types.banking.credit import CreditAccount
from src.models.account_types.banking.savings import SavingsAccount
from src.models.accounts import Account
from src.utils.datetime_utils import naive_utc_now


@pytest_asyncio.fixture
async def test_checking_account(db_session: AsyncSession) -> CheckingAccount:
    """
    Create a primary test checking account for use in various tests.

    Args:
        db_session: Database session fixture

    Returns:
        CheckingAccount: Created checking account
    """
    checking_account = CheckingAccount(
        name="Primary Test Checking",
        available_balance=Decimal("1000.00"),
        current_balance=Decimal("1000.00"),  # Added current_balance which is required
        created_at=naive_utc_now(),
        updated_at=naive_utc_now(),
    )
    db_session.add(checking_account)
    await db_session.flush()
    await db_session.refresh(checking_account)
    return checking_account


@pytest_asyncio.fixture
async def test_savings_account(db_session: AsyncSession) -> SavingsAccount:
    """
    Create a test savings account for recurring income.

    Args:
        db_session: Database session fixture

    Returns:
        SavingsAccount: Created savings account
    """
    # Create model instance directly using SavingsAccount
    account = SavingsAccount(
        name="Test Savings Account",
        available_balance=Decimal("500.00"),
        current_balance=Decimal("500.00"),  # Added current_balance which is required
    )

    # Add to session manually
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)

    return account


@pytest_asyncio.fixture
async def test_second_account(db_session: AsyncSession) -> CheckingAccount:
    """
    Create a second test checking account for use in split payment tests.

    Args:
        db_session: Database session fixture

    Returns:
        CheckingAccount: Created checking account
    """
    # Create model instance directly using CheckingAccount
    account = CheckingAccount(
        name="Second Checking Account",
        available_balance=Decimal("2000.00"),
        current_balance=Decimal("2000.00"),  # Added current_balance which is required
    )

    # Add to session manually
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)

    return account


@pytest_asyncio.fixture
async def test_multiple_accounts(db_session: AsyncSession) -> List[Account]:
    """
    Create multiple test accounts of different types.

    Args:
        db_session: Database session fixture

    Returns:
        List[Account]: List of created accounts of various types
    """
    accounts = []

    # Create a checking account
    checking = CheckingAccount(
        name="Checking A",
        available_balance=Decimal("1200.00"),
        current_balance=Decimal("1200.00"),
    )
    db_session.add(checking)
    accounts.append(checking)

    # Create a savings account
    savings = SavingsAccount(
        name="Savings B",
        available_balance=Decimal("5000.00"),
        current_balance=Decimal("5000.00"),
    )
    db_session.add(savings)
    accounts.append(savings)

    # Create a credit account
    credit = CreditAccount(
        name="Credit Card C",
        available_balance=Decimal("-700.00"),
        current_balance=Decimal("-700.00"),
        credit_limit=Decimal("3000.00"),
        available_credit=Decimal("2300.00"),
    )
    db_session.add(credit)
    accounts.append(credit)

    # Create another savings account (previously "Investment")
    savings2 = SavingsAccount(
        name="Investment D",
        available_balance=Decimal("10000.00"),
        current_balance=Decimal("10000.00"),
    )
    db_session.add(savings2)
    accounts.append(savings2)

    # Flush to get IDs and establish database rows
    await db_session.flush()

    # Refresh all entries to make sure they reflect what's in the database
    for account in accounts:
        await db_session.refresh(account)

    return accounts


@pytest_asyncio.fixture
async def test_credit_account(db_session: AsyncSession) -> CreditAccount:
    """
    Create a test credit account for use in various tests.

    Args:
        db_session: Database session fixture

    Returns:
        CreditAccount: Created credit account
    """
    credit_account = CreditAccount(
        name="Test Credit Card",
        available_balance=Decimal("-500.00"),
        current_balance=Decimal("-500.00"),  # Added current_balance which is required
        credit_limit=Decimal("2000.00"),  # Credit accounts use credit_limit
        available_credit=Decimal("1500.00"),  # total_limit - abs(available_balance)
        created_at=naive_utc_now(),
        updated_at=naive_utc_now(),
    )
    db_session.add(credit_account)
    await db_session.flush()
    await db_session.refresh(credit_account)
    return credit_account
