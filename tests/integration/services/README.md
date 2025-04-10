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

## Best Practices

1. **Use Real Repositories**: Follow ADR-014 by using real repositories instead of mocks
2. **Test Business Rules**: Focus on testing business rules and service-specific logic
3. **Test Error Handling**: Verify that services handle errors appropriately
4. **Test Transaction Boundaries**: Verify that transactions are properly managed
5. **Follow UTC Datetime Compliance**: Use proper timezone-aware datetime functions
6. **Test Feature Flag Integration**: Verify feature flag integration when applicable

## Test Organization

Tests are organized to mirror the structure of the `src/services` directory:

```
services/
├── test_account_service.py
├── test_bill_service.py
└── account_types/
    └── banking/
        ├── test_checking_service.py
        ├── test_savings_service.py
        └── test_credit_service.py
```
