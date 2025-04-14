# CRUD Repository Tests

## Purpose

This directory contains CRUD (Create, Read, Update, Delete) tests for Debtonator's repository layer. These tests focus on validating the basic data access operations while following our "Real Objects Testing Philosophy."

## Related Documentation

- [Parent: Repository Tests](/code/debtonator/tests/integration/repositories/README.md)
- [Schema Factories](/code/debtonator/tests/helpers/schema_factories/README.md)
- [Account Types CRUD Tests](./account_types/banking/README.md)

## Architecture

CRUD tests validate that repositories correctly implement the core data access operations:

- **Create**: Adding new entities to the database
- **Read**: Retrieving entities by ID, filtering, and listing operations
- **Update**: Modifying existing entities
- **Delete**: Removing entities from the database

Each test file corresponds to a specific repository class and focuses solely on these basic operations. More complex queries and specialized methods are tested in the [advanced tests](/code/debtonator/tests/integration/repositories/advanced/README.md).

## Implementation Patterns

### Four-Step Test Pattern

Each CRUD test should follow the four-step pattern described in the parent README:

1. **Arrange**: Set up test data and dependencies
2. **Schema**: Create and validate data through schema factories
3. **Act**: Pass validated data to repository methods
4. **Assert**: Verify the repository operation results

### Full CRUD Coverage Pattern

Every repository test file should include tests for all core CRUD operations:

```python
@pytest.mark.asyncio
async def test_create_entity(entity_repository, db_session, dependencies):
    """Test creating an entity with proper validation flow."""
    # Implementation

@pytest.mark.asyncio
async def test_get_entity(entity_repository, db_session, test_entity):
    """Test retrieving an entity by ID."""
    # Implementation

@pytest.mark.asyncio
async def test_update_entity(entity_repository, db_session, test_entity):
    """Test updating an entity with proper validation flow."""
    # Implementation

@pytest.mark.asyncio
async def test_delete_entity(entity_repository, db_session, test_entity):
    """Test deleting an entity."""
    # Implementation
```

### Schema Factory Usage Pattern

Always use schema factories to create and validate entity data before passing it to the repository:

```python
from tests.helpers.schema_factories import create_entity_schema

# Create schema with factory function
entity_schema = create_entity_schema(
    name="Test Entity",
    value=Decimal("100.00")
)

# Convert to dict for repository method
entity_data = entity_schema.model_dump()

# Use the repository method
entity = await entity_repository.create(entity_data)
```

This pattern:

- Ensures proper validation flow
- Mirrors the service-repository interaction in production
- Makes tests more reliable and realistic

## Key Responsibilities

- Test basic CRUD operations for each repository
- Validate schema-to-repository workflow
- Ensure proper field validation through schemas
- Maintain clean separation from advanced tests
- Follow consistent test patterns

## Testing Strategy

- Each test file should correspond to a single repository class
- Test each CRUD operation independently
- Use model fixtures for dependencies (not repositories)
- Avoid circular dependencies by using model fixtures
- Follow 'No Mocks' policy

## Known Considerations

- CRUD tests should not test specialized repository methods
- Create operations should validate that ID is assigned and all fields match
- Update operations should validate partial updates work correctly
- For polymorphic entities, use the specialized create/update methods
- Timezone-aware fields should use the utility functions from `src/utils/datetime_utils.py`
