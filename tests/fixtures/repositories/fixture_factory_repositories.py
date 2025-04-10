"""
Fixtures for repository factory.

This module provides pytest fixtures for creating and managing repository factory
instances in tests.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.factory import RepositoryFactory


@pytest_asyncio.fixture
async def repository_factory(db_session: AsyncSession) -> RepositoryFactory:
    """
    Create a repository factory for testing.
    
    This fixture provides a real RepositoryFactory connected to the test
    database session for integration testing without mocks.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        RepositoryFactory: Factory for creating repositories
    """
    return RepositoryFactory(db_session)
