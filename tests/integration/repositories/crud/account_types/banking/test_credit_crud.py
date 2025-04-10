"""
Integration tests for credit account repository CRUD operations.

This module tests the base repository's polymorphic handling of credit accounts
for basic CRUD operations. Following the "Real Objects Testing Philosophy" with no mocks.
"""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.credit import CreditAccount
from src.repositories.accounts import AccountRepository
from src.utils.datetime_utils import utc_now
from tests.helpers.schema_factories.account_types.banking.credit_schema_factories import (
    create_credit_account_schema,
    create_credit_account_update_schema,
)

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_get_with_type_returns_credit_account(
    repository: AccountRepository, test_credit_account: CreditAccount
):
    """
    Test that get_with_type returns a CreditAccount instance.
    
    This test verifies that the repository correctly retrieves a credit account
    with the appropriate polymorphic identity.
    
    Args:
        repository: Base account repository
        test_credit_account: Credit account fixture
    """
    # 1. ARRANGE: Repository and test account are provided by fixtures

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Retrieve the account with type information
    result = await repository.get_with_type(test_credit_account.id)

    # 4. ASSERT: Verify the result is a credit account
    assert result is not None
    assert isinstance(result, CreditAccount)
    assert result.id == test_credit_account.id
    assert result.name == test_credit_account.name
    assert result.account_type == "credit"

    # Verify credit-specific fields are loaded
    assert hasattr(result, "credit_limit")
    if hasattr(test_credit_account, "apr"):
        assert result.apr == test_credit_account.apr


@pytest.mark.asyncio
async def test_get_by_type_returns_only_credit_accounts(
    repository: AccountRepository,
    test_credit_account: CreditAccount,
    test_checking_account,
    test_savings_account,
):
    """
    Test that get_by_type returns only credit accounts.
    
    This test verifies that the repository correctly filters accounts by type
    when retrieving credit accounts.
    
    Args:
        repository: Base account repository
        test_credit_account: Credit account fixture
        test_checking_account: Checking account fixture
        test_savings_account: Savings account fixture
    """
    # 1. ARRANGE: Repository and test accounts are provided by fixtures

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Retrieve accounts by type
    credit_accounts = await repository.get_by_type("credit")

    # 4. ASSERT: Verify only credit accounts are returned
    assert len(credit_accounts) >= 1
    assert all(isinstance(a, CreditAccount) for a in credit_accounts)
    assert all(a.account_type == "credit" for a in credit_accounts)

    # Verify the test account is in the results
    account_ids = [a.id for a in credit_accounts]
    assert test_credit_account.id in account_ids

    # Verify other account types are not in the results
    assert test_checking_account.id not in account_ids
    assert test_savings_account.id not in account_ids


@pytest.mark.asyncio
async def test_create_typed_account_with_credit_type(
    repository: AccountRepository, db_session: AsyncSession
):
    """
    Test creating a typed credit account.
    
    This test verifies that the repository correctly creates a credit account
    with the appropriate polymorphic identity and type-specific fields.
    
    Args:
        repository: Base account repository
        db_session: Database session
    """
    # 1. ARRANGE: Repository is provided by fixture

    # 2. SCHEMA: Create and validate through schema factory
    account_schema = create_credit_account_schema(
        name="New Credit Account",
        current_balance=Decimal("-500.00"),
        available_balance=Decimal("-500.00"),
        credit_limit=Decimal("3000.00"),
        available_credit=Decimal("2500.00"),
        apr=Decimal("15.99"),
    )

    # 3. ACT: Create the account
    result = await repository.create_typed_account(
        "credit", account_schema.model_dump()
    )

    # 4. ASSERT: Verify the account was created correctly
    assert result is not None
    assert isinstance(result, CreditAccount)
    assert result.id is not None
    assert result.name == "New Credit Account"
    assert result.account_type == "credit"
    assert result.current_balance == Decimal("-500.00")
    assert result.available_balance == Decimal("-500.00")
    assert result.credit_limit == Decimal("3000.00")
    assert result.available_credit == Decimal("2500.00")
    assert result.apr == Decimal("15.99")

    # Verify it was actually persisted
    persisted = await repository.get(result.id)
    assert persisted is not None
    assert persisted.id == result.id


@pytest.mark.asyncio
async def test_update_typed_account_with_credit_type(
    repository: AccountRepository, test_credit_account: CreditAccount
):
    """
    Test updating a typed credit account.
    
    This test verifies that the repository correctly updates a credit account
    with the appropriate polymorphic identity and type-specific fields.
    
    Args:
        repository: Base account repository
        test_credit_account: Credit account fixture
    """
    # 1. ARRANGE: Repository and test account are provided by fixtures

    # 2. SCHEMA: Create and validate through schema factory
    update_schema = create_credit_account_update_schema(
        name="Updated Credit Account",
        apr=Decimal("14.99"),
        rewards_program="Travel Points",
        autopay_status="minimum",
    )

    # 3. ACT: Update the account
    result = await repository.update_typed_account(
        test_credit_account.id, "credit", update_schema.model_dump()
    )

    # 4. ASSERT: Verify the account was updated correctly
    assert result is not None
    assert isinstance(result, CreditAccount)
    assert result.id == test_credit_account.id
    assert result.name == "Updated Credit Account"
    assert result.apr == Decimal("14.99")
    assert result.rewards_program == "Travel Points"
    assert result.autopay_status == "minimum"
