# Unit Tests for Test Helpers

This directory contains unit tests for the helper modules in `tests/helpers/`. These tests validate that the test-specific models, schemas, and schema factories used throughout Debtonator's test suite work correctly and follow the project's "Real Objects Testing Philosophy".

## Directory Structure

The helpers test directory structure mirrors the structure of the `tests/helpers` directory:

```
unit/helpers/
├── __init__.py
├── models/               (Tests for helper models)
│   ├── __init__.py
│   ├── test_test_item.py
│   ├── test_test_parent.py
│   └── ...
├── schemas/              (Tests for helper schemas)
│   ├── __init__.py
│   ├── test_test_item.py
│   ├── test_test_parent.py
│   └── ...
└── schema_factories/     (Tests for schema factories)
    ├── __init__.py
    ├── test_basic_test_schema_factories.py
    ├── test_complex_schema_factories.py
    └── ...
```

## Purpose of Helper Tests

Helper tests serve several important roles:

1. **Validate Test Infrastructure**: Ensure that the test infrastructure itself is reliable
2. **Document Helper Usage**: Demonstrate how to use test helpers correctly
3. **Prevent Regressions**: Guard against changes that would break the test suite
4. **Improve Test Coverage**: Help achieve comprehensive test coverage
5. **Maintain ADR Compliance**: Verify helpers comply with ADRs (especially ADR-011 and ADR-014)

## Testing Focus for Helper Components

### 1. Test Models (SQLAlchemy)

The `tests/helpers/models` directory contains simplified SQLAlchemy models used specifically for testing base functionality without involving business models. Test that these models work correctly:

```python
async def test_test_item_creation(db_session):
    """Test that a TestItem can be created and stored in the database."""
    test_item = TestItem(
        name="SQLAlchemy Test Item", 
        value=42,
        created_at=naive_utc_now()  # Use naive_utc_now() per ADR-011
    )
    db_session.add(test_item)
    await db_session.flush()
    
    assert test_item.id is not None
    assert test_item.name == "SQLAlchemy Test Item"
    assert test_item.value == 42
    
    # Verify it can be retrieved from the database
    from sqlalchemy import select
    stmt = select(TestItem).where(TestItem.id == test_item.id)
    result = await db_session.execute(stmt)
    retrieved_item = result.scalars().first()
    
    assert retrieved_item is not None
    assert retrieved_item.name == "SQLAlchemy Test Item"
    assert retrieved_item.value == 42
```

### 2. Test Schemas (Pydantic)

The `tests/helpers/schemas` directory contains test-specific Pydantic schemas. Test that these schemas validate correctly:

```python
def test_test_item_schema_validation():
    """Test validation in TestItem schema."""
    # Valid data
    valid_data = {"name": "Pydantic Test Item", "value": 42}
    schema = TestItemCreate(**valid_data)
    assert schema.name == "Pydantic Test Item"
    assert schema.value == 42
    
    # Invalid data (name too short)
    with pytest.raises(ValidationError) as excinfo:
        TestItemCreate(name="", value=42)  # Empty name
    
    errors = excinfo.value.errors()
    assert any(
        error["type"] == "string_too_short" and
        error["loc"][0] == "name"
        for error in errors
    )
    
    # Invalid data (negative value)
    with pytest.raises(ValidationError) as excinfo:
        TestItemCreate(name="Valid Name", value=-1)  # Negative value
    
    errors = excinfo.value.errors()
    assert any(
        error["type"] == "greater_than_equal" and
        error["loc"][0] == "value"
        for error in errors
    )
```

### 3. Schema Factories

The `tests/helpers/schema_factories` directory contains factory functions for creating schema instances. Test that these factories produce valid instances:

```python
def test_create_test_item_schema():
    """Test that create_test_item_schema produces valid schemas."""
    schema = create_test_item_schema(name="Custom Factory Item", value=99)
    
    assert schema.name == "Custom Factory Item"
    assert schema.value == 99
    assert isinstance(schema, TestItemCreate)

def test_create_test_item_schema_defaults():
    """Test that create_test_item_schema uses sensible defaults."""
    schema = create_test_item_schema()
    
    assert schema.name is not None
    assert schema.name.startswith("Test Item")
    assert schema.value >= 0
    assert isinstance(schema, TestItemCreate)
```

## Testing Integration Between Helper Components

