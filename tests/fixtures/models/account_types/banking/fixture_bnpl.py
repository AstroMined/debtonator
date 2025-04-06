"""
Fixtures for BNPLAccount models.

This module contains fixtures for creating BNPLAccount test instances.
"""

from decimal import Decimal

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.bnpl import BNPLAccount
from src.utils.datetime_utils import utc_now, days_from_now


@pytest_asyncio.fixture
async def test_bnpl_account(db_session: AsyncSession) -> BNPLAccount:
    """Create a basic BNPL account for testing."""
    # Create account with polymorphic identity
    account = BNPLAccount(
        name="Test Affirm Account",
        bnpl_provider="Affirm",
        current_balance=Decimal("400.00"),
        available_balance=Decimal("0.00"),
        original_amount=Decimal("400.00"),
        installment_count=4,
        installments_paid=0,
        installment_amount=Decimal("100.00"),
        payment_frequency="biweekly",
        next_payment_date=days_from_now(14),
        created_at=utc_now(),
        updated_at=utc_now()
    )
    
    # Add to session manually
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)
    
    return account


@pytest_asyncio.fixture
async def test_bnpl_account_with_upcoming_payment(db_session: AsyncSession) -> BNPLAccount:
    """Create a BNPL account with an upcoming payment."""
    # Create account with an upcoming payment (in 3 days)
    account = BNPLAccount(
        name="BNPL With Upcoming Payment",
        bnpl_provider="Klarna",
        current_balance=Decimal("300.00"),
        available_balance=Decimal("0.00"),
        original_amount=Decimal("400.00"),
        installment_count=4,
        installments_paid=1,
        installment_amount=Decimal("100.00"),
        payment_frequency="biweekly",
        next_payment_date=days_from_now(3),  # Soon payment
        created_at=utc_now(),
        updated_at=utc_now()
    )
    
    # Add to session manually
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)
    
    return account


@pytest_asyncio.fixture
async def test_bnpl_account_nearly_paid(db_session: AsyncSession) -> BNPLAccount:
    """Create a BNPL account that is almost paid off."""
    # Create account with almost all installments paid
    account = BNPLAccount(
        name="BNPL Nearly Paid",
        bnpl_provider="Afterpay",
        current_balance=Decimal("100.00"),
        available_balance=Decimal("0.00"),
        original_amount=Decimal("400.00"),
        installment_count=4,
        installments_paid=3,
        installment_amount=Decimal("100.00"),
        payment_frequency="biweekly",
        next_payment_date=days_from_now(14),
        created_at=utc_now(),
        updated_at=utc_now()
    )
    
    # Add to session manually
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)
    
    return account
