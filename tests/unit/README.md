# Unit Tests

This directory contains unit tests for individual components of the Debtonator application. The tests follow the "Real Objects Testing Philosophy" established in ADR-014, focusing on testing a single layer of the application.

## What is a Unit Test?

Unit tests in Debtonator verify the functionality of a **single layer** of the application in isolation. They ensure that components work correctly independently, while respecting layer boundaries.

The following components can be properly unit tested:
- **Models** (`models/`)
- **Schemas** (`schemas/`)
- **Errors** (`errors/`)
- **Registry** (`registry/`)
- **Utils** (`utils/`)
- **Helpers** (`helpers/`)

## Directory Structure

Each subdirectory follows the structure of the corresponding source code directory:

```
unit/
├── models/            # Tests for SQLAlchemy models
├── schemas/           # Tests for Pydantic schemas
├── errors/            # Tests for error classes
├── registry/          # Tests for registry components
├── utils/             # Tests for utility functions
└── helpers/           # Tests for test helpers
```

## Testing Principles

1. **Layer Isolation**: Each test should focus on a single layer without crossing boundaries
2. **Real Objects**: Use real objects rather than mocks (per ADR-014)
3. **Proper Coverage**: Test all public functionality and edge cases
4. **Clear Test Names**: Use descriptive, action-oriented test names
5. **UTC Datetime Compliance**: Follow ADR-011 for datetime handling

## Target Test Categories

The `unit/` directory should only contain tests that focus on a single layer:

```python
# EXAMPLE: Model unit test - tests only model behavior
async def test_checking_account_overdraft(db_session):
    """Test that checking account enforces overdraft limit."""
    account = CheckingAccount(
        name="Test Account",
        available_balance=Decimal("100.00"),
        current_balance=Decimal("100.00"),
        overdraft_limit=Decimal("50.00")
    )
    
    # Test model-level validation - this is appropriate for a unit test
    with pytest.raises(ValueError):
        account.withdraw(Decimal("151.00"))  # Exceeds available balance + overdraft
```

## When to Use Integration Tests Instead

If your test needs to span multiple layers or requires testing interactions between components, it should be placed in the `integration/` directory:

- Tests for **services**, **repositories**, and **API** layers should be integration tests, not unit tests
- Tests that verify cross-layer behavior belong in the integration directory
- Tests that require database setup with multiple interrelated entities

## Learn More

For detailed guidance on testing specific components, see the README.md in each subdirectory:

- [Model Tests](./models/README.md)
- [Schema Tests](./schemas/README.md)
- [Utils Tests](./utils/README.md)
- [Registry Tests](./registry/README.md)
- [Errors Tests](./errors/README.md)
- [Helper Tests](./helpers/README.md)
