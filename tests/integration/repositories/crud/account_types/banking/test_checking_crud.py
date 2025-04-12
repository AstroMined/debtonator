"""
Integration tests for checking account repository CRUD operations.

This module tests the base repository's polymorphic handling of checking accounts
for basic CRUD operations. Following the "Real Objects Testing Philosophy" with no mocks.
"""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.checking import CheckingAccount
from src.registry.account_types import account_type_registry
from src.repositories.accounts import AccountRepository
from tests.helpers.schema_factories.account_types.banking.checking_schema_factories import (
    create_checking_account_schema,
    create_checking_account_update_schema,
)

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_get_with_type_returns_checking_account(
    account_repository: AccountRepository, test_checking_account: CheckingAccount
):
    """
    Test that get_with_type returns a CheckingAccount instance.

    This test verifies that the repository correctly retrieves a checking account
    with the appropriate polymorphic identity.

    Args:
        account_repository: Base account repository
        test_checking_account: Checking account fixture
    """
    # 1. ARRANGE: Repository and test account are provided by fixtures

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Retrieve the account with type information
    result = await account_repository.get_with_type(test_checking_account.id)

    # 4. ASSERT: Verify the result is a checking account
    assert result is not None
    assert isinstance(result, CheckingAccount)
    assert result.id == test_checking_account.id
    assert result.name == test_checking_account.name
    assert result.account_type == "checking"

    # Verify checking-specific fields are loaded
    assert hasattr(result, "has_overdraft_protection")
    if hasattr(test_checking_account, "routing_number"):
        assert result.routing_number == test_checking_account.routing_number


@pytest.mark.asyncio
async def test_get_by_type_returns_only_checking_accounts(
    account_repository: AccountRepository,
    test_checking_account: CheckingAccount,
    test_savings_account,
    test_credit_account,
):
    """
    Test that get_by_type returns only checking accounts.

    This test verifies that the repository correctly filters accounts by type
    when retrieving checking accounts.

    Args:
        account_repository: Base account repository
        test_checking_account: Checking account fixture
        test_savings_account: Savings account fixture
        test_credit_account: Credit account fixture
    """
    # 1. ARRANGE: Repository and test accounts are provided by fixtures

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Retrieve accounts by type
    checking_accounts = await account_repository.get_by_type("checking")

    # 4. ASSERT: Verify only checking accounts are returned
    assert len(checking_accounts) >= 1
    assert all(isinstance(a, CheckingAccount) for a in checking_accounts)
    assert all(a.account_type == "checking" for a in checking_accounts)

    # Verify the test account is in the results
    account_ids = [a.id for a in checking_accounts]
    assert test_checking_account.id in account_ids

    # Verify other account types are not in the results
    assert test_savings_account.id not in account_ids
    assert test_credit_account.id not in account_ids


@pytest.mark.asyncio
async def test_create_typed_account_with_checking_type(
    account_repository: AccountRepository, db_session: AsyncSession
):
    """
    Test creating a typed checking account.

    This test verifies that the repository correctly creates a checking account
    with the appropriate polymorphic identity and type-specific fields.

    Args:
        account_repository: Base account repository
        db_session: Database session
    """
    # 1. ARRANGE: Repository is provided by fixture

    # 2. SCHEMA: Create and validate through schema factory
    account_schema = create_checking_account_schema(
        name="New Checking Account",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
        has_overdraft_protection=True,
        overdraft_limit=Decimal("500.00"),
    )

    # 3. ACT: Create the account
    result = await account_repository.create_typed_account(
        "checking",
        account_schema.model_dump(),
        account_type_registry=account_type_registry,
    )

    # 4. ASSERT: Verify the account was created correctly
    assert result is not None
    assert isinstance(result, CheckingAccount)
    assert result.id is not None
    assert result.name == "New Checking Account"
    assert result.account_type == "checking"
    assert result.current_balance == Decimal("1000.00")
    assert result.available_balance == Decimal("1000.00")
    assert result.has_overdraft_protection is True
    assert result.overdraft_limit == Decimal("500.00")

    # Verify it was actually persisted
    persisted = await account_repository.get(result.id)
    assert persisted is not None
    assert persisted.id == result.id


@pytest.mark.asyncio
async def test_update_typed_account_with_checking_type(
    account_repository: AccountRepository, test_checking_account: CheckingAccount
):
    """
    Test updating a typed checking account.

    This test verifies that the repository correctly updates a checking account
    with the appropriate polymorphic identity and type-specific fields.

    Args:
        account_repository: Base account repository
        test_checking_account: Checking account fixture
    """
    # 1. ARRANGE: Repository and test account are provided by fixtures

    # 2. SCHEMA: Create and validate through schema factory
    update_schema = create_checking_account_update_schema(
        name="Updated Checking Account",
        has_overdraft_protection=True,
        overdraft_limit=Decimal("250.00"),
        monthly_fee=Decimal("5.99"),
    )

    # 3. ACT: Update the account
    result = await account_repository.update_typed_account(
        test_checking_account.id,
        "checking",
        update_schema.model_dump(),
        account_type_registry=account_type_registry,
    )

    # 4. ASSERT: Verify the account was updated correctly
    assert result is not None
    assert isinstance(result, CheckingAccount)
    assert result.id == test_checking_account.id
    assert result.name == "Updated Checking Account"
    assert result.has_overdraft_protection is True
    assert result.overdraft_limit == Decimal("250.00")
    assert result.monthly_fee == Decimal("5.99")
