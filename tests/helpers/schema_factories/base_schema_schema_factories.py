"""
Base schema factory utilities.

This module provides base utility functions and classes for schema factories.
These utilities help standardize factory creation and reduce duplication.
"""

from decimal import Decimal
from typing import Any, Callable, Dict, Type, TypeVar, cast

from pydantic import BaseModel

# Generic type for Pydantic schemas
SchemaType = TypeVar("SchemaType", bound=BaseModel)
FactoryFunc = TypeVar("FactoryFunc", bound=Callable[..., Dict[str, Any]])


def extract_model_data(model: Any) -> Dict[str, Any]:
    """
    Extract data from a model instance as a dictionary.

    Args:
        model: A Pydantic model instance or dictionary

    Returns:
        Dict[str, Any]: The model's data as a dictionary
    """
    if hasattr(model, "model_dump"):
        return model.model_dump()
    elif isinstance(model, dict):
        return model
    else:
        # Handle unknown types by returning the object itself
        # This might cause errors but it's better than silent failure
        return model


def process_factory_data(data: Any) -> Any:
    """
    Process factory data to handle nested models.

    Recursively processes dictionaries and lists to extract data from model instances.

    Args:
        data: Data structure that might contain model instances

    Returns:
        Any: Processed data structure with model data extracted
    """
    if isinstance(data, dict):
        result = {}
        for key, value in data.items():
            result[key] = process_factory_data(value)
        return result
    elif isinstance(data, list):
        return [process_factory_data(item) for item in data]
    elif hasattr(data, "model_dump"):  # Pydantic v2 model
        return process_factory_data(data.model_dump())
    else:
        return data


def factory_function(
    schema_cls: Type[SchemaType],
) -> Callable[[FactoryFunc], Callable[..., SchemaType]]:
    """
    Enhanced decorator for factory functions that handles model instances properly.

    This decorator ensures proper handling of model instances in nested structures
    and consistent data extraction from models.

    Args:
        schema_cls: The schema class that the factory creates

    Returns:
        Callable: Decorator function
    """

    def decorator(func: FactoryFunc) -> Callable[..., SchemaType]:
        def wrapper(*args: Any, **kwargs: Any) -> SchemaType:
            # Get raw data from factory function
            data = func(*args, **kwargs)

            # Process the data to handle nested models
            processed_data = process_factory_data(data)

            # Create and return the schema instance
            return schema_cls(**processed_data)

        # Preserve function metadata for better IDE integration
        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        wrapper.__annotations__ = func.__annotations__

        return cast(Callable[..., SchemaType], wrapper)

    return decorator


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


# Common testing amounts as constants
TINY_AMOUNT = Decimal("1.00")
SMALL_AMOUNT = Decimal("10.00")
MEDIUM_AMOUNT = Decimal("100.00")
LARGE_AMOUNT = Decimal("1000.00")
HUGE_AMOUNT = Decimal("10000.00")

# Dictionary of common amounts for flexible usage
COMMON_AMOUNTS = {
    "tiny": TINY_AMOUNT,
    "small": SMALL_AMOUNT,
    "medium": MEDIUM_AMOUNT,
    "large": LARGE_AMOUNT,
    "huge": HUGE_AMOUNT,
}
