"""
Fixtures for test item repositories.

This module provides pytest fixtures for creating and managing repositories
for TestBasicDBModel instances in tests.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.base_repository import BaseRepository
from tests.helpers.models.basic_test_models import TestBasicDBModel


@pytest_asyncio.fixture
async def test_item_repository(db_session: AsyncSession) -> BaseRepository:
    """
    Create a repository for TestBasicDBModel instances.

    This fixture provides a real BaseRepository connected to the test
    database session for integration testing without mocks.

    Args:
        db_session: Database session fixture

    Returns:
        BaseRepository: Repository for TestBasicDBModel instances
    """
    return BaseRepository(db_session, TestBasicDBModel)
