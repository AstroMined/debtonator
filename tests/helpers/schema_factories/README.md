# Schema Factories

## Overview

This directory contains factory functions for creating Pydantic schema instances for testing purposes. These factories ensure that all repository tests follow the proper validation flow by passing data through Pydantic schemas before using repositories.

## Important: Breaking Changes

**All backward compatibility has been removed.** This is a clean break to reduce technical debt.

### Migration Guide

If your tests previously used:
```python
from tests.helpers.schema_factories import create_account_schema
```

Update to:
```python
from tests.helpers.schema_factories.accounts import create_account_schema
```

## Structure

- Each domain model has its own factory file (e.g., `accounts.py`, `liabilities.py`)
- All factory functions follow consistent naming with "_schema" suffix (e.g., `create_account_schema`)
- Factory functions use the `@factory_function` decorator from `base.py` where appropriate

## Adding New Factory Functions

When adding new factory functions:

1. Place them in the appropriate domain-specific file (create one if needed)
2. Use the `@factory_function` decorator
3. Follow the established naming pattern: `create_<entity>_schema` and `create_<entity>_update_schema`
4. Add default values for common fields
5. Add parameters for fields that typically need customization
6. Add proper docstrings with parameter descriptions

## Factory Function Template

```python
@factory_function(ExampleCreate)
def create_example_schema(
    required_id: int,
    name: str = "Default Name",
    amount: Optional[Decimal] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid ExampleCreate schema instance.

    Args:
        required_id: ID of the required related entity
        name: Name field (defaults to "Default Name")
        amount: Amount field (defaults to 100.00)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create ExampleCreate schema
    """
    if amount is None:
        amount = MEDIUM_AMOUNT  # Using constant from base

    data = {
        "required_id": required_id,
        "name": name,
        "amount": amount,
        **kwargs,
    }

    return data
```

## Best Practices

1. **Provide Good Defaults**: Make it easy to create valid schemas with minimal parameters
2. **Use Type Hints**: Include proper type hints for all parameters and return values
3. **Add Docstrings**: Document parameters, default values, and return types
4. **Allow Overriding**: Use `**kwargs` to allow any field to be overridden
5. **Use Base Constants**: Use predefined constants from base.py instead of magic values
6. **Keep Focused**: Each factory module should focus on a single domain model
