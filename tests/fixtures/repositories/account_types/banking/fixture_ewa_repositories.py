"""
Fixtures for EWA account repositories.

This module provides pytest fixtures for creating and managing Earned Wage Access (EWA)
account repository instances in tests.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.factory import RepositoryFactory


@pytest_asyncio.fixture
async def ewa_repository(
    db_session: AsyncSession, 
    repository_factory: RepositoryFactory,
    feature_flag_service=None
) -> RepositoryFactory:
    """
    Create an EWA account repository for testing.
    
    This fixture provides a specialized repository for Earned Wage Access (EWA) accounts
    with all EWA-specific operations available.
    
    Args:
        db_session: Database session fixture
        repository_factory: Repository factory fixture
        feature_flag_service: Optional feature flag service fixture
        
    Returns:
        AccountRepository: Repository with EWA-specific operations
    """
    # Repository factory will use the feature_flag_service parameter we fixed earlier
    return repository_factory(account_type="ewa")
