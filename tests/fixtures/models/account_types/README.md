# Account Types Model Fixtures

This directory contains fixture functions for creating test instances of different account type models, organized by account category. The fixtures follow the polymorphic inheritance patterns defined in ADR-016 and the system architecture.

## Related Documentation

- [Parent Models Fixtures README](../README.md)
- [Repository Account Types Fixtures](../../../repositories/account_types/README.md)
- [ADR-016: Account Type Polymorphic Models](/code/debtonator/docs/adr/backend/ADR-016-account-type-polymorphic-models.md)

## Architecture

The account type model fixtures mirror the polymorphic hierarchy of the account models in the application:

```tree
Account (Base Class)
├── BankingAccount (Abstract)
│   ├── CheckingAccount
│   ├── SavingsAccount
│   └── CreditAccount
│   └── BNPLAccount
│   └── EWAAccount
│   └── PaymentAppAccount
├── InvestmentAccount (Abstract)
│   ├── BrokerageAccount
│   ├── RetirementAccount
│   └── ...
├── LoanAccount (Abstract)
│   ├── MortgageAccount
│   ├── AutoLoanAccount
│   └── ...
└── ...
```

## Implementation Patterns

All fixtures in this directory and its subdirectories follow these key patterns:

### Polymorphic Instantiation

Always use concrete subclasses that match the intended polymorphic type:

```python
# ✅ Correct: Use concrete subclass constructor
checking = CheckingAccount(name="Primary Checking", ...)

# ❌ Incorrect: Setting type on base class
account = Account(name="Primary Checking", account_type="checking", ...)
```

### Category Organization

Account types are organized by category subdirectories:

- `banking/`: Traditional and modern banking account types
- `investment/`: Investment and brokerage account types (future)
- `loan/`: Loan and credit account types (future)

### Model Fixture Structure

Each model fixture follows a consistent pattern:

```python
@pytest_asyncio.fixture
async def test_account_name(db_session: AsyncSession) -> ConcreteAccountType:
    """Clear docstring describing the account configuration."""
    account = ConcreteAccountType(
        name="Descriptive Name",
        # Type-specific fields...
        created_at=naive_utc_now(),
        updated_at=naive_utc_now()
    )
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)
    return account
```

## Available Subdirectories

### Banking Account Types (`banking/`)

Contains fixtures for various banking account types:

- Checking accounts
- Savings accounts
- Credit accounts
- Buy-now-pay-later (BNPL) accounts
- Early wage access (EWA) accounts
- Payment app accounts

See [Banking Account Types README](banking/README.md) for details.

### Investment Account Types (`investment/`)

This directory will contain fixtures for investment account types (future):

- Brokerage accounts
- Retirement accounts
- Education savings accounts
- Trading accounts

### Loan Account Types (`loan/`)

This directory will contain fixtures for loan account types (future):

- Mortgage accounts
- Auto loan accounts
- Personal loan accounts
- Student loan accounts

## Testing Strategy

These fixtures are designed to support testing that verifies:

1. **Polymorphic Functionality**: Proper instantiation and type handling
2. **Inheritance Behavior**: Correct field inheritance and overrides
3. **Type-Specific Validation**: Proper validation for specialized fields
4. **Relationships**: Correct loading of type-specific relationships
5. **Database Operations**: Proper persistence and retrieval of polymorphic entities

## Best Practices

1. **Explicit Type Handling**: Always use concrete subclasses for instantiation
2. **Consistent Naming**: Use descriptive fixture names that indicate the account type and configuration
3. **Comprehensive Docstrings**: Include clear docstrings for all fixtures
4. **Minimal Dependencies**: Keep fixture dependencies to a minimum
5. **UTC Compliance**: Follow ADR-011 for datetime handling
6. **Proper Field Types**: Use Decimal for all monetary values
7. **Clear Categories**: Organize fixtures by account category
