"""
Fixtures for balance history repositories.

This module provides pytest fixtures for creating and managing balance history repository
instances in tests.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.balance_history import BalanceHistoryRepository


@pytest_asyncio.fixture
async def balance_history_repository(
    db_session: AsyncSession,
) -> BalanceHistoryRepository:
    """
    Fixture for BalanceHistoryRepository with test database session.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        BalanceHistoryRepository: Repository for balance history operations
    """
    return BalanceHistoryRepository(db_session)
