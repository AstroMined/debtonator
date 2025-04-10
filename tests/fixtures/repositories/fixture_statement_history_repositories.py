"""
Fixtures for statement history repositories.

This module provides pytest fixtures for creating and managing statement history repository
instances in tests.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.statement_history import StatementHistoryRepository


@pytest_asyncio.fixture
async def statement_history_repository(
    db_session: AsyncSession,
) -> StatementHistoryRepository:
    """
    Fixture for StatementHistoryRepository with test database session.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        StatementHistoryRepository: Repository for statement history operations
    """
    return StatementHistoryRepository(db_session)
