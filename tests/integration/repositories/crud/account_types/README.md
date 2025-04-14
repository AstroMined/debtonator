# Account Types CRUD Tests

## Purpose

This directory contains CRUD (Create, Read, Update, Delete) tests for Debtonator's polymorphic account type repositories. These tests validate the implementation of the Polymorphic Repository Pattern across different account type categories.

## Related Documentation

- [Parent: CRUD Repository Tests](/code/debtonator/tests/integration/repositories/crud/README.md)
- [Banking Account Types Tests](./banking/README.md)
- [System Patterns: Polymorphic Repository Pattern](/code/debtonator/docs/system_patterns.md#polymorphic-repository-pattern)

## Architecture

Account types in Debtonator follow a polymorphic design pattern where specialized account types inherit from a base Account model and are stored in a single table with a discriminator field. The repositories implement the Polymorphic Repository Pattern to enforce proper type handling and identity management.

The account type hierarchy is organized by category:

```tree
Account (Base)
├── Banking Accounts
│   ├── CheckingAccount
│   ├── SavingsAccount
│   └── CreditAccount
├── Modern Financial Accounts
│   ├── BNPLAccount (Buy Now, Pay Later)
│   ├── EWAAccount (Earned Wage Access)
│   └── PaymentAppAccount
└── Investment Accounts (future)
```

## Implementation Patterns

### Polymorphic Type Creation Pattern

When testing account type creation, always use the type-specific schema factory and the `create_typed_entity` method:

```python
# Create schema for specific account type
account_schema = create_checking_account_schema(
    name="Primary Checking",
    current_balance=Decimal("1000.00"),
    available_balance=Decimal("1000.00")
)

# Convert to dict for repository
account_data = account_schema.model_dump()

# Use typed entity creation
account = await account_repository.create_typed_entity("checking", account_data)
```

### Polymorphic Type Update Pattern

When testing account type updates, use the type-specific update schema and the `update_typed_entity` method:

```python
# Create schema for account type update
update_schema = create_checking_account_update_schema(
    name="Renamed Checking",
    available_balance=Decimal("1500.00")
)

# Convert to dict for repository
update_data = update_schema.model_dump()

# Use typed entity update
updated = await account_repository.update_typed_entity(
    entity_id=account.id,
    entity_type="checking",
    data=update_data
)
```

## Key Responsibilities

- Test CRUD operations for all account types
- Validate proper polymorphic type handling
- Ensure field validation through type-specific schemas
- Verify type-specific properties and behaviors
- Test proper inheritance and discriminator field handling

## Testing Strategy

- Organize tests by account category
- Use the appropriate schema factory for each account type
- Always use `create_typed_entity` and `update_typed_entity` methods
- Verify type-specific fields are properly stored and retrieved
- Test both full and partial updates to ensure field preservation

## Known Considerations

- Polymorphic repositories disable base `create` and `update` methods
- Direct use of disabled methods raises `NotImplementedError`
- Each account type has unique required fields
- Update operations should preserve fields not explicitly changed
- Account types require consistent implementation of the discriminator field
- Schema factories should match the corresponding account type class
