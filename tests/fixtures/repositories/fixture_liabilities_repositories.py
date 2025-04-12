"""
Fixtures for liability repositories.

This module provides pytest fixtures for creating and managing liability repository
instances in tests.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.liabilities import LiabilityRepository


@pytest_asyncio.fixture
async def liability_repository(db_session: AsyncSession) -> LiabilityRepository:
    """
    Fixture for LiabilityRepository with test database session.

    Args:
        db_session: Database session fixture

    Returns:
        LiabilityRepository: Repository for liability operations
    """
    return LiabilityRepository(db_session)
