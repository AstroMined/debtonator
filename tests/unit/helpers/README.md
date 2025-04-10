# Unit Tests for Test Helpers

This directory contains unit tests for the helper modules in `tests/helpers/`. These tests validate that the test-specific models, schemas, and schema factories used throughout Debtonator's test suite work correctly.

## Directory Structure

```
helpers/
├── models/               # Tests for helper models
├── schemas/              # Tests for helper schemas
└── schema_factories/     # Tests for schema factories
```

## Purpose

Helper tests serve several important roles:

1. **Validate Test Infrastructure**: Ensure that the test infrastructure itself is reliable
2. **Document Helper Usage**: Demonstrate how to use test helpers correctly
3. **Prevent Regressions**: Guard against changes that would break the test suite

## Testing Focus Areas

### Test Models

Test that the SQLAlchemy models used specifically for testing work correctly:

```python
async def test_test_item_creation(db_session):
    """Test that a TestItem can be created in the database."""
    test_item = TestItem(
        name="SQLAlchemy Test Item", 
        value=42,
        created_at=naive_utc_now()
    )
    db_session.add(test_item)
    await db_session.flush()
    
    assert test_item.id is not None
    assert test_item.name == "SQLAlchemy Test Item"
    assert test_item.value == 42
```

### Test Schemas

Test that Pydantic schemas used specifically for testing validate correctly:

```python
def test_test_item_schema_validation():
    """Test validation in TestItem schema."""
    # Valid data
    valid_data = {"name": "Pydantic Test Item", "value": 42}
    schema = TestItemCreate(**valid_data)
    assert schema.name == "Pydantic Test Item"
    assert schema.value == 42
    
    # Invalid data (name too short)
    with pytest.raises(ValidationError):
        TestItemCreate(name="", value=42)  # Empty name
```

### Schema Factories

Test that schema factory functions produce valid schema instances:

```python
def test_create_test_item_schema():
    """Test that create_test_item_schema produces valid schemas."""
    schema = create_test_item_schema(name="Custom Factory Item", value=99)
    
    assert schema.name == "Custom Factory Item"
    assert schema.value == 99
    assert isinstance(schema, TestItemCreate)
```

## Best Practices

1. **Test All Helper Components**: Ensure all test models, schemas, and factories have tests
2. **Verify Integration**: Test that helper components work together correctly
3. **Test Customization**: Verify that schema factories support parameter customization
4. **Follow ADRs**: Ensure all helpers and tests comply with ADRs (especially ADR-011)
