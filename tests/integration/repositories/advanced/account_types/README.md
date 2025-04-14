# Account Types Advanced Tests

## Purpose

This directory contains advanced tests for Debtonator's polymorphic account type repositories. These tests validate specialized functionality, type-specific behaviors, and complex operations beyond basic CRUD operations.

## Related Documentation

- [Parent: Advanced Repository Tests](/code/debtonator/tests/integration/repositories/advanced/README.md)
- [Banking Account Types Tests](./banking/README.md)
- [System Patterns: Repository Module Pattern](/code/debtonator/docs/system_patterns.md#repository-module-pattern)

## Architecture

Debtonator implements the Repository Module Pattern for account types, where specialized repository functionality is organized by account type category in dedicated modules:

```tree
src/repositories/account_types/
├── banking/
│   ├── checking.py       # Checking account-specific repository operations
│   ├── savings.py        # Savings account-specific repository operations
│   └── credit.py         # Credit account-specific repository operations
└── modern/
    ├── bnpl.py           # Buy Now, Pay Later account-specific operations
    ├── ewa.py            # Earned Wage Access account-specific operations
    └── payment_app.py    # Payment app account-specific operations
```

This test directory validates that repository modules are correctly loaded and specialized methods work as expected.

## Implementation Patterns

### Type-Specific Method Testing Pattern

Tests should focus on specialized methods unique to each account type:

```python
@pytest.mark.asyncio
async def test_get_available_credit(account_repository, db_session, test_credit_account):
    """Test retrieving available credit for a credit account."""
    # Test implementation for a credit account-specific method
    available_credit = await account_repository.get_available_credit(test_credit_account.id)
    
    assert available_credit is not None
    assert isinstance(available_credit, Decimal)
    assert available_credit == test_credit_account.available_credit
```

### Dynamic Module Loading Testing Pattern

Tests should verify that repository factory correctly loads type-specific modules:

```python
@pytest.mark.asyncio
async def test_dynamic_module_loading(repository_factory, db_session):
    """Test that repository factory loads the correct module for each account type."""
    # Get repository instance for a specific account type
    credit_repo = repository_factory.get_repository(Account, db_session)
    
    # Verify credit-specific methods are available
    assert hasattr(credit_repo, "get_statement_balance")
    assert callable(credit_repo.get_statement_balance)
    
    # Verify methods from other account types are NOT available
    assert not hasattr(credit_repo, "get_interest_rate")  # Savings-specific method
```

## Key Responsibilities

- Test specialized methods for each account type
- Validate complex operations like balance calculations
- Test relationships with other entities (statements, transactions)
- Verify type-specific validation logic
- Test dynamic loading of repository modules

## Testing Strategy

- Group tests by account type category
- Test all specialized methods for each account type
- Verify error handling for type-specific operations
- Test edge cases and boundary conditions
- Test complex calculations with appropriate validation

## Known Considerations

- Methods vary significantly between account types
- Some methods require complex setup with multiple related entities
- Repository methods should validate input types
- Type-specific behaviors should be well-documented
- Date-sensitive operations should use proper datetime utilities
- Tests should verify error handling for operations on incorrect account types
