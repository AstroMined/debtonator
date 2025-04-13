"""
Fixtures for repository factory.

This module provides pytest fixtures for creating and managing repository factory
instances in tests.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.factory import RepositoryFactory
from src.repositories.accounts import AccountRepository


@pytest_asyncio.fixture
async def repository_factory(db_session: AsyncSession, feature_flag_service=None):
    """
    Create a repository factory for testing.

    This fixture provides a real RepositoryFactory connected to the test
    database session for integration testing without mocks.

    Args:
        db_session: Database session fixture
        feature_flag_service: Optional feature flag service fixture

    Returns:
        Function: Factory function for creating repositories
    """
    async def factory(account_type=None):
        return await RepositoryFactory.create_account_repository(
            db_session, account_type, feature_flag_service
        )
    return factory


@pytest_asyncio.fixture
async def repository(db_session: AsyncSession):
    """
    Alias for account_repository fixture.

    This fixture provides backward compatibility for tests that use 'repository'
    instead of 'account_repository'.

    Args:
        db_session: Database session fixture

    Returns:
        AccountRepository: Repository for account operations
    """

    return AccountRepository(db_session)
