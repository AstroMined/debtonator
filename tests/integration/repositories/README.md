# Repository Test Pattern Guide

## Overview

This guide outlines the standard pattern for writing repository tests that properly simulate the validation flow in our application architecture. All repository tests should follow this pattern to ensure consistency and proper testing of our architectural boundaries.

## Directory Structure

The repository tests are organized in a clear two-part structure:

```
tests/integration/repositories/
├── README.md                                  # This guide
├── crud/                                      # Basic CRUD operations only
│   ├── test_account_repository_crud.py
│   ├── test_bill_split_repository_crud.py
│   └── account_types/                         # Account type-specific CRUD tests
│       └── banking/
│           ├── test_checking_crud.py
│           ├── test_credit_crud.py
│           └── ...
└── advanced/                                  # All non-CRUD operations
    ├── test_account_repository_advanced.py
    ├── test_bill_split_repository_advanced.py
    └── account_types/                         # Account type-specific advanced tests
        └── banking/
            ├── test_checking_advanced.py
            ├── test_credit_advanced.py
            └── ...
```

## Test Organization

Repository tests should always be split between two directories:

- The directory `tests/integration/repositories/crud` is for testing the simple CRUD operations from the repositories:
  - Create operations
  - Read operations (simple get by ID)
  - Update operations
  - Delete operations

- The directory `tests/integration/repositories/advanced` is for testing all other operations:
  - Complex queries and filtering
  - Business logic operations
  - Specialized repository methods
  - Cross-entity operations
  - Performance considerations
  - Any specialized functionality (like bill splits with account types)

CRUD tests should always be written first and made to pass to ensure simple operations work before testing advanced options.

## Naming Conventions

### File Naming

Test files must follow a consistent naming pattern:
- CRUD tests: `test_[repository_name]_crud.py`
- Advanced tests: `test_[repository_name]_advanced.py`
- Account type tests: `test_[account_type]_crud.py` and `test_[account_type]_advanced.py`

### Function Naming

Test functions should follow:
- `test_create_[entity]` for create operations
- `test_get_[entity]` for simple read operations
- `test_update_[entity]` for update operations
- `test_delete_[entity]` for delete operations
- `test_[operation]_[entity]` for advanced operations

### Function-Style Tests

**Important**: All tests must use function-style tests, not class-style tests:

```python
# ✅ CORRECT: Function-style tests
@pytest.mark.asyncio
async def test_create_account(account_repository):
    """Test creating an account."""
    # Test implementation...

# ❌ INCORRECT: Class-style tests
class TestAccountRepository:
    @pytest.mark.asyncio
    async def test_create_account(self, account_repository):
        """Test creating an account."""
        # Test implementation...
```

## Fixture Organization

Fixtures should be moved to the appropriate fixture directory based on their type:

- **Model Fixtures**: Move to `tests/fixtures/models/`
  - Fixtures that create database model instances (e.g., `test_account`, `test_bill`)
  - Follow naming conventions in `tests/fixtures/models/README.md`
  - Example: `test_checking_account`, `test_category_with_bills`

- **Repository Fixtures**: Move to `tests/fixtures/repositories/`
  - Fixtures that create repository instances (e.g., `account_repository`, `bill_repository`)
  - Repository fixtures should mirror the source code structure:
    - `fixture_[repository_name]_repositories.py` for base repositories
    - `account_types/banking/fixture_[account_type]_repositories.py` for account type repositories
  - Fixture naming should follow:
    - `[entity_name]_repository` for base repositories
    - `[account_type]_repository` for account type repositories
    - `[entity_name]_repository_with_[feature]` for specialized repositories

- **Service Fixtures**: Move to `tests/fixtures/services/`
  - Fixtures that create service instances (e.g., `feature_flag_service`, `account_service`)
  - Follow naming conventions in `tests/fixtures/services/README.md`

- **Other Fixture Types**: Create appropriate directories if needed
  - Registry fixtures might go in `tests/fixtures/registries/`
  - Database fixtures might go in `tests/fixtures/database/`
  - Follow the established naming patterns for consistency

**Important**: No fixtures should be defined in the test files themselves. All fixtures should be defined in the appropriate fixture directory based on their type.

## Schema Factory Usage

### Why Schema Factories Matter

In our architecture, services are responsible for validating data through Pydantic schemas before passing it to repositories. Repositories assume data has been validated and focus on data access. Using schema factories ensures our tests reflect the actual application flow, catching validation issues early and making tests more realistic.

### Using Schema Factories

All repository tests must use schema factories from `tests/helpers/schema_factories/` to create valid test data:

