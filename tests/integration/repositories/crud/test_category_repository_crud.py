"""
Integration tests for CategoryRepository.

This module contains tests that validate the behavior of the CategoryRepository
against a real database.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.categories import CategoryRepository

pytestmark = pytest.mark.asyncio


async def test_create_category(db_session: AsyncSession):
    """Test creating a category."""
    # Create repository
    repo = CategoryRepository(db_session)

    # Create category
    category = await repo.create(
        {"name": "Test Category", "description": "Test category description"}
    )

    # Assert created category
    assert category.id is not None
    assert category.name == "Test Category"
    assert category.description == "Test category description"
    assert category.parent_id is None
