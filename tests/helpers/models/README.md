# Test Helper Models

This directory contains simple SQLAlchemy models used exclusively for testing purposes. These models provide minimal implementations that can be used to test base functionality without involving the full complexity of business models.

## Purpose

The models in this directory serve several key purposes:

1. **Testing Base Repository**: These models are used to test the `BaseRepository` class and other generic repository functionality without relying on actual business models.

2. **Testing Generic Functionality**: They provide clean, simple models for testing generic functionality that applies across all models.

3. **Avoiding Circular Dependencies**: These test-only models help avoid circular dependencies that might arise when using business models in tests.

4. **Simplifying Test Setup**: They simplify test setup by providing minimalistic models that only implement the features needed for testing.

## Usage

These models are used in conjunction with corresponding fixtures in `/code/debtonator/tests/fixtures/models/fixture_basic_test_models.py` and schema factories in `/code/debtonator/tests/helpers/schema_factories/basic_test_schema_factories.py`.

Example usage:

```python
# In a test file
from tests.helpers.models.test_item import TestItem
from tests.fixtures.models.fixture_basic_test_models import test_item
from tests.helpers.schema_factories.basic_test_schema_factories import create_test_item_schema

async def test_base_repository_create(db_session, test_item):
    """Test creating an item using BaseRepository."""
    # Test implementation using the test models
    repository = BaseRepository(db_session, TestItem)
    
    # Create test data using the schema factory
    test_data = create_test_item_schema(name="Test Item").model_dump()
    
    # Use repository with test model
    result = await repository.create(test_data)
    assert result.name == "Test Item"
```

## Models

The models in this directory include:

- **TestItem**: A simple model with basic fields for testing generic repository operations
- **TestParent**: A parent model for testing relationship operations
- **TestChild**: A child model for testing relationship operations

## Design Principles

1. **Minimalism**: Models include only fields and relationships necessary for testing
2. **Conformity**: Follow the same patterns as business models (e.g., UTC datetime handling)
3. **Independence**: No dependencies on business logic or business models
4. **Clarity**: Clear, descriptive naming that indicates test-only purpose

## Adding New Test Models

When adding new test models:

1. Follow the naming convention: `Test{Purpose}` (e.g., `TestItem`, `TestParent`)
2. Create corresponding fixtures in `/code/debtonator/tests/fixtures/models/fixture_basic_test_models.py`
3. Create corresponding schema factories in `/code/debtonator/tests/helpers/schema_factories/basic_test_schema_factories.py`
4. Ensure models comply with ADR-011 for datetime handling
5. Keep models simple and focused on specific testing needs
