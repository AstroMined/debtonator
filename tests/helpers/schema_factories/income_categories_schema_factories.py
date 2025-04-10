"""
Income category schema factory functions.

This module provides factory functions for creating valid IncomeCategory-related
Pydantic schema instances for use in tests.
"""

from typing import Any, Dict, Optional

from src.schemas.income_categories import IncomeCategoryCreate, IncomeCategoryUpdate
from tests.helpers.schema_factories.base_schema_schema_factories import factory_function


@factory_function(IncomeCategoryCreate)
def create_income_category_schema(
    name: str = "Test Income Category",
    description: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid IncomeCategoryCreate schema instance.

    Args:
        name: Name of the income category
        description: Optional description of the income category
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create IncomeCategoryCreate schema
    """
    data = {"name": name, **kwargs}

    if description is not None:
        data["description"] = description

    return data


@factory_function(IncomeCategoryUpdate)
def create_income_category_update_schema(
    name: Optional[str] = None,
    description: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid IncomeCategoryUpdate schema instance.

    Args:
        name: Updated name of the income category
        description: Updated description of the income category
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create IncomeCategoryUpdate schema
    """
    data = {**kwargs}

    if name is not None:
        data["name"] = name

    if description is not None:
        data["description"] = description

    return data
