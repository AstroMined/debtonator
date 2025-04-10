"""
Fixtures for bill split repositories.

This module provides pytest fixtures for creating and managing bill split repository
instances in tests.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.bill_splits import BillSplitRepository


@pytest_asyncio.fixture
async def bill_split_repository(db_session: AsyncSession) -> BillSplitRepository:
    """
    Fixture for BillSplitRepository with test database session.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        BillSplitRepository: Repository for bill split operations
    """
    return BillSplitRepository(db_session)
