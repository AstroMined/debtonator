"""
Fixtures for credit account repositories.

This module provides pytest fixtures for creating and managing credit account repository
instances in tests.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.factory import RepositoryFactory


@pytest_asyncio.fixture
async def credit_repository(
    db_session: AsyncSession, repository_factory: RepositoryFactory
) -> RepositoryFactory:
    """
    Create a credit account repository for testing.

    This fixture provides a specialized repository for credit accounts
    with all credit-specific operations available.

    Args:
        db_session: Database session fixture
        repository_factory: Repository factory fixture

    Returns:
        AccountRepository: Repository with credit-specific operations
    """
    return await repository_factory(account_type="credit")
