# Banking Account Types Repository Fixtures

This directory contains fixture functions for creating banking account type repository instances used in testing the Debtonator application. These repositories follow the Repository Module Pattern and Polymorphic Repository Pattern defined in the system architecture.

## Related Documentation

- [Parent Repository Fixtures README](../../README.md)
- [Model Banking Account Types Fixtures](../../../../models/account_types/banking/README.md)
- [ADR-014: Repository Pattern](/code/debtonator/docs/adr/backend/ADR-014-repository-pattern.md)
- [ADR-016: Account Type Polymorphic Models](/code/debtonator/docs/adr/backend/ADR-016-account-type-polymorphic-models.md)
- [System Patterns: Repository Module Pattern](/code/debtonator/docs/system_patterns.md#repository-module-pattern)
- [System Patterns: Polymorphic Repository Pattern](/code/debtonator/docs/system_patterns.md#polymorphic-repository-pattern)

## Architecture

Banking account type repositories extend the base `AccountRepository` using the Repository Module Pattern. This pattern allows for specialized repository functionality to scale to multiple account types without creating unwieldy monolithic repositories.

```tree
AccountRepository (Base)
├── CheckingAccountRepository
├── SavingsAccountRepository
├── CreditAccountRepository
├── BNPLAccountRepository
├── EWAAccountRepository
└── PaymentAppAccountRepository
```

## Implementation Patterns

### Repository Module Pattern

The Repository Module Pattern organizes account type-specific repository operations into specialized modules:

```python
# Each module contains functions specific to a particular account type
# All functions take SQLAlchemy session as their first parameter

# Example from src/repositories/account_types/banking/checking.py
async def get_overdraft_status(session: AsyncSession, account_id: int) -> bool:
    """Get the overdraft status for a checking account."""
    stmt = select(CheckingAccount).where(CheckingAccount.id == account_id)
    result = await session.execute(stmt)
    account = result.scalars().first()
    
    if not account:
        raise AccountNotFoundError(account_id=account_id)
        
    return account.current_balance < Decimal("0.00")
```

### Polymorphic Repository Pattern

The Polymorphic Repository Pattern provides a specialized base repository for polymorphic entities:

```python
# The PolymorphicBaseRepository enforces proper type handling
checking_account = await account_repository.create_typed_entity(
    "checking", account_data
)

# Direct creation without type is disabled
account = await account_repository.create(account_data)  # Raises NotImplementedError
```

## Available Fixtures

### fixture_checking_repositories.py

- **checking_account_repository**: Repository for checking account operations
- **checking_account_type_module**: Access to the checking account type module
- **checking_account_with_repository**: Combined fixture with both account and repository

### fixture_savings_repositories.py

- **savings_account_repository**: Repository for savings account operations
- **savings_account_type_module**: Access to the savings account type module
- **savings_account_with_repository**: Combined fixture with both account and repository

### fixture_credit_repositories.py

- **credit_account_repository**: Repository for credit account operations
- **credit_account_type_module**: Access to the credit account type module
- **credit_account_with_repository**: Combined fixture with both account and repository

### fixture_bnpl_repositories.py

- **bnpl_account_repository**: Repository for BNPL account operations
- **bnpl_account_type_module**: Access to the BNPL account type module
- **bnpl_account_with_repository**: Combined fixture with both account and repository

### fixture_ewa_repositories.py

- **ewa_account_repository**: Repository for EWA account operations
- **ewa_account_type_module**: Access to the EWA account type module
- **ewa_account_with_repository**: Combined fixture with both account and repository

### fixture_payment_app_repositories.py

- **payment_app_account_repository**: Repository for payment app account operations
- **payment_app_account_type_module**: Access to the payment app account type module
- **payment_app_account_with_repository**: Combined fixture with both account and repository

## Testing Strategy

These fixtures are designed to support testing that verifies:

1. **Type-Specific Operations**: Methods specific to each account type
2. **Polymorphic Repository Functions**: Proper enforcement of polymorphic identity
3. **Validation**: Correct validation for each account type
4. **Error Handling**: Proper error generation and translation
5. **Feature Flag Integration**: Conditional loading based on feature flags

## Best Practices

1. **Repository Factory Usage**: Use the repository factory to create repositories instead of direct instantiation
2. **Proper Transaction Handling**: Ensure transactions are properly managed with `async with` blocks
3. **Polymorphic Repository Methods**: Use `create_typed_entity` and `update_typed_entity` instead of base methods
4. **Real Database Sessions**: Always use real database sessions, not mocks
5. **Timezone Awareness**: Follow ADR-011 for datetime handling in repository tests

## Example Usage

```python
async def test_create_checking_account(checking_account_repository):
    """Test creating a checking account with the repository."""
    # Create account data
    account_data = {
        "name": "Test Checking",
        "available_balance": Decimal("1000.00"),
        "current_balance": Decimal("1000.00"),
        "overdraft_limit": Decimal("500.00"),
    }
    
    # Create account with typed entity method
    account = await checking_account_repository.create_typed_entity(
        "checking", account_data
    )
    
    # Verify account was created with correct type
    assert account is not None
    assert account.name == "Test Checking"
    assert account.account_type == "checking"
    assert account.overdraft_limit == Decimal("500.00")
```

## Known Considerations

1. **Repository Method Transition**: Methods have been renamed from `create/update_typed_account` to `create/update_typed_entity`
2. **Async Consistency**: All repository methods must be properly awaited
3. **Transaction Boundaries**: Repository operations should be wrapped in transactions
4. **UTC Datetime Compliance**: Always use naive datetimes for database queries as per ADR-011
5. **Field Preservation**: The polymorphic repository preserves optional fields with existing values during partial updates
