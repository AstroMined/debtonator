# Unit Tests

This directory contains unit tests for individual components of the Debtonator application. These tests follow the "Real Objects Testing Philosophy" established in ADR-014, emphasizing integration testing with real components while maintaining proper layer isolation.

## Purpose

The unit tests in this directory serve to:

1. **Verify Component Behavior**: Test that individual components work correctly in isolation
2. **Validate Layer Boundaries**: Ensure components respect their layer boundaries
3. **Document Usage Patterns**: Demonstrate how components should be used
4. **Test Edge Cases**: Verify components handle exceptional conditions properly
5. **Enforce Type Safety**: Validate type safety across the application

## Strict No-Mocks Policy

As mandated by ADR-014, Debtonator follows a strict **no-mocks policy**:

- **❌ PROHIBITED**: `unittest.mock`, `MagicMock`, or any other mocking libraries
- **✅ REQUIRED**: Real database sessions, repositories, and models in all tests
- **✅ REQUIRED**: Real validation logic and real Pydantic schemas
- **✅ REQUIRED**: Integration-first approach with proper isolation

This policy ensures tests validate actual behavior rather than simulated expectations.

## Directory Structure

The unit test directory structure mirrors the source code directory structure:

```
unit/
├── __init__.py
├── core/              (Tests for core functionality)
│   ├── __init__.py
│   ├── test_config.py
│   └── test_constants.py
├── errors/            (Tests for error handling and custom exceptions)
│   ├── __init__.py
│   ├── test_account_errors.py
│   └── test_bill_errors.py
├── helpers/           (Tests for test helper functions)
│   ├── __init__.py
│   ├── models/
│   ├── schemas/
│   └── schema_factories/
├── models/            (Tests for SQLAlchemy models)
│   ├── __init__.py
│   ├── test_accounts.py
│   ├── test_bills.py
│   └── account_types/
│       ├── banking/
│       │   ├── test_checking.py
│       │   ├── test_credit.py
│       │   └── ...
├── registry/          (Tests for registry functionality)
│   ├── __init__.py
│   └── test_account_type_registry.py
├── schemas/           (Tests for Pydantic schemas)
│   ├── __init__.py
│   ├── test_accounts.py
│   └── account_types/
│       ├── banking/
│       │   ├── test_checking.py
│       │   └── ...
├── services/          (Tests for service layer components)
│   ├── __init__.py
│   ├── test_account_service.py
│   └── ...
└── utils/             (Tests for utility functions)
    ├── __init__.py
    ├── test_datetime_utils.py
    └── test_decimal_precision.py
```

## Test Categorization

Debtonator divides tests into three categories:

1. **Unit Tests**: Focus on a single component within a single layer
   - Example: Testing a model's properties, a schema's validation, or a utility function
   - Location: `tests/unit/*`

2. **Integration Tests**: Test interactions between multiple components or layers
   - Example: Testing a service with real repositories and database
   - Location: `tests/integration/*`

3. **Functional Tests**: Test complete features from API to database
   - Example: Testing the entire bill splitting flow
   - Location: `tests/functional/*`

## Layer Separation in Unit Tests

Unit tests should respect layer boundaries:

- **Model Tests**: Test only model behavior (relationships, constraints, properties, etc.)
- **Schema Tests**: Test schema validation and conversion logic
- **Repository Tests**: Test data access patterns without invoking service-layer logic
- **Service Tests**: Test business logic with real repositories
- **Utility Tests**: Test utility functions without complex dependencies

Unit tests should not cross application layers. For example, model unit tests should not test service layer behavior.

## Unit Test Principles

### 1. Focus on a Single Layer

Unit tests should focus on testing a single layer of the application. While we use real objects for testing (not mocks), unit tests should validate that a specific component works correctly in isolation.

### 2. Test with Real Objects

Following ADR-014, we use real objects instead of mocks:

