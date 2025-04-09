"""
Fixtures for test items.

This module provides pytest fixtures for creating and managing test items
in the database for testing purposes.
"""

# pylint: disable=no-member

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.base_repository import BaseRepository
from tests.helpers.models.test_basic_db_model import TestBasicDBModel
from tests.helpers.schema_factories.basic_test_schema_factories import (
    create_test_item_schema,
)


@pytest.fixture
async def test_item_repository(db_session: AsyncSession):
    """
    Create a repository for TestItem models.

    Args:
        db_session: Database session fixture

    Returns:
        BaseRepository: Repository for TestItem models
    """
    return BaseRepository(db_session, TestBasicDBModel)


@pytest.fixture
async def test_item(test_item_repository: BaseRepository):
    """
    Create a test item in the database.

    Args:
        test_item_repository: Repository for TestItem models

    Returns:
        TestItem: Created test item
    """
    test_item_schema = create_test_item_schema(name="Fixture Test Item")
    # Convert schema to dict for repository
    schema_dict = test_item_schema.model_dump()
    return await test_item_repository.create(schema_dict)


@pytest.fixture
async def test_items(test_item_repository: BaseRepository):
    """
    Create multiple test items in the database.

    Args:
        test_item_repository: Repository for TestItem models

    Returns:
        list[TestItem]: List of created test items
    """
    items = []
    for i in range(5):
        test_item_schema = create_test_item_schema(
            name=f"Fixture Test Item {i}",
            numeric_value=i * 100,
        )
        # Convert schema to dict for repository
        schema_dict = test_item_schema.model_dump()
        item = await test_item_repository.create(schema_dict)
        items.append(item)
    return items
