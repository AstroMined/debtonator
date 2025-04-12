"""
Fixtures for income category repositories.

This module provides pytest fixtures for creating and managing income category repository
instances in tests.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.income_categories import IncomeCategoryRepository


@pytest_asyncio.fixture
async def income_category_repository(
    db_session: AsyncSession,
) -> IncomeCategoryRepository:
    """
    Fixture for IncomeCategoryRepository with test database session.

    Args:
        db_session: Database session fixture

    Returns:
        IncomeCategoryRepository: Repository for income category operations
    """
    return IncomeCategoryRepository(db_session)
