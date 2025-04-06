"""
Fixtures for EWAAccount models.

This module contains fixtures for creating EWAAccount test instances.
"""

from decimal import Decimal

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.ewa import EWAAccount
from src.utils.datetime_utils import utc_now, days_from_now


@pytest_asyncio.fixture
async def test_ewa_account(db_session: AsyncSession) -> EWAAccount:
    """Create a basic EWA account for testing."""
    # Create account with polymorphic identity
    account = EWAAccount(
        name="Test PayActiv Account",
        provider="PayActiv",
        current_balance=Decimal("250.00"),
        available_balance=Decimal("0.00"),
        max_advance_percentage=Decimal("50.00"),
        per_transaction_fee=Decimal("5.00"),
        next_payday=days_from_now(7),
        pay_period_start=days_from_now(-7),
        pay_period_end=days_from_now(7),
        created_at=utc_now(),
        updated_at=utc_now()
    )
    
    # Add to session manually
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)
    
    return account


@pytest_asyncio.fixture
async def test_ewa_account_approaching_payday(db_session: AsyncSession) -> EWAAccount:
    """Create an EWA account with an approaching payday."""
    # Create account with imminent payday
    account = EWAAccount(
        name="EWA With Approaching Payday",
        provider="DailyPay",
        current_balance=Decimal("300.00"),
        available_balance=Decimal("0.00"),
        max_advance_percentage=Decimal("50.00"),
        per_transaction_fee=Decimal("2.99"),
        next_payday=days_from_now(2),  # Very soon
        pay_period_start=days_from_now(-12),
        pay_period_end=days_from_now(2),
        created_at=utc_now(),
        updated_at=utc_now()
    )
    
    # Add to session manually
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)
    
    return account


@pytest_asyncio.fixture
async def test_ewa_account_no_transaction_fee(db_session: AsyncSession) -> EWAAccount:
    """Create an EWA account with no transaction fee."""
    # Create account with no fee
    account = EWAAccount(
        name="EWA No Fee",
        provider="Employer Direct",
        current_balance=Decimal("175.00"),
        available_balance=Decimal("0.00"),
        max_advance_percentage=Decimal("75.00"),
        per_transaction_fee=Decimal("0.00"),
        next_payday=days_from_now(14),
        pay_period_start=days_from_now(-14),
        pay_period_end=days_from_now(14),
        created_at=utc_now(),
        updated_at=utc_now()
    )
    
    # Add to session manually
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)
    
    return account
