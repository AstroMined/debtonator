"""
Integration tests for savings account repository CRUD operations.

This module tests the base repository's polymorphic handling of savings accounts
for basic CRUD operations. Following the "Real Objects Testing Philosophy" with no mocks.
"""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.savings import SavingsAccount
from src.repositories.accounts import AccountRepository
from src.utils.datetime_utils import utc_now
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
async def test_create_typed_account_with_savings_type(
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
    result = await repository.create_typed_account(
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
async def test_update_typed_account_with_savings_type(
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
    result = await repository.update_typed_account(
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
