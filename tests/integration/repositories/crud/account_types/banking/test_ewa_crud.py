# pylint: disable=no-member,no-value-for-argument
"""
Integration tests for EWA account repository CRUD operations.

Following the four-step pattern and Real Objects Testing Philosophy.
"""

from decimal import Decimal

import pytest

from src.models.account_types.banking.ewa import EWAAccount
from src.repositories.accounts import AccountRepository
from tests.helpers.schema_factories.account_types.banking.ewa_schema_factories import (
    create_ewa_account_schema,
)

pytestmark = pytest.mark.asyncio


async def test_create_ewa_account(ewa_repository: AccountRepository):
    """
    Test creating an EWA account following the four-step pattern.

    Args:
        ewa_repository: Repository fixture for EWA accounts
    """
    # 1. ARRANGE: Nothing needed here

    # 2. SCHEMA: Create and validate through Pydantic schema
    account_schema = create_ewa_account_schema(
        name="My Earnin Account",
        provider="Earnin",
        current_balance=Decimal("250.00"),
        max_advance_percentage=Decimal("50.00"),
        per_transaction_fee=Decimal("2.99"),
    )

    # Convert validated schema to dict for repository
    validated_data = account_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    # Ensure only invalid fields are excluded
    invalid_fields = ["available_credit"]
    filtered_data = {k: v for k, v in validated_data.items() if k not in invalid_fields}
    result = await ewa_repository.create_typed_account("ewa", filtered_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert isinstance(result, EWAAccount)
    assert result.id is not None
    assert result.name == "My Earnin Account"
    assert result.provider == "Earnin"
    assert result.current_balance == Decimal("250.00")
    assert result.max_advance_percentage == Decimal("50.00")
    assert result.per_transaction_fee == Decimal("2.99")


async def test_get_ewa_account(
    ewa_repository: AccountRepository, test_ewa_account: EWAAccount
):
    """
    Test retrieving an EWA account by ID.

    Args:
        ewa_repository: Repository fixture for EWA accounts
        test_ewa_account: Test EWA account fixture
    """
    # 1. ARRANGE: Use fixture for test account

    # 2. ACT: Get account by ID
    result = await ewa_repository.get(test_ewa_account.id)

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert isinstance(result, EWAAccount)
    assert result.id == test_ewa_account.id
    assert result.name == test_ewa_account.name
    assert result.provider == test_ewa_account.provider
    assert result.max_advance_percentage == test_ewa_account.max_advance_percentage


async def test_update_ewa_account(
    ewa_repository: AccountRepository, test_ewa_account: EWAAccount
):
    """
    Test updating an EWA account.

    Args:
        ewa_repository: Repository fixture for EWA accounts
        test_ewa_account: Test EWA account fixture
    """
    # 1. ARRANGE: Use fixture for test account
    account_id = test_ewa_account.id

    # 2. SCHEMA: Create update data with schema
    update_schema = create_ewa_account_schema(
        name="Updated PayActiv Account",
        max_advance_percentage=Decimal("60.00"),  # Increased max advance percentage
        per_transaction_fee=Decimal("3.99"),  # Increased fee
    )

    validated_data = update_schema.model_dump()

    # 3. ACT: Update the account using typed update method
    result = await ewa_repository.update_typed_account(
        account_id=account_id, account_type="ewa", data=validated_data
    )

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert isinstance(result, EWAAccount)
    assert result.id == account_id
    assert result.name == "Updated PayActiv Account"
    assert result.max_advance_percentage == Decimal("60.00")
    assert result.per_transaction_fee == Decimal("3.99")
    # Original properties should remain unchanged
    assert result.provider == test_ewa_account.provider
    assert result.current_balance == test_ewa_account.current_balance


async def test_delete_ewa_account(
    ewa_repository: AccountRepository, test_ewa_account: EWAAccount
):
    """
    Test deleting (soft delete) an EWA account.

    Args:
        ewa_repository: Repository fixture for EWA accounts
        test_ewa_account: Test EWA account fixture
    """
    # 1. ARRANGE: Use fixture for test account
    account_id = test_ewa_account.id

    # 2. ACT: Delete the account
    result = await ewa_repository.delete(account_id)

    # 3. ASSERT: Verify soft deletion
    assert result is True

    # Verify the account is marked as closed, not physically deleted
    account = await ewa_repository.get(account_id)
    assert account is not None
    assert account.is_closed is True
