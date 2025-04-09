# Test Helpers

This directory contains supporting modules, utilities, and test-specific implementations that help enable Debtonator's comprehensive testing strategy while following the "Real Objects Testing Philosophy" established in ADR-014.

## Directory Overview

```
helpers/
├── __init__.py
├── models/                   (Test-specific SQLAlchemy models)
├── schemas/                  (Test-specific Pydantic schemas)
└── schema_factories/         (Schema factory functions for test data creation)
```

## Helper Categories

### Test Models

Contains [SQLAlchemy models designed specifically for testing](/code/debtonator/tests/helpers/models/README.md) base functionality without involving business models. These models support testing of generic components like the `BaseRepository` class.

### Test Schemas

Contains [Pydantic schemas designed specifically for testing](/code/debtonator/tests/helpers/schemas/README.md) validation flow and base functionality. These schemas work with the test models to enable comprehensive testing of generic components.

### Schema Factories

Contains [factory functions for creating schema instances](/code/debtonator/tests/helpers/schema_factories/README.md) used in tests. These factories ensure proper validation flow from schemas to repositories and provide consistent test data creation patterns.

## Key Principles

1. **Real Objects**: Helpers support our "no mocks" philosophy by providing real objects for testing
2. **Isolation**: Test-specific models and schemas allow testing of base functionality in isolation
3. **Consistency**: Helpers enforce consistent patterns across all tests
4. **Simplicity**: Test helpers are deliberately kept simple to focus on specific testing needs
5. **ADR Compliance**: All helpers comply with relevant ADRs (especially ADR-011 and ADR-014)

## Usage Examples

### Test Models and Schemas

```python
from tests.helpers.models.test_item import TestItem
from tests.helpers.schemas.test_item import TestItemCreate
from tests.helpers.schema_factories.basic_test_schema_factories import create_test_item_schema
from src.utils.datetime_utils import naive_utc_now  # Proper import from src/utils

# Create test data using schema factory
test_data = create_test_item_schema(name="Test Item")

# Use the data with a repository
result = await repository.create(test_data.model_dump())
```

## Adding New Helpers

When adding new test helpers:

1. Follow established naming conventions and patterns
2. Add appropriate documentation
3. Create corresponding tests for any non-trivial functionality
4. Ensure ADR compliance, especially for datetime handling (using src/utils/datetime_utils.py)
5. Keep helpers focused on specific testing needs
