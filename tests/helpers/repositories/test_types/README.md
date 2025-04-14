# Repository Test Types

This directory contains specialized repository modules designed for testing the repository factory's dynamic module loading capabilities.

## Purpose

The test types modules serve several key purposes:

1. **Testing Repository Factory**: Validate the dynamic module loading and method binding capabilities of the repository factory
2. **Type-Specific Operations**: Demonstrate how type-specific repository operations can be organized in dedicated modules
3. **Testing Pattern Consistency**: Ensure consistency with the Repository Module Pattern described in system_patterns.md
4. **Independent Test Implementation**: Provide self-contained implementations that don't depend on business logic

## Test Type Modules

### Type A (`type_a.py`)

Contains specialized repository operations for Type A entities:

- `get_type_a_entities_with_field_value()`: Retrieves Type A entities with a specific field value
- `count_type_a_entities()`: Counts the number of Type A entities in the database

Example usage:

```python
# These methods are dynamically bound to the repository by the repository factory
entities = await repository.get_type_a_entities_with_field_value("test value")
count = await repository.count_type_a_entities()
```

### Type B (`type_b.py`)

Contains specialized repository operations for Type B entities:

- `get_type_b_entities_with_field_value()`: Retrieves Type B entities with a specific field value
- `sum_b_field_values()`: Calculates the sum of all b_field values

Example usage:

```python
# These methods are dynamically bound to the repository by the repository factory
entities = await repository.get_type_b_entities_with_field_value("test value")
total = await repository.sum_b_field_values()
```

## Module Pattern

Each test type module follows the Session-First Pattern established in the Repository Module Pattern:

1. **Function-Based**: Modules contain standalone async functions (not class methods)
2. **Session-First Parameter**: All functions take SQLAlchemy AsyncSession as their first parameter
3. **Model-Specific Operations**: Functions implement specialized operations for a specific entity type
4. **Consistent Parameter Conventions**: Parameters follow consistent naming conventions
5. **Comprehensive Docstrings**: Each function includes a descriptive docstring
6. **Proper Type Annotations**: All parameters and return values have appropriate type annotations
7. **Async Implementation**: All functions are implemented as async functions

## Integration with Repository Factory

These modules are integrated with the repository factory through the module registry:

```python
# Create repository with factory that loads specialized modules
repository = repository_factory(
    db_session,
    TestPolymorphicModel,
    "entity_type",
    {
        "type_a": "tests.helpers.repositories.test_types.type_a",
        "type_b": "tests.helpers.repositories.test_types.type_b"
    }
)

# Use dynamically loaded methods
type_a_entities = await repository.get_type_a_entities_with_field_value("test value")
```

## Related Documentation

- [Repository Test Helpers](../README.md)
- [Repository Module Pattern](../../../../../docs/system_patterns.md#repository-module-pattern)
- [Repository Factory Tests](../../../integration/repositories/test_factory.py)
