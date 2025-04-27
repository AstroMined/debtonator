# Banking Account Types Services Tests

## Purpose

This directory contains integration tests for banking account type services in Debtonator. These tests validate the specialized business logic and repository integration for different banking account types following ADR-014 Repository Layer Compliance.

## Related Documentation

- [Services Integration Tests](../../README.md)
- [Repository Banking Tests](../../../repositories/crud/account_types/banking/README.md)
- [ADR-014: Repository Layer Compliance](/code/debtonator/docs/adr/implementation/adr014-implementation-checklist.md)

## Architecture

Banking account type services leverage the polymorphic repository pattern and extend the standard account service functionality with type-specific business rules. These tests verify:

1. Type-specific operations work correctly
2. Specialized business rules are applied
3. Polymorphic repository integration functions correctly
4. Services properly inherit from BaseService
5. Services use _get_repository() with polymorphic_type parameter

## Implementation Patterns

### Testing Polymorphic Repository Access

Each banking account type service test should verify proper polymorphic repository access:

```python
async def test_checking_service_operations(db_session):
    """Test checking account specific operations."""
    # Create service directly with session
    checking_service = CheckingService(session=db_session)
    
    # Create account schema
    account_schema = create_checking_account_schema(
        name="Primary Checking",
        current_balance=Decimal("1000.00")
    )
    
    # Create account through service
    checking_account = await checking_service.create_account(account_schema.model_dump())
    
    # Verify account was created with correct type
    assert checking_account.account_type == "checking"
    assert isinstance(checking_account, CheckingAccount)
    
    # Test type-specific operations
    await checking_service.set_overdraft_limit(checking_account.id, Decimal("500.00"))
    
    # Verify operation result
    updated_account = await checking_service.get_account(checking_account.id)
    assert updated_account.overdraft_limit == Decimal("500.00")
```

### Testing Type-Specific Business Rules

Each account type has specialized business rules that should be tested:

```python
async def test_bnpl_lifecycle_management(db_session):
    """Test BNPL account lifecycle operations."""
    # Create service
    bnpl_service = BNPLService(session=db_session)
    
    # Create BNPL account
    account_schema = create_bnpl_account_schema(
        name="Buy Now Pay Later",
        current_balance=Decimal("0.00"),
        credit_limit=Decimal("1000.00")
    )
    
    # Create account
    bnpl_account = await bnpl_service.create_account(account_schema.model_dump())
    
    # Test lifecycle management (type-specific business logic)
    await bnpl_service.activate_plan(
        account_id=bnpl_account.id,
        plan_data={
            "amount": Decimal("500.00"),
            "term_months": 6,
            "payments_made": 0
        }
    )
    
    # Verify business rules applied correctly
    updated_account = await bnpl_service.get_account(bnpl_account.id)
    assert updated_account.status == "active"
    assert updated_account.available_credit == Decimal("500.00")  # Original 1000 - 500 used
    assert len(updated_account.payment_plans) == 1
    assert updated_account.payment_plans[0].amount == Decimal("500.00")
    assert updated_account.payment_plans[0].term_months == 6
```

## Testing Focus Areas

### Account Type-Specific Operations

Each banking account type has specialized operations that should be tested:

1. **Checking Accounts**
   - Overdraft protection settings
   - Minimum balance requirements
   - Fee calculation and management

2. **Savings Accounts**
   - Interest calculation
   - Withdrawal limits
   - Minimum balance requirements

3. **Credit Accounts**
   - Credit limit management
   - Statement generation
   - Minimum payment calculation
   - Available credit calculation

4. **BNPL Accounts**
   - Payment plan creation
   - Installment tracking
   - Plan status management
   - Repayment scheduling

### Polymorphic Type Handling

Test proper handling of account types through the polymorphic repository pattern:

```python
async def test_polymorphic_type_handling(db_session):
    """Test service correctly handles polymorphic account types."""
    # Create service with session
    account_service = AccountService(session=db_session)
    
    # Create different account types
    checking_schema = create_checking_account_schema(name="My Checking")
    credit_schema = create_credit_account_schema(name="My Credit Card")
    
    # Create accounts with type parameter
    checking = await account_service.create_account(
        account_type="checking",
        account_data=checking_schema.model_dump()
    )
    
    credit = await account_service.create_account(
        account_type="credit",
        account_data=credit_schema.model_dump()
    )
    
    # Verify correct types created
    assert checking.account_type == "checking"
    assert isinstance(checking, CheckingAccount)
    
    assert credit.account_type == "credit"
    assert isinstance(credit, CreditAccount)
```

## Best Practices

1. **Test Type-Specific Operations**: Verify that type-specific operations work correctly
2. **Test Polymorphic Repository Access**: Use _get_repository with polymorphic_type parameter
3. **Test Business Rules**: Verify account type-specific business rules are applied
4. **Test Validation Rules**: Verify type-specific validation rules are enforced
5. **Follow UTC Datetime Compliance**: Use proper timezone-aware datetime functions
6. **Test Proper Inheritance**: Verify services properly inherit from BaseService

## Testing Guidelines

When testing banking account type services:

1. Create the appropriate service instance for the account type
2. Test type-specific operations and business rules
3. Verify proper polymorphic repository access
4. Test error handling for type-specific validation rules
5. Verify inheritance from BaseService
6. Test cross-service integration where appropriate

## Recent Improvements

The banking account type services have been fully refactored to comply with ADR-014:

1. **Polymorphic Repository Pattern**
   - Services use _get_repository with polymorphic_type parameter
   - Type-specific operations delegated to appropriate repository methods
   - Proper inheritance from BaseService

2. **Business Rule Enforcement**
   - Type-specific business rules moved to the service layer
   - Validation using schema factories before repository operations
   - Clear separation of concerns between validation and data access

3. **Service Method Standardization**
   - Consistent method signatures across all account type services
   - Proper error handling for type-specific validation
   - Consistent transaction boundary management
