"""
Response formatter for API endpoints to ensure consistent decimal precision.

This module implements the API response formatting strategy defined in ADR-013,
providing utilities to ensure consistent decimal precision in API responses.
"""

import inspect
from decimal import Decimal
from typing import Any, Optional, Set

from pydantic import BaseModel

from src.utils.decimal_precision import DecimalPrecision


def format_decimal_precision(
    data: Any,
    _processed_objects: Optional[Set[int]] = None,
    _percentage_field_names: Optional[Set[str]] = None,
) -> Any:
    """
    Recursively format decimal values in API responses to ensure consistent precision.

    Implements ADR-013 "Decimal Precision Handling" for API responses:
    - Rounds monetary values to 2 decimal places
    - Preserves 4 decimal places for identified percentage fields
    - Handles nested dictionaries, lists, and Pydantic models

    Args:
        data: The data to format (can be any type)
        _processed_objects: Set of object IDs already processed (to avoid circular references)
        _percentage_field_names: Set of field names known to be percentage fields

    Returns:
        The formatted data with consistent decimal precision
    """
    # Initialize tracking of processed objects to avoid circular references
    if _processed_objects is None:
        _processed_objects = set()

    # Initialize set of known percentage field names for special handling
    if _percentage_field_names is None:
        _percentage_field_names = {
            "confidence_score",
            "trend_strength",
            "percentage_of_total",
            "seasonal_strength",
            "overall_confidence",
            "forecast_confidence",
            "credit_utilization",
            "confidence_threshold",
        }

    # Skip already processed objects (prevent infinite recursion)
    obj_id = id(data)
    if obj_id in _processed_objects:
        return data

    # Track this object
    if isinstance(data, (dict, list, tuple, set, BaseModel)):
        _processed_objects.add(obj_id)

    # Format data based on type
    if isinstance(data, dict):
        return {
            key: format_decimal_precision(
                value, _processed_objects, _percentage_field_names
            )
            for key, value in data.items()
        }

    elif isinstance(data, list):
        return [
            format_decimal_precision(item, _processed_objects, _percentage_field_names)
            for item in data
        ]

    elif isinstance(data, tuple):
        return tuple(
            format_decimal_precision(item, _processed_objects, _percentage_field_names)
            for item in data
        )

    elif isinstance(data, set):
        return {
            format_decimal_precision(item, _processed_objects, _percentage_field_names)
            for item in data
        }

    elif isinstance(data, BaseModel):
        # Convert Pydantic model to dict and format
        return format_decimal_precision(
            data.model_dump(), _processed_objects, _percentage_field_names
        )

    elif isinstance(data, Decimal):
        # Special handling for known percentage fields
        # We need to check the caller's stack to determine the field name
        # This is a bit of a hack, but it works for our use case
        frame = inspect.currentframe()
        try:
            if frame and frame.f_back:
                # Look for the key name in the caller's context
                for key, value in frame.f_back.f_locals.items():
                    if key == "key" and value in _percentage_field_names:
                        # This is a percentage field - use 4 decimal places
                        return DecimalPrecision.round_for_calculation(data)
        finally:
            # Always delete the frame reference to avoid reference cycles
            del frame

        # Standard monetary field - round to 2 decimal places
        return DecimalPrecision.round_for_display(data)

    # Return other data types unchanged
    return data


def format_response(response_data: Any) -> Any:
    """
    Format an API response to ensure consistent decimal precision.

    This is the main entry point for API response formatting.

    Args:
        response_data: The response data to format

    Returns:
        The formatted response data
    """
    return format_decimal_precision(response_data)


def with_formatted_response(func):
    """
    Decorator for API endpoints to automatically format decimal values in responses.

    Example:
        @router.get("/items/{item_id}")
        @with_formatted_response
        async def get_item(item_id: int):
            return {"item": {"id": item_id, "price": Decimal("10.12345")}}

    Args:
        func: The API endpoint function to decorate

    Returns:
        The decorated function that formats decimal values in responses
    """

    async def wrapper(*args, **kwargs):
        response = await func(*args, **kwargs)
        return format_response(response)

    return wrapper
