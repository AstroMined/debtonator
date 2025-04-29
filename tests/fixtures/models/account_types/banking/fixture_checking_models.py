"""
Fixtures for CheckingAccount models.

This module contains fixtures for creating CheckingAccount test instances.
"""

from decimal import Decimal

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.checking import CheckingAccount
from src.utils.datetime_utils import naive_utc_now


@pytest_asyncio.fixture
async def test_checking_account(db_session: AsyncSession) -> CheckingAccount:
    """
    Create a basic checking account for testing.

    This is a replacement for the standard test_checking_account fixture that uses
    the polymorphic CheckingAccount model instead of the base Account model.
    """
    # Create a checking account with polymorphic identity
    account = CheckingAccount(
        name="Primary Test Checking",
        available_balance=Decimal("1000.00"),
        has_overdraft_protection=False,
    )

    # Add to session manually
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)

    return account


@pytest_asyncio.fixture
async def test_second_checking_account(db_session: AsyncSession) -> CheckingAccount:
    """
    Create a second test checking account for use in split payment tests.

    This fixture is heavily used in payment, bill split, and recurring model tests
    for split payment scenarios.

    Args:
        db_session: Database session fixture

    Returns:
        CheckingAccount: Created checking account
    """
    # Create model instance directly using CheckingAccount
    account = CheckingAccount(
        name="Second Checking Account",
        available_balance=Decimal("2000.00"),
        current_balance=Decimal("2000.00"),
    )

    # Add to session manually
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)

    return account


@pytest_asyncio.fixture
async def test_checking_with_overdraft(db_session: AsyncSession) -> CheckingAccount:
    """Create a checking account with overdraft protection."""
    # Create a checking account with polymorphic identity and overdraft protection
    account = CheckingAccount(
        name="Checking With Overdraft",
        available_balance=Decimal("500.00"),
        has_overdraft_protection=True,
        overdraft_limit=Decimal("200.00"),
        monthly_fee=Decimal("12.00"),
    )

    # Add to session manually
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)

    return account


@pytest_asyncio.fixture
async def test_international_checking(db_session: AsyncSession) -> CheckingAccount:
    """Create a checking account with international banking details."""
    # Create a checking account with international banking details
    account = CheckingAccount(
        name="International Checking",
        available_balance=Decimal("1500.00"),
        currency="EUR",
        has_overdraft_protection=False,
        iban="DE89370400440532013000",
        swift_bic="DEUTDEFF",
        account_format="iban",
    )

    # Add to session manually
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)

    return account


@pytest_asyncio.fixture
async def test_checking_for_module(db_session: AsyncSession) -> CheckingAccount:
    """
    Create a checking account for testing module-specific repository methods.

    This fixture creates a checking account with overdraft protection specifically
    for testing the dynamic method binding in the repository factory.

    Args:
        db_session: Database session fixture

    Returns:
        CheckingAccount: Checking account with overdraft protection
    """
    account = CheckingAccount(
        name="Module Test Checking",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
        has_overdraft_protection=True,
        overdraft_limit=Decimal("500.00"),
        created_at=naive_utc_now(),
        updated_at=naive_utc_now(),
    )
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)
    return account
