# Unit Tests for Schema Factories

This directory contains unit tests for the schema factory functions in `tests/helpers/schema_factories/`. These tests validate that schema factories produce valid schema instances with correct default values and customization options.

## Purpose

Schema factory tests serve to:

1. **Verify Factory Behavior**: Ensure factories create valid schema instances
2. **Test Customization Options**: Verify that custom parameters override defaults correctly
3. **Document Factory Usage**: Demonstrate how to use schema factories effectively

## Testing Focus Areas

### Basic Factory Functionality

Test that factories create valid schema instances with expected defaults:

```python
def test_create_test_item_schema():
    """Test that create_test_item_schema produces valid schemas."""
    schema = create_test_item_schema()
    
    assert schema.name is not None
    assert schema.name.startswith("Test Item")
    assert schema.value >= 0
    assert isinstance(schema, TestItemCreate)
```

### Parameter Customization

Test that all parameters can be customized:

```python
def test_create_test_item_schema_customization():
    """Test parameter customization in test item schema factory."""
    schema = create_test_item_schema(
        name="Custom Factory Item", 
        value=99
    )
    
    assert schema.name == "Custom Factory Item"
    assert schema.value == 99
    assert isinstance(schema, TestItemCreate)
```

### Schema Factory Integration

Test integration between schemas and models:

```python
async def test_schema_to_model_integration(db_session):
    """Test integration between schema factory and model."""
    # Create schema from factory
    schema = create_test_item_schema(name="Integration Test", value=100)
    
    # Convert to dict for model creation
    data = schema.model_dump()
    
    # Create model instance
    test_item = TestItem(**data)
    db_session.add(test_item)
    await db_session.flush()
    
    # Verify model was created correctly
    assert test_item.id is not None
    assert test_item.name == "Integration Test"
    assert test_item.value == 100
```

## Best Practices

1. **Test Every Factory Function**: Ensure all factory functions have dedicated tests
2. **Test Default Values**: Ensure defaults are appropriate and follow business rules
3. **Test All Parameters**: Verify that each parameter can be customized
4. **Test Validation Flow**: Ensure generated schemas pass validation
5. **Document Factory Usage**: Use tests to demonstrate proper usage patterns
