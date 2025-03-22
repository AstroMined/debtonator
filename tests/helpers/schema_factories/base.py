"""
Base schema factory utilities.

This module provides base utility functions and classes for schema factories.
These utilities help standardize factory creation and reduce duplication.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Callable, Dict, Type, TypeVar

from pydantic import BaseModel

# Generic type for Pydantic schemas
SchemaType = TypeVar("SchemaType", bound=BaseModel)


def merge_kwargs(base_data: Dict[str, Any], kwargs: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge base data with overrides from kwargs.
    
    This function allows factory functions to have default values that
    can be overridden by kwargs, while also supporting nested updates.
    
    Args:
        base_data: Base data dictionary with default values
        kwargs: Override values from factory function call
        
    Returns:
        Dict[str, Any]: Merged data dictionary
    """
    result = base_data.copy()
    result.update(kwargs)
    return result


def utc_now() -> datetime:
    """
    Get current datetime with UTC timezone.
    
    Returns:
        datetime: Current time with UTC timezone
    """
    return datetime.now(timezone.utc)


def default_if_none(value: Any, default: Any) -> Any:
    """
    Return default value if provided value is None.
    
    Args:
        value: The value to check
        default: Default value to use if value is None
        
    Returns:
        Any: Either the original value or the default
    """
    return default if value is None else value


def create_validated_schema(
    schema_cls: Type[SchemaType], **data: Any
) -> SchemaType:
    """
    Create and validate a schema instance.
    
    This is a generic function that creates a schema instance of the specified
    type and validates it according to the schema's validation rules.
    
    Args:
        schema_cls: The schema class to instantiate
        **data: Data to initialize the schema with
        
    Returns:
        SchemaType: Validated schema instance
    """
    return schema_cls(**data)


def factory_function(schema_cls: Type[SchemaType]) -> Callable:
    """
    Decorator to simplify creating factory functions.
    
    This decorator can be used to create factory functions with less boilerplate.
    It takes care of instantiating and validating the schema.
    
    Args:
        schema_cls: The schema class that the factory creates
        
    Returns:
        Callable: Decorated factory function
    """
    def decorator(func: Callable) -> Callable:
        def wrapper(*args: Any, **kwargs: Any) -> SchemaType:
            data = func(*args, **kwargs)
            return schema_cls(**data)
        return wrapper
    return decorator


def decimal_default(value: Any, default: str = "100.00") -> Decimal:
    """
    Helper for handling Decimal defaults in factory functions.
    
    Args:
        value: Value to check if None
        default: Default decimal string value
        
    Returns:
        Decimal: Either the value or default as Decimal
    """
    if value is None:
        return Decimal(default)
    return value


# Common testing amounts
COMMON_AMOUNTS = {
    "tiny": Decimal("1.00"),
    "small": Decimal("10.00"),
    "medium": Decimal("100.00"),
    "large": Decimal("1000.00"),
    "huge": Decimal("10000.00"),
}
