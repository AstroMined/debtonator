"""
Base schema factory utilities.

This module provides base utility functions and classes for schema factories.
These utilities help standardize factory creation and reduce duplication.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Callable, Dict, Type, TypeVar, cast

from pydantic import BaseModel


# Generic type for Pydantic schemas
SchemaType = TypeVar("SchemaType", bound=BaseModel)
FactoryFunc = TypeVar("FactoryFunc", bound=Callable[..., Dict[str, Any]])


def factory_function(
    schema_cls: Type[SchemaType],
) -> Callable[[FactoryFunc], Callable[..., SchemaType]]:
    """
    Decorator to simplify creating factory functions.

    This decorator transforms a function that returns a dictionary into one that
    returns a validated schema instance.

    Args:
        schema_cls: The schema class that the factory creates

    Returns:
        Callable: Decorator function
    """

    def decorator(func: FactoryFunc) -> Callable[..., SchemaType]:
        def wrapper(*args: Any, **kwargs: Any) -> SchemaType:
            data = func(*args, **kwargs)
            return schema_cls(**data)

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
