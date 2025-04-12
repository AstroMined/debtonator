"""
Fixtures for recurring bill repositories.

This module provides pytest fixtures for creating and managing recurring bill repository
instances in tests.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.recurring_bills import RecurringBillRepository


@pytest_asyncio.fixture
async def recurring_bill_repository(
    db_session: AsyncSession,
) -> RecurringBillRepository:
    """
    Fixture for RecurringBillRepository with test database session.

    Args:
        db_session: Database session fixture

    Returns:
        RecurringBillRepository: Repository for recurring bill operations
    """
    return RecurringBillRepository(db_session)
