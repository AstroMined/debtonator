# Test Fixtures for Services

This directory contains fixture functions for creating service instances used in testing the Debtonator application. Service fixtures represent the business logic layer and often depend on repository fixtures, following our "real objects" testing philosophy.

## Directory Structure

The fixtures directory should mirror the structure of the `src/services` directory:

```
fixtures/
├── fixture_services.py  (Main service fixtures)
└── services/           (Future subdirectory for specialized services)
    ├── __init__.py
    ├── fixture_account_services.py
    ├── fixture_bill_services.py
    └── account_types/
        ├── __init__.py
        ├── banking/
        │   ├── __init__.py
        │   ├── fixture_checking_services.py
        │   ├── fixture_credit_services.py
        │   ├── ...
```

## Naming Convention

All service fixture files should follow a consistent naming convention:

- Files must start with the prefix `fixture_`
- The middle part should match the service name in `src/services`
- Files should end with the suffix `_services`

For example:
- `src/services/accounts.py` → `fixture_account_services.py`
- `src/services/account_types/banking/checking.py` → `fixture_checking_services.py`

## Creating New Service Fixtures

When adding a new service to the codebase, follow these steps to create the corresponding fixture:

1. Create a new file with the appropriate naming convention
2. Import the necessary service classes from `src/services/`
3. Import dependent repository fixtures from `tests/fixtures/repositories/`
4. Create fixture functions that instantiate and return service instances
5. Register the new fixture file in `tests/conftest.py` if needed

## Service Fixture Guidelines

### Basic Rules

1. Use `@pytest_asyncio.fixture` for all fixture functions to ensure proper async support
2. Every service class should have at least one corresponding fixture
3. Service fixtures should use real repository instances, not mocks
4. Inject repository fixtures as parameters to service fixtures
5. Include clear docstrings for each fixture function explaining its purpose
6. Handle dependencies explicitly and transparently

### Managing Service Dependencies

Services often have multiple dependencies. There are several approaches to managing them:

1. **Direct Dependencies**: Pass repository fixtures directly to the service constructor
2. **Factory Pattern**: Use a factory fixture to create services with their dependencies
3. **Dependency Injection**: Use a dependency injection container for complex dependency graphs

### Example Service Fixture with Direct Dependencies

```python
from typing import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.accounts import AccountService
from src.repositories.accounts import AccountRepository


@pytest_asyncio.fixture
async def account_service(
    account_repository: AccountRepository,
    feature_flag_service,  # Another service dependency
) -> AsyncGenerator[AccountService, None]:
    """
    Create an AccountService instance for testing.
    
    This fixture provides a real AccountService connected to the test
    repository for integration testing without mocks.
    """
    service = AccountService(
        repository=account_repository,
        feature_flag_service=feature_flag_service,
    )
    yield service
    # No cleanup needed as dependencies handle this
```

### Example Service Factory Pattern

```python
from typing import AsyncGenerator

import pytest_asyncio

from src.services.factory import ServiceFactory
from src.repositories.factory import RepositoryFactory


@pytest_asyncio.fixture
async def service_factory(
    repository_factory: RepositoryFactory,
    feature_flag_service,
) -> AsyncGenerator[ServiceFactory, None]:
    """
    Create a ServiceFactory instance for testing.
    
    This fixture provides a real ServiceFactory that can create any
    service type with appropriate dependencies.
    """
    factory = ServiceFactory(
        repository_factory=repository_factory,
        feature_flag_service=feature_flag_service,
    )
    yield factory
    # No cleanup needed as dependencies handle this
```

### Example Service with Complex Dependencies

