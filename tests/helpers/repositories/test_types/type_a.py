"""
Repository module for Type A entities.

This module provides specialized repository operations for Type A entities,
specifically designed for testing the repository factory's dynamic loading capability.
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers.models.polymorphic_test_models import TestTypeAModel


async def get_type_a_entities_with_field_value(
    session: AsyncSession, field_value: Optional[str] = None
) -> List[TestTypeAModel]:
    """
    Get Type A entities that match the specified field value.

    This function is designed to be dynamically bound to a repository by the
    repository factory, demonstrating specialized repository operations.

    Args:
        session: Database session for operations
        field_value: Optional filter value for a_field

    Returns:
        List of TestTypeAModel instances matching the criteria
    """
    query = select(TestTypeAModel)

    if field_value is not None:
        query = query.where(TestTypeAModel.a_field == field_value)

    result = await session.execute(query)
    return list(result.scalars().all())


async def count_type_a_entities(session: AsyncSession) -> int:
    """
    Count the number of Type A entities in the database.

    This function is designed to be dynamically bound to a repository by the
    repository factory, demonstrating specialized repository operations.

    Args:
        session: Database session for operations

    Returns:
        Number of TestTypeAModel instances
    """
    query = select(TestTypeAModel)
    result = await session.execute(query)
    return len(list(result.scalars().all()))
