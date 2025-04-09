# Test Fixtures for Repositories

This directory contains fixture functions for creating repository instances used in testing the Debtonator application. Repository fixtures are crucial for testing service-layer components without having to mock database interactions, following our "real objects" testing philosophy.

## Directory Structure

The fixtures directory should mirror the structure of the `src/repositories` directory:

```
fixtures/
├── fixture_repositories.py  (Main repository fixtures)
└── repositories/           (Future subdirectory for specialized repositories)
    ├── __init__.py
    ├── fixture_account_repositories.py
    ├── fixture_bill_repositories.py
    └── account_types/
        ├── __init__.py
        ├── banking/
        │   ├── __init__.py
        │   ├── fixture_checking_repositories.py
        │   ├── fixture_credit_repositories.py
        │   ├── ...
```

## Naming Convention

All repository fixture files should follow a consistent naming convention:

- Files must start with the prefix `fixture_`
- The middle part should match the repository name in `src/repositories`
- Files should end with the suffix `_repositories`

For example:
- `src/repositories/accounts.py` → `fixture_account_repositories.py`
- `src/repositories/account_types/banking/checking.py` → `fixture_checking_repositories.py`

## Creating New Repository Fixtures

When adding a new repository to the codebase, follow these steps to create the corresponding fixture:

1. Create a new file with the appropriate naming convention
2. Import the necessary repository classes from `src/repositories/`
3. Import `pytest_asyncio` and any required model fixtures
4. Create fixture functions that instantiate and return repository instances
5. Register the new fixture file in `tests/conftest.py` if needed

## Repository Fixture Guidelines

### Basic Rules

1. Use `@pytest_asyncio.fixture` for all fixture functions to ensure proper async support
2. Every repository class should have at least one corresponding fixture
3. Repository fixtures should use the real database session, not mocks
4. Inject the `db_session` fixture as a parameter to all repository fixtures
5. Include clear docstrings for each fixture function explaining its purpose

### Example Repository Fixture

```python
from typing import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.accounts import AccountRepository


@pytest_asyncio.fixture
async def account_repository(
    db_session: AsyncSession
) -> AsyncGenerator[AccountRepository, None]:
    """
    Create an AccountRepository instance for testing.
    
    This fixture provides a real AccountRepository connected to the test
    database session for integration testing without mocks.
    """
    repository = AccountRepository(db_session)
    yield repository
    # No cleanup needed as db_session handles this
```

## Repository Factory Pattern

For repositories that use the factory pattern:

```python
from typing import AsyncGenerator

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.factory import RepositoryFactory
from src.repositories.accounts import AccountRepository
from src.repositories.bills import BillRepository


@pytest_asyncio.fixture
async def repository_factory(
    db_session: AsyncSession
) -> AsyncGenerator[RepositoryFactory, None]:
    """
    Create a RepositoryFactory instance for testing.
    
    This fixture provides a real RepositoryFactory that can create any
    repository type connected to the test database session.
    """
    factory = RepositoryFactory(db_session)
    yield factory
    # No cleanup needed as db_session handles this
```

## Specialized Repository Fixtures

For repositories that require specific setup or have specialized behavior:

```python
@pytest_asyncio.fixture
async def account_repository_with_feature_flags(
    db_session: AsyncSession,
    feature_flag_service
) -> AsyncGenerator[AccountRepository, None]:
    """
    Create an AccountRepository with feature flags enabled.
    
    This fixture provides a repository with specific feature flags enabled
    for testing feature-specific functionality.
    """
    # Enable relevant feature flags
    await feature_flag_service.enable_flag("INTERNATIONAL_ACCOUNTS")
    
    # Create repository
    repository = AccountRepository(db_session)
    yield repository
    
    # Disable flags after test
    await feature_flag_service.disable_flag("INTERNATIONAL_ACCOUNTS")
```

## Repository Module Pattern Fixtures

For repositories that use the module pattern (like account types):

```python
@pytest_asyncio.fixture
async def checking_repository(
    db_session: AsyncSession
) -> AsyncGenerator[CheckingAccountRepository, None]:
    """
    Create a CheckingAccountRepository instance for testing.
    
    This fixture provides a specialized repository for checking accounts
    with all checking-specific operations available.
    """
    from src.repositories.account_types.banking.checking import CheckingAccountRepository
    
    repository = CheckingAccountRepository(db_session)
    yield repository
```

## Best Practices

1. **Real Database Sessions**: Always use real database session fixtures, not mocks
2. **Comprehensive Coverage**: Create fixtures for all repository types in the application
3. **Minimal Setup**: Keep fixture setup simple and focused on the repository being created
4. **Feature Flag Integration**: Create fixtures with different feature flag configurations when needed
5. **Repository Variants**: Create specialized fixtures for common repository configurations
6. **Correct Session Handling**: Use `yield` pattern to ensure proper session cleanup
7. **Proper Type Annotations**: Always include proper return types for fixtures
8. **Clear Docstrings**: Include informative docstrings for all fixtures
9. **Consistent Naming**: Use descriptive and consistent naming for fixtures
10. **Module Registration**: Register all fixture modules in conftest.py

## Common Patterns

### Repository Factory Pattern

```python
@pytest_asyncio.fixture
async def repository_factory(db_session: AsyncSession) -> RepositoryFactory:
    """Create a repository factory for testing."""
    return RepositoryFactory(db_session)
```

### Repository Instance Pattern

```python
@pytest_asyncio.fixture
async def bill_repository(db_session: AsyncSession) -> BillRepository:
    """Create a bill repository for testing."""
    return BillRepository(db_session)
```

### Repository with Dependencies Pattern

```python
@pytest_asyncio.fixture
async def cashflow_repository(
    db_session: AsyncSession,
    bill_repository: BillRepository,
    account_repository: AccountRepository
) -> CashflowRepository:
    """Create a cashflow repository with dependencies for testing."""
    return CashflowRepository(
        session=db_session,
        bill_repository=bill_repository,
        account_repository=account_repository
    )
```
