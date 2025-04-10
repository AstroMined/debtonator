"""
Integration tests for the IncomeCategoryRepository.

This module contains tests for the IncomeCategoryRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.

These tests verify CRUD operations and specialized methods for the
IncomeCategoryRepository, ensuring proper validation flow and data integrity.
"""

# pylint: disable=no-member

import pytest

from src.models.income_categories import IncomeCategory
from src.repositories.income_categories import IncomeCategoryRepository

# Import schemas and schema factories - essential part of the validation pattern
from src.utils.datetime_utils import datetime_greater_than
from tests.helpers.schema_factories.income_categories_schema_factories import (
    create_income_category_schema,
    create_income_category_update_schema,
)

pytestmark = pytest.mark.asyncio


async def test_create_income_category(
    income_category_repository: IncomeCategoryRepository,
):
    """Test creating an income category with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. SCHEMA: Create and validate through Pydantic schema
    category_schema = create_income_category_schema(
        name="New Test Category",
        description="A newly created test category",
    )

    # Convert validated schema to dict for repository
    validated_data = category_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await income_category_repository.create(validated_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id is not None
    assert result.name == "New Test Category"
    assert result.description == "A newly created test category"
    assert result.created_at is not None
    assert result.updated_at is not None


async def test_get_income_category(
    income_category_repository: IncomeCategoryRepository,
    test_income_category: IncomeCategory,
):
    """Test retrieving an income category by ID."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get the income category
    result = await income_category_repository.get(test_income_category.id)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_income_category.id
    assert result.name == test_income_category.name
    assert result.description == test_income_category.description


async def test_update_income_category(
    income_category_repository: IncomeCategoryRepository,
    test_income_category: IncomeCategory,
):
    """Test updating an income category with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures

    # Store original timestamp before update
    original_updated_at = test_income_category.updated_at

    # 2. SCHEMA: Create and validate update data through Pydantic schema
    update_schema = create_income_category_update_schema(
        name="Updated Category Name",
        description="Updated category description",
    )

    # Convert validated schema to dict for repository
    update_data = update_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await income_category_repository.update(
        test_income_category.id, update_data
    )

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_income_category.id
    assert result.name == "Updated Category Name"
    assert result.description == "Updated category description"
    assert datetime_greater_than(
        result.updated_at, original_updated_at, ignore_timezone=True
    )


async def test_delete_income_category(
    income_category_repository: IncomeCategoryRepository,
    test_income_category: IncomeCategory,
):
    """Test deleting an income category."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Delete the income category
    result = await income_category_repository.delete(test_income_category.id)

    # 4. ASSERT: Verify the operation results
    assert result is True

    # Verify it's actually deleted
    deleted_category = await income_category_repository.get(test_income_category.id)
    assert deleted_category is None
