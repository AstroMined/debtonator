"""
Fixtures for credit limit history repositories.

This module provides pytest fixtures for creating and managing credit limit history repository
instances in tests.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.credit_limit_history import CreditLimitHistoryRepository


@pytest_asyncio.fixture
async def credit_limit_history_repository(
    db_session: AsyncSession,
) -> CreditLimitHistoryRepository:
    """
    Fixture for CreditLimitHistoryRepository with test database session.

    Args:
        db_session: Database session fixture

    Returns:
        CreditLimitHistoryRepository: Repository for credit limit history operations
    """
    return CreditLimitHistoryRepository(db_session)
