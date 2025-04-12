"""
Fixtures for payment repositories.

This module provides pytest fixtures for creating and managing payment repository
instances in tests.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.payments import PaymentRepository


@pytest_asyncio.fixture
async def payment_repository(db_session: AsyncSession) -> PaymentRepository:
    """
    Fixture for PaymentRepository with test database session.

    Args:
        db_session: Database session fixture

    Returns:
        PaymentRepository: Repository for payment operations
    """
    return PaymentRepository(db_session)