- Test models with a real database session
- Test repositories with real models and database
- Test schemas with real validation logic
- Test services with real repositories

### 3. Proper Test Isolation

Despite using real objects, tests should maintain proper isolation:

- Each test should create its own test data
- Tests should not depend on data created by other tests
- Use the `db_session` fixture which provides a fresh database for each test

### 4. Clear Naming Convention

Tests should follow a consistent naming pattern:

- Test functions should start with `test_`
- Names should clearly describe what is being tested
- Include the expected outcome in the name
- Example: `test_checking_account_withdrawal_with_insufficient_funds_raises_error`

### 5. Arrange-Act-Assert Pattern

Tests should follow the "Arrange-Act-Assert" pattern:

```python
# Arrange - set up the test conditions
checking_account = CheckingAccount(
    name="Test Account", 
    available_balance=Decimal("100.00"),
    current_balance=Decimal("100.00"),
    overdraft_limit=Decimal("0.00")
)
db_session.add(checking_account)
await db_session.flush()

# Act - perform the action being tested
with pytest.raises(InsufficientFundsError) as excinfo:
    checking_account.withdraw(Decimal("150.00"))  # Exceeds available balance

# Assert - check the results
assert "insufficient funds" in str(excinfo.value).lower()
assert checking_account.available_balance == Decimal("100.00")  # Unchanged
```

### 6. Test Financial Operations with Precision

For financial operations, always test with exact Decimal values:

```python
# Test precise financial calculations
assert account.calculate_interest(Decimal("0.05")) == Decimal("50.00")
```

### 7. Test Bill Split Functionality Thoroughly

Bill splitting is a central feature of Debtonator and needs thorough testing:

```python
# Test bill split validation
bill = Bill(
    name="Utilities",
    amount=Decimal("100.00"),
    primary_account_id=checking.id
)
db_session.add(bill)
await db_session.flush()

split1 = BillSplit(
    bill_id=bill.id,
    account_id=savings.id,
    amount=Decimal("60.00")
)
db_session.add(split1)
await db_session.flush()

# Primary split should be automatically created for remainder
from sqlalchemy import select
stmt = select(BillSplit).where(
    (BillSplit.bill_id == bill.id) & 
    (BillSplit.account_id == checking.id)
)
result = await db_session.execute(stmt)
primary_split = result.scalars().first()

assert primary_split is not None
assert primary_split.amount == Decimal("40.00")  # 100 - 60
```

### 8. Test in UTC Timezone (ADR-011)

All datetime tests should use timezone-aware UTC datetimes:

```python
from src.utils.datetime_utils import naive_utc_now, utc_now

# Use naive_utc_now() for database operations
model = StatementHistory(
    account_id=account.id,
    statement_date=naive_utc_now(),
    statement_balance=Decimal("500.00")
)

# Use utc_now() for timezone-aware business logic
assert model.is_current_statement(utc_now())
```

## Test Coverage Targets

For Debtonator, we aim for the following coverage metrics:

- **Line Coverage**: 95%+ for critical modules (financial calculations, bill split logic)
- **Line Coverage**: 90%+ for all other modules
- **Branch Coverage**: 90%+ for critical modules
- **Branch Coverage**: 85%+ for all other modules
- **Function Coverage**: 100% for all public APIs
- **Overall Project Coverage**: Minimum 90%

### Review Coverage Reports

Run the coverage report regularly:

```bash
# Generate coverage report
pytest --cov=src --cov-report=html tests/

# Open HTML report
open htmlcov/index.html
```

## Performance Considerations

Debtonator unit tests should run quickly to facilitate rapid development:

- **Test Execution Time**: Unit tests should complete in < 5 minutes
- **Individual Test Time**: Each unit test should run in < 1 second
- **Database Setup**: Use in-memory SQLite for fastest performance
- **Efficient Test Data**: Create only the data needed for each test

### Debugging Test Failures

When tests fail, follow these debugging steps:

