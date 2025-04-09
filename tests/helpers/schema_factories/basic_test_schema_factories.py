"""
Test item schema factory functions.

This module provides factory functions for creating valid TestItem-related
Pydantic schema instances for use in generic repository tests.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from src.utils.datetime_utils import utc_now
from tests.helpers.schema_factories.base_schema_schema_factories import (
    MEDIUM_AMOUNT,
    factory_function,
)
from tests.helpers.schemas.basic_test_schemas import (
    TestItemCreate,
    TestItemInDB,
    TestItemUpdate,
)


@factory_function(TestItemCreate)
def create_test_item_schema(
    name: str = "Test Item",
    description: Optional[str] = "Test description",
    numeric_value: Optional[Decimal] = None,
    is_active: bool = True,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid TestItemCreate schema instance.

    Args:
        name: Item name (defaults to "Test Item")
        description: Item description (defaults to "Test description")
        numeric_value: Numeric value (defaults to 100.00)
        is_active: Whether the item is active (defaults to True)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create TestItemCreate schema
    """
    if numeric_value is None:
        numeric_value = MEDIUM_AMOUNT

    data = {
        "name": name,
        "description": description,
        "numeric_value": numeric_value,
        "is_active": is_active,
        **kwargs,
    }

    return data


@factory_function(TestItemUpdate)
def create_test_item_update_schema(
    name: Optional[str] = None,
    description: Optional[str] = None,
    numeric_value: Optional[Decimal] = None,
    is_active: Optional[bool] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid TestItemUpdate schema instance.

    Args:
        name: New item name (optional)
        description: New item description (optional)
        numeric_value: New numeric value (optional)
        is_active: New active status (optional)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create TestItemUpdate schema
    """
    data = {}

    if name is not None:
        data["name"] = name

    if description is not None:
        data["description"] = description

    if numeric_value is not None:
        data["numeric_value"] = numeric_value

    if is_active is not None:
        data["is_active"] = is_active

    # Add any additional fields from kwargs
    data.update(kwargs)

    return data


@factory_function(TestItemInDB)
def create_test_item_in_db_schema(
    id: int,
    name: str = "Test Item",
    description: Optional[str] = "Test description",
    numeric_value: Optional[Decimal] = None,
    is_active: bool = True,
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid TestItemInDB schema instance.

    Args:
        id: Item ID (unique identifier)
        name: Item name (defaults to "Test Item")
        description: Item description (defaults to "Test description")
        numeric_value: Numeric value (defaults to 100.00)
        is_active: Whether the item is active (defaults to True)
        created_at: Creation timestamp (defaults to current UTC time)
        updated_at: Last update timestamp (defaults to current UTC time)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create TestItemInDB schema
    """
    if numeric_value is None:
        numeric_value = MEDIUM_AMOUNT

    if created_at is None:
        created_at = utc_now()

    if updated_at is None:
        updated_at = utc_now()

    data = {
        "id": id,
        "name": name,
        "description": description,
        "numeric_value": numeric_value,
        "is_active": is_active,
        "created_at": created_at,
        "updated_at": updated_at,
        **kwargs,
    }

    return data
