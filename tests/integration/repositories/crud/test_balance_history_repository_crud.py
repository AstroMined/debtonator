"""
Integration tests for the BalanceHistoryRepository.

This module contains tests for the BalanceHistoryRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.
"""

from decimal import Decimal

import pytest

from src.models.accounts import Account
from src.models.balance_history import BalanceHistory
from src.repositories.balance_history import BalanceHistoryRepository
from src.utils.datetime_utils import datetime_equals, datetime_greater_than
from tests.helpers.schema_factories.balance_history_schema_factories import (
    create_balance_history_schema,
    create_balance_history_update_schema,
)

pytestmark = pytest.mark.asyncio


async def test_create_balance_history(
    balance_history_repository: BalanceHistoryRepository,
    test_checking_account: Account,
):
    """Test creating a balance history record with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. SCHEMA: Create and validate through Pydantic schema
    balance_schema = create_balance_history_schema(
        account_id=test_checking_account.id,
        balance=Decimal("1000.00"),
        is_reconciled=False,
        notes="Initial balance entry",
    )

    # Convert validated schema to dict for repository
    validated_data = balance_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await balance_history_repository.create(validated_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id is not None
    assert result.account_id == test_checking_account.id
    assert result.balance == Decimal("1000.00")
    assert result.is_reconciled is False
    assert result.notes == "Initial balance entry"
    assert result.created_at is not None
    assert result.updated_at is not None


async def test_get_balance_history(
    balance_history_repository: BalanceHistoryRepository,
    test_balance_history: BalanceHistory,
):
    """Test retrieving a balance history record by ID."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get the balance history by ID
    result = await balance_history_repository.get(test_balance_history.id)

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_balance_history.id
    assert result.account_id == test_balance_history.account_id
    assert result.balance == test_balance_history.balance
    assert result.is_reconciled == test_balance_history.is_reconciled
    assert result.notes == test_balance_history.notes
    assert datetime_equals(
        result.timestamp, test_balance_history.timestamp, ignore_timezone=True
    )


async def test_update_balance_history(
    balance_history_repository: BalanceHistoryRepository,
    test_balance_history: BalanceHistory,
):
    """Test updating a balance history record with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures

    # Store original timestamp before update
    original_updated_at = test_balance_history.updated_at

    # 2. SCHEMA: Create and validate update data through Pydantic schema
    update_schema = create_balance_history_update_schema(
        balance=Decimal("1100.00"),
        is_reconciled=True,
        notes="Updated balance entry",
    )

    # Convert validated schema to dict for repository
    update_data = update_schema.model_dump(exclude_unset=True)

    # 3. ACT: Pass validated data to repository
    result = await balance_history_repository.update(
        test_balance_history.id, update_data
    )

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_balance_history.id
    assert result.balance == Decimal("1100.00")
    assert result.is_reconciled is True
    assert result.notes == "Updated balance entry"
    # Fields not in update_data should remain unchanged
    assert result.account_id == test_balance_history.account_id
    assert datetime_equals(
        result.timestamp, test_balance_history.timestamp, ignore_timezone=True
    )
    # Compare against stored original timestamp
    assert datetime_greater_than(
        result.updated_at, original_updated_at, ignore_timezone=True
    )


async def test_delete_balance_history(
    balance_history_repository: BalanceHistoryRepository,
    test_balance_history: BalanceHistory,
):
    """Test deleting a balance history record."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Delete the balance history
    result = await balance_history_repository.delete(test_balance_history.id)

    # 3. ASSERT: Verify the operation results
    assert result is True

    # Verify the balance history is actually deleted
    deleted_check = await balance_history_repository.get(test_balance_history.id)
    assert deleted_check is None
