"""
Fixtures for category repositories.

This module provides pytest fixtures for creating and managing category repository
instances in tests.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.categories import CategoryRepository


@pytest_asyncio.fixture
async def category_repository(db_session: AsyncSession) -> CategoryRepository:
    """
    Fixture for CategoryRepository with test database session.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        CategoryRepository: Repository for category operations
    """
    return CategoryRepository(db_session)
