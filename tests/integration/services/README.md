# Integration Tests for Service Layer

## Purpose

This directory contains integration tests for the service layer components in Debtonator. These tests validate the business logic, repository integration, and service operations following the repository pattern defined in ADR-014.

## Related Documentation

- [Repository Integration Tests](../repositories/README.md)
- [Integration Tests Overview](../README.md)
- [ADR-014: Repository Layer Compliance](/code/debtonator/docs/adr/implementation/adr014-implementation-checklist.md)

## Child Documentation

- [Account Types Services Tests](./account_types/banking/README.md)
- [Interceptors Tests](./interceptors/README.md)
- [Proxies Tests](./proxies/README.md)

## Architecture

Service layer integration tests validate that:

1. Services properly inherit from `BaseService`
2. Services use repositories through `_get_repository()` method
3. Business logic is correctly implemented
4. Services handle errors appropriately
5. Transaction boundaries are properly managed
6. Services follow UTC datetime compliance

## Implementation Patterns

### Service Construction Pattern

All services under test should follow the BaseService implementation pattern:

```python
import pytest_asyncio
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.accounts import AccountService
from tests.fixtures.models.account_types.banking.fixture_checking import create_test_checking_account

@pytest_asyncio.fixture
async def account_service(db_session: AsyncSession):
    """Create an account service for testing."""
    # Services now accept session directly, not repositories
    return AccountService(
        session=db_session,
        # Optional: feature_flag_service can be passed for specific tests
        # Optional: config_provider can be passed for specific tests
    )
```

Note that we no longer pass repositories to services - the services use `_get_repository()` internally.

### The Four-Step Test Pattern

Service tests should follow this four-step pattern:

#### 1. Arrange: Set up test data and dependencies

```python
# Create test data for the operation
checking_account = await create_test_checking_account(db_session)
```

#### 2. Schema: Create and validate data through schema factories

```python
# Create and validate through schema factory
bill_schema = create_bill_schema(
    name="Test Bill",
    amount=Decimal("100.00"),
    primary_account_id=checking_account.id
)
```

#### 3. Act: Pass validated data to service methods

```python
# Convert validated schema to dict for service
validated_data = bill_schema.model_dump()

# Pass validated data to service
result = await bill_service.create_bill(validated_data)
```

#### 4. Assert: Verify the service operation results

```python
# Verify the operation results
assert result is not None
assert result.id is not None
assert result.name == "Test Bill"
assert result.amount == Decimal("100.00")
```

## Testing Focus Areas

### Business Logic

Test that business logic is correctly implemented:

```python
async def test_account_service_calculate_total_balance(account_service, db_session):
    """Test total balance calculation business logic."""
    # Create test accounts
    checking = await create_test_checking_account(
        db_session, 
        available_balance=Decimal("1000.00")
    )
    savings = await create_test_savings_account(
        db_session, 
        available_balance=Decimal("2000.00")
    )
    
    # Test business logic
    total_balance = await account_service.calculate_total_balance()
    
    # Verify calculation is correct
    assert total_balance == Decimal("3000.00")
```

### Repository Layer Integration

Test that services use repositories correctly through the `_get_repository()` method:

```python
async def test_account_service_find_accounts_by_type(account_service, db_session):
    """Test finding accounts by type using repository layer."""
    # Create test accounts
    checking1 = await create_test_checking_account(db_session, name="Checking 1")
    checking2 = await create_test_checking_account(db_session, name="Checking 2")
    savings = await create_test_savings_account(db_session, name="Savings")
    
    # Test repository integration
    checking_accounts = await account_service.find_accounts_by_type("checking")
    
    assert len(checking_accounts) == 2
    account_names = [a.name for a in checking_accounts]
    assert "Checking 1" in account_names
    assert "Checking 2" in account_names
```

### Error Handling

Test error handling in services:

```python
async def test_account_service_error_handling(account_service):
    """Test handling of non-existent account."""
    # Test with non-existent ID
    from src.errors.account_errors import AccountNotFoundError
    
    with pytest.raises(AccountNotFoundError) as excinfo:
        await account_service.get_account_by_id(999999)
    
    # Error should include ID
    assert "999999" in str(excinfo.value)
```

### Transaction Boundaries

Test proper transaction handling:

```python
async def test_transaction_boundary_handling(bill_service, db_session):
    """Test transaction rollback on validation failure."""
    # Create test data with invalid values that should trigger validation error
    try:
        await bill_service.create_bill_with_splits({
            "name": "Test Bill",
            "amount": Decimal("100.00"),
            "due_date": datetime.now(),
            "splits": [
                {"account_id": 999999, "amount": Decimal("50.00")},  # Invalid account ID
                {"account_id": 999998, "amount": Decimal("50.00")}   # Another invalid ID
            ]
        })
        assert False, "Expected validation error was not raised"
    except ValidationError:
        # Transaction should have been rolled back
        # Verify bill was not created in the database
        stmt = select(Bill).where(Bill.name == "Test Bill")
        result = await db_session.execute(stmt)
        assert result.scalar_one_or_none() is None
```

### Polymorphic Type Handling

Test polymorphic type handling in services:

