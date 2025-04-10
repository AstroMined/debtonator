"""
Integration tests for the BillSplitRepository using the standard validation pattern.

This test file demonstrates the proper validation flow for repository tests,
simulating how services call repositories in the actual application flow.
It follows the standard pattern:

1. Arrange: Set up test data and dependencies
2. Schema: Create and validate data through Pydantic schemas
3. Act: Pass validated data to repository methods
4. Assert: Verify the repository operation results
"""

from decimal import Decimal
from typing import List

import pytest

from src.models.accounts import Account
from src.models.bill_splits import BillSplit
from src.models.liabilities import Liability
from src.repositories.bill_splits import BillSplitRepository
from src.utils.datetime_utils import datetime_greater_than
from tests.helpers.schema_factories.bill_splits_schema_factories import (
    create_bill_split_schema,
    create_bill_split_update_schema,
)

pytestmark = pytest.mark.asyncio


async def test_create_bill_split(
    bill_split_repository: BillSplitRepository,
    test_liability: Liability,
    test_checking_account: Account,
):
    """Test creating a bill split with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. SCHEMA: Create and validate through Pydantic schema
    bill_split_schema = create_bill_split_schema(
        liability_id=test_liability.id,
        account_id=test_checking_account.id,
        amount=Decimal("150.00"),
    )

    # Convert validated schema to dict for repository
    validated_data = bill_split_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await bill_split_repository.create(validated_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id is not None
    assert result.liability_id == test_liability.id
    assert result.account_id == test_checking_account.id
    assert result.amount == Decimal("150.00")
    assert result.created_at is not None
    assert result.updated_at is not None


async def test_get_bill_split(
    bill_split_repository: BillSplitRepository,
    test_bill_splits: List[BillSplit],
):
    """Test retrieving a bill split by ID."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get the bill split by ID
    result = await bill_split_repository.get(test_bill_splits[0].id)

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_bill_splits[0].id
    assert result.liability_id == test_bill_splits[0].liability_id
    assert result.account_id == test_bill_splits[0].account_id
    assert result.amount == test_bill_splits[0].amount


async def test_update_bill_split(
    bill_split_repository: BillSplitRepository,
    test_bill_splits: List[BillSplit],
):
    """Test updating a bill split with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures

    # Store original timestamp before update
    original_updated_at = test_bill_splits[0].updated_at

    # 2. SCHEMA: Create and validate through Pydantic schema
    bill_split_id = test_bill_splits[0].id
    new_amount = Decimal("175.00")

    # Create schema with factory function
    update_schema = create_bill_split_update_schema(id=bill_split_id, amount=new_amount)

    # Convert validated schema to dict for repository
    update_data = update_schema.model_dump(exclude={"id"})

    # 3. ACT: Pass validated data to repository
    result = await bill_split_repository.update(bill_split_id, update_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == bill_split_id
    assert result.amount == new_amount
    # Compare against stored original timestamp
    assert datetime_greater_than(
        result.updated_at, original_updated_at, ignore_timezone=True
    )


async def test_delete_bill_split(
    bill_split_repository: BillSplitRepository,
    test_bill_splits: List[BillSplit],
):
    """Test deleting a bill split."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Delete the bill split
    result = await bill_split_repository.delete(test_bill_splits[0].id)

    # 3. ASSERT: Verify the operation results
    assert result is True

    # Verify it's actually deleted
    deleted_split = await bill_split_repository.get(test_bill_splits[0].id)
    assert deleted_split is None
