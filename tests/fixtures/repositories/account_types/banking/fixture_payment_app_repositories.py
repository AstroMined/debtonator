"""
Fixtures for payment app account repositories.

This module provides pytest fixtures for creating and managing payment app account
repository instances in tests.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.factory import RepositoryFactory


@pytest_asyncio.fixture
async def payment_app_repository(
    db_session: AsyncSession, repository_factory: RepositoryFactory
) -> RepositoryFactory:
    """
    Create a payment app account repository for testing.
    
    This fixture provides a specialized repository for payment app accounts
    with all payment app-specific operations available.
    
    Args:
        db_session: Database session fixture
        repository_factory: Repository factory fixture
        
    Returns:
        AccountRepository: Repository with payment app-specific operations
    """
    return repository_factory(account_type="payment_app")