```python
async def test_polymorphic_type_services(account_service, db_session):
    """Test service operations with polymorphic account types."""
    # Create account schema for checking account
    checking_schema = create_checking_account_schema(
        name="Primary Checking",
        current_balance=Decimal("1000.00")
    )
    
    # Create checking account through service
    checking_account = await account_service.create_account(
        account_type="checking",
        account_data=checking_schema.model_dump()
    )
    
    # Verify account was created with correct type
    assert checking_account.account_type == "checking"
    assert isinstance(checking_account, CheckingAccount)
```

## UTC Datetime Compliance

All tests involving datetimes must follow the patterns established in ADR-011:

```python
from src.utils.datetime_utils import ensure_utc, datetime_equals, utc_now

@pytest.mark.asyncio
async def test_date_range_filtering(bill_service, db_session):
    """Test filtering bills by date range."""
    # Create date range for test
    start_date = ensure_utc(datetime(2025, 1, 1))
    end_date = ensure_utc(datetime(2025, 1, 31))
    
    # Use service method with date range
    bills = await bill_service.get_bills_due_in_range(
        start_date=start_date,
        end_date=end_date
    )
    
    # When comparing dates, use datetime_equals with appropriate parameters
    for bill in bills:
        assert datetime_equals(bill.due_date, start_date, greater_than_or_equal=True)
        assert datetime_equals(bill.due_date, end_date, less_than_or_equal=True)
```

## Testing Guidelines

All service tests must follow these guidelines:

1. **Write Function-Style Tests**: Write all tests in function style with descriptive docstrings
2. **Use Registered Fixtures**: Never define fixtures in test files - use fixtures that are registered in conftest.py
3. **Follow Four-Step Pattern**: Arrange, Schema, Act, Assert pattern for all tests
4. **Provide Clear Docstrings**: Every test should have a clear descriptive docstring
5. **One Assertion Focus**: Each test should focus on verifying one specific behavior
6. **Descriptive Test Names**: Name tests with pattern `test_[service]_[functionality]`

When testing services:

1. Use registered fixtures for services (via conftest.py, not direct imports)
2. Test service-specific operations and business rules 
3. Verify proper repository integration (standard or polymorphic)
4. Test error handling for validation rules
5. Verify inheritance from BaseService
6. Test cross-service integration where appropriate

## Best Practices

1. **Use Function-Style Tests**: All tests should be function-style and not class-style

   ```python
   # CORRECT: Function-style test
   @pytest.mark.asyncio
   async def test_some_service_functionality(db_session, some_service):
       """Test some service functionality with clear docstring."""
       # Test implementation...
       
   # INCORRECT: Class-style test
   class TestSomeService:
       @pytest.mark.asyncio
       async def test_some_functionality(self, db_session, some_service):
           # Test implementation...
   ```

2. **Use Registered Fixtures**: No fixtures should be defined in the test files
   - Use fixtures that are registered in conftest.py
   - These fixtures are automatically available throughout the test suite
   - If needed, add new fixtures to appropriate fixture files in tests/fixtures/
   - See README.md files in the fixtures directories for patterns
   - Example:

   ```python
   # CORRECT: Use pytest fixtures that are automatically available
   @pytest.mark.asyncio
   async def test_account_service_operations(db_session, account_service):
       """Test account service operations using registered fixtures."""
       # Test implementation using account_service fixture
       
   # INCORRECT: Defining fixtures in test files
   @pytest_asyncio.fixture
   async def account_service(db_session):
       return AccountService(session=db_session)
   ```

3. **Use Real Objects**: Follow the "No Mocks Policy" by using real models, repositories, and services
4. **Test Business Rules**: Focus on testing business rules and service-specific logic
5. **Test Error Handling**: Verify that services handle errors appropriately
6. **Test Transaction Boundaries**: Verify that transactions are properly managed
7. **Follow UTC Datetime Compliance**: Use proper timezone-aware datetime functions
8. **Test BaseService Integration**: Verify services properly inherit from BaseService and use _get_repository()

## Test Directory Structure

Tests are organized to mirror the structure of the `src/services` directory:

```tree
services/
├── account_types/               # Account type-specific service tests
│   └── banking/                 # Banking account types service tests
│       ├── README.md            # Banking service tests documentation
│       ├── test_bnpl_service.py
│       └── test_checking_service.py
├── interceptors/                # Service interceptor tests
│   └── test_feature_flag_interceptor.py
├── proxies/                     # Repository proxy tests
│   └── test_feature_flag_proxy.py
├── README.md                    # This file
├── test_account_service.py      # Core account service tests
├── test_balance_history_services.py
├── test_bill_splits_services.py
├── test_cashflow_services.py
└── ... (other service tests)
```

## Recent Improvements

The services layer has been fully refactored to comply with ADR-014 Repository Layer standards:

1. **BaseService Implementation**
   - All services now inherit from BaseService
   - Services use _get_repository() for standardized repository access
   - Clear distinction between standard and polymorphic repositories
   - Lazy loading and caching of repositories

2. **Repository Access Pattern**
   - No direct database access in services
   - Standard repositories accessed directly through BaseService._get_repository()
   - Polymorphic repositories accessed with polymorphic_type parameter
   - Consistent repository access pattern across all services

3. **Proper DateTime Handling**
   - Services use datetime utility functions from src/utils/datetime_utils.py
   - Timezone-aware datetime handling for API boundaries
   - Naive datetime handling for database operations
   - Consistent patterns for date range filtering and comparisons
