# pylint: disable=no-member,no-value-for-argument
"""
Integration tests for savings account repository CRUD operations.

Following the four-step pattern and Real Objects Testing Philosophy.
"""

from decimal import Decimal

import pytest

from src.models.account_types.banking.savings import SavingsAccount
from src.repositories.accounts import AccountRepository
from tests.helpers.schema_factories.account_types.banking.savings_schema_factories import (
    create_savings_account_schema,
)

pytestmark = pytest.mark.asyncio


async def test_create_savings_account(savings_repository: AccountRepository):
    """
    Test creating a savings account following the four-step pattern.

    Args:
        savings_repository: Repository fixture for savings accounts
    """
    # 1. ARRANGE: Nothing needed here

    # 2. SCHEMA: Create and validate through Pydantic schema
    account_schema = create_savings_account_schema(
        name="My High-Yield Savings",
        current_balance=Decimal("5000.00"),
        available_balance=Decimal("5000.00"),
        interest_rate=Decimal("0.0175"),
        compound_frequency="daily",
    )

    # Convert validated schema to dict for repository
    validated_data = account_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await savings_repository.create_typed_account("savings", validated_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert isinstance(result, SavingsAccount)
    assert result.id is not None
    assert result.name == "My High-Yield Savings"
    assert result.current_balance == Decimal("5000.00")
    assert result.available_balance == Decimal("5000.00")
    assert result.interest_rate == Decimal("0.0175")
    assert result.compound_frequency == "daily"


async def test_get_savings_account(
    savings_repository: AccountRepository, test_savings_account: SavingsAccount
):
    """
    Test retrieving a savings account by ID.

    Args:
        savings_repository: Repository fixture for savings accounts
        test_savings_account: Test savings account fixture
    """
    # 1. ARRANGE: Use fixture for test account

    # 2. ACT: Get account by ID
    result = await savings_repository.get(test_savings_account.id)

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert isinstance(result, SavingsAccount)
    assert result.id == test_savings_account.id
    assert result.name == test_savings_account.name
    assert result.account_type == "savings"


async def test_update_savings_account(
    savings_repository: AccountRepository, test_savings_account: SavingsAccount
):
    """
    Test updating a savings account.

    Args:
        savings_repository: Repository fixture for savings accounts
        test_savings_account: Test savings account fixture
    """
    # 1. ARRANGE: Use fixture for test account
    account_id = test_savings_account.id

    # 2. SCHEMA: Create update data with schema
    update_schema = create_savings_account_schema(
        name="Updated Savings Account",
        interest_rate=Decimal("0.0225"),
        compound_frequency="quarterly",
        minimum_balance=Decimal("1000.00"),
    )

    validated_data = update_schema.model_dump()

    # 3. ACT: Update the account using typed update method
    result = await savings_repository.update_typed_account(
        account_id=account_id, account_type="savings", data=validated_data
    )

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert isinstance(result, SavingsAccount)
    assert result.id == account_id
    assert result.name == "Updated Savings Account"
    assert result.interest_rate == Decimal("0.0225")
    assert result.compound_frequency == "quarterly"
    assert result.minimum_balance == Decimal("1000.00")


async def test_delete_savings_account(
    savings_repository: AccountRepository, test_savings_account: SavingsAccount
):
    """
    Test deleting (soft delete) a savings account.

    Args:
        savings_repository: Repository fixture for savings accounts
        test_savings_account: Test savings account fixture
    """
    # 1. ARRANGE: Use fixture for test account
    account_id = test_savings_account.id

    # 2. ACT: Delete the account
    result = await savings_repository.delete(account_id)

    # 3. ASSERT: Verify soft deletion
    assert result is True

    # Verify the account is marked as closed, not physically deleted
    account = await savings_repository.get(account_id)
    assert account is not None
    assert account.is_closed is True
