"""
Fixtures for transaction history repositories.

This module provides pytest fixtures for creating and managing transaction history repository
instances in tests.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.transaction_history import TransactionHistoryRepository


@pytest_asyncio.fixture
async def transaction_history_repository(
    db_session: AsyncSession,
) -> TransactionHistoryRepository:
    """
    Fixture for TransactionHistoryRepository with test database session.

    Args:
        db_session: Database session fixture

    Returns:
        TransactionHistoryRepository: Repository for transaction history operations
    """
    return TransactionHistoryRepository(db_session)
