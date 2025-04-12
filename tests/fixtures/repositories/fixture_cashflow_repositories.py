"""
Fixtures for cashflow repositories.

This module provides pytest fixtures for creating and managing cashflow repository
instances in tests.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.cashflow import CashflowForecastRepository


@pytest_asyncio.fixture
async def cashflow_forecast_repository(
    db_session: AsyncSession,
) -> CashflowForecastRepository:
    """
    Fixture for CashflowForecastRepository with test database session.

    Args:
        db_session: Database session fixture

    Returns:
        CashflowForecastRepository: Repository for cashflow forecast operations
    """
    return CashflowForecastRepository(db_session)
