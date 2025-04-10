"""
Fixtures for account repositories.

This module provides pytest fixtures for creating and managing account repository
instances in tests.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.accounts import AccountRepository
from src.repositories.factory import RepositoryFactory


@pytest_asyncio.fixture
async def account_repository(db_session: AsyncSession) -> AccountRepository:
    """
    Fixture for AccountRepository with test database session.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        AccountRepository: Repository for account operations
    """
    return AccountRepository(db_session)