Test that helper components work together correctly, mirroring how they're used in actual tests:

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
    
    # Test full round-trip to response schema
    from tests.helpers.schemas.test_item import TestItemResponse
    
    response_data = {
        "id": test_item.id,
        "name": test_item.name,
        "value": test_item.value,
        "created_at": test_item.created_at
    }
    
    response_schema = TestItemResponse(**response_data)
    assert response_schema.id == test_item.id
    assert response_schema.name == test_item.name
    assert response_schema.value == test_item.value
```

## Testing DateTime Compliance (ADR-011)

Per ADR-011, all test helpers must use proper UTC datetime handling:

```python
async def test_datetime_compliance(db_session):
    """Test that helper models comply with ADR-011."""
    from src.utils.datetime_utils import naive_utc_now, utc_now
    
    # Create model with naive UTC datetime (for database)
    test_item = TestItem(
        name="DateTime Test",
        value=42,
        created_at=naive_utc_now()  # Naive UTC datetime for database
    )
    db_session.add(test_item)
    await db_session.flush()
    
    # Create schema with timezone-aware UTC datetime
    aware_now = utc_now()  # Timezone-aware UTC datetime
    schema = TestItemWithDateCreate(
        name="DateTime Schema Test",
        value=42,
        timestamp=aware_now
    )
    
    # Test validation enforces UTC timezone
    from datetime import datetime, timezone, timedelta
    non_utc = datetime.now(timezone(timedelta(hours=1)))  # Non-UTC timezone
    
    with pytest.raises(ValidationError) as excinfo:
        TestItemWithDateCreate(
            name="Invalid DateTime Test",
            value=42,
            timestamp=non_utc
        )
    
    errors = excinfo.value.errors()
    assert any(
        "UTC" in error["msg"].upper()
        for error in errors
    )
```

## Testing Complex Nested Structures

Test helpers often involve complex nested structures. Test these thoroughly:

```python
def test_nested_schema_factory():
    """Test factory for schemas with nested objects."""
    schema = create_complex_test_schema(
        name="Parent Test",
        children_count=3
    )
    
    assert schema.name == "Parent Test"
    assert len(schema.children) == 3
    
    # Verify children were created correctly
    for i, child in enumerate(schema.children):
        assert child.name.startswith(f"Child {i+1}")
        assert child.parent_name == "Parent Test"
        
    # Test that all children have unique IDs
    child_ids = [child.id for child in schema.children if hasattr(child, 'id')]
    if child_ids:  # If IDs are generated
        assert len(set(child_ids)) == len(child_ids)  # No duplicates
```

## Testing Realistic Financial Test Data

Test that schema factories create realistic financial test data:

```python
def test_financial_test_data():
    """Test that financial test data is realistic."""
    # Create financial test schema
    schema = create_test_financial_schema(
        principal=Decimal("1000.00"),
        interest_rate=Decimal("0.05"),  # 5%
        payment_amount=Decimal("100.00")
    )
    
    assert schema.principal == Decimal("1000.00")
    assert schema.interest_rate == Decimal("0.05")
    assert schema.payment_amount == Decimal("100.00")
    
    # Test defaults are within realistic ranges
    default_schema = create_test_financial_schema()
    
    # Principal should be a positive amount with proper precision
    assert default_schema.principal > Decimal("0")
    assert default_schema.principal.as_tuple().exponent <= -2  # At least 2 decimal places
    
    # Interest rate should be a small decimal (typically under 30%)
    assert Decimal("0") < default_schema.interest_rate < Decimal("0.30")
    
    # Payment amount should be positive and proportional to principal
    assert default_schema.payment_amount > Decimal("0")
    ratio = default_schema.payment_amount / default_schema.principal
    assert Decimal("0.01") < ratio < Decimal("0.50")  # Typical monthly payment range
```

## Testing Schema List Factories

Test factories that create lists of schemas:

```python
def test_schema_list_factory():
    """Test factory for creating lists of schemas."""
    schemas = create_test_item_schema_list(count=5)
    
    assert len(schemas) == 5
    assert all(isinstance(schema, TestItemCreate) for schema in schemas)
    
    # Verify unique values (each schema should be different)
    names = [schema.name for schema in schemas]
    assert len(set(names)) == 5  # All names should be unique
    
    # Test parameter customization for all schemas
    custom_schemas = create_test_item_schema_list(
        count=3,
        value=99,
        prefix="Custom List Item"
    )
    
    assert len(custom_schemas) == 3
    assert all(schema.value == 99 for schema in custom_schemas)
    assert all(schema.name.startswith("Custom List Item") for schema in custom_schemas)
