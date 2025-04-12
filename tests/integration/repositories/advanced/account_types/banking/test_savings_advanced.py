"""
Integration tests for savings account repository advanced operations.

This module tests the specialized operations in the savings account repository module.
Following the "Real Objects Testing Philosophy" with no mocks.
"""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.savings import SavingsAccount
from src.repositories.accounts import AccountRepository
from tests.helpers.schema_factories.account_types.banking.savings_schema_factories import (
    create_savings_account_schema,
)

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_get_accounts_by_interest_rate_threshold(
    savings_repository: AccountRepository,
    test_savings_with_interest: SavingsAccount,
    test_savings_with_min_balance: SavingsAccount,
    test_savings_account: SavingsAccount,
    db_session: AsyncSession,
):
    """
    Test getting savings accounts with interest rate above threshold.

    This test verifies that the specialized repository method correctly
    identifies savings accounts with interest rates above a specified threshold.

    Args:
        savings_repository: Savings account repository
        test_savings_with_interest: Savings account with high interest rate
        test_savings_with_min_balance: Savings account with high interest rate
        test_savings_account: Basic savings account
        db_session: Database session
    """
    # 1. ARRANGE: Ensure basic test_savings_account has a low interest rate
    if hasattr(test_savings_account, "interest_rate") and (
        test_savings_account.interest_rate is None
        or test_savings_account.interest_rate > Decimal("1.0")
    ):
        test_savings_account.interest_rate = Decimal("0.50")
        await db_session.flush()

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Call the specialized repository method
    high_interest = await savings_repository.get_accounts_by_interest_rate_threshold(
        Decimal("2.0")
    )

    # 4. ASSERT: Verify the results
    assert len(high_interest) >= 2  # Should have our test accounts with 2.5% and 3.0%

    # Verify the right accounts are included
    account_ids = [a.id for a in high_interest]
    assert test_savings_with_interest.id in account_ids
    assert test_savings_with_min_balance.id in account_ids

    # Verify low interest account is excluded
    if hasattr(
        test_savings_account, "interest_rate"
    ) and test_savings_account.interest_rate < Decimal("2.0"):
        assert test_savings_account.id not in account_ids

    # All accounts should have interest rates above threshold
    assert all(
        a.interest_rate is not None and a.interest_rate >= Decimal("2.0")
        for a in high_interest
    )


@pytest.mark.asyncio
async def test_get_accounts_with_minimum_balance(
    savings_repository: AccountRepository,
    test_savings_with_min_balance: SavingsAccount,
    test_savings_with_interest: SavingsAccount,
):
    """
    Test getting savings accounts with minimum balance requirements.

    This test verifies that the specialized repository method correctly
    identifies savings accounts that have minimum balance requirements.

    Args:
        savings_repository: Savings account repository
        test_savings_with_min_balance: Savings account with minimum balance
        test_savings_with_interest: Savings account without minimum balance
    """
    # 1. ARRANGE: Accounts are provided by fixtures

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Call the specialized repository method
    min_balance_accounts = await savings_repository.get_accounts_with_minimum_balance()

    # 4. ASSERT: Verify the results
    assert len(min_balance_accounts) >= 1

    # Verify account with minimum balance is included
    account_ids = [a.id for a in min_balance_accounts]
    assert test_savings_with_min_balance.id in account_ids

    # Verify account without minimum balance is excluded (if it doesn't have one)
    if (
        not hasattr(test_savings_with_interest, "minimum_balance")
        or test_savings_with_interest.minimum_balance is None
    ):
        assert test_savings_with_interest.id not in account_ids

    # All accounts should have a minimum balance
    assert all(
        a.minimum_balance is not None and a.minimum_balance > 0
        for a in min_balance_accounts
    )


