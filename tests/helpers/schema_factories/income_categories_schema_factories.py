"""
Income category schema factory functions.

This module provides factory functions for creating valid IncomeCategory-related
Pydantic schema instances for use in tests.
"""

from typing import Any, Dict, Optional

from src.schemas.income_categories import IncomeCategoryCreate
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