```

## Testing Deterministic vs. Random Behavior

Test that factories are appropriately deterministic or random as needed:

```python
def test_deterministic_schema_factory():
    """Test deterministic schema factory behavior."""
    # With fixed seed, output should be consistent
    schema1 = create_deterministic_test_schema(seed=123)
    schema2 = create_deterministic_test_schema(seed=123)
    
    # Same seed should produce identical output
    assert schema1.name == schema2.name
    assert schema1.value == schema2.value
    
    # Different seeds should produce different results
    schema3 = create_deterministic_test_schema(seed=456)
    assert schema1.name != schema3.name or schema1.value != schema3.value

def test_random_schema_factory():
    """Test random schema factory behavior."""
    # Multiple calls should produce different results
    schemas = [create_random_test_schema() for _ in range(10)]
    name_values = [(s.name, s.value) for s in schemas]
    unique_values = set(name_values)
    
    assert len(unique_values) > 1  # Should have some variation
```

## Testing Helper Models

### 1. Test Model Properties

Test properties and methods on helper models:

```python
async def test_test_item_properties(db_session):
    """Test properties on TestItem model."""
    test_item = TestItem(name="Property Test", value=50)
    db_session.add(test_item)
    await db_session.flush()
    
    # Test calculated property
    assert test_item.is_high_value == (test_item.value > 100)
    
    # Test property after update
    test_item.value = 150
    await db_session.flush()
    assert test_item.is_high_value is True
```

### 2. Test Model Methods

Test methods on helper models:

```python
async def test_test_item_methods(db_session):
    """Test methods on TestItem model."""
    test_item = TestItem(name="Method Test", value=50)
    db_session.add(test_item)
    await db_session.flush()
    
    # Test method
    test_item.increase_value(25)
    await db_session.flush()
    assert test_item.value == 75
    
    # Test method with validation
    with pytest.raises(ValueError):
        test_item.increase_value(-10)  # Negative increase not allowed
```

### 3. Test Model Relationships

Test relationships between helper models:

```python
async def test_test_item_relationships(db_session):
    """Test relationships between helper models."""
    # Create parent
    parent = TestParent(name="Parent Test")
    db_session.add(parent)
    await db_session.flush()
    
    # Create children
    for i in range(3):
        child = TestChild(name=f"Child {i}", parent_id=parent.id)
        db_session.add(child)
    
    await db_session.flush()
    await db_session.refresh(parent)
    
    # Test relationship
    assert len(parent.children) == 3
    assert parent.children[0].name == "Child 0"
    assert parent.children[1].name == "Child 1"
    assert parent.children[2].name == "Child 2"
    
    # Test cascading delete
    await db_session.delete(parent)
    await db_session.flush()
    
    # Children should be deleted too
    from sqlalchemy import select
    stmt = select(TestChild).where(TestChild.parent_id == parent.id)
    result = await db_session.execute(stmt)
    remaining_children = result.scalars().all()
    
    assert len(remaining_children) == 0
```

## Testing Generic Repository Components

Test the interaction between helper models and generic repositories:

```python
async def test_generic_repository_with_test_models(db_session):
    """Test generic repository functionality with test models."""
    from src.repositories.base_repository import BaseRepository
    from tests.helpers.models.test_item import TestItem
    
    # Create a generic repository for TestItem
    class TestItemRepository(BaseRepository):
        model = TestItem
    
    repo = TestItemRepository(db_session)
    
    # Test basic CRUD operations
    # 1. Create
    item_data = {"name": "Repository Test", "value": 42}
    created_item = await repo.create(item_data)
    
    assert created_item.id is not None
    assert created_item.name == "Repository Test"
    assert created_item.value == 42
    
    # 2. Read
    retrieved_item = await repo.get_by_id(created_item.id)
    
    assert retrieved_item is not None
    assert retrieved_item.id == created_item.id
    assert retrieved_item.name == "Repository Test"
    
    # 3. Update
    updated_data = {"value": 99}
    updated_item = await repo.update(created_item.id, updated_data)
    
    assert updated_item.id == created_item.id
    assert updated_item.name == "Repository Test"  # Unchanged
    assert updated_item.value == 99  # Updated
    
    # 4. Delete
    await repo.delete(created_item.id)
    
    # Verify item was deleted
    deleted_item = await repo.get_by_id(created_item.id)
    assert deleted_item is None