```python
@pytest_asyncio.fixture
async def banking_overview_service(
    account_repository: AccountRepository,
    bill_repository: BillRepository,
    payment_repository: PaymentRepository,
    income_repository: IncomeRepository,
    cashflow_repository: CashflowRepository,
    feature_flag_service,
) -> AsyncGenerator[BankingOverviewService, None]:
    """
    Create a BankingOverviewService with all required dependencies.
    
    This service has multiple repository dependencies and requires
    careful setup to ensure all dependencies are available.
    """
    service = BankingOverviewService(
        account_repository=account_repository,
        bill_repository=bill_repository,
        payment_repository=payment_repository,
        income_repository=income_repository,
        cashflow_repository=cashflow_repository,
        feature_flag_service=feature_flag_service,
    )
    yield service
```

## Service Registry Pattern

For services that use a registry pattern (like account types):

```python
@pytest_asyncio.fixture
async def account_type_service_registry(
    repository_factory: RepositoryFactory,
    feature_flag_service,
) -> AsyncGenerator[AccountTypeServiceRegistry, None]:
    """
    Create an AccountTypeServiceRegistry for testing.
    
    This fixture provides a registry that can create specialized
    account type services based on account type.
    """
    from src.services.account_types.registry import AccountTypeServiceRegistry
    
    registry = AccountTypeServiceRegistry(
        repository_factory=repository_factory,
        feature_flag_service=feature_flag_service,
    )
    yield registry
```

## Handling Stateful Services

Some services maintain state or perform initialization. Handle these carefully:

```python
@pytest_asyncio.fixture
async def stateful_service(db_session: AsyncSession):
    """
    Create a stateful service that requires initialization.
    
    This fixture handles proper initialization and cleanup.
    """
    # Create service
    service = StatefulService(db_session)
    
    # Initialize service
    await service.initialize()
    
    yield service
    
    # Clean up
    await service.shutdown()
```

## Handling Circular Dependencies

When services have circular dependencies, use one of these approaches:

1. **Lazy Initialization**: Pass None initially, then set the dependency after creation
2. **Dependency Function**: Pass a function that returns the dependency when needed
3. **Service Locator**: Use a central registry to resolve dependencies at runtime

Example with lazy initialization:

```python
@pytest_asyncio.fixture
async def service_a(repository_a: RepositoryA):
    """Service A that has a circular dependency with Service B."""
    # Create with None for the circular dependency
    service = ServiceA(repository=repository_a, service_b=None)
    yield service


@pytest_asyncio.fixture
async def service_b(repository_b: RepositoryB, service_a: ServiceA):
    """Service B that depends on Service A."""
    # Create with reference to service_a
    service = ServiceB(repository=repository_b, service_a=service_a)
    
    # Now set service_b on service_a to complete the circular reference
    service_a._service_b = service
    
    yield service
```

## Feature Flag Integration

Create service fixtures with different feature flag configurations:

```python
@pytest_asyncio.fixture
async def account_service_with_international_support(
    account_repository: AccountRepository,
    feature_flag_service,
) -> AsyncGenerator[AccountService, None]:
    """
    Create an AccountService with international features enabled.
    
    This fixture enables the INTERNATIONAL_ACCOUNTS feature flag
    before creating the service.
    """
    # Enable feature flag
    await feature_flag_service.enable_flag("INTERNATIONAL_ACCOUNTS")
    
    # Create service
    service = AccountService(
        repository=account_repository,
        feature_flag_service=feature_flag_service,
    )
    
    yield service
    
    # Disable feature flag after test
    await feature_flag_service.disable_flag("INTERNATIONAL_ACCOUNTS")
```

## Best Practices

1. **Real Dependencies**: Always use real dependency instances, not mocks
2. **Explicit Dependencies**: Make all service dependencies explicit in fixture arguments
3. **Proper Initialization**: Ensure services are properly initialized before yielding
4. **Proper Cleanup**: Provide cleanup for services that require it
5. **Feature Flag Configuration**: Create fixtures with specific feature flag configurations
6. **Clear Docstrings**: Include informative docstrings for all fixtures
7. **Consistent Naming**: Use descriptive and consistent naming for fixtures
8. **Module Registration**: Register all fixture modules in conftest.py
9. **Minimize Fixture Dependencies**: Keep the dependency chain as shallow as possible
10. **Handle Circular Dependencies**: Use appropriate patterns for circular dependencies

