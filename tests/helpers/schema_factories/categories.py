"""
Category schema factory functions.

This module provides factory functions for creating valid Category-related
Pydantic schema instances for use in tests.
"""

from typing import Any, Dict, Optional

from src.schemas.categories import CategoryCreate, CategoryUpdate
from tests.helpers.schema_factories.base import factory_function


@factory_function(CategoryCreate)
def create_category_schema(
    name: str = "Test Category",
    description: Optional[str] = None,
    parent_id: Optional[int] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid CategoryCreate schema instance.

    Args:
        name: Category name
        description: Optional description for the category
        parent_id: Optional parent category ID for hierarchical categories
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create CategoryCreate schema
    """
    data = {
        "name": name,
        **kwargs,
    }

    if description is not None:
        data["description"] = description

    if parent_id is not None:
        data["parent_id"] = parent_id

    return data


@factory_function(CategoryUpdate)
def create_category_update_schema(
    name: Optional[str] = None,
    description: Optional[str] = None,
    parent_id: Optional[int] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid CategoryUpdate schema instance.

    Args:
        name: Updated category name (optional)
        description: Updated description (optional)
        parent_id: Updated parent category ID (optional)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create CategoryUpdate schema
    """
    data = {**kwargs}

    if name is not None:
        data["name"] = name

    if description is not None:
        data["description"] = description

    if parent_id is not None:
        data["parent_id"] = parent_id

    return data
