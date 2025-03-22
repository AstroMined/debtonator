# Schema Factories

## Overview

This directory contains factory functions for creating Pydantic schema instances for testing purposes. These factories ensure that all repository tests follow the proper validation flow by passing data through Pydantic schemas before using repositories.

## Structure

- Each domain model has its own factory file (e.g., `accounts.py`, `liabilities.py`)
- The `__init__.py` file re-exports all factory functions to maintain backward compatibility
- All factory functions follow consistent naming conventions and patterns

## Adding New Factory Functions

When adding new factory functions:

1. Place them in the appropriate domain-specific file (create one if needed)
2. Follow the established naming pattern: `create_<entity>_schema()`
3. Add default values for common fields
4. Add parameters for fields that typically need customization
5. Add proper docstrings with parameter descriptions
6. Re-export the function in `__init__.py`

## Factory Function Template

```python
def create_example_schema(
    required_id: int,
    name: str = "Default Name",
    amount: Optional[Decimal] = None,
    **kwargs: Any,
) -> ExampleCreate:
    """
    Create a valid ExampleCreate schema instance.

    Args:
        required_id: ID of the required related entity
        name: Name field (defaults to "Default Name")
        amount: Amount field (defaults to 100.00)
        **kwargs: Additional fields to override

    Returns:
        ExampleCreate: Validated schema instance
    """
    if amount is None:
        amount = Decimal("100.00")

    data = {
        "required_id": required_id,
        "name": name,
        "amount": amount,
        **kwargs,
    }

    return ExampleCreate(**data)
```

## Best Practices

1. **Provide Good Defaults**: Make it easy to create valid schemas with minimal parameters
2. **Use Type Hints**: Include proper type hints for all parameters and return values
3. **Add Docstrings**: Document parameters, default values, and return types
4. **Allow Overriding**: Use `**kwargs` to allow any field to be overridden
5. **Validate Early**: Return a validated schema, not just a data dictionary
6. **Keep Focused**: Each factory module should focus on a single domain model