```python
from tests.helpers.schema_factories import create_entity_schema

@pytest.mark.asyncio
async def test_create_entity(entity_repository):
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

### Preventing Circular Dependencies

When testing repositories, you should:
- Use the repository being tested for the data access being tested
- Use model fixtures for all other data access to prevent circular dependencies

For example, when testing a bill repository that depends on accounts:
- Use the bill repository for bill operations
- Use account model fixtures (not account repositories) for setting up accounts

```python
# ✅ CORRECT: Using model fixtures for dependencies
@pytest.mark.asyncio
async def test_create_bill_with_account(
    bill_repository,
    test_checking_account  # Model fixture, not repository
):
    """Test creating a bill with an account."""
    bill_schema = create_bill_schema(
        account_id=test_checking_account.id
    )
    
    result = await bill_repository.create(bill_schema.model_dump())
    
    assert result.account_id == test_checking_account.id
```

## The Four-Step Pattern

### 1. Arrange: Set up test data and dependencies

Set up any test fixtures, database session, and other dependencies needed for the test.

### 2. Schema: Create and validate data through schema factories

Create a schema instance using a schema factory for the data you want to use in the test. This is a critical step that simulates the service layer's validation process.

### 3. Act: Pass validated data to repository methods

Convert the validated schema to a dictionary using `model_dump()` and pass it to the repository method.

### 4. Assert: Verify the repository operation results

Check that the operation produced the expected results in the database.

## Code Template

```python
@pytest.mark.asyncio
async def test_create_entity(entity_repository):
    """Test creating an entity with proper validation flow."""
    # 1. ARRANGE: Set up test dependencies
    # ... any setup code
    
    # 2. SCHEMA: Create and validate through schema factory
    entity_schema = create_entity_schema(
        name="Test Entity",
        value=100
    )
    
    # Convert validated schema to dict for repository
    validated_data = entity_schema.model_dump()
    
    # 3. ACT: Pass validated data to repository
    result = await entity_repository.create(validated_data)
    
    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id is not None
    assert result.name == "Test Entity"
    assert result.value == 100
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
   schema = create_entity_schema(name="Test", value=100)
   result = await repository.create(schema.model_dump())
   ```

3. **Defining Fixtures in Test Files**: Always define fixtures in the appropriate fixture files

   ```python
   # INCORRECT ❌
   @pytest.fixture
   async def test_entity(db_session):
       """Create a test entity."""
       # Fixture implementation...
   
   # CORRECT ✅
   # Import from tests/fixtures/repositories/fixture_entity_repositories.py
   from tests.fixtures.repositories.fixture_entity_repositories import test_entity
   ```

4. **Using Repository for Non-Tested Data Access**: Use model fixtures for dependencies

   ```python
   # INCORRECT ❌
   account = await account_repository.create(account_data)
   bill = await bill_repository.create({"account_id": account.id})
   
   # CORRECT ✅
   # Use model fixture for account
   bill_schema = create_bill_schema(account_id=test_account.id)
   bill = await bill_repository.create(bill_schema.model_dump())
   ```

5. **Class-Style Tests**: Use function-style tests instead

   ```python
   # INCORRECT ❌
   class TestEntityRepository:
       async def test_create_entity(self, entity_repository):
           # Test implementation...
   
   # CORRECT ✅
   async def test_create_entity(entity_repository):
       # Test implementation...
   ```

6. **Skipping Schema Validation**: Always use schema factories

   ```python
   # INCORRECT ❌
   result = await repository.create({"name": "Test"})
   
   # CORRECT ✅
   schema = create_entity_schema(name="Test")
   result = await repository.create(schema.model_dump())
   ```

7. **Modifying After Validation**: Don't modify data after validation

   ```python
   # INCORRECT ❌
   validated = schema.model_dump()
   validated["extra_field"] = "value"  # Adding unvalidated data
   
   # CORRECT ✅
   # Include all fields in the schema creation
   schema = create_entity_schema(name="Test", extra_field="value")
   ```

## Refactoring Existing Tests

When refactoring existing tests to follow this pattern:

1. Move fixtures to the appropriate location in `tests/fixtures/repositories/`
2. Update tests to use schema factories from `tests/helpers/schema_factories/`
3. Ensure tests are in the correct directories (crud vs. advanced)
4. Update naming conventions for files and functions
5. Convert any class-style tests to function-style tests
6. Replace direct dictionary creation with schema factories
7. Use model fixtures for dependencies instead of repositories

## Pylint Configuration

When using schema factories, you may encounter Pylint errors related to the `model_dump()` method not being recognized on objects returned by factory functions. This is because Pylint cannot see through the decorator magic used in the schema factories.

To address this issue, we've added a global Pylint configuration in `pyproject.toml` to disable the "no-member" warning:

```toml
[tool.pylint.messages_control]
disable = [
    "no-member",  # Disable no-member warnings globally (for schema factory decorator magic)
]
```

This configuration disables the "no-member" warning globally, allowing Pylint to ignore the false positives related to schema factory return values.

If for some reason the global configuration doesn't work in your environment, you can still add the following directive at the top of your test files:

```python
# pylint: disable=no-member
```

## Conclusion

Following this repository test pattern ensures our tests accurately reflect the application's validation flow, catching issues early and making our tests more effective. All repository tests should be updated to follow this pattern for consistency and reliability.
