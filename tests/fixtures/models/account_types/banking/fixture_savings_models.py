"""
Fixtures for SavingsAccount models.

This module contains fixtures for creating SavingsAccount test instances.
"""

from decimal import Decimal

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.savings import SavingsAccount


@pytest_asyncio.fixture
async def test_savings_account(db_session: AsyncSession) -> SavingsAccount:
    """
    Create a basic savings account for testing.
    """
    # Create a savings account with polymorphic identity
    account = SavingsAccount(
        name="Test Savings Account",
        available_balance=Decimal("5000.00"),
        interest_rate=Decimal("0.50"),  # 0.50% APY
        compound_frequency="monthly",
        minimum_balance=Decimal("300.00"),
        withdrawal_limit=6,
    )

    # Add to session manually
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)

    return account


@pytest_asyncio.fixture
async def test_high_yield_savings(db_session: AsyncSession) -> SavingsAccount:
    """Create a high-yield savings account with higher interest rate."""
    account = SavingsAccount(
        name="High Yield Savings",
        available_balance=Decimal("10000.00"),
        interest_rate=Decimal("3.75"),  # 3.75% APY
        compound_frequency="daily",
        interest_earned_ytd=Decimal("156.25"),
        minimum_balance=Decimal("500.00"),
        withdrawal_limit=3,
    )

    # Add to session manually
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)

    return account


@pytest_asyncio.fixture
async def test_emergency_fund(db_session: AsyncSession) -> SavingsAccount:
    """Create an emergency fund savings account."""
    account = SavingsAccount(
        name="Emergency Fund",
        available_balance=Decimal("15000.00"),
        interest_rate=Decimal("1.25"),  # 1.25% APY
        compound_frequency="quarterly",
        interest_earned_ytd=Decimal("45.75"),
        minimum_balance=Decimal("0.00"),  # No minimum balance
        withdrawal_limit=0,  # Unlimited withdrawals
    )

    # Add to session manually
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)

    return account


@pytest_asyncio.fixture
async def test_savings_with_interest(db_session: AsyncSession) -> SavingsAccount:
    """
    Create a savings account with high interest rate for testing.

    Args:
        db_session: Database session fixture

    Returns:
        SavingsAccount: Savings account with 2.5% interest rate
    """
    account = SavingsAccount(
        name="High Interest Savings",
        available_balance=Decimal("7500.00"),
        interest_rate=Decimal("2.50"),  # 2.50% APY
        compound_frequency="monthly",
        interest_earned_ytd=Decimal("85.25"),
        minimum_balance=None,  # No minimum balance
        withdrawal_limit=4,
    )

    # Add to session manually
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)

    return account


@pytest_asyncio.fixture
async def test_savings_with_min_balance(db_session: AsyncSession) -> SavingsAccount:
    """
    Create a savings account with minimum balance requirement and high interest.

    Args:
        db_session: Database session fixture

    Returns:
        SavingsAccount: Savings account with minimum balance and 3% interest
    """
    account = SavingsAccount(
        name="Premium Savings",
        available_balance=Decimal("12000.00"),
        interest_rate=Decimal("3.00"),  # 3.00% APY (highest rate)
        compound_frequency="daily",
        interest_earned_ytd=Decimal("175.50"),
        minimum_balance=Decimal("1000.00"),  # Substantial minimum balance
        withdrawal_limit=2,  # Limited withdrawals
    )

    # Add to session manually
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)

    return account
