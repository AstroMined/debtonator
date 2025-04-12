"""
Integration tests for the TransactionHistoryRepository.

This module contains tests for the TransactionHistoryRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.
"""

# pylint: disable=no-member

from decimal import Decimal

import pytest

from src.models.accounts import Account
from src.models.transaction_history import TransactionHistory, TransactionType
from src.repositories.transaction_history import TransactionHistoryRepository
from src.utils.datetime_utils import datetime_greater_than, ensure_utc
from tests.helpers.schema_factories.transaction_history_schema_factories import (
    create_transaction_history_schema,
    create_transaction_history_update_schema,
)

pytestmark = pytest.mark.asyncio


async def test_create_transaction_history(
    transaction_history_repository: TransactionHistoryRepository,
    test_checking_account: Account,
):
    """Test creating a transaction history entry with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. SCHEMA: Create and validate through Pydantic schema
    transaction_schema = create_transaction_history_schema(
        account_id=test_checking_account.id,
        amount=Decimal("150.00"),
        transaction_type=TransactionType.DEBIT,
        description="Test purchase",
    )

    # Convert validated schema to dict for repository
    validated_data = transaction_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await transaction_history_repository.create(validated_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id is not None
    assert result.account_id == test_checking_account.id
    assert result.amount == Decimal("150.00")
    assert result.transaction_type == TransactionType.DEBIT
    assert result.description == "Test purchase"
    assert result.transaction_date is not None


async def test_get_transaction_history(
    transaction_history_repository: TransactionHistoryRepository,
    test_transaction_history: TransactionHistory,
):
    """Test retrieving a transaction history entry by ID."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. SCHEMA: No schema needed for get operation

    # 3. ACT: Get the transaction entry
    result = await transaction_history_repository.get(test_transaction_history.id)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_transaction_history.id
    assert result.account_id == test_transaction_history.account_id
    assert result.amount == test_transaction_history.amount
    assert result.transaction_type == test_transaction_history.transaction_type
    assert result.description == test_transaction_history.description


async def test_update_transaction_history(
    transaction_history_repository: TransactionHistoryRepository,
    test_transaction_history: TransactionHistory,
):
    """Test updating a transaction history entry with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures
    # Store original timestamp before update
    original_updated_at = test_transaction_history.updated_at

    # Make the naive transaction_date timezone-aware by adding UTC timezone info
    utc_transaction_date = ensure_utc(test_transaction_history.transaction_date)

    # 2. SCHEMA: Create and validate update data through Pydantic schema
    update_schema = create_transaction_history_update_schema(
        id=test_transaction_history.id,
        amount=Decimal("125.00"),
        description="Updated transaction description",
        transaction_date=utc_transaction_date,
    )

    # Convert validated schema to dict for repository
    update_data = update_schema.model_dump(exclude={"id"})

    # 3. ACT: Pass validated data to repository
    result = await transaction_history_repository.update(
        test_transaction_history.id, update_data
    )

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_transaction_history.id
    assert result.amount == Decimal("125.00")
    assert result.description == "Updated transaction description"
    assert datetime_greater_than(
        result.updated_at, original_updated_at, ignore_timezone=True
    )


async def test_delete_transaction_history(
    transaction_history_repository: TransactionHistoryRepository,
    test_transaction_history: TransactionHistory,
):
    """Test deleting a transaction history entry."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. SCHEMA: No schema needed for delete operation

    # 3. ACT: Delete the transaction history
    result = await transaction_history_repository.delete(test_transaction_history.id)

    # 4. ASSERT: Verify the operation results
    assert result is True

    # Verify the transaction history is actually deleted
    deleted_check = await transaction_history_repository.get(
        test_transaction_history.id
    )
    assert deleted_check is None
