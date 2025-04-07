"""
Schema factory functions for test items.

This module provides factory functions for creating test item schema instances
with sensible defaults for testing.
"""

from decimal import Decimal
from typing import Dict, Any, Optional

from tests.helpers.schemas.test_schemas import TestItemCreate, TestItemUpdate
from tests.helpers.schema_factories.base import factory_function, merge_kwargs, COMMON_AMOUNTS


@factory_function(TestItemCreate)
def create_test_item_schema(
    name: str = "Test Item",
    description: Optional[str] = "Test description",
    numeric_value: Decimal = COMMON_AMOUNTS["medium"],
    is_active: bool = True,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Create a TestItemCreate schema with sensible defaults.
    
    Args:
        name: Item name
        description: Item description
        numeric_value: Numeric value for the item
        is_active: Whether the item is active
        **kwargs: Additional fields to override defaults
        
    Returns:
        Dict[str, Any]: Dictionary of fields for TestItemCreate schema
    """
    data = {
        "name": name,
        "description": description,
        "numeric_value": numeric_value,
        "is_active": is_active,
    }
    
    return merge_kwargs(data, kwargs)


@factory_function(TestItemUpdate)
def create_test_item_update_schema(
    name: Optional[str] = None,
    description: Optional[str] = None,
    numeric_value: Optional[Decimal] = None,
    is_active: Optional[bool] = None,
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Create a TestItemUpdate schema for partial updates.
    
    Args:
        name: Optional new name
        description: Optional new description
        numeric_value: Optional new numeric value
        is_active: Optional new active status
        **kwargs: Additional fields to override defaults
        
    Returns:
        Dict[str, Any]: Dictionary of fields for TestItemUpdate schema
    """
    data = {
        "name": name,
        "description": description,
        "numeric_value": numeric_value,
        "is_active": is_active,
    }
    
    # Filter out None values for cleaner partial updates
    filtered_data = {k: v for k, v in data.items() if v is not None}
    
    return merge_kwargs(filtered_data, kwargs)
