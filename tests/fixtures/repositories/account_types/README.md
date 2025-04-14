# Account Types Repository Fixtures

This directory contains fixture functions for creating account type repository instances used in testing the Debtonator application. These repositories follow the Repository Module Pattern and Polymorphic Repository Pattern defined in the system architecture.

## Related Documentation

- [Parent Repository Fixtures README](../README.md)
- [Model Account Types Fixtures](../../models/account_types/README.md)
- [ADR-014: Repository Pattern](/code/debtonator/docs/adr/backend/ADR-014-repository-pattern.md)
- [ADR-016: Account Type Polymorphic Models](/code/debtonator/docs/adr/backend/ADR-016-account-type-polymorphic-models.md)
- [System Patterns: Repository Module Pattern](/code/debtonator/docs/system_patterns.md#repository-module-pattern)
- [System Patterns: Polymorphic Repository Pattern](/code/debtonator/docs/system_patterns.md#polymorphic-repository-pattern)

## Architecture

The account type repository fixtures mirror the polymorphic structure of account types in the application:

```tree
AccountRepository (Base, Polymorphic)
├── BankingAccountRepository (Abstract)
│   ├── CheckingAccountRepository
│   ├── SavingsAccountRepository
│   ├── CreditAccountRepository
│   ├── BNPLAccountRepository
│   ├── EWAAccountRepository
│   └── PaymentAppAccountRepository
├── InvestmentAccountRepository (Abstract)
│   ├── BrokerageAccountRepository
│   ├── RetirementAccountRepository
│   └── ...
├── LoanAccountRepository (Abstract)
│   ├── MortgageAccountRepository
│   ├── AutoLoanAccountRepository
│   └── ...
└── ...
```

## Implementation Patterns

### Repository Module Pattern

The Repository Module Pattern allows for specialized repository functionality to scale to numerous account types without creating unwieldy monolithic repositories:

- **Module Organization**: Account type-specific repository operations are organized into specialized modules
- **Dynamic Loading**: Repository factory dynamically loads the correct module based on account type
- **Registry Integration**: AccountTypeRegistry maps account types to their repository modules
- **Feature Flag Integration**: Repository modules can be enabled/disabled through feature flags

### Polymorphic Repository Pattern

The Polymorphic Repository Pattern provides a specialized base repository for polymorphic entities:

1. **Enforced Polymorphic Identity**:
   - Base `create` and `update` methods are disabled
   - Only type-specific creation and updates are allowed through specialized methods
   - Examples:

   ```python
   # ✅ Correct: Using typed entity creation
   account = await account_repository.create_typed_entity("checking", account_data)
   
   # ❌ Incorrect: Using base create method (raises NotImplementedError)
   account = await account_repository.create(account_data)
   ```

2. **Field Validation and Filtering**:
   - Automatically filters input data to include only valid fields for the specific model class
   - Prevents setting invalid fields that don't exist on the model
   - Preserves required fields during updates
   - Ensures discriminator field is always set correctly

## Available Subdirectories

### Banking Account Types (`banking/`)

Contains repository fixtures for banking account types:

- Checking accounts
- Savings accounts
- Credit accounts
- BNPL accounts
- EWA accounts
- Payment app accounts

See [Banking Account Types README](banking/README.md) for details.

### Investment Account Types (`investment/`)

This directory will contain repository fixtures for investment account types (future):

- Brokerage accounts
- Retirement accounts
- Education savings accounts
- Trading accounts

### Loan Account Types (`loan/`)

This directory will contain repository fixtures for loan account types (future):

- Mortgage accounts
- Auto loan accounts
- Personal loan accounts
- Student loan accounts

## Testing Strategy

The repository fixtures in this directory and its subdirectories support testing:

1. **Polymorphic Repository Operations**: Create, update, delete operations with proper type handling
2. **Type-Specific Methods**: Specialized methods for each account type
3. **Field Validation**: Correct field validation and filtering based on account type
4. **Error Handling**: Proper error generation for invalid operations
5. **Feature Flag Integration**: Conditional repository functionality based on feature flags

## Best Practices

1. **Factory Usage**: Use repository factory to create type-specific repositories
2. **Typed Entity Methods**: Use `create_typed_entity` and `update_typed_entity` for polymorphic operations
3. **Transaction Boundaries**: Use transactions for all repository operations
4. **UTC Compliance**: Follow ADR-011 for datetime handling in database operations
5. **Error Handling**: Catch and translate repository errors appropriately
6. **Integration-First Approach**: Test with real database sessions instead of mocks
7. **Complete Repository Tests**: Test CRUD operations, specialized methods, and error cases

## Example Repository Fixture

```python
@pytest_asyncio.fixture
async def checking_account_repository(
    db_session: AsyncSession
) -> AsyncGenerator[CheckingAccountRepository, None]:
    """
    Create a CheckingAccountRepository instance for testing.
    
    This fixture provides a repository for checking account operations.
    """
    from src.repositories.account_types.banking.checking import CheckingAccountRepository
    
    repository = CheckingAccountRepository(db_session)
    yield repository
    # No cleanup needed as db_session handles this
```

## Example Repository Factory Fixture

```python
@pytest_asyncio.fixture
async def account_repository_factory(
    db_session: AsyncSession
) -> AsyncGenerator[AccountRepositoryFactory, None]:
    """
    Create an AccountRepositoryFactory instance for testing.
    
    This fixture provides a factory that can create repositories for
    any account type based on the polymorphic identity.
    """
    from src.repositories.factory import AccountRepositoryFactory
    
    factory = AccountRepositoryFactory(db_session)
    yield factory
    # No cleanup needed as db_session handles this
```
