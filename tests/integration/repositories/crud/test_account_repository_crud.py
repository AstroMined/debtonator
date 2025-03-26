"""
Integration tests for the AccountRepository.

This module contains tests for the AccountRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.statement_history import StatementHistory
from src.repositories.accounts import AccountRepository
from src.repositories.statement_history import StatementHistoryRepository
from src.utils.datetime_utils import (datetime_equals,
                                          datetime_greater_than, utc_now)
from tests.helpers.schema_factories.accounts import (
    create_account_schema, create_account_update_schema)
from tests.helpers.schema_factories.statement_history import \
    create_statement_history_schema

pytestmark = pytest.mark.asyncio


async def test_create_account(account_repository: AccountRepository):
    """Test creating an account with proper validation flow."""
    # 1. ARRANGE: No setup needed for this test

    # 2. SCHEMA: Create and validate through Pydantic schema
    account_schema = create_account_schema(
        name="New Test Account",
        account_type="savings",
        available_balance=Decimal("2500.00"),
        description="Test savings account created through repository",
    )

    # Convert validated schema to dict for repository
    validated_data = account_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await account_repository.create(validated_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id is not None
    assert result.name == "New Test Account"
    assert result.type == "savings"
    assert result.available_balance == Decimal("2500.00")
    assert result.description == "Test savings account created through repository"
    assert result.created_at is not None
    assert result.updated_at is not None


async def test_get_account(
    account_repository: AccountRepository, test_checking_account: Account
):
    """Test retrieving an account by ID."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get the account by ID
    result = await account_repository.get(test_checking_account.id)

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_checking_account.id
    assert result.name == test_checking_account.name
    assert result.type == test_checking_account.type
    assert result.available_balance == test_checking_account.available_balance


async def test_update_account(
    account_repository: AccountRepository, test_checking_account: Account
):
    """Test updating an account with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures

    # Store original timestamp before update
    original_updated_at = test_checking_account.updated_at

    # 2. SCHEMA: Create and validate update data through Pydantic schema
    update_schema = create_account_update_schema(
        id=test_checking_account.id,
        name="Updated Account Name",
        description="Updated account description",
    )

    # Convert validated schema to dict for repository
    update_data = update_schema.model_dump(exclude={"id"})

    # 3. ACT: Pass validated data to repository
    result = await account_repository.update(test_checking_account.id, update_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_checking_account.id
    assert result.name == "Updated Account Name"
    assert result.description == "Updated account description"
    # Fields not in update_data should remain unchanged
    assert result.type == test_checking_account.type
    assert result.available_balance == test_checking_account.available_balance
    # Compare against stored original timestamp instead of test_checking_account.updated_at
    assert datetime_greater_than(
        result.updated_at, original_updated_at, ignore_timezone=True
    )


async def test_delete_account(
    account_repository: AccountRepository, test_checking_account: Account
):
    """Test deleting an account."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Delete the account
    result = await account_repository.delete(test_checking_account.id)

    # 3. ASSERT: Verify the operation results
    assert result is True

    # Verify the account is actually deleted
    deleted_check = await account_repository.get(test_checking_account.id)
    assert deleted_check is None
