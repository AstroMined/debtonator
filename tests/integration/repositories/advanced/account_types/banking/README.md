# Banking Account Types Advanced Tests

## Purpose

This directory contains advanced tests for Debtonator's banking account type repositories. These tests validate specialized methods, type-specific behaviors, and complex operations beyond basic CRUD functionality.

## Related Documentation

- [Parent: Advanced Repository Tests](/code/debtonator/tests/integration/repositories/advanced/README.md)
- [Banking Account Types CRUD Tests](/code/debtonator/tests/integration/repositories/crud/account_types/banking/README.md)
- [System Patterns: Repository Module Pattern](/code/debtonator/docs/system_patterns.md#repository-module-pattern)

## Architecture

Banking account types use the Repository Module Pattern where specialized repository functionality is organized into modules. Each account type has type-specific methods that are dynamically loaded based on account type.

This test directory validates the specialized methods for each banking account type:

- **Checking Accounts**: Overdraft handling, transaction processing
- **Savings Accounts**: Interest calculations, minimum balance enforcement
- **Credit Accounts**: Available credit calculations, statement management, utilization metrics
- **BNPL Accounts**: Payment plans, installment tracking, status transitions
- **EWA Accounts**: Access limit calculations, repayment tracking
- **Payment App Accounts**: Transfer limits, linked account management

## Implementation Patterns

### Type-Specific Method Testing Pattern

Tests for specialized account type methods should focus on the unique behaviors for each type:

```python
@pytest.mark.asyncio
async def test_get_credit_utilization(account_repository, db_session, test_credit_account):
    """Test retrieving credit utilization percentage for a credit account."""
    # Test implementation for credit account-specific method
    utilization = await account_repository.get_credit_utilization(test_credit_account.id)
    assert isinstance(utilization, Decimal)
    assert utilization >= Decimal('0.0') and utilization <= Decimal('1.0')
```

### Repository Module Registry Testing

Tests should verify that type-specific methods are properly registered and accessible:

```python
@pytest.mark.asyncio
async def test_type_specific_method_availability(repository_factory, db_session):
    """Test that type-specific methods are available for the appropriate account types."""
    # Get repository for checking accounts
    checking_repo = repository_factory.get_repository(Account, db_session)
    
    # Verify checking-specific methods are available
    assert hasattr(checking_repo, "get_overdraft_history")
    
    # Verify credit-specific methods are NOT available on checking repo
    assert not hasattr(checking_repo, "get_credit_utilization")
```

### Account Lifecycle Testing Pattern

For account types with lifecycle states (like BNPL accounts), test state transitions:

```python
@pytest.mark.asyncio
async def test_bnpl_account_lifecycle(account_repository, db_session, test_bnpl_account):
    """Test the lifecycle transitions of a BNPL account."""
    # Test status transitions through repository methods
    await account_repository.update_bnpl_status(test_bnpl_account.id, "active")
    updated = await account_repository.get(test_bnpl_account.id)
    assert updated.status == "active"
    
    # Test transition to paid off status
    await account_repository.update_bnpl_status(test_bnpl_account.id, "paid_off")
    updated = await account_repository.get(test_bnpl_account.id)
    assert updated.status == "paid_off"
```

## Key Responsibilities

- Test specialized methods for each account type
- Validate complex account-specific operations
- Test state transitions for account types with lifecycle states
- Verify proper relationship handling for linked entities
- Test date-based operations for statement cycles and payment periods

## Testing Strategy

- Create dedicated test files for each account type
- Test specialized methods defined in account type modules
- Verify proper error handling for invalid operations
- Test boundary conditions for account-specific constraints
- Test complex calculations with appropriate validation

## Known Considerations

- Methods vary significantly between account types - consult the repository module documentation
- Some methods require complex setup with multiple related entities
- Use the repository factory to create repositories with the right type-specific methods
- Balance-changing operations should verify all related balances are updated correctly
- For date-sensitive operations, use the datetime utilities to ensure UTC compliance
- BNPL, EWA, and other modern account types have unique state transitions that should be carefully tested
