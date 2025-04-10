# Debtonator Test Suite

This directory contains tests for the Debtonator application. The test suite follows the "Real Objects Testing Philosophy" established in ADR-014, emphasizing integration testing with real components while maintaining proper layer isolation.

## Directory Structure

```
tests/
├── conftest.py             # Pytest configuration and shared fixtures
├── fixtures/               # Test fixtures for creating test instances
│   ├── models/             # SQLAlchemy model fixtures
│   ├── repositories/       # Repository fixtures
│   └── services/           # Service fixtures
├── helpers/                # Helper modules for testing
│   ├── models/             # Test-specific SQLAlchemy models
│   ├── schemas/            # Test-specific Pydantic schemas
│   └── schema_factories/   # Factory functions for creating schemas
├── unit/                   # Tests for single-layer components
│   ├── models/             # Tests for SQLAlchemy models
│   ├── schemas/            # Tests for Pydantic schemas
│   ├── errors/             # Tests for error classes
│   ├── registry/           # Tests for registry components
│   ├── utils/              # Tests for utility functions
│   └── helpers/            # Tests for test helpers
└── integration/            # Tests for multi-layer components
    ├── repositories/       # Tests for repository layer
    ├── services/           # Tests for service layer
    └── api/                # Tests for API endpoints
```

## Test Types

Debtonator has two main types of tests:

### Unit Tests

Unit tests focus on a single layer of the application:

- **Models**: Testing model properties, methods, and constraints
- **Schemas**: Testing schema validation and serialization
- **Utils**: Testing utility functions
- **Registry**: Testing registry components
- **Errors**: Testing error classes

Example unit test:
```python
def test_account_schema_validation():
    """Test validation in AccountCreate schema."""
    # Valid data should pass validation
    valid_data = {
        "name": "Test Account",
        "account_type": "checking",
        "available_balance": Decimal("1000.00"),
        "current_balance": Decimal("1000.00")
    }
    schema = AccountCreate(**valid_data)
    assert schema.name == "Test Account"
    
    # Invalid data should fail validation
    with pytest.raises(ValidationError):
        AccountCreate(name="", account_type="checking")  # Empty name
```

### Integration Tests

Integration tests focus on components that span multiple layers:

- **Repositories**: Testing data access patterns and database interactions
- **Services**: Testing business logic components that use repositories
- **API**: Testing API endpoints that use services

Example integration test:
```python
async def test_create_bill(bill_service, db_session):
    """Test creating a bill through the service layer."""
    # Create account for bill
    account = await create_test_checking_account(db_session)
    
    # Create bill data
    bill_data = {
        "name": "Test Bill",
        "amount": Decimal("100.00"),
        "due_day": 15,
        "primary_account_id": account.id
    }
    
    # Create bill through service
    bill = await bill_service.create_bill(bill_data)
    
    # Verify bill was created correctly
    assert bill.id is not None
    assert bill.name == "Test Bill"
    assert bill.amount == Decimal("100.00")
    assert bill.primary_account_id == account.id
```

## Testing Philosophy

Debtonator follows these core testing principles:

1. **No Mocks Policy**: We strictly prohibit using unittest.mock, MagicMock, or any mocking libraries
2. **Real Database Testing**: Tests use a real test database that gets set up/torn down between tests
3. **Cross-Layer Integration**: Tests verify real interactions between layers using actual objects
4. **Real Schemas**: All test data is validated through real Pydantic schemas
5. **UTC Datetime Compliance**: All datetime handling follows ADR-011

## Learn More

For detailed guidance on specific test types, see the README.md in each subdirectory:

- [Unit Tests](./unit/README.md)
- [Integration Tests](./integration/README.md)
- [Fixtures](./fixtures/README.md)
- [Helpers](./helpers/README.md)
