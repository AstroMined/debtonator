"""
Fixtures for payment source repositories.

This module provides pytest fixtures for creating and managing payment source repository
instances in tests.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.payment_sources import PaymentSourceRepository


@pytest_asyncio.fixture
async def payment_source_repository(
    db_session: AsyncSession,
) -> PaymentSourceRepository:
    """
    Fixture for PaymentSourceRepository with test database session.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        PaymentSourceRepository: Repository for payment source operations
    """
    return PaymentSourceRepository(db_session)
