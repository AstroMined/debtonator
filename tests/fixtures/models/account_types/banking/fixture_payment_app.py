"""
Fixtures for PaymentAppAccount models.

This module contains fixtures for creating PaymentAppAccount test instances.
"""

from decimal import Decimal

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.payment_app import PaymentAppAccount
from src.utils.datetime_utils import utc_now


@pytest_asyncio.fixture
async def test_payment_app_account(db_session: AsyncSession) -> PaymentAppAccount:
    """Create a basic payment app account for testing."""
    # Create account with polymorphic identity
    account = PaymentAppAccount(
        name="Test PayPal Account",
        platform="PayPal",
        current_balance=Decimal("150.00"),
        available_balance=Decimal("150.00"),
        has_debit_card=True,
        card_last_four="1234",
        created_at=utc_now(),
        updated_at=utc_now()
    )
    
    # Add to session manually
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)
    
    return account


@pytest_asyncio.fixture
async def test_payment_app_account_with_linked_accounts(db_session: AsyncSession) -> PaymentAppAccount:
    """Create a payment app account with linked accounts."""
    # Create account with linked accounts
    account = PaymentAppAccount(
        name="Venmo With Links",
        platform="Venmo",
        current_balance=Decimal("250.00"),
        available_balance=Decimal("250.00"),
        has_debit_card=False,
        supports_direct_deposit=True,
        linked_account_ids="1,2,3",  # Comma-separated account IDs
        created_at=utc_now(),
        updated_at=utc_now()
    )
    
    # Add to session manually
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)
    
    return account
