"""
Fixtures for basic test models.

This module provides pytest fixtures for creating and managing TestBasicDBModel
instances in the database for testing purposes.
"""

from decimal import Decimal

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers.models.basic_test_models import TestBasicDBModel


@pytest_asyncio.fixture
async def test_item(db_session: AsyncSession) -> TestBasicDBModel:
    """
    Create a test item in the database.

    Args:
        db_session: Database session fixture

    Returns:
        TestBasicDBModel: Created test item
    """
    test_item = TestBasicDBModel(
        name="Fixture Test Item",
        description="Test description",
        numeric_value=Decimal("100.0000"),
        is_active=True,
    )
    db_session.add(test_item)
    await db_session.flush()
    await db_session.refresh(test_item)
    return test_item


@pytest_asyncio.fixture
async def test_items(db_session: AsyncSession) -> list[TestBasicDBModel]:
    """
    Create multiple test items in the database.

    Args:
        db_session: Database session fixture

    Returns:
        list[TestBasicDBModel]: List of created test items
    """
    items = []
    for i in range(5):
        test_item = TestBasicDBModel(
            name=f"Fixture Test Item {i}",
            description=f"Test description {i}",
            numeric_value=Decimal(f"{i * 100}.0000"),
            is_active=True,
        )
        db_session.add(test_item)
        items.append(test_item)

    await db_session.flush()

    # Refresh all items
    for item in items:
        await db_session.refresh(item)

    return items
