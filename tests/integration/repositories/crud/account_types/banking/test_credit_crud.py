# pylint: disable=no-member,no-value-for-argument
"""
Integration tests for credit account repository CRUD operations.

Following the four-step pattern and Real Objects Testing Philosophy.
"""

from decimal import Decimal

import pytest

from src.models.account_types.banking.credit import CreditAccount
from src.repositories.accounts import AccountRepository
from tests.helpers.schema_factories.account_types.banking.credit_schema_factories import (
    create_credit_account_schema,
)

pytestmark = pytest.mark.asyncio


async def test_create_credit_account(credit_repository: AccountRepository):
    """
    Test creating a credit account following the four-step pattern.

    Args:
        credit_repository: Repository fixture for credit accounts
    """
    # 1. ARRANGE: Nothing needed here

    # 2. SCHEMA: Create and validate through Pydantic schema
    account_schema = create_credit_account_schema(
        name="My Rewards Credit Card",
        current_balance=Decimal("-500.00"),
        available_balance=Decimal("-500.00"),
        credit_limit=Decimal("3000.00"),
        available_credit=Decimal("2500.00"),
        apr=Decimal("15.99"),
    )

    # Convert validated schema to dict for repository
    validated_data = account_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await credit_repository.create_typed_account("credit", validated_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert isinstance(result, CreditAccount)
    assert result.id is not None
    assert result.name == "My Rewards Credit Card"
    assert result.current_balance == Decimal("-500.00")
    assert result.available_balance == Decimal("-500.00")
    assert result.credit_limit == Decimal("3000.00")
    assert result.apr == Decimal("15.99")


async def test_get_credit_account(
    credit_repository: AccountRepository, test_credit_account: CreditAccount
):
    """
    Test retrieving a credit account by ID.

    Args:
        credit_repository: Repository fixture for credit accounts
        test_credit_account: Test credit account fixture
    """
    # 1. ARRANGE: Use fixture for test account

    # 2. ACT: Get account by ID
    result = await credit_repository.get(test_credit_account.id)

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert isinstance(result, CreditAccount)
    assert result.id == test_credit_account.id
    assert result.name == test_credit_account.name
    assert result.account_type == "credit"


async def test_update_credit_account(
    credit_repository: AccountRepository, test_credit_account: CreditAccount
):
    """
    Test updating a credit account.

    Args:
        credit_repository: Repository fixture for credit accounts
        test_credit_account: Test credit account fixture
    """
    # 1. ARRANGE: Use fixture for test account
    account_id = test_credit_account.id

    # 2. SCHEMA: Create update data with schema
    update_schema = create_credit_account_schema(
        name="Updated Credit Card",
        apr=Decimal("14.99"),
        rewards_program="Travel Points",
        autopay_status="minimum",
    )

    validated_data = update_schema.model_dump()

    # 3. ACT: Update the account using typed update method
    result = await credit_repository.update_typed_account(
        account_id=account_id, account_type="credit", data=validated_data
    )

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert isinstance(result, CreditAccount)
    assert result.id == account_id
    assert result.name == "Updated Credit Card"
    assert result.apr == Decimal("14.99")
    assert result.rewards_program == "Travel Points"
    assert result.autopay_status == "minimum"


async def test_delete_credit_account(
    credit_repository: AccountRepository, test_credit_account: CreditAccount
):
    """
    Test deleting (soft delete) a credit account.

    Args:
        credit_repository: Repository fixture for credit accounts
        test_credit_account: Test credit account fixture
    """
    # 1. ARRANGE: Use fixture for test account
    account_id = test_credit_account.id

    # 2. ACT: Delete the account
    result = await credit_repository.delete(account_id)

    # 3. ASSERT: Verify soft deletion
    assert result is True

    # Verify the account is marked as closed, not physically deleted
    account = await credit_repository.get(account_id)
    assert account is not None
    assert account.is_closed is True
