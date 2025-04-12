# pylint: disable=no-member,no-value-for-argument
"""
Integration tests for checking account repository CRUD operations.

Following the four-step pattern and Real Objects Testing Philosophy.
"""

from decimal import Decimal

import pytest

from src.models.account_types.banking.checking import CheckingAccount
from src.repositories.accounts import AccountRepository
from tests.helpers.schema_factories.account_types.banking.checking_schema_factories import (
    create_checking_account_schema,
)

pytestmark = pytest.mark.asyncio


async def test_create_checking_account(checking_repository: AccountRepository):
    """
    Test creating a checking account following the four-step pattern.

    Args:
        checking_repository: Repository fixture for checking accounts
    """
    # 1. ARRANGE: Nothing needed here

    # 2. SCHEMA: Create and validate through Pydantic schema
    account_schema = create_checking_account_schema(
        name="My Primary Checking",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
        has_overdraft_protection=True,
        overdraft_limit=Decimal("500.00"),
    )

    # Convert validated schema to dict for repository
    validated_data = account_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await checking_repository.create_typed_account("checking", validated_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert isinstance(result, CheckingAccount)
    assert result.id is not None
    assert result.name == "My Primary Checking"
    assert result.current_balance == Decimal("1000.00")
    assert result.available_balance == Decimal("1000.00")
    assert result.has_overdraft_protection is True
    assert result.overdraft_limit == Decimal("500.00")


async def test_get_checking_account(
    checking_repository: AccountRepository, test_checking_account: CheckingAccount
):
    """
    Test retrieving a checking account by ID.

    Args:
        checking_repository: Repository fixture for checking accounts
        test_checking_account: Test checking account fixture
    """
    # 1. ARRANGE: Use fixture for test account

    # 2. ACT: Get account by ID
    result = await checking_repository.get(test_checking_account.id)

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert isinstance(result, CheckingAccount)
    assert result.id == test_checking_account.id
    assert result.name == test_checking_account.name
    assert result.account_type == "checking"


async def test_update_checking_account(
    checking_repository: AccountRepository, test_checking_account: CheckingAccount
):
    """
    Test updating a checking account.

    Args:
        checking_repository: Repository fixture for checking accounts
        test_checking_account: Test checking account fixture
    """
    # 1. ARRANGE: Use fixture for test account
    account_id = test_checking_account.id

    # 2. SCHEMA: Create update data with schema
    update_schema = create_checking_account_schema(
        name="Updated Checking Account",
        has_overdraft_protection=True,
        overdraft_limit=Decimal("250.00"),
        monthly_fee=Decimal("5.99"),
    )

    validated_data = update_schema.model_dump()

    # 3. ACT: Update the account using typed update method
    result = await checking_repository.update_typed_account(
        account_id=account_id, account_type="checking", data=validated_data
    )

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert isinstance(result, CheckingAccount)
    assert result.id == account_id
    assert result.name == "Updated Checking Account"
    assert result.has_overdraft_protection is True
    assert result.overdraft_limit == Decimal("250.00")
    assert result.monthly_fee == Decimal("5.99")


async def test_delete_checking_account(
    checking_repository: AccountRepository, test_checking_account: CheckingAccount
):
    """
    Test deleting (soft delete) a checking account.

    Args:
        checking_repository: Repository fixture for checking accounts
        test_checking_account: Test checking account fixture
    """
    # 1. ARRANGE: Use fixture for test account
    account_id = test_checking_account.id

    # 2. ACT: Delete the account
    result = await checking_repository.delete(account_id)

    # 3. ASSERT: Verify soft deletion
    assert result is True

    # Verify the account is marked as closed, not physically deleted
    account = await checking_repository.get(account_id)
    assert account is not None
    assert account.is_closed is True
