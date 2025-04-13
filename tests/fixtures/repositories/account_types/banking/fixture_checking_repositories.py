"""
Fixtures for checking account repositories.

This module provides pytest fixtures for creating and managing checking account repository
instances in tests.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.factory import RepositoryFactory


@pytest_asyncio.fixture
async def checking_repository(
    db_session: AsyncSession, repository_factory: RepositoryFactory
) -> RepositoryFactory:
    """
    Create a checking account repository for testing.

    This fixture provides a specialized repository for checking accounts
    with all checking-specific operations available.

    Args:
        db_session: Database session fixture
        repository_factory: Repository factory fixture

    Returns:
        AccountRepository: Repository with checking-specific operations
    """
    return await repository_factory(account_type="checking")
