"""
Fixtures for payment schedule repositories.

This module provides pytest fixtures for creating and managing payment schedule repository
instances in tests.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.payment_schedules import PaymentScheduleRepository


@pytest_asyncio.fixture
async def payment_schedule_repository(
    db_session: AsyncSession,
) -> PaymentScheduleRepository:
    """
    Fixture for PaymentScheduleRepository with test database session.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        PaymentScheduleRepository: Repository for payment schedule operations
    """
    return PaymentScheduleRepository(db_session)
