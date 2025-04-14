# Banking Account Types CRUD Tests

## Purpose

This directory contains CRUD (Create, Read, Update, Delete) tests for Debtonator's banking account type repositories. These tests validate basic operations for specialized account types following the polymorphic repository pattern.

## Related Documentation

- [Parent: CRUD Repository Tests](/code/debtonator/tests/integration/repositories/crud/README.md)
- [Advanced Account Types Tests](/code/debtonator/tests/integration/repositories/advanced/account_types/banking/README.md)
- [System Patterns: Polymorphic Repository Pattern](/code/debtonator/docs/system_patterns.md#polymorphic-repository-pattern)

## Architecture

Banking account types follow a polymorphic design pattern where specialized account types inherit from a base Account model. The repositories implement the Polymorphic Repository Pattern that enforces proper type handling and identity management.

Account types tested in this directory include:

- **Checking Accounts**: Standard checking accounts
- **Savings Accounts**: Interest-bearing savings accounts
- **Credit Accounts**: Credit card and line of credit accounts
- **BNPL Accounts**: Buy Now, Pay Later accounts
- **EWA Accounts**: Earned Wage Access accounts
- **Payment App Accounts**: Payment application accounts

## Implementation Patterns

### Polymorphic Repository Operations Pattern

Unlike standard repositories, polymorphic repositories require specialized methods for entity creation and updates:

```python
# ✅ Correct: Using typed entity creation
account = await account_repository.create_typed_entity("checking", account_data)

# ❌ Incorrect: Using base create method (raises NotImplementedError)
account = await account_repository.create(account_data)
```

### Typed Account Test Pattern

Tests for polymorphic entities should use the appropriate schema factory for the specific account type:

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

### Type-Specific Validation Pattern

Each account type has its own validation rules that should be tested:

```python
# Testing validation for credit account
credit_schema = create_credit_account_schema(
    name="Primary Credit Card",
    current_balance=Decimal("500.00"),
    credit_limit=Decimal("2000.00"),
    available_credit=Decimal("1500.00"),
    last_statement_balance=Decimal("400.00")
)
```

## Key Responsibilities

- Test CRUD operations for each banking account type
- Validate proper polymorphic type handling
- Ensure proper field validation through schemas
- Test type-specific field requirements
- Verify polymorphic identity management

## Testing Strategy

- Use the appropriate schema factory for each account type
- Always use `create_typed_entity` and `update_typed_entity` methods
- Test each account type in a dedicated test file
- Verify type-specific fields are properly stored and retrieved
- Test validation for required type-specific fields

## Known Considerations

- Polymorphic repositories disable base `create` and `update` methods
- Each account type has its own unique set of required fields
- Update operations should test both full updates and partial updates
- Schema factories should be used to validate input data before repository operations
- Testing partial updates should verify other fields remain unchanged
- Account types require consistent implementation of the `account_type` discriminator field
