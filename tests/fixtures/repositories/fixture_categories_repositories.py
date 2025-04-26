"""
Fixtures for category repositories.

This module provides pytest fixtures for creating and managing category repository
instances in tests.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.categories import CategoryRepository
from src.services.system_initialization import SystemInitializationService


@pytest_asyncio.fixture
async def category_repository(db_session: AsyncSession) -> CategoryRepository:
    """
    Fixture for CategoryRepository with test database session.

    Initializes system categories to ensure proper test behavior.

    Args:
        db_session: Database session fixture

    Returns:
        CategoryRepository: Repository for category operations
    """
    repo = CategoryRepository(db_session)

    # Initialize system categories to ensure default category exists
    # Use the service class directly instead of the legacy function
    service = SystemInitializationService(db_session)
    await service.ensure_system_categories()

    return repo
