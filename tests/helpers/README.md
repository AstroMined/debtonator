# Test Helpers

This directory contains supporting modules, utilities, and test-specific implementations that enable Debtonator's comprehensive testing strategy while following the "Real Objects Testing Philosophy" established in ADR-014.

## Directory Structure

```
helpers/
├── __init__.py
├── models/                   # Test-specific SQLAlchemy models
├── schemas/                  # Test-specific Pydantic schemas
└── schema_factories/         # Schema factory functions for test data creation
```

## Helper Categories

### Test Models

Contains SQLAlchemy models designed specifically for testing base functionality without involving business models. These models support testing of generic components like the `BaseRepository` class.

Example usage:
```python
from tests.helpers.models.test_item import TestItem

# Create test model
test_item = TestItem(name="Test Item", value=42)
db_session.add(test_item)
await db_session.flush()
```

### Test Schemas

Contains Pydantic schemas designed specifically for testing validation flow and base functionality. These schemas work with the test models to enable comprehensive testing of generic components.

Example usage:
```python
from tests.helpers.schemas.test_item import TestItemCreate

# Create test schema
schema = TestItemCreate(name="Test Item", value=42)
assert schema.name == "Test Item"
assert schema.value == 42
```

### Schema Factories

Contains factory functions for creating schema instances used in tests. These factories ensure proper validation flow from schemas to repositories and provide consistent test data creation patterns.

Example usage:
```python
from tests.helpers.schema_factories.basic_test_schema_factories import create_test_item_schema

# Create schema with factory
schema = create_test_item_schema(name="Factory Item", value=42)

# Use in repository test
data = schema.model_dump()
result = await repository.create(data)
```

## Key Principles

1. **Real Objects**: Helpers support our "no mocks" philosophy by providing real objects for testing
2. **Isolation**: Test-specific models and schemas allow testing of base functionality in isolation
3. **Consistency**: Helpers enforce consistent patterns across all tests
4. **Simplicity**: Test helpers are deliberately kept simple to focus on specific testing needs
5. **ADR Compliance**: All helpers comply with relevant ADRs (especially ADR-011 and ADR-014)

## Adding New Helpers

When adding new test helpers:

1. Follow established naming conventions and patterns
2. Add appropriate documentation
3. Create corresponding tests for any non-trivial functionality
4. Ensure ADR compliance, especially for datetime handling
5. Keep helpers focused on specific testing needs

## Learn More

For detailed information about specific helper categories, see these READMEs:

- [Test Models](./models/README.md)
- [Test Schemas](./schemas/README.md)
- [Schema Factories](./schema_factories/README.md)
