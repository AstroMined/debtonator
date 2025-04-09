# Schema Factories

## Overview

This directory contains factory functions for creating Pydantic schema instances for testing purposes. These factories ensure that all repository tests follow the proper validation flow by passing data through Pydantic schemas before using repositories.

## Directory Structure

The schema factories directory mirrors the structure of the `src/schemas` directory:

```
schema_factories/
├── __init__.py
├── accounts_schema_factories.py
├── balance_history_schema_factories.py
├── bill_splits_schema_factories.py
├── ...
├── account_types/
│   ├── __init__.py
│   ├── banking/
│   │   ├── __init__.py
│   │   ├── checking_schema_factories.py
│   │   ├── credit_schema_factories.py
│   │   ├── ...
└── cashflow/
    ├── __init__.py
    ├── base_schema_factories.py
    ├── cashflow_account_analysis_schema_factories.py
    ├── ...
```

## Naming Convention

All schema factory files follow a consistent naming convention:

- Files must be named after the original schema file they represent
- The file name must end with the suffix `_schema_factories`

For example:
- `src/schemas/accounts.py` → `accounts_schema_factories.py`
- `src/schemas/account_types/banking/checking.py` → `checking_schema_factories.py`

The naming convention for factory functions within these files follows this pattern:
- Functions that create a schema should be named `create_[schema_name]_schema` where `[schema_name]` is the name of the Pydantic model, converted to snake_case.

For example:
- `AccountCreate` → `create_account_schema`
- `CheckingAccountResponse` → `create_checking_account_response_schema`

## Mandatory Usage Areas

Schema factories MUST be used in:

1. **Repository Tests** - All repository tests must use schema factories to create valid test data, ensuring proper validation flow from schemas to repositories
2. **Integration Tests** - Any test that interacts with repositories must use schema factories to guarantee data consistency
3. **Service Tests** - Tests for service-layer functionality that involves data validation
4. **Cross-Layer Tests** - Any test that crosses application layers and requires validated test data
5. **API Tests** - Tests for API endpoints that validate request payloads

## Creating New Schema Factories

When adding a new schema to the codebase, follow these steps to create the corresponding factory:

1. Create a new file with the appropriate naming convention or add to an existing file
2. Import the necessary schema classes from `src/schemas/`
3. Create factory functions for each schema class, following the function naming convention
4. Use the `@factory_function` decorator from `base.py` where appropriate
5. Ensure factory functions have appropriate defaults and allow all fields to be overridden

## Datetime Handling Requirements

All datetime operations in schema factories MUST use the helper functions from `src/utils/datetime_utils.py` to ensure ADR-011 compliance:

### Required Datetime Practices

1. **Always use timezone-aware datetimes**:
   ```python
   # ✅ Correct
   from src.utils.datetime_utils import utc_now, utc_datetime
   
   created_at = utc_now()
   specific_date = utc_datetime(2025, 3, 15, 14, 30)
   
   # ❌ Incorrect
   from datetime import datetime
   created_at = datetime.now()  # Naive datetime without timezone
   ```

2. **Compare datetimes correctly**:
   ```python
   # ✅ Correct
   from src.utils.datetime_utils import datetime_equals
   
   assert datetime_equals(schema.created_at, expected_date)
   
   # ❌ Incorrect
   assert schema.created_at == expected_date  # Doesn't handle timezone correctly
   ```

3. **Generate relative dates properly**:
   ```python
   # ✅ Correct
   from src.utils.datetime_utils import days_from_now, days_ago
   
   future_date = days_from_now(7)  # 7 days in the future
   past_date = days_ago(30)  # 30 days ago
   
   # ❌ Incorrect
   from datetime import datetime, timedelta
   future_date = datetime.now() + timedelta(days=7)  # No timezone
   ```

## Structure

- Each schema file has its own factory file (e.g., `accounts_schema_factories.py`, `liabilities_schema_factories.py`)
- All factory functions follow consistent naming with "_schema" suffix (e.g., `create_account_schema`)
- Factory functions use the `@factory_function` decorator from `base.py` where appropriate
- Complex nested structures should use specialized factory functions for each level

## Factory Function Template

```python
@factory_function(ExampleCreate)
def create_example_schema(
    required_id: int,
    name: str = "Default Name",
    amount: Optional[Decimal] = None,
    created_at: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid ExampleCreate schema instance.

    Args:
        required_id: ID of the required related entity
        name: Name field (defaults to "Default Name")
        amount: Amount field (defaults to 100.00)
        created_at: Creation timestamp (defaults to current UTC time)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create ExampleCreate schema
    """
    if amount is None:
        amount = MEDIUM_AMOUNT  # Using constant from base
    
    if created_at is None:
        created_at = utc_now()  # Using datetime_utils

    data = {
        "required_id": required_id,
        "name": name,
        "amount": amount,
        "created_at": created_at,
        **kwargs,
    }

    return data
```

## Testing Schema Factories

Schema factories themselves should be thoroughly tested to ensure they produce valid instances. Test files for schema factories exist in `/code/debtonator/tests/unit/helpers/schema_factories`.

When testing schema factories:

1. **Test Default Values** - Ensure factories create valid schemas with minimal parameters
2. **Test Custom Values** - Verify that parameter overrides work correctly
3. **Test Datetime Compliance** - Validate that all datetime fields comply with ADR-011
4. **Test Nested Structures** - Verify complex nested objects are created correctly
5. **Test Validation Rules** - Ensure schema validation rules are respected

## Best Practices

1. **Provide Good Defaults**: Make it easy to create valid schemas with minimal parameters
2. **Use Type Hints**: Include proper type hints for all parameters and return values
3. **Add Docstrings**: Document parameters, default values, and return types
4. **Allow Overriding**: Use `**kwargs` to allow any field to be overridden
5. **Use Base Constants**: Use predefined constants from base.py instead of magic values
6. **Keep Focused**: Each factory module should focus on a single domain model
7. **Use Datetime Utils**: Always use functions from `datetime_utils.py` for datetime operations
8. **Handle Nested Objects**: Use proper factory functions for nested objects
9. **Follow Validation Flow**: Ensure schemas mirror the validation flow in production code
10. **Test Edge Cases**: Create factory functions that cover validation edge cases

## Advanced Usage Patterns

### Nested Object Handling

For schemas with nested objects, use a hierarchical factory approach:

```python
@factory_function(ParentSchema)
def create_parent_schema(
    child_data: Optional[Dict[str, Any]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """Create a parent schema with nested child object."""
    if child_data is None:
        # Create child object using its factory
        child_data = create_child_schema().model_dump()
    
    data = {
        "name": "Parent Name",
        "child": child_data,
        **kwargs,
    }
    
    return data
```

### Dynamic Type Selection

For polymorphic schemas, use account type routing pattern:

```python
def create_entity_schema(entity_type: str = "default", **kwargs: Any) -> EntityUnion:
    """Create the appropriate entity type based on entity_type parameter."""
    if entity_type == "type_a":
        return create_type_a_schema(**kwargs)
    elif entity_type == "type_b":
        return create_type_b_schema(**kwargs)
    else:
        raise ValueError(f"Unsupported entity type: {entity_type}")
```

### Repository Test Integration

Schema factories should be used in repository tests to maintain the validation flow:

```python
async def test_repository_create():
    """Test creating an entity through repository."""
    # Arrange
    repo = EntityRepository(db_session)
    
    # Schema - This follows the service validation flow
    entity_data = create_entity_schema(name="Test Entity")
    
    # Act
    entity = await repo.create(entity_data.model_dump())
    
    # Assert
    assert entity.id is not None
    assert entity.name == "Test Entity"
```
