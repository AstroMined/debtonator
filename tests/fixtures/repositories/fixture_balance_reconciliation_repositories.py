"""
Fixtures for balance reconciliation repositories.

This module provides pytest fixtures for creating and managing balance reconciliation repository
instances in tests.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.balance_reconciliation import BalanceReconciliationRepository


@pytest_asyncio.fixture
async def balance_reconciliation_repository(
    db_session: AsyncSession,
) -> BalanceReconciliationRepository:
    """
    Fixture for BalanceReconciliationRepository with test database session.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        BalanceReconciliationRepository: Repository for balance reconciliation operations
    """
    return BalanceReconciliationRepository(db_session)
