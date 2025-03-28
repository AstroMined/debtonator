"""
Integration tests for the LiabilityRepository.

This module contains tests for the LiabilityRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.categories import Category
from src.models.liabilities import Liability, LiabilityStatus
from src.repositories.liabilities import LiabilityRepository
from src.schemas.liabilities import LiabilityCreate, LiabilityUpdate
from src.utils.datetime_utils import datetime_equals, datetime_greater_than, utc_now
from tests.helpers.schema_factories.accounts import create_account_schema
from tests.helpers.schema_factories.categories import create_category_schema
from tests.helpers.schema_factories.liabilities import create_liability_schema

pytestmark = pytest.mark.asyncio


async def test_create_liability(
    liability_repository: LiabilityRepository,
    test_checking_account: Account,
    test_category: Category,
):
    """Test creating a liability with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures
    due_date = utc_now() + timedelta(days=30)

    # 2. SCHEMA: Create and validate through Pydantic schema
    liability_schema = create_liability_schema(
        name="Test Monthly Bill",
        amount=Decimal("75.50"),
        due_date=due_date,
        category_id=test_category.id,
        primary_account_id=test_checking_account.id,
        description="Monthly service bill",
    )

    # Convert validated schema to dict for repository
    validated_data = liability_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await liability_repository.create(validated_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id is not None
    assert result.name == "Test Monthly Bill"
    assert result.amount == Decimal("75.50")
    assert datetime_equals(result.due_date, due_date, ignore_timezone=True)
    assert result.category_id == test_category.id
    assert result.primary_account_id == test_checking_account.id
    assert result.description == "Monthly service bill"
    assert result.paid is False
    assert result.status == LiabilityStatus.PENDING


async def test_get_liability(
    liability_repository: LiabilityRepository,
    test_liability: Liability,
):
    """Test retrieving a liability by ID."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get the liability by ID
    result = await liability_repository.get(test_liability.id)

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_liability.id
    assert result.name == test_liability.name
    assert result.amount == test_liability.amount
    assert datetime_equals(
        result.due_date, test_liability.due_date, ignore_timezone=True
    )
    assert result.category_id == test_liability.category_id
    assert result.primary_account_id == test_liability.primary_account_id


async def test_update_liability(
    liability_repository: LiabilityRepository,
    test_liability: Liability,
):
    """Test updating a liability with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures

    # Store original timestamp before update
    original_updated_at = test_liability.updated_at

    # 2. SCHEMA: Create and validate update data through Pydantic schema
    update_schema = LiabilityUpdate(
        id=test_liability.id,
        name="Updated Bill Name",
        amount=Decimal("150.00"),
        description="Updated description",
    )

    # Convert validated schema to dict for repository
    update_data = update_schema.model_dump(exclude={"id"})

    # 3. ACT: Pass validated data to repository
    result = await liability_repository.update(test_liability.id, update_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_liability.id
    assert result.name == "Updated Bill Name"
    assert result.amount == Decimal("150.00")
    assert result.description == "Updated description"
    # Fields not in update_data should remain unchanged
    assert datetime_equals(
        result.due_date, test_liability.due_date, ignore_timezone=True
    )
    assert result.category_id == test_liability.category_id
    assert result.primary_account_id == test_liability.primary_account_id
    assert datetime_greater_than(
        result.updated_at, original_updated_at, ignore_timezone=True
    )


async def test_delete_liability(
    liability_repository: LiabilityRepository,
    test_liability: Liability,
):
    """Test deleting a liability."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Delete the liability
    result = await liability_repository.delete(test_liability.id)

    # 3. ASSERT: Verify the operation results
    assert result is True

    # Verify the liability is actually deleted
    deleted_check = await liability_repository.get(test_liability.id)
    assert deleted_check is None
