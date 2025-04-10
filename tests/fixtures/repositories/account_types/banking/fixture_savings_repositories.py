"""
Fixtures for savings account repositories.

This module provides pytest fixtures for creating and managing savings account repository
instances in tests.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.factory import RepositoryFactory


@pytest_asyncio.fixture
async def savings_repository(
    db_session: AsyncSession, repository_factory: RepositoryFactory
) -> RepositoryFactory:
    """
    Create a savings account repository for testing.
    
    This fixture provides a specialized repository for savings accounts
    with all savings-specific operations available.
    
    Args:
        db_session: Database session fixture
        repository_factory: Repository factory fixture
        
    Returns:
        AccountRepository: Repository with savings-specific operations
    """
    return repository_factory.create_account_repository(
        session=db_session, account_type="savings"
    )