@pytest.mark.asyncio
async def test_get_accounts_below_minimum_balance(
    savings_repository: AccountRepository, db_session: AsyncSession
):
    """
    Test getting savings accounts with balance below their minimum requirement.

    This test verifies that the specialized repository method correctly
    identifies savings accounts with balances below their minimum requirements.

    Args:
        savings_repository: Savings account repository
        db_session: Database session
    """
    # 1. ARRANGE: Create accounts with balances above and below minimum
    below_min_schema = create_savings_account_schema(
        name="Below Minimum",
        current_balance=Decimal("800.00"),
        available_balance=Decimal("800.00"),
        minimum_balance=Decimal("1000.00"),
    )

    above_min_schema = create_savings_account_schema(
        name="Above Minimum",
        current_balance=Decimal("2000.00"),
        available_balance=Decimal("2000.00"),
        minimum_balance=Decimal("1000.00"),
    )

    below_min = SavingsAccount(**below_min_schema.model_dump())
    above_min = SavingsAccount(**above_min_schema.model_dump())

    db_session.add_all([below_min, above_min])
    await db_session.flush()

    # 2. SCHEMA: Used for creating the test accounts

    # 3. ACT: Call the specialized repository method
    below_min_accounts = await savings_repository.get_accounts_below_minimum_balance()

    # 4. ASSERT: Verify the results
    assert len(below_min_accounts) >= 1

    # Verify correct accounts are included/excluded
    account_ids = [a.id for a in below_min_accounts]
    assert below_min.id in account_ids
    assert above_min.id not in account_ids

    # All accounts should be below their minimum balance
    for account in below_min_accounts:
        assert account.minimum_balance is not None
        assert account.available_balance < account.minimum_balance


@pytest.mark.asyncio
async def test_get_highest_yield_accounts(
    savings_repository: AccountRepository,
    test_savings_with_interest: SavingsAccount,
    test_savings_with_min_balance: SavingsAccount,
    test_savings_account: SavingsAccount,
    db_session: AsyncSession,
):
    """
    Test getting highest yield savings accounts with limit.

    This test verifies that the specialized repository method correctly
    returns savings accounts sorted by interest rate with a specified limit.

    Args:
        savings_repository: Savings account repository
        test_savings_with_interest: Savings account with high interest rate
        test_savings_with_min_balance: Savings account with highest interest rate
        test_savings_account: Basic savings account
        db_session: Database session
    """
    # 1. ARRANGE: Accounts are provided by fixtures

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Call the specialized repository method
    top_accounts = await savings_repository.get_highest_yield_accounts(limit=2)

    # 4. ASSERT: Verify the results
    assert len(top_accounts) <= 2  # Should respect the limit

    # Verify top accounts are returned in descending order of interest rate
    if len(top_accounts) >= 2:
        assert top_accounts[0].interest_rate >= top_accounts[1].interest_rate

    # Verify the highest interest rate account is included
    # (test_savings_with_min_balance has 3.00%)
    if len(top_accounts) > 0:
        assert top_accounts[0].id == test_savings_with_min_balance.id


@pytest.mark.asyncio
async def test_repository_has_specialized_methods(
    savings_repository: AccountRepository,
):
    """
    Test that the repository has the specialized savings methods.

    This test verifies that the savings repository correctly includes
    all the specialized methods for savings account operations.

    Args:
        savings_repository: Savings account repository
    """
    # 1. ARRANGE: Repository is provided by fixture

    # 2. SCHEMA: Not applicable for this test

    # 3. ACT & ASSERT: Verify the repository has specialized savings methods
    assert hasattr(savings_repository, "get_accounts_by_interest_rate_threshold")
    assert callable(
        getattr(savings_repository, "get_accounts_by_interest_rate_threshold")
    )

    assert hasattr(savings_repository, "get_accounts_with_minimum_balance")
    assert callable(getattr(savings_repository, "get_accounts_with_minimum_balance"))

    assert hasattr(savings_repository, "get_accounts_below_minimum_balance")
    assert callable(getattr(savings_repository, "get_accounts_below_minimum_balance"))

    assert hasattr(savings_repository, "get_highest_yield_accounts")
    assert callable(getattr(savings_repository, "get_highest_yield_accounts"))