## Common Patterns

### Basic Service Pattern

```python
@pytest_asyncio.fixture
async def account_service(account_repository: AccountRepository) -> AccountService:
    """Create an account service for testing."""
    return AccountService(repository=account_repository)
```

### Service with Multiple Repositories Pattern

```python
@pytest_asyncio.fixture
async def bill_service(
    bill_repository: BillRepository,
    account_repository: AccountRepository,
) -> BillService:
    """Create a bill service with multiple repository dependencies."""
    return BillService(
        bill_repository=bill_repository,
        account_repository=account_repository,
    )
```

### Service with Other Service Dependencies Pattern

```python
@pytest_asyncio.fixture
async def cashflow_service(
    cashflow_repository: CashflowRepository,
    account_service: AccountService,
    bill_service: BillService,
) -> CashflowService:
    """Create a cashflow service that depends on other services."""
    return CashflowService(
        repository=cashflow_repository,
        account_service=account_service,
        bill_service=bill_service,
    )
```

### Specialized Service Factory Pattern

```python
@pytest_asyncio.fixture
async def specialized_account_service_factory(
    repository_factory: RepositoryFactory,
    feature_flag_service,
) -> SpecializedAccountServiceFactory:
    """Create a factory for specialized account type services."""
    return SpecializedAccountServiceFactory(
        repository_factory=repository_factory,
        feature_flag_service=feature_flag_service,
    )
```

### Basic Service Testing

```python
async def test_account_service_create(
    account_service: AccountService,
    db_session: AsyncSession,
):
    """Test creating an account through the service layer."""
    # Create account data
    account_data = {
        "name": "Test Account",
        "account_type": "checking",
        "available_balance": Decimal("1000.00"),
    }
    
    # Use service to create account
    account = await account_service.create_account(account_data)
    
    # Assert it was created correctly
    assert account is not None
    assert account.name == "Test Account"
    assert account.account_type == "checking"
    assert account.available_balance == Decimal("1000.00")
    
    # Verify it exists in the database
    from sqlalchemy import select
    from src.models.accounts import Account
    
    stmt = select(Account).where(Account.id == account.id)
    result = await db_session.execute(stmt)
    db_account = result.scalars().first()
    
    assert db_account is not None
    assert db_account.id == account.id
```

### Testing with Service Factory

```python
async def test_service_factory(
    service_factory: ServiceFactory,
    test_checking_account: CheckingAccount,
):
    """Test creating and using services from the factory."""
    # Get account service from factory
    account_service = service_factory.get_account_service()
    
    # Use service to get account
    account = await account_service.get_by_id(test_checking_account.id)
    assert account is not None
    
    # Get specialized service based on account type
    specialized_service = service_factory.get_specialized_account_service(account)
    
    # Use specialized methods
    account_details = await specialized_service.get_detailed_account_info(account.id)
    assert account_details is not None
```

## Testing Service Integration

### Testing Cross-Service Interactions

```python
async def test_bill_payment_integration(
    bill_service: BillService,
    payment_service: PaymentService,
    account_service: AccountService,
    test_checking_account: CheckingAccount,
):
    """Test integration between bill, payment, and account services."""
    # Create a bill
    bill_data = {
        "name": "Test Bill",
        "amount": Decimal("100.00"),
        "due_day": 15,
        "primary_account_id": test_checking_account.id,
    }
    bill = await bill_service.create_bill(bill_data)
    
    # Create a payment for the bill
    payment_data = {
        "bill_id": bill.id,
        "amount": Decimal("100.00"),
        "payment_date": naive_utc_now(),
        "account_id": test_checking_account.id,
    }
    payment = await payment_service.create_payment(payment_data)
    
    # Verify bill is marked as paid
    updated_bill = await bill_service.get_by_id(bill.id)
    assert updated_bill.is_paid is True
    
    # Verify account balance was updated
    updated_account = await account_service.get_by_id(test_checking_account.id)
    assert updated_account.available_balance == test_checking_account.available_balance - Decimal("100.00")
```

