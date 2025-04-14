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
    create_savings_account_update_schema,
)

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_get_with_type_returns_savings_account(
    repository: AccountRepository, test_savings_account: SavingsAccount
):
    """
    Test that get_with_type returns a SavingsAccount instance.

    This test verifies that the repository correctly retrieves a savings account
    with the appropriate polymorphic identity.

    Args:
        repository: Base account repository
        test_savings_account: Savings account fixture
    """
    # 1. ARRANGE: Repository and test account are provided by fixtures

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Retrieve the account with type information
    result = await repository.get_with_type(test_savings_account.id)

    # 4. ASSERT: Verify the result is a savings account
    assert result is not None
    assert isinstance(result, SavingsAccount)
    assert result.id == test_savings_account.id
    assert result.name == test_savings_account.name
    assert result.account_type == "savings"

    # Verify savings-specific fields are loaded
    assert hasattr(result, "interest_rate")
    if hasattr(test_savings_account, "compound_frequency"):
        assert result.compound_frequency == test_savings_account.compound_frequency


@pytest.mark.asyncio
async def test_get_by_type_returns_only_savings_accounts(
    repository: AccountRepository,
    test_savings_account: SavingsAccount,
    test_checking_account,
    test_credit_account,
):
    """
    Test that get_by_type returns only savings accounts.

    This test verifies that the repository correctly filters accounts by type
    when retrieving savings accounts.

    Args:
        repository: Base account repository
        test_savings_account: Savings account fixture
        test_checking_account: Checking account fixture
        test_credit_account: Credit account fixture
    """
    # 1. ARRANGE: Repository and test accounts are provided by fixtures

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Retrieve accounts by type
    savings_accounts = await repository.get_by_type("savings")

    # 4. ASSERT: Verify only savings accounts are returned
    assert len(savings_accounts) >= 1
    assert all(isinstance(a, SavingsAccount) for a in savings_accounts)
    assert all(a.account_type == "savings" for a in savings_accounts)

    # Verify the test account is in the results
    account_ids = [a.id for a in savings_accounts]
    assert test_savings_account.id in account_ids

    # Verify other account types are not in the results
    assert test_checking_account.id not in account_ids
    assert test_credit_account.id not in account_ids


@pytest.mark.asyncio
async def test_create_typed_entity_with_savings_type(
    repository: AccountRepository, db_session: AsyncSession
):
    """
    Test creating a typed savings account.

    This test verifies that the repository correctly creates a savings account
    with the appropriate polymorphic identity and type-specific fields.

    Args:
        repository: Base account repository
        db_session: Database session
    """
    # 1. ARRANGE: Repository is provided by fixture

    # 2. SCHEMA: Create and validate through schema factory
    account_schema = create_savings_account_schema(
        name="New Savings Account",
        current_balance=Decimal("5000.00"),
        available_balance=Decimal("5000.00"),
        interest_rate=Decimal("0.0175"),
        compound_frequency="daily",
    )

    # 3. ACT: Create the account
    result = await repository.create_typed_entity(
        "savings", account_schema.model_dump()
    )

    # 4. ASSERT: Verify the account was created correctly
    assert result is not None
    assert isinstance(result, SavingsAccount)
    assert result.id is not None
    assert result.name == "New Savings Account"
    assert result.account_type == "savings"
    assert result.current_balance == Decimal("5000.00")
    assert result.available_balance == Decimal("5000.00")
    assert result.interest_rate == Decimal("0.0175")
    assert result.compound_frequency == "daily"

    # Verify it was actually persisted
    persisted = await repository.get(result.id)
    assert persisted is not None
    assert persisted.id == result.id


@pytest.mark.asyncio
async def test_update_typed_entity_with_savings_type(
    repository: AccountRepository, test_savings_account: SavingsAccount
):
    """
    Test updating a typed savings account.

    This test verifies that the repository correctly updates a savings account
    with the appropriate polymorphic identity and type-specific fields.

    Args:
        repository: Base account repository
        test_savings_account: Savings account fixture
    """
    # 1. ARRANGE: Repository and test account are provided by fixtures

    # 2. SCHEMA: Create and validate through schema factory
    update_schema = create_savings_account_update_schema(
        name="Updated Savings Account",
        interest_rate=Decimal("0.0225"),
        compound_frequency="quarterly",
        minimum_balance=Decimal("1000.00"),
    )

    # 3. ACT: Update the account
    result = await repository.update_typed_entity(
        test_savings_account.id, "savings", update_schema.model_dump()
    )

    # 4. ASSERT: Verify the account was updated correctly
    assert result is not None
    assert isinstance(result, SavingsAccount)
    assert result.id == test_savings_account.id
    assert result.name == "Updated Savings Account"
    assert result.interest_rate == Decimal("0.0225")
    assert result.compound_frequency == "quarterly"
    assert result.minimum_balance == Decimal("1000.00")


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
    high_interest = await savings_repository.get_savings_accounts_by_interest_rate_threshold(
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
    min_balance_accounts = await savings_repository.get_savings_accounts_with_minimum_balance()

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
    below_min_accounts = await savings_repository.get_savings_accounts_below_minimum_balance()

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
    top_accounts = await savings_repository.get_highest_yield_savings_accounts(limit=2)

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
    assert hasattr(savings_repository, "get_savings_accounts_by_interest_rate_threshold")
    assert callable(
        getattr(savings_repository, "get_savings_accounts_by_interest_rate_threshold")
    )

    assert hasattr(savings_repository, "get_savings_accounts_with_minimum_balance")
    assert callable(getattr(savings_repository, "get_savings_accounts_with_minimum_balance"))

    assert hasattr(savings_repository, "get_savings_accounts_below_minimum_balance")
    assert callable(getattr(savings_repository, "get_savings_accounts_below_minimum_balance"))

    assert hasattr(savings_repository, "get_highest_yield_savings_accounts")
    assert callable(getattr(savings_repository, "get_highest_yield_savings_accounts"))
