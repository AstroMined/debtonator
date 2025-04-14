"""
Fixtures for CreditAccount models.

This module contains fixtures for creating CreditAccount test instances.
"""

from datetime import timedelta
from decimal import Decimal

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.credit import CreditAccount
from src.utils.datetime_utils import naive_utc_now


@pytest_asyncio.fixture
async def test_credit_account(db_session: AsyncSession) -> CreditAccount:
    """
    Create a basic credit account for testing.

    This is a replacement for the standard test_credit_account fixture that uses
    the polymorphic CreditAccount model instead of the base Account model.
    """
    # Create a credit account with polymorphic identity
    account = CreditAccount(
        name="Test Credit Card",
        available_balance=Decimal("-500.00"),  # Negative balance represents amount owed
        credit_limit=Decimal(
            "2000.00"
        ),  # Now using credit_limit instead of total_limit
        statement_balance=Decimal("500.00"),
        minimum_payment=Decimal("25.00"),
        apr=Decimal("19.99"),
    )

    # Add to session manually
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)

    return account


@pytest_asyncio.fixture
async def test_credit_with_statement(db_session: AsyncSession) -> CreditAccount:
    """Create a credit account with statement details."""
    # Get current time and set due date in the future
    now = naive_utc_now()
    due_date = (now + timedelta(days=20)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    statement_date = (now - timedelta(days=10)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    # Create credit account with statement details
    account = CreditAccount(
        name="Credit With Statement",
        available_balance=Decimal("-1200.00"),
        credit_limit=Decimal("5000.00"),
        statement_balance=Decimal("1200.00"),
        statement_due_date=due_date,
        minimum_payment=Decimal("35.00"),
        apr=Decimal("18.99"),
        autopay_status="minimum",
        last_statement_date=statement_date,
    )

    # Add to session manually
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)

    return account


@pytest_asyncio.fixture
async def test_credit_with_due_date(db_session: AsyncSession) -> CreditAccount:
    """
    Create a credit account with an upcoming due date for payment testing.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        CreditAccount: Credit account with due date in the next 10 days
    """
    # Get current time and set due date in the near future (10 days)
    now = naive_utc_now()
    due_date = (now + timedelta(days=10)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )
    statement_date = (now - timedelta(days=20)).replace(
        hour=0, minute=0, second=0, microsecond=0
    )

    # Create credit account with upcoming due date
    account = CreditAccount(
        name="Credit With Due Date",
        available_balance=Decimal("-2000.00"),
        credit_limit=Decimal("5000.00"),
        statement_balance=Decimal("2000.00"),
        statement_due_date=due_date,
        minimum_payment=Decimal("50.00"),
        apr=Decimal("17.99"),
        last_statement_date=statement_date,
    )

    # Add to session manually
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)

    return account


@pytest_asyncio.fixture
async def test_credit_with_rewards(db_session: AsyncSession) -> CreditAccount:
    """
    Create a credit account with rewards program and autopay enabled.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        CreditAccount: Credit account with rewards and autopay
    """
    account = CreditAccount(
        name="Rewards Credit Card",
        available_balance=Decimal("-750.00"),
        credit_limit=Decimal("10000.00"),
        statement_balance=Decimal("750.00"),
        apr=Decimal("22.99"),
        annual_fee=Decimal("95.00"),
        rewards_program="Cash Back",
        autopay_status="full_balance",  # Autopay enabled for full balance
        minimum_payment=Decimal("30.00"),
    )

    # Add to session manually
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)

    return account
