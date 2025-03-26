"""
Integration tests for CategoryRepository.

This module contains tests that validate the behavior of the CategoryRepository
against a real database.
"""

from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.constants import (DEFAULT_CATEGORY_DESCRIPTION, DEFAULT_CATEGORY_ID,
                           DEFAULT_CATEGORY_NAME)
from src.models.categories import Category
from src.models.liabilities import Liability
from src.repositories.categories import CategoryRepository
from src.repositories.liabilities import LiabilityRepository
from src.utils.datetime_utils import utc_datetime

pytestmark = pytest.mark.asyncio


async def test_create_category(db_session: AsyncSession):
    """Test creating a category."""
    # Create repository
    repo = CategoryRepository(db_session)

    # Create category
    category = await repo.create(
        {"name": "Test Category", "description": "Test category description"}
    )

    # Assert created category
    assert category.id is not None
    assert category.name == "Test Category"
    assert category.description == "Test category description"
    assert category.parent_id is None
