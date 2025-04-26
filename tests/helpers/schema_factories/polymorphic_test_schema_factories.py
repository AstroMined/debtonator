"""
Schema factory functions for polymorphic entity testing.

This module provides factory functions for creating valid schema instances
for polymorphic entity testing, following the project's schema factory pattern.
"""

from datetime import datetime
from typing import Any, Dict, Optional

from src.utils.datetime_utils import utc_now
from tests.helpers.schema_factories.base_schema_schema_factories import factory_function
from tests.helpers.schemas.polymorphic_test_schemas import (
    TestBaseModelCreate,
    TestBaseModelInDB,
    TestBaseModelUpdate,
    TestTypeACreate,
    TestTypeAInDB,
    TestTypeAUpdate,
    TestTypeBCreate,
    TestTypeBInDB,
    TestTypeBUpdate,
)


@factory_function(TestTypeACreate)
def create_test_type_a_schema(
    name: str = "Test Type A Entity",
    a_field: Optional[str] = "Test A Field Value",
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid TestTypeACreate schema instance.

    Args:
        name: Entity name (defaults to "Test Type A Entity")
        a_field: Type A specific field (defaults to "Test A Field Value")
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create TestTypeACreate schema
    """
    data = {
        "name": name,
        "model_type": "type_a",
        **kwargs,
    }

    if a_field is not None:
        data["a_field"] = a_field

    return data


@factory_function(TestTypeBCreate)
def create_test_type_b_schema(
    name: str = "Test Type B Entity",
    b_field: str = "Required B Field Value",
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid TestTypeBCreate schema instance.

    Args:
        name: Entity name (defaults to "Test Type B Entity")
        b_field: Type B required field (defaults to "Required B Field Value")
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create TestTypeBCreate schema
    """
    data = {
        "name": name,
        "model_type": "type_b",
        "b_field": b_field,
        **kwargs,
    }

    return data


@factory_function(TestTypeAUpdate)
def create_test_type_a_update_schema(
    name: Optional[str] = None,
    a_field: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid TestTypeAUpdate schema instance.

    Args:
        name: New entity name (optional)
        a_field: New Type A specific field value (optional)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create TestTypeAUpdate schema
    """
    data = {}

    if name is not None:
        data["name"] = name

    if a_field is not None:
        data["a_field"] = a_field

    # Add any additional fields from kwargs
    data.update(kwargs)

    return data


@factory_function(TestTypeBUpdate)
def create_test_type_b_update_schema(
    name: Optional[str] = None,
    b_field: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid TestTypeBUpdate schema instance.

    Args:
        name: New entity name (optional)
        b_field: New Type B required field value (optional)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create TestTypeBUpdate schema
    """
    data = {}

    if name is not None:
        data["name"] = name

    if b_field is not None:
        data["b_field"] = b_field

    # Add any additional fields from kwargs
    data.update(kwargs)

    return data


@factory_function(TestTypeAInDB)
def create_test_type_a_in_db_schema(
    id: int,
    name: str = "Test Type A Entity",
    a_field: Optional[str] = "Test A Field Value",
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid TestTypeAInDB schema instance.

    Args:
        id: Entity ID (unique identifier)
        name: Entity name (defaults to "Test Type A Entity")
        a_field: Type A specific field (defaults to "Test A Field Value")
        created_at: Creation timestamp (defaults to current UTC time)
        updated_at: Last update timestamp (defaults to current UTC time)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create TestTypeAInDB schema
    """
    if created_at is None:
        created_at = utc_now()

    if updated_at is None:
        updated_at = utc_now()

    data = {
        "id": id,
        "name": name,
        "model_type": "type_a",
        "created_at": created_at,
        "updated_at": updated_at,
        **kwargs,
    }

    if a_field is not None:
        data["a_field"] = a_field

    return data


@factory_function(TestTypeBInDB)
def create_test_type_b_in_db_schema(
    id: int,
    name: str = "Test Type B Entity",
    b_field: str = "Required B Field Value",
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid TestTypeBInDB schema instance.

    Args:
        id: Entity ID (unique identifier)
        name: Entity name (defaults to "Test Type B Entity")
        b_field: Type B required field (defaults to "Required B Field Value")
        created_at: Creation timestamp (defaults to current UTC time)
        updated_at: Last update timestamp (defaults to current UTC time)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create TestTypeBInDB schema
    """
    if created_at is None:
        created_at = utc_now()

    if updated_at is None:
        updated_at = utc_now()

    data = {
        "id": id,
        "name": name,
        "model_type": "type_b",
        "b_field": b_field,
        "created_at": created_at,
        "updated_at": updated_at,
        **kwargs,
    }

    return data
