"""
Repository module for Type B entities.

This module provides specialized repository operations for Type B entities,
specifically designed for testing the repository factory's dynamic loading capability.
"""

from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers.models.polymorphic_test_models import TestTypeBModel


async def get_type_b_entities_with_required_field(
    session: AsyncSession, field_value: Optional[str] = None
) -> List[TestTypeBModel]:
    """
    Get Type B entities that match the specified required field value.

    This function is designed to be dynamically bound to a repository by the
    repository factory, demonstrating specialized repository operations.

    Args:
        session: Database session for operations
        field_value: Optional filter value for b_field

    Returns:
        List of TestTypeBModel instances matching the criteria
    """
    query = select(TestTypeBModel)
    
    if field_value is not None:
        query = query.where(TestTypeBModel.b_field == field_value)
    
    result = await session.execute(query)
    return list(result.scalars().all())


async def find_type_b_by_name_pattern(
    session: AsyncSession, name_pattern: str
) -> List[TestTypeBModel]:
    """
    Find Type B entities with names matching a pattern.

    This function is designed to be dynamically bound to a repository by the
    repository factory, demonstrating specialized repository operations.

    Args:
        session: Database session for operations
        name_pattern: Pattern to match against entity names

    Returns:
        List of TestTypeBModel instances matching the name pattern
    """
    query = select(TestTypeBModel).where(TestTypeBModel.name.like(f"%{name_pattern}%"))
    result = await session.execute(query)
    return list(result.scalars().all())
