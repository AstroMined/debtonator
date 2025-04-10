"""
Fixtures for feature flag repositories.

This module provides pytest fixtures for creating and managing feature flag repository
instances in tests.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.feature_flags import FeatureFlagRepository


@pytest_asyncio.fixture
async def feature_flag_repository(
    db_session: AsyncSession,
) -> FeatureFlagRepository:
    """
    Fixture for FeatureFlagRepository with test database session.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        FeatureFlagRepository: Repository for feature flag operations
    """
    return FeatureFlagRepository(db_session)
