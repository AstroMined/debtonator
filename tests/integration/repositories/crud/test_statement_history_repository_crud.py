"""
Integration tests for the StatementHistoryRepository.

This module contains tests for the StatementHistoryRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.
"""

from datetime import timedelta
from decimal import Decimal

import pytest

from src.models.accounts import Account
from src.models.statement_history import StatementHistory
from src.repositories.statement_history import StatementHistoryRepository
from src.schemas.statement_history import StatementHistoryUpdate
from src.utils.datetime_utils import datetime_equals, datetime_greater_than, utc_now

# Import schema factory functions directly
from tests.helpers.schema_factories.statement_history import (
    create_statement_history_schema,
)

pytestmark = pytest.mark.asyncio


async def test_create_statement_history(
    statement_history_repository: StatementHistoryRepository,
    test_credit_account: Account,
):
    """Test creating a statement history record with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures
    statement_date = utc_now().replace(day=1)  # First of current month
    due_date = statement_date + timedelta(days=21)

    # 2. SCHEMA: Create and validate through Pydantic schema
    statement_schema = create_statement_history_schema(
        account_id=test_credit_account.id,
        statement_date=statement_date,
        statement_balance=Decimal("500.00"),
        minimum_payment=Decimal("25.00"),
        due_date=due_date,
    )

    # Convert validated schema to dict for repository
    validated_data = statement_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await statement_history_repository.create(validated_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id is not None
    assert result.account_id == test_credit_account.id
    assert datetime_equals(result.statement_date, statement_date, ignore_timezone=True)
    assert result.statement_balance == Decimal("500.00")
    assert result.minimum_payment == Decimal("25.00")
    assert datetime_equals(result.due_date, due_date, ignore_timezone=True)
    assert result.created_at is not None
    assert result.updated_at is not None


async def test_get_statement_history(
    statement_history_repository: StatementHistoryRepository,
    test_statement_history: StatementHistory,
):
    """Test retrieving a statement history record by ID."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get the statement history by ID
    result = await statement_history_repository.get(test_statement_history.id)

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_statement_history.id
    assert result.account_id == test_statement_history.account_id
    assert datetime_equals(
        result.statement_date,
        test_statement_history.statement_date,
        ignore_timezone=True,
    )
    assert result.statement_balance == test_statement_history.statement_balance
    assert result.minimum_payment == test_statement_history.minimum_payment
    assert datetime_equals(
        result.due_date, test_statement_history.due_date, ignore_timezone=True
    )


async def test_update_statement_history(
    statement_history_repository: StatementHistoryRepository,
    test_statement_history: StatementHistory,
):
    """Test updating a statement history entry with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures

    # Store original timestamp before update
    original_updated_at = test_statement_history.updated_at

    # 2. SCHEMA: Create and validate update data through Pydantic schema
    update_schema = StatementHistoryUpdate(
        statement_balance=Decimal("550.00"),
        minimum_payment=Decimal("30.00"),
    )

    # Convert validated schema to dict for repository
    update_data = update_schema.model_dump(exclude_unset=True)

    # 3. ACT: Pass validated data to repository
    result = await statement_history_repository.update(
        test_statement_history.id, update_data
    )

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_statement_history.id
    assert result.statement_balance == Decimal("550.00")
    assert result.minimum_payment == Decimal("30.00")
    # Fields not in update_data should remain unchanged
    assert result.account_id == test_statement_history.account_id
    assert datetime_equals(
        result.statement_date,
        test_statement_history.statement_date,
        ignore_timezone=True,
    )
    assert datetime_equals(
        result.due_date, test_statement_history.due_date, ignore_timezone=True
    )
    assert datetime_greater_than(
        result.updated_at, original_updated_at, ignore_timezone=True
    )


async def test_delete_statement_history(
    statement_history_repository: StatementHistoryRepository,
    test_statement_history: StatementHistory,
):
    """Test deleting a statement history record."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Delete the statement history
    result = await statement_history_repository.delete(test_statement_history.id)

    # 3. ASSERT: Verify the operation results
    assert result is True

    # Verify the statement history is actually deleted
    deleted_check = await statement_history_repository.get(test_statement_history.id)
    assert deleted_check is None
