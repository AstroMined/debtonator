# pylint: disable=no-member,no-value-for-argument
"""
Integration tests for BNPL account repository CRUD operations.

Following the four-step pattern and Real Objects Testing Philosophy.
"""

from decimal import Decimal

import pytest

from src.models.account_types.banking.bnpl import BNPLAccount
from src.repositories.accounts import AccountRepository
from tests.helpers.schema_factories.account_types.banking.bnpl_schema_factories import (
    create_bnpl_account_schema,
)

pytestmark = pytest.mark.asyncio


async def test_create_bnpl_account(bnpl_repository: AccountRepository):
    """
    Test creating a BNPL account following the four-step pattern.

    Args:
        bnpl_repository: Repository fixture for BNPL accounts
    """
    # 1. ARRANGE: Nothing needed here

    # 2. SCHEMA: Create and validate through Pydantic schema
    account_schema = create_bnpl_account_schema(
        name="My Affirm Account",
        bnpl_provider="Affirm",
        current_balance=Decimal("400.00"),
        original_amount=Decimal("400.00"),
        installment_count=4,
        installments_paid=0,
        installment_amount=Decimal("100.00"),
        payment_frequency="biweekly",
    )

    # Convert validated schema to dict for repository
    validated_data = account_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    # Ensure only invalid fields are excluded
    invalid_fields = ["available_credit"]
    filtered_data = {k: v for k, v in validated_data.items() if k not in invalid_fields}
    result = await bnpl_repository.create_typed_account("bnpl", filtered_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert isinstance(result, BNPLAccount)
    assert result.id is not None
    assert result.name == "My Affirm Account"
    assert result.bnpl_provider == "Affirm"
    assert result.current_balance == Decimal("400.00")
    assert result.installment_count == 4
    assert result.installments_paid == 0
    assert result.installment_amount == Decimal("100.00")
    assert result.payment_frequency == "biweekly"


async def test_get_bnpl_account(
    bnpl_repository: AccountRepository, test_bnpl_account: BNPLAccount
):
    """
    Test retrieving a BNPL account by ID.

    Args:
        bnpl_repository: Repository fixture for BNPL accounts
        test_bnpl_account: Test BNPL account fixture
    """
    # 1. ARRANGE: Use fixture for test account

    # 2. ACT: Get account by ID
    result = await bnpl_repository.get(test_bnpl_account.id)

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert isinstance(result, BNPLAccount)
    assert result.id == test_bnpl_account.id
    assert result.name == test_bnpl_account.name
    assert result.bnpl_provider == test_bnpl_account.bnpl_provider


async def test_update_bnpl_account(
    bnpl_repository: AccountRepository, test_bnpl_account: BNPLAccount
):
    """
    Test updating a BNPL account.

    Args:
        bnpl_repository: Repository fixture for BNPL accounts
        test_bnpl_account: Test BNPL account fixture
    """
    # 1. ARRANGE: Use fixture for test account
    account_id = test_bnpl_account.id

    # 2. SCHEMA: Create update data with schema
    update_schema = create_bnpl_account_schema(
        name="Updated Affirm Account",
        installments_paid=1,  # Increment the installments paid
    )

    validated_data = update_schema.model_dump()

    # 3. ACT: Update the account using typed update method
    result = await bnpl_repository.update_typed_account(
        account_id=account_id, account_type="bnpl", data=validated_data
    )

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert isinstance(result, BNPLAccount)
    assert result.id == account_id
    assert result.name == "Updated Affirm Account"
    assert result.installments_paid == 1
    # Original properties should remain unchanged
    assert result.bnpl_provider == test_bnpl_account.bnpl_provider
    assert result.installment_count == test_bnpl_account.installment_count
    assert result.installment_amount == test_bnpl_account.installment_amount


async def test_delete_bnpl_account(
    bnpl_repository: AccountRepository, test_bnpl_account: BNPLAccount
):
    """
    Test deleting (soft delete) a BNPL account.

    Args:
        bnpl_repository: Repository fixture for BNPL accounts
        test_bnpl_account: Test BNPL account fixture
    """
    # 1. ARRANGE: Use fixture for test account
    account_id = test_bnpl_account.id

    # 2. ACT: Delete the account
    result = await bnpl_repository.delete(account_id)

    # 3. ASSERT: Verify soft deletion
    assert result is True

    # Verify the account is marked as closed, not physically deleted
    account = await bnpl_repository.get(account_id)
    assert account is not None
    assert account.is_closed is True