### Testing with Feature Flags

```python
async def test_service_with_feature_flags(
    account_service: AccountService,
    feature_flag_service,
):
    """Test service behavior with different feature flag settings."""
    # Enable a feature flag
    await feature_flag_service.enable_flag("INTERNATIONAL_ACCOUNTS")
    
    # Create an account with international details
    account_data = {
        "name": "International Account",
        "account_type": "checking",
        "available_balance": Decimal("1000.00"),
        "currency": "EUR",
        "iban": "DE89370400440532013000",
        "swift_bic": "DEUTDEFF",
    }
    
    # This should succeed with the feature flag enabled
    account = await account_service.create_account(account_data)
    assert account.currency == "EUR"
    
    # Disable the feature flag
    await feature_flag_service.disable_flag("INTERNATIONAL_ACCOUNTS")
    
    # Trying to create another international account should now fail
    with pytest.raises(FeatureFlagDisabledError):
        await account_service.create_account(account_data)
```

## Handling Stateful Services

Some services maintain state or perform initialization. Handle these carefully:

```python
@pytest_asyncio.fixture
async def stateful_service(db_session: AsyncSession):
    """
    Create a stateful service that requires initialization.
    
    This fixture handles proper initialization and cleanup.
    """
    # Create service
    service = StatefulService(db_session)
    
    # Initialize service
    await service.initialize()
    
    yield service
    
    # Clean up
    await service.shutdown()
```

## Best Practices

1. **Real Dependencies**: Always use real dependency instances, not mocks
2. **Explicit Dependencies**: Make all service dependencies explicit in fixture arguments
3. **Integration Testing**: Focus on integration tests that verify service-repository interactions
4. **Business Rule Validation**: Test that services enforce business rules correctly
5. **Error Handling**: Test service error scenarios and exception handling
6. **Feature Flag Testing**: Test services with different feature flag combinations
7. **Cross-Service Testing**: Test interactions between multiple services
8. **Stateful Service Cleanup**: Ensure proper cleanup for stateful services
9. **Comprehensive Coverage**: Create fixtures for all service types
10. **Minimal Setup**: Keep fixture setup focused on the services being tested

## Common Patterns

### Basic Service Pattern

```python
@pytest_asyncio.fixture
async def account_service(account_repository: AccountRepository) -> AccountService:
    """Create an account service for testing."""
    return AccountService(repository=account_repository)
```

### Service with Multiple Repositories Pattern

```python
@pytest_asyncio.fixture
async def bill_service(
    bill_repository: BillRepository,
    account_repository: AccountRepository,
) -> BillService:
    """Create a bill service with multiple repository dependencies."""
    return BillService(
        bill_repository=bill_repository,
        account_repository=account_repository,
    )
```

### Service with Other Service Dependencies Pattern

```python
@pytest_asyncio.fixture
async def cashflow_service(
    cashflow_repository: CashflowRepository,
    account_service: AccountService,
    bill_service: BillService,
) -> CashflowService:
    """Create a cashflow service that depends on other services."""
    return CashflowService(
        repository=cashflow_repository,
        account_service=account_service,
        bill_service=bill_service,
    )
```

### Specialized Service Factory Pattern

```python
@pytest_asyncio.fixture
async def specialized_account_service_factory(
    repository_factory: RepositoryFactory,
    feature_flag_service,
) -> SpecializedAccountServiceFactory:
    """Create a factory for specialized account type services."""
    return SpecializedAccountServiceFactory(
        repository_factory=repository_factory,
        feature_flag_service=feature_flag_service,
    )
```