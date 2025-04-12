"""
Fixtures for deposit schedule repositories.

This module provides pytest fixtures for creating and managing deposit schedule repository
instances in tests.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.deposit_schedules import DepositScheduleRepository


@pytest_asyncio.fixture
async def deposit_schedule_repository(
    db_session: AsyncSession,
) -> DepositScheduleRepository:
    """
    Fixture for DepositScheduleRepository with test database session.

    Args:
        db_session: Database session fixture

    Returns:
        DepositScheduleRepository: Repository for deposit schedule operations
    """
    return DepositScheduleRepository(db_session)
