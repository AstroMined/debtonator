# Integration Tests for Repositories

This directory contains integration tests for Debtonator's repository layer. These tests validate the data access patterns, query capabilities, and database interactions while following our "Real Objects Testing Philosophy."

## Child Documentation

- [CRUD Tests Documentation](./crud/README.md)
- [Advanced Tests Documentation](./advanced/README.md)
- [Bill Splits Tests Documentation](./bill_splits/README.md)

## Directory Structure

```tree
repositories/
├── crud/                                   # Basic CRUD operations tests
│   ├── README.md                           # CRUD tests documentation
│   ├── test_account_repository_crud.py
│   ├── test_bill_repository_crud.py
│   └── account_types/                      # Account type-specific CRUD tests
│       └── banking/
│           ├── README.md                   # Banking account types CRUD documentation
│           ├── test_checking_crud.py
│           ├── test_credit_crud.py
│           ├── test_savings_crud.py
│           ├── test_bnpl_crud.py
│           ├── test_ewa_crud.py
│           └── test_payment_app_crud.py
├── advanced/                               # Complex operations tests
│   ├── README.md                           # Advanced tests documentation
│   ├── test_account_repository_advanced.py
│   ├── test_bill_repository_advanced.py
│   ├── bill_splits/                        # Bill split advanced tests
│   │   ├── README.md                       # Bill splits advanced documentation
│   │   └── test_bill_splits_with_account_types_advanced.py
│   └── account_types/                      # Account type-specific advanced tests
│       └── banking/
│           ├── README.md                   # Banking account types advanced documentation
│           ├── test_checking_advanced.py
│           ├── test_credit_advanced.py
│           ├── test_savings_advanced.py
│           ├── test_bnpl_advanced.py
│           ├── test_ewa_advanced.py
│           └── test_payment_app_advanced.py
├── bill_splits/                            # Bill splits functionality tests
│   └── README.md                           # Bill splits documentation
├── test_base_repository.py                 # BaseRepository tests
├── test_factory.py                         # Repository factory tests
└── test_polymorphic_base_repository.py     # PolymorphicBaseRepository tests
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

## Repository Patterns

### Standard Repository Pattern

For non-polymorphic entities, use the standard repository methods:

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

### Polymorphic Repository Pattern

For polymorphic entities like account types, use specialized repository methods:

```python
@pytest.mark.asyncio
async def test_create_typed_entity(account_repository, db_session):
    """Test creating a checking account using the polymorphic repository pattern."""
    # 1. ARRANGE: Setup is minimal as we're testing creation
    
    # 2. SCHEMA: Create and validate using the appropriate schema factory
    account_schema = create_checking_account_schema(
        name="Primary Checking",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00")
    )
    
    # Convert to dict for repository method
    account_data = account_schema.model_dump()
    
    # 3. ACT: Use typed entity creation (NOT the base create method)
    result = await account_repository.create_typed_entity("checking", account_data)
    
    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id is not None
    assert result.name == "Primary Checking"
    assert result.current_balance == Decimal("1000.00")
    assert result.available_balance == Decimal("1000.00")
    assert result.account_type == "checking"
    
    # Verify we created the proper polymorphic type
    assert isinstance(result, CheckingAccount)
```

## UTC Datetime Compliance

All tests involving datetimes must follow the patterns established in ADR-011:

```python
from src.utils.datetime_utils import ensure_utc, datetime_equals

@pytest.mark.asyncio
async def test_date_range_filtering(repository, db_session, test_entity):
    """Test filtering entities by date range."""
    # Create date range for test
    start_date = ensure_utc(datetime(2025, 1, 1))
    end_date = ensure_utc(datetime(2025, 1, 31))
    
    # Use repository method with date range
    results = await repository.get_by_date_range(
        start_date=start_date,
        end_date=end_date
    )
    
    # When comparing dates, use datetime_equals with appropriate parameters
    for result in results:
        assert datetime_equals(result.created_at, start_date, greater_than=True)
        assert datetime_equals(result.created_at, end_date, less_than=True)
```

## Recent Improvements

All 1265 tests in the `/code/debtonator/tests/integration/repositories` directory are now passing. Recent improvements include:

1. **Fixed Account Schema Testing**
   - Corrected schema testing approach to align with polymorphic design
   - Enhanced type-specific validation testing
   - Added proper tests for discriminated unions

2. **Fixed UTC Datetime Handling**
   - Improved datetime handling in repository tests per ADR-011
   - Fixed timezone handling in date-based tests
   - Used proper utility functions like `ensure_utc` and `datetime_equals`

3. **Bill Splits Standardization**
   - Standardized on "liability_id" terminology throughout bill split code
   - Added transaction boundaries with proper rollback on errors
   - Implemented validation to prevent invalid split amounts
   - Added proper account validation and error handling

4. **Account Type Implementations**
   - Fixed polymorphic repository pattern implementation
   - Added specialized repository methods for each account type
   - Improved schema-model field alignment
   - Enhanced type-specific functionality testing
