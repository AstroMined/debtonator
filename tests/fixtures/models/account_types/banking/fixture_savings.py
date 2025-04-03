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
