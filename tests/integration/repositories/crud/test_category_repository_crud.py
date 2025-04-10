"""
Integration tests for CategoryRepository.

This module contains tests for the CategoryRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.

These tests verify CRUD operations for the CategoryRepository, ensuring
proper validation flow and data integrity.
"""

#pylint: disable=no-member

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.categories import Category
from src.repositories.categories import CategoryRepository
from tests.helpers.schema_factories.categories_schema_factories import (
    create_category_schema,
    create_category_update_schema,
)

pytestmark = pytest.mark.asyncio


async def test_create_category(category_repository: CategoryRepository):
    """Test creating a category with proper validation flow."""
    # 1. ARRANGE: No additional setup needed

    # 2. SCHEMA: Create and validate through Pydantic schema
    category_schema = create_category_schema(
        name="Test Category",
        description="Test category description"
    )

    # Convert validated schema to dict for repository
    validated_data = category_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await category_repository.create(validated_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id is not None
    assert result.name == "Test Category"
    assert result.description == "Test category description"
    assert result.parent_id is None


async def test_get_category(
    category_repository: CategoryRepository,
    test_category: Category,
):
    """Test retrieving a category by ID."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Get the category
    result = await category_repository.get(test_category.id)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_category.id
    assert result.name == test_category.name
    assert result.description == test_category.description


async def test_update_category(
    category_repository: CategoryRepository,
    test_category: Category,
):
    """Test updating a category with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. SCHEMA: Create and validate update data through Pydantic schema
    update_schema = create_category_update_schema(
        name="Updated Category",
        description="Updated description"
    )

    # Convert validated schema to dict for repository
    update_data = update_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await category_repository.update(test_category.id, update_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_category.id
    assert result.name == "Updated Category"
    assert result.description == "Updated description"


async def test_delete_category(
    category_repository: CategoryRepository,
    test_category: Category,
):
    """Test deleting a category."""
    # 1. ARRANGE & 2. SCHEMA: Setup is already done with fixtures

    # 3. ACT: Delete the category
    result = await category_repository.delete(test_category.id)

    # 4. ASSERT: Verify the operation results
    assert result is True

    # Verify it's actually deleted
    deleted_category = await category_repository.get(test_category.id)
    assert deleted_category is None
