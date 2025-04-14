# Test Helpers

This directory contains supporting modules, utilities, and test-specific implementations that enable Debtonator's comprehensive testing strategy while following the "Real Objects Testing Philosophy" established in ADR-014.

## Directory Structure

```tree
helpers/
├── __init__.py
├── models/                   # Test-specific SQLAlchemy models
├── repositories/             # Repository modules for testing factory functionality
│   └── test_types/           # Type-specific repository modules for testing
├── schemas/                  # Test-specific Pydantic schemas
├── schema_factories/         # Schema factory functions for test data creation
├── feature_flag_utils/       # Feature flag testing utilities
└── test_data/                # Sample data files for testing import/export
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

### Repository Test Modules

Contains specialized repository modules designed for testing the repository factory's dynamic module loading capabilities and type-specific repositories.

Example usage:

```python
# Create repository with factory that loads specialized modules
repository = repository_factory(
    db_session,
    TestPolymorphicModel,
    "entity_type",
    {"type_a": "tests.helpers.repositories.test_types.type_a"}
)

# Use dynamically loaded methods
entities = await repository.get_type_a_entities_with_field_value("test value")
```

### Feature Flag Utilities

Contains utilities for testing with feature flags, including solutions for cache-related issues in test environments.

Example usage:

```python
from tests.helpers.feature_flag_utils import ZeroTTLConfigProvider, create_test_requirements

# Create zero-TTL config provider for testing
requirements = create_test_requirements("CHECKING_ACCOUNTS", "checking")
config_provider = ZeroTTLConfigProvider(requirements)

# Use in tests
feature_flag_service = FeatureFlagService(config_provider=config_provider)
```

### Test Data Files

Contains sample data files for testing import, validation, and processing functionality.

Example usage:

```python
# Get path to test data file
test_file_path = Path(__file__).parent.parent / "helpers" / "test_data" / "valid_liabilities.csv"

# Test import function
result = await import_service.import_liabilities_from_csv(test_file_path)
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
- [Repository Test Modules](./repositories/README.md)
- [Repository Test Types](./repositories/test_types/README.md)
- [Feature Flag Utilities](./feature_flag_utils/README.md)
- [Test Data Files](./test_data/README.md)
