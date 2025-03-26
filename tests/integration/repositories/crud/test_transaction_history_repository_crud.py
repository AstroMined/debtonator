"""
Integration tests for the TransactionHistoryRepository.

This module contains tests for the TransactionHistoryRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.
"""

import asyncio
from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.transaction_history import TransactionHistory, TransactionType
from src.repositories.accounts import AccountRepository
from src.repositories.transaction_history import TransactionHistoryRepository
from src.schemas.transaction_history import (TransactionHistoryCreate,
                                             TransactionHistoryUpdate)
from src.utils.datetime_utils import (datetime_equals,
                                          datetime_greater_than, utc_now)
from tests.helpers.schema_factories.accounts import create_account_schema
from tests.helpers.schema_factories.transaction_history import \
    create_transaction_history_schema

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

    # 2. ACT: Get the transaction entry
    result = await transaction_history_repository.get(test_transaction_history.id)

    # 3. ASSERT: Verify the operation results
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

    # 2. SCHEMA: Create and validate update data through Pydantic schema
    # Make the naive transaction_date timezone-aware by adding UTC timezone info
    utc_transaction_date = datetime.replace(
        test_transaction_history.transaction_date, tzinfo=timezone.utc
    )

    update_schema = TransactionHistoryUpdate(
        id=test_transaction_history.id,
        amount=Decimal("125.00"),
        description="Updated transaction description",
        transaction_type=test_transaction_history.transaction_type,  # Explicitly include to avoid NULL constraint error
        transaction_date=utc_transaction_date,  # Make it timezone-aware with UTC
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
    assert (
        result.transaction_type == test_transaction_history.transaction_type
    )  # Unchanged
    assert datetime_greater_than(
        result.updated_at, original_updated_at, ignore_timezone=True
    )
