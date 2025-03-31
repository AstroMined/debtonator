# Repository Test Pattern Guide

## Overview

This guide outlines the standard pattern for writing repository tests that properly simulate the validation flow in our application architecture. All repository tests should follow this pattern to ensure consistency and proper testing of our architectural boundaries.

## Why This Pattern Matters

In our architecture, services are responsible for validating data through Pydantic schemas before passing it to repositories. Repositories assume data has been validated and focus on data access. This pattern ensures our tests reflect the actual application flow, catching validation issues early and making tests more realistic.

## The Four-Step Pattern

### 1. Arrange: Set up test data and dependencies

Set up any test fixtures, database session, and other dependencies needed for the test.

### 2. Schema: Create and validate data through Pydantic schemas

Create a Pydantic schema instance for the data you want to use in the test. This is a critical step that simulates the service layer's validation process.

### 3. Act: Pass validated data to repository methods

Convert the validated schema to a dictionary using `model_dump()` and pass it to the repository method.

### 4. Assert: Verify the repository operation results

Check that the operation produced the expected results in the database.

## Code Template

```python
@pytest.mark.asyncio
async def test_create_entity(
    entity_repository: EntityRepository,
    # ... other fixtures
):
    """Test creating an entity with proper validation flow."""
    # 1. ARRANGE: Set up test dependencies
    # ... any setup code
    
    # 2. SCHEMA: Create and validate through Pydantic schema
    entity_schema = EntityCreate(
        name="Test Entity",
        value=100,
        # ... other required fields
    )
    
    # Convert validated schema to dict for repository
    validated_data = entity_schema.model_dump()
    
    # 3. ACT: Pass validated data to repository
    result = await entity_repository.create(validated_data)
    
    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id is not None
    assert result.name == entity_schema.name
    assert result.value == entity_schema.value
    # ... other assertions
```

## Using Schema Factory Functions

To streamline test code and reduce duplication, use the schema factory functions in `tests/helpers/schema_factories.py`:

```python
from tests.helpers.schema_factories import create_entity_schema

@pytest.mark.asyncio
async def test_create_entity(entity_repository: EntityRepository):
    """Test creating an entity with factory function."""
    # Create schema with factory function
    entity_schema = create_entity_schema(
        name="Test Entity",
        value=100
    )
    
    # Convert and pass to repository
    result = await entity_repository.create(entity_schema.model_dump())
    
    # Assert results
    assert result.name == "Test Entity"
    assert result.value == 100
```

## Testing Validation Errors

It's valuable to test that invalid data would be caught by schema validation:

```python
@pytest.mark.asyncio
async def test_validation_error_handling(entity_repository: EntityRepository):
    """Test that schema validation catches invalid data."""
    # Try creating a schema with invalid data
    try:
        invalid_schema = EntityCreate(
            name="",  # Invalid empty name
            value=-10  # Invalid negative value
        )
        assert False, "Schema should have raised a validation error"
    except ValueError as e:
        # This is expected - schema validation should catch the error
        assert "name" in str(e) or "value" in str(e)
```

## Testing Philosophy: Real Objects, No Mocks

Debtonator follows an integration-first testing approach with real objects:

1. **No Mocks Policy**: We strictly prohibit using unittest.mock, MagicMock, or any mocking libraries
2. **Real Database Testing**: Tests use a real test database that gets set up/torn down between tests
3. **Cross-Layer Integration**: Tests verify real interactions between layers using actual objects
4. **Real Schemas**: All test data is validated through real Pydantic schemas

Benefits of this approach:

- Tests catch integration issues that mocks would miss
- Tests validate actual database operations and constraints
- Test maintenance is simpler without complex mock setup
- Greater confidence that tests reflect production behavior

## Common Pitfalls to Avoid

1. **Using Mocks**: Never use mocks for repositories, schemas, or any other components

   ```python
   # INCORRECT ❌
   mock_repo = MagicMock()
   mock_repo.get.return_value = None
   
   # CORRECT ✅
   repo = Repository(db_session)  # Use real repository with test database
   ```

2. **Direct Dictionary Creation**: Never create raw dictionaries for repository methods

   ```python
   # INCORRECT ❌
   data = {"name": "Test", "value": 100}
   result = await repository.create(data)
   
   # CORRECT ✅
   schema = EntityCreate(name="Test", value=100)
   result = await repository.create(schema.model_dump())
   ```

3. **Missing Schema Import**: Always import the appropriate schema classes

   ```python
   # Required at the top of your test file
   from src.schemas.entities import EntityCreate, EntityUpdate
   ```

4. **Forgetting Validation**: Don't skip the schema validation step

   ```python
   # INCORRECT ❌
   result = await repository.create({"name": "Test"})
   
   # CORRECT ✅
   schema = EntityCreate(name="Test")
   result = await repository.create(schema.model_dump())
   ```

5. **Modifying After Validation**: Don't modify data after validation

   ```python
   # INCORRECT ❌
   validated = schema.model_dump()
   validated["extra_field"] = "value"  # Adding unvalidated data
   
   # CORRECT ✅
   # Include all fields in the schema creation
   schema = EntityCreate(name="Test", extra_field="value")
   ```

## Example Tests

See `tests/integration/repositories/test_bill_split_repository.py` for a complete reference implementation of this pattern.

## Refactoring Existing Tests

When refactoring existing tests to follow this pattern:

1. Import the appropriate schema classes
2. Replace direct dictionary creation with schema instances
3. Add `model_dump()` to convert schemas to dictionaries
4. Update assertions to verify results against schema data
5. Add validation error tests where appropriate

## Conclusion

Following this repository test pattern ensures our tests accurately reflect the application's validation flow, catching issues early and making our tests more effective. All repository tests should be updated to follow this pattern for consistency and reliability.
