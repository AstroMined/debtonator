"""
Fixtures for BNPL account repositories.

This module provides pytest fixtures for creating and managing Buy Now Pay Later (BNPL)
account repository instances in tests.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.factory import RepositoryFactory


@pytest_asyncio.fixture
async def bnpl_repository(
    db_session: AsyncSession, repository_factory: RepositoryFactory
) -> RepositoryFactory:
    """
    Create a BNPL account repository for testing.

    This fixture provides a specialized repository for Buy Now Pay Later (BNPL) accounts
    with all BNPL-specific operations available.

    Args:
        db_session: Database session fixture
        repository_factory: Repository factory fixture

    Returns:
        AccountRepository: Repository with BNPL-specific operations
    """
    return await repository_factory(account_type="bnpl")
