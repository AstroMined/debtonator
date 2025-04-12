"""
Fixtures for recurring income repositories.

This module provides pytest fixtures for creating and managing recurring income repository
instances in tests.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.recurring_income import RecurringIncomeRepository


@pytest_asyncio.fixture
async def recurring_income_repository(
    db_session: AsyncSession,
) -> RecurringIncomeRepository:
    """
    Fixture for RecurringIncomeRepository with test database session.

    Args:
        db_session: Database session fixture

    Returns:
        RecurringIncomeRepository: Repository for recurring income operations
    """
    return RecurringIncomeRepository(db_session)
