# Repository Test Helpers

This directory contains specialized repository modules designed for testing the Dynamic Repository Module Pattern and Repository Factory functionality in Debtonator.

## Purpose

The repository test helpers serve several key purposes:

1. **Testing Dynamic Module Loading**: Validate that the repository factory correctly discovers and loads specialized repository modules
2. **Testing Dynamic Method Binding**: Ensure specialized methods are correctly bound to repository instances
3. **Testing Type-Specific Operations**: Verify that type-specific operations work correctly when dynamically loaded
4. **Testing Repository Pattern Extensibility**: Demonstrate how the repository pattern can be extended with specialized functionality
5. **Supporting Generic Repository Tests**: Provide reusable test implementations that don't rely on business models

## Directory Structure

```tree
repositories/
├── __init__.py
└── test_types/           # Type-specific repository modules
    ├── __init__.py
    ├── type_a.py         # Type A specialized operations
    └── type_b.py         # Type B specialized operations
```

## Usage

These test modules are primarily used in the repository factory tests to validate dynamic module loading and method binding:

```python
# Example from test_factory.py
async def test_dynamic_method_binding():
    """Test that repository factory correctly binds methods from modules."""
    # Arrange
    entity = TestPolymorphicModel(entity_type="type_a", a_field="test value")
    db_session.add(entity)
    await db_session.flush()
    
    # Create repository with factory
    repo = repository_factory(
        db_session,
        TestPolymorphicModel,
        "entity_type",
        {"type_a": "tests.helpers.repositories.test_types.type_a"}
    )
    
    # Act: Call dynamically loaded method
    entities = await repo.get_type_a_entities_with_field_value("test value")
    
    # Assert
    assert len(entities) == 1
    assert entities[0].id == entity.id
    assert entities[0].a_field == "test value"
```

## Test Types

The `test_types` directory contains modules that provide specialized repository operations for different entity types. These modules follow the same pattern used in the application's repository modules:

1. **Session-First Parameter**: All functions take SQLAlchemy session as their first parameter
2. **Async Implementation**: Functions are implemented as async functions
3. **Type-Specific Logic**: Each module contains operations specific to that entity type
4. **Clear Documentation**: Functions include descriptive docstrings

## Adding New Test Modules

When adding new test modules:

1. Create a new module in `test_types/` directory with appropriate entity type name
2. Implement specialized async functions that take session as first parameter
3. Add descriptive docstrings to all functions
4. Update `__init__.py` with appropriate imports
5. Add corresponding tests in `tests/integration/repositories/test_factory.py`

## Related Documentation

For more information about the Repository Pattern and Factory implementation:

- [System Patterns: Repository Module Pattern](../../../../docs/system_patterns.md#repository-module-pattern)
- [Repository Base Implementation](../../../../src/repositories/base.py)
- [Repository Factory Tests](../../integration/repositories/test_factory.py)
