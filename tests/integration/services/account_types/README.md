# Account Types Services Tests

## Purpose

This directory contains integration tests for account type services in Debtonator. These tests validate specialized business logic, repository integration, and type-specific operations for different account types following ADR-014 Repository Layer Compliance.

## Related Documentation

- [Services Integration Tests](../README.md)
- [Repository Account Types Tests](../../repositories/crud/account_types/README.md)
- [ADR-014: Repository Layer Compliance](/code/debtonator/docs/adr/implementation/adr014-implementation-checklist.md)

## Child Documentation

- [Banking Account Types Services Tests](./banking/README.md)

## Architecture

Account type services follow the polymorphic repository pattern and extend the standard account service functionality with type-specific business rules. The tests in this directory verify:

1. Type-specific operations work correctly
2. Specialized business rules are applied
3. Polymorphic repository integration functions correctly
4. Services properly inherit from BaseService
5. Services use _get_repository() with polymorphic_type parameter

## Implementation Patterns

### Polymorphic Repository Access Pattern

Services that work with polymorphic entities should use the polymorphic repository access pattern:

```python
class SomeAccountTypeService(BaseService):
    """Service for specific account type operations."""
    
    def __init__(
        self,
        session: AsyncSession,
        feature_flag_service: Optional[FeatureFlagService] = None,
        config_provider: Optional[Any] = None
    ):
        super().__init__(session, feature_flag_service, config_provider)
        
    async def some_type_specific_operation(self, account_id: int) -> Result:
        # Get polymorphic repository with type
        account_repo = await self._get_repository(
            AccountRepository, 
            polymorphic_type="some_account_type"
        )
        
        # Use repository methods
        account = await account_repo.get(account_id)
        
        # Apply type-specific business logic
        # ...
        
        # Return result
        return result
```

### Testing Type-Specific Services

Tests for type-specific services should:

1. Verify proper inheritance from BaseService
2. Test polymorphic repository access
3. Validate type-specific business rules
4. Test error handling for type-specific validations

```python
async def test_account_type_service(db_session):
    """Test account type specific service operations."""
    # Create service with session
    service = SomeAccountTypeService(session=db_session)
    
    # Create account schema
    account_schema = create_some_account_type_schema(
        name="Type-Specific Account",
        # Type-specific fields...
    )
    
    # Create account through service
    account = await service.create_account(account_schema.model_dump())
    
    # Test type-specific operations
    result = await service.some_type_specific_operation(account.id)
    
    # Verify result
    assert result is not None
    # Validate type-specific result properties...
```

## Testing Focus Areas

### Type-Specific Operations

Test type-specific operations for each account type:

1. Creation and validation of type-specific properties
2. Business rule enforcement for each account type
3. Type-specific validation rules
4. Type-specific error handling

### Polymorphic Repository Integration

Test proper integration with polymorphic repositories:

1. Proper use of _get_repository() with polymorphic_type parameter
2. Handling of type-specific repository methods
3. Type safety in repository operations
4. Error handling for invalid types

### Cross-Type Operations

Test operations that work across multiple account types:

1. Account type discovery and registration
2. Type-specific operation routing
3. Type-specific validation across multiple types
4. Cross-type business rules

## Best Practices

1. **Type-Specific Fixtures**: Use fixtures designed for specific account types
2. **Test Type-Specific Rules**: Verify business rules specific to each account type
3. **Test Validation**: Verify type-specific validation rules are enforced
4. **Check Inheritance**: Verify services properly inherit from BaseService
5. **Test Repository Access**: Verify proper use of _get_repository() with polymorphic_type
6. **Test Error Handling**: Verify type-specific error handling

## Recent Improvements

The account type services have been fully refactored to comply with ADR-014:

1. **BaseService Implementation**
   - All services now inherit from BaseService
   - Services use _get_repository() with polymorphic_type parameter
   - Consistent service interface across all account types

2. **Repository Integration**
   - Proper use of polymorphic repositories with type parameters
   - Type-specific repository methods delegated through _get_repository()
   - Clear separation between standard and polymorphic repositories

3. **Business Rule Enforcement**
   - Type-specific business rules moved to service layer
   - Validation using schema factories before repository operations
   - Clear separation of concerns between validation and data access
