"""
Fixture module for account models that don't fit in a specialized fixture file.

This module contains fixtures that are either:
1. Collections of different account types (test_multiple_accounts)
2. Support fixtures used across many test files

For specialized account type fixtures, use the appropriate module in
tests/fixtures/models/account_types/banking/ instead:
- CheckingAccount: fixture_checking_models.py
- SavingsAccount: fixture_savings_models.py
- CreditAccount: fixture_credit_models.py
"""

from decimal import Decimal
from typing import List

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.checking import CheckingAccount
from src.models.account_types.banking.credit import CreditAccount
from src.models.account_types.banking.savings import SavingsAccount
from src.models.accounts import Account


@pytest_asyncio.fixture
async def test_multiple_accounts(db_session: AsyncSession) -> List[Account]:
    """
    Create multiple test accounts of different types.

    This fixture creates a collection of different account types for testing
    operations that need to work across multiple account types.

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
