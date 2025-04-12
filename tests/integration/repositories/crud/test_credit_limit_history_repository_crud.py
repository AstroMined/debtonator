"""
Integration tests for the CreditLimitHistoryRepository.

This module contains tests for the CreditLimitHistoryRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.

These tests verify CRUD operations for the CreditLimitHistoryRepository, ensuring
proper validation flow and data integrity.
"""

# pylint: disable=no-member

from decimal import Decimal

import pytest

from src.models.account_types.banking.credit import CreditAccount
from src.models.credit_limit_history import CreditLimitHistory
from src.repositories.credit_limit_history import CreditLimitHistoryRepository
from src.utils.datetime_utils import datetime_greater_than, utc_now
from tests.helpers.schema_factories.credit_limit_history_schema_factories import (
    create_credit_limit_history_schema,
    create_credit_limit_history_update_schema,
)

pytestmark = pytest.mark.asyncio


async def test_create_credit_limit_history(
    credit_limit_history_repository: CreditLimitHistoryRepository,
    test_credit_account: CreditAccount,
):
    """Test creating a credit limit history entry with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. SCHEMA: Create and validate through Pydantic schema
    history_schema = create_credit_limit_history_schema(
        account_id=test_credit_account.id,
        credit_limit=Decimal("10000.00"),
        reason="Credit limit increase due to excellent payment history",
    )

    # Convert validated schema to dict for repository
    validated_data = history_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await credit_limit_history_repository.create(validated_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id is not None
    assert result.account_id == test_credit_account.id
    assert result.credit_limit == Decimal("10000.00")
    assert result.reason == "Credit limit increase due to excellent payment history"
    assert result.effective_date is not None


async def test_get_credit_limit_history(
    credit_limit_history_repository: CreditLimitHistoryRepository,
    test_credit_limit_history: CreditLimitHistory,
):
    """Test retrieving a credit limit history entry by ID."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get the history entry
    result = await credit_limit_history_repository.get(test_credit_limit_history.id)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_credit_limit_history.id
    assert result.account_id == test_credit_limit_history.account_id
    assert result.credit_limit == test_credit_limit_history.credit_limit
    assert result.reason == test_credit_limit_history.reason


async def test_update_credit_limit_history(
    credit_limit_history_repository: CreditLimitHistoryRepository,
    test_credit_limit_history: CreditLimitHistory,
):
    """Test updating a credit limit history entry with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures

    # Store original timestamp before update
    original_updated_at = test_credit_limit_history.updated_at

    # 2. SCHEMA: Create and validate update data through Pydantic schema
    update_schema = create_credit_limit_history_update_schema(
        id=test_credit_limit_history.id,
        credit_limit=Decimal("12000.00"),
        reason="Updated credit limit increase",
        effective_date=utc_now(),  # Provide required effective_date
    )

    # Convert validated schema to dict for repository
    update_data = update_schema.model_dump(exclude={"id"})

    # 3. ACT: Pass validated data to repository
    result = await credit_limit_history_repository.update(
        test_credit_limit_history.id, update_data
    )

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_credit_limit_history.id
    assert result.credit_limit == Decimal("12000.00")
    assert result.reason == "Updated credit limit increase"
    assert datetime_greater_than(
        result.updated_at, original_updated_at, ignore_timezone=True
    )


async def test_delete_credit_limit_history(
    credit_limit_history_repository: CreditLimitHistoryRepository,
    test_credit_limit_history: CreditLimitHistory,
):
    """Test deleting a credit limit history entry."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Delete the history entry
    result = await credit_limit_history_repository.delete(test_credit_limit_history.id)

    # 4. ASSERT: Verify the operation results
    assert result is True

    # Verify it's actually deleted
    deleted_history = await credit_limit_history_repository.get(
        test_credit_limit_history.id
    )
    assert deleted_history is None