```

## Best Practices

1. **Test All Helper Components**: Ensure all test models, schemas, and factories have tests
2. **Verify Integration**: Test that helper components work together correctly
3. **Test Customization**: Verify that schema factories support parameter customization
4. **Test Default Behavior**: Verify that sensible defaults are used when parameters are omitted
5. **Test Range of Values**: Verify behavior with different values (min, max, typical)
6. **Test Validation**: Verify that validation rules work correctly
7. **Test Edge Cases**: Include tests for boundary conditions and edge cases
8. **Maintain Isolation**: Keep helper tests isolated from application tests
9. **Follow ADRs**: Ensure all helpers and tests comply with ADRs (especially ADR-011 and ADR-014)
10. **Document Usage Patterns**: Use tests to document how to use helper components correctly
11. **Test Realistic Financial Data**: Ensure test data for financial fields is realistic
12. **Test Database Integration**: Verify helper models work correctly with the database
13. **Test Repository Integration**: Verify helper models work with generic repositories
14. **Maintain Independence**: Ensure test helpers don't depend unnecessarily on application code
15. **Keep Helpers Simple**: Test helpers should be simple and focused on testing needs

## Common Anti-Patterns to Avoid

1. **Complex Test Helpers**: Keep test helpers simple and focused; avoid complex logic
2. **Untested Helper Components**: Don't forget to test the test helpers themselves
3. **Helper Dependencies on Application Code**: Test helpers should have minimal dependencies
4. **Circular Dependencies**: Avoid circular dependencies between helper components
5. **Duplicate Test Models**: Don't create duplicate test models; reuse existing ones
6. **Inconsistent Naming**: Follow established naming conventions for helper components
7. **Direct Database Access**: Use the db_session fixture for database access
8. **Naive Datetimes**: Use proper timezone-aware UTC datetimes (per ADR-011)
9. **Hardcoded IDs**: Don't use hardcoded IDs in tests
10. **Unrealistic Test Data**: Ensure financial test data is realistic (proper decimal precision, etc.)
11. **Missing Validation**: Ensure test schemas validate data properly
12. **Business Logic in Test Helpers**: Keep business logic in application code, not test helpers
13. **Missing Documentation**: Document all test helpers thoroughly
14. **SQLAlchemy 1.x Patterns**: Use SQLAlchemy 2.0 patterns in all test helpers

## Example Test File Structure

```python
import pytest
import pytest_asyncio
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import ValidationError

from tests.helpers.models.test_item import TestItem
from tests.helpers.schemas.test_item import TestItemCreate, TestItemBase, TestItemResponse
from tests.helpers.schema_factories.basic_test_schema_factories import (
    create_test_item_schema,
    create_test_item_schema_list,
)
from src.utils.datetime_utils import naive_utc_now, utc_now

# Model tests
async def test_test_item_model_creation(db_session: AsyncSession):
    """Test that TestItem model can be created."""
    # Test implementation...

# Schema tests
def test_test_item_schema_validation():
    """Test validation in TestItemCreate schema."""
    # Test implementation...

# Factory tests
def test_create_test_item_schema():
    """Test create_test_item_schema factory."""
    # Test implementation...

# Integration tests
async def test_schema_to_model_integration(db_session: AsyncSession):
    """Test integration between schema factory and model."""
    # Test implementation...
```

## Fixture Integration

Test helpers can be integrated with pytest fixtures:

```python
@pytest.fixture
def test_item_schema():
    """Fixture providing a sample TestItemCreate schema."""
    return create_test_item_schema(name="Fixture Sample", value=42)

@pytest_asyncio.fixture
async def test_item_model(db_session):
    """Fixture providing a sample TestItem model instance."""
    item = TestItem(name="Model Fixture Sample", value=42)
    db_session.add(item)
    await db_session.flush()
    await db_session.refresh(item)
    return item

def test_with_fixtures(test_item_schema, test_item_model):
    """Test using helper fixtures."""
    assert test_item_schema.name == "Fixture Sample"
    assert test_item_schema.value == 42
    
    assert test_item_model.name == "Model Fixture Sample"
    assert test_item_model.value == 42
```
