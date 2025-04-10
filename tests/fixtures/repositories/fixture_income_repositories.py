"""
Fixtures for income repositories.

This module provides pytest fixtures for creating and managing income repository
instances in tests.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.income import IncomeRepository


@pytest_asyncio.fixture
async def income_repository(db_session: AsyncSession) -> IncomeRepository:
    """
    Fixture for IncomeRepository with test database session.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        IncomeRepository: Repository for income operations
    """
    return IncomeRepository(db_session)
