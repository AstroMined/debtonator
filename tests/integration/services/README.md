# Integration Tests for Service Layer

This directory contains integration tests for service components in the Debtonator application. These tests validate the business logic, repository integration, and cross-entity operations performed by the service layer.

## Why Services Require Integration Tests

Service layer components inherently cross application layer boundaries:

- Services use repositories to access data
- Services implement business logic that spans multiple entities
- Services perform validations that depend on database state
- Services often interact with other services or components

Therefore, service tests are **integration tests by definition**, not unit tests.

## Testing Focus Areas

### Business Logic

Test that business logic is correctly implemented:

```python
async def test_account_service_calculate_total_balance(account_service, db_session):
    """Test total balance calculation business logic."""
    # Create test accounts
    checking = await create_test_checking_account(
        db_session, 
        available_balance=Decimal("1000.00")
    )
    savings = await create_test_savings_account(
        db_session, 
        available_balance=Decimal("2000.00")
    )
    
    # Test business logic
    total_balance = await account_service.calculate_total_balance()
    
    # Verify calculation is correct
    assert total_balance == Decimal("3000.00")
```

### Repository Integration

Test that services interact correctly with repositories:

```python
async def test_account_service_find_accounts_by_type(account_service, db_session):
    """Test finding accounts by type using repository layer."""
    # Create test accounts
    checking1 = await create_test_checking_account(db_session, name="Checking 1")
    checking2 = await create_test_checking_account(db_session, name="Checking 2")
    savings = await create_test_savings_account(db_session, name="Savings")
    
    # Test repository integration
    checking_accounts = await account_service.find_accounts_by_type("checking")
    
    assert len(checking_accounts) == 2
    account_names = [a.name for a in checking_accounts]
    assert "Checking 1" in account_names
    assert "Checking 2" in account_names
```

### Error Handling

Test error handling in services:

```python
async def test_account_service_error_handling(account_service):
    """Test handling of non-existent account."""
    # Test with non-existent ID
    from src.errors.account_errors import AccountNotFoundError
    
    with pytest.raises(AccountNotFoundError) as excinfo:
        await account_service.get_account_by_id(999999)
    
    # Error should include ID
    assert "999999" in str(excinfo.value)
```

## Integration Test Setup

Proper setup is critical for service integration tests:

```python
import pytest_asyncio
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.account_service import AccountService
from src.repositories.account_repository import AccountRepository
from tests.fixtures.models.fixture_accounts_models import create_test_checking_account

@pytest_asyncio.fixture
async def account_repository(db_session: AsyncSession):
    """Create an account repository for testing."""
    return AccountRepository(db_session)

@pytest_asyncio.fixture
async def account_service(account_repository):
    """Create an account service with repository dependency."""
    return AccountService(account_repository)
```

## Feature Flag System Testing

Testing the Feature Flag System (ADR-024) components requires special attention:

### Interceptor and Proxy Testing

The Feature Flag Service Proxy and Interceptor enforce feature flag requirements at architectural boundaries:

```python
async def test_feature_flag_enforcement(
    account_service, 
    feature_flag_repository, 
    db_session
):
    """Test service proxy blocks operations when feature is disabled."""
    # Set up test data
    schema = AccountCreateSchema(
        name="Test Account",
        account_type="ewa",  # Feature-controlled account type
        # Other required fields...
    )
    
    # CASE 1: Feature disabled
    # Disable the feature flag in the database
    await feature_flag_repository.update(
        "BANKING_ACCOUNT_TYPES_ENABLED", 
        {"value": False}
    )
    
    # Attempt should be blocked with appropriate error
    with pytest.raises(FeatureDisabledError) as excinfo:
        await account_service.create_account(schema)
    
    # Verify error details
    assert excinfo.value.feature_name == "BANKING_ACCOUNT_TYPES_ENABLED"
    assert excinfo.value.entity_type == "account_type"
    assert excinfo.value.entity_id == "ewa"
    
    # CASE 2: Feature enabled
    # Enable the feature flag in the database
    await feature_flag_repository.update(
        "BANKING_ACCOUNT_TYPES_ENABLED", 
        {"value": True}
    )
    
    # Operation should now succeed
    result = await account_service.create_account(schema)
    assert result.account_type == "ewa"
```

### Testing at Different Layers

The Feature Flag System operates at multiple architectural boundaries:

1. **Repository Layer Tests**: Test that proxied repositories enforce feature flags
2. **Service Layer Tests**: Test service interceptors enforce feature flags
3. **Cross-Layer Tests**: Test that changes to feature flags propagate correctly

### Testing Caching Behavior

Feature flag requirements use caching for performance:

```python
async def test_feature_flag_caching(
    account_service, 
    feature_flag_repository, 
    db_session
):
    """Test caching behavior of feature flag system."""
    # Set up test data
    schema = AccountCreateSchema(
        name="Test Account",
        account_type="ewa",
        # Other required fields...
    )
    
    # Enable the feature
    await feature_flag_repository.update(
        "BANKING_ACCOUNT_TYPES_ENABLED", 
        {"value": True}
    )
    
    # First call should work and cache the result
    result1 = await account_service.create_account(schema)
    
    # Disable feature in database
    await feature_flag_repository.update(
        "BANKING_ACCOUNT_TYPES_ENABLED", 
        {"value": False}
    )
    
    # Second call should still work if cache hasn't expired
    # This demonstrates the caching behavior
    schema.name = "Test Account 2"
    result2 = await account_service.create_account(schema)
    
    # Force cache invalidation
    await service._proxy.invalidate_cache()
    
    # Now the operation should be blocked
    with pytest.raises(FeatureDisabledError):
        schema.name = "Test Account 3"
        await account_service.create_account(schema)
```

## Best Practices

1. **Use Real Repositories**: Follow ADR-014 by using real repositories instead of mocks
2. **Test Business Rules**: Focus on testing business rules and service-specific logic
3. **Test Error Handling**: Verify that services handle errors appropriately
4. **Test Transaction Boundaries**: Verify that transactions are properly managed
5. **Follow UTC Datetime Compliance**: Use proper timezone-aware datetime functions
6. **Test Feature Flag Integration**: Verify feature flag enforcement at service boundaries
   - Test both enabled and disabled states for each feature flag
   - Test with account-type-specific requirements
   - Test caching behavior and cache invalidation
   - Test propagation of feature flag changes

## Test Organization

Tests are organized to mirror the structure of the `src/services` directory:

```
services/
├── test_account_service.py
├── test_bill_service.py
├── interceptors/
│   └── test_feature_flag_interceptor.py
├── proxies/
│   └── test_feature_flag_proxy.py
└── account_types/
    └── banking/
        ├── test_checking_service.py
        ├── test_savings_service.py
        └── test_credit_service.py
```

In accordance with ADR-024, the new test files verify that feature flags are correctly enforced at service layer boundaries.
