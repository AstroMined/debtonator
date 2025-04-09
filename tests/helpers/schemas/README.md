# Test Helper Schemas

This directory contains Pydantic schemas used exclusively for testing purposes. These schemas provide minimal implementations that can be used to test base functionality without involving the full complexity of business schemas.

## Purpose

The schemas in this directory serve several key purposes:

1. **Testing Base Components**: These schemas are used to test base classes and generic functionality without relying on actual business schemas.

2. **Testing Validation Flow**: They provide clean, simple schemas for testing the validation flow from API to database.

3. **Simplifying Test Setup**: They simplify test setup by providing minimalistic schemas that only implement the features needed for testing.

4. **Supporting Test Models**: They provide schema validation for the test models defined in `/code/debtonator/tests/helpers/models/`.

## Usage

These schemas are used in conjunction with corresponding schema factories in `/code/debtonator/tests/helpers/schema_factories/basic_test_schema_factories.py` and test models in `/code/debtonator/tests/helpers/models/`.

Example usage:

```python
# In a test file
from tests.helpers.schemas.test_item import TestItemCreate
from tests.helpers.schema_factories.basic_test_schema_factories import create_test_item_schema

async def test_validation_flow():
    """Test schema validation flow."""
    # Create test data using the schema factory
    test_data = create_test_item_schema(name="Test Item")
    
    # Use the schema for validation
    assert isinstance(test_data, TestItemCreate)
    assert test_data.name == "Test Item"
    
    # Use the validated data with a repository
    result = await repository.create(test_data.model_dump())
```

## Schema Types

The schemas typically follow the common pattern used throughout the application:

- **{Name}Create**: For creating new instances (e.g., `TestItemCreate`)
- **{Name}Update**: For updating existing instances (e.g., `TestItemUpdate`)
- **{Name}InDB**: For database model representation (e.g., `TestItemInDB`)
- **{Name}Response**: For API responses (e.g., `TestItemResponse`)

## Design Principles

1. **Minimalism**: Schemas include only fields necessary for testing
2. **Conformity**: Follow the same patterns as business schemas (e.g., validation rules)
3. **Independence**: No dependencies on business logic or business schemas
4. **Clarity**: Clear, descriptive naming that indicates test-only purpose
5. **ADR Compliance**: Follow ADR requirements (e.g., ADR-011 for datetime handling)

## Adding New Test Schemas

When adding new test schemas:

1. Follow the naming convention: `Test{Purpose}{Type}` (e.g., `TestItemCreate`, `TestItemResponse`)
2. Create corresponding schema factories in `/code/debtonator/tests/helpers/schema_factories/basic_test_schema_factories.py`
3. Ensure schemas comply with Pydantic v2 requirements
4. Ensure datetime fields use the appropriate types for ADR-011 compliance
5. Keep schemas simple and focused on specific testing needs