1. **Check Test Output**: Review the test error message and traceback
2. **Examine Test Database**: Use the `--keep-db` flag to retain the test database
3. **Add Debug Logging**: Use `caplog` fixture to capture logs
4. **Run Single Test**: Use `pytest tests/path/to/test.py::test_name -v`
5. **Use PDB**: Add `import pdb; pdb.set_trace()` for interactive debugging

## Fixture Usage Guidelines

Decide between fixtures and in-test creation:

- **Use Fixtures For**:
  - Common test database setup
  - Reusable model instances
  - Service and repository instances

- **Create In-Test For**:
  - Test-specific model instances
  - Instances that will be modified
  - Special case testing data

## Parameterized Tests

Use pytest's parameterize for testing multiple related scenarios:

```python
@pytest.mark.parametrize(
    "initial_balance,withdrawal,expected_balance,expected_error", [
        (Decimal("100.00"), Decimal("50.00"), Decimal("50.00"), None),
        (Decimal("100.00"), Decimal("100.00"), Decimal("0.00"), None),
        (Decimal("100.00"), Decimal("150.00"), Decimal("100.00"), InsufficientFundsError),
        (Decimal("100.00"), Decimal("-50.00"), Decimal("100.00"), ValueError),
    ]
)
async def test_checking_account_withdrawal(
    db_session, initial_balance, withdrawal, expected_balance, expected_error
):
    """Test checking account withdrawal with various scenarios."""
    account = CheckingAccount(
        name="Test Account", 
        available_balance=initial_balance,
        current_balance=initial_balance
    )
    db_session.add(account)
    await db_session.flush()
    
    if expected_error:
        with pytest.raises(expected_error):
            account.withdraw(withdrawal)
    else:
        account.withdraw(withdrawal)
        await db_session.flush()
        assert account.available_balance == expected_balance
```

## Integration with CI/CD

Unit tests are integrated into Debtonator's CI/CD pipeline:

- **Automatic Execution**: All unit tests run on every PR
- **Coverage Enforcement**: PRs with coverage drops are flagged
- **Fast Feedback**: Unit test failures block merging

## Common Anti-Patterns to Avoid

1. **Crossing Layer Boundaries**: Don't test service logic in model tests
2. **Using Mocks**: Don't use unittest.mock or similar mocking libraries
3. **Test Interdependence**: Don't create tests that depend on other tests
4. **Hardcoded IDs**: Don't use hardcoded IDs in tests
5. **Naive Datetimes**: Don't use naive datetime objects (per ADR-011)
6. **Direct Service-Database Interaction**: Services should use repositories, not direct DB access
7. **Complex Setup Code**: Keep test setup as simple as possible
8. **Testing Implementation Details**: Test behavior, not implementation
9. **Missing Edge Cases**: Don't forget to test boundary conditions
10. **Using Direct Queries**: Use repositories for data access

## Test Utilities and Helpers

The `tests/helpers` directory contains utilities to support unit testing:

- **Test Models**: Simplified SQLAlchemy models for testing base functionality
- **Test Schemas**: Specialized Pydantic schemas for testing validation flow
- **Schema Factories**: Functions for creating test data

## Environment Variables for Testing

Debtonator's test suite recognizes these environment variables:

- `DEBTONATOR_TEST_DB_URL`: Override the test database URL
- `DEBTONATOR_TEST_LOG_LEVEL`: Set logging level for tests
- `DEBTONATOR_TEST_KEEP_DB`: Keep test database after test run
- `DEBTONATOR_TEST_TIMEOUT`: Override default test timeout (seconds)

## Learn More

For detailed guidelines on writing tests for specific component types, refer to the README.md files in the subdirectories:
- [Model Tests](./models/README.md)
- [Schema Tests](./schemas/README.md)
- [Helper Tests](./helpers/README.md)
- [Registry Tests](./registry/README.md)
- [Service Tests](./services/README.md)
- [Utils Tests](./utils/README.md)
