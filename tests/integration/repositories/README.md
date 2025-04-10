# Integration Tests for Repositories

This directory contains integration tests for Debtonator's repository layer. These tests validate the data access patterns, query capabilities, and database interactions while following our "Real Objects Testing Philosophy."

## Directory Structure

```
repositories/
├── crud/                  # Basic CRUD operations tests
│   ├── test_account_repository_crud.py
│   ├── test_bill_repository_crud.py
│   └── account_types/     # Account type-specific CRUD tests
│       └── banking/
│           ├── test_checking_crud.py
│           └── test_credit_crud.py
└── advanced/              # Complex operations tests
    ├── test_account_repository_advanced.py
    ├── test_bill_repository_advanced.py
    └── account_types/     # Account type-specific advanced tests
        └── banking/
            ├── test_checking_advanced.py
            └── test_credit_advanced.py
```

## Test Organization

Repository tests are organized into two main categories:

1. **CRUD Tests** (`repositories/crud/`): Basic create, read, update, and delete operations
2. **Advanced Tests** (`repositories/advanced/`): Complex queries, filtering, and specialized methods

This separation helps maintain focus and simplifies test maintenance.

## The Four-Step Pattern

Each repository test should follow this four-step pattern:

### 1. Arrange: Set up test data and dependencies

```python
# Create test data for the operation
checking_account = await create_test_checking_account(db_session)
```

### 2. Schema: Create and validate data through schema factories

```python
# Create and validate through schema factory
bill_schema = create_bill_schema(
    name="Test Bill",
    amount=Decimal("100.00"),
    primary_account_id=checking_account.id
)
```

### 3. Act: Pass validated data to repository methods

```python
# Convert validated schema to dict for repository
validated_data = bill_schema.model_dump()

# Pass validated data to repository
result = await bill_repository.create(validated_data)
```

### 4. Assert: Verify the repository operation results

```python
# Verify the operation results
assert result is not None
assert result.id is not None
assert result.name == "Test Bill"
assert result.amount == Decimal("100.00")
```

## Using Schema Factories

Always use schema factories to create valid test data:

```python
from tests.helpers.schema_factories import create_bill_schema

# Create schema with factory function
bill_schema = create_bill_schema(
    name="Test Bill",
    amount=Decimal("100.00"),
    primary_account_id=checking_account.id
)

# Convert to dict for repository method
bill_data = bill_schema.model_dump()

# Create bill through repository
bill = await bill_repository.create(bill_data)
```

This approach:
- Ensures proper validation flow (schemas validate data before repositories use it)
- Mirrors the service-repository interaction in production code
- Catches validation issues early in the testing process
- Makes tests more realistic and reliable

## Testing Philosophy

Debtonator follows an integration-first testing approach with real objects:

1. **Real Database**: Tests use a real test database that resets between tests
2. **Real Objects**: Tests use real models, schemas, and repositories
3. **No Mocks**: We prohibit using unittest.mock, MagicMock, or any mocking libraries

## Fixture Organization

Fixtures should be placed in the appropriate directories:
- **Model Fixtures**: `tests/fixtures/models/`
- **Repository Fixtures**: `tests/fixtures/repositories/`
- **Schema Factory Fixtures**: `tests/helpers/schema_factories/`

## Example Repository Test

```python
@pytest.mark.asyncio
async def test_create_bill(bill_repository, db_session, test_checking_account):
    """Test creating a bill with proper validation flow."""
    # 1. ARRANGE: Set up test dependencies (using model fixture)
    
    # 2. SCHEMA: Create and validate through schema factory
    bill_schema = create_bill_schema(
        name="Test Bill",
        amount=Decimal("100.00"),
        primary_account_id=test_checking_account.id
    )
    
    # Convert validated schema to dict for repository
    validated_data = bill_schema.model_dump()
    
    # 3. ACT: Pass validated data to repository
    result = await bill_repository.create(validated_data)
    
    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id is not None
    assert result.name == "Test Bill"
    assert result.amount == Decimal("100.00")
    assert result.primary_account_id == test_checking_account.id
```
