# Test Fixtures

This directory contains fixture functions for creating test instances of various components in the Debtonator application. These fixtures follow the "Real Objects Testing Philosophy" established in ADR-014, which prohibits mocking and emphasizes integration testing with real components.

## Core Principles

Fixtures in Debtonator adhere to these principles:

1. **No Mocks**: We strictly avoid using mocks, stubs, or other test doubles
2. **Real Components**: All fixtures instantiate real objects that interact with other real objects
3. **Integration-First**: Fixtures support our integration-first testing approach
4. **Real Database**: Tests use a real SQLite database that resets between tests
5. **Single Responsibility**: Each fixture has a single clear purpose

## Directory Structure

```
fixtures/
├── __init__.py
├── models/                  # Model fixtures
│   ├── __init__.py
│   ├── fixture_accounts_models.py
│   ├── fixture_bill_models.py
│   └── account_types/
│       └── banking/
│           ├── __init__.py
│           ├── fixture_checking_models.py
│           └── ...
├── repositories/            # Repository fixtures
│   ├── __init__.py
│   ├── fixture_account_repositories.py
│   └── ...
└── services/                # Service fixtures
    ├── __init__.py
    ├── fixture_account_services.py
    └── ...
```

## Fixture Categories

### Model Fixtures

Model fixtures create SQLAlchemy model instances for testing:

```python
@pytest_asyncio.fixture
async def test_checking_account(db_session: AsyncSession) -> CheckingAccount:
    """Primary Test Checking Account for use in various tests."""
    checking_account = CheckingAccount(
        name="Primary Test Checking",
        available_balance=Decimal("1000.00"),
        current_balance=Decimal("1000.00"),
        created_at=naive_utc_now(),
        updated_at=naive_utc_now(),
    )
    db_session.add(checking_account)
    await db_session.flush()
    await db_session.refresh(checking_account)
    return checking_account
```

### Repository Fixtures

Repository fixtures create repository instances connected to the test database:

```python
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

### Service Fixtures

Service fixtures create service instances with real repository dependencies:

```python
@pytest_asyncio.fixture
async def account_service(
    account_repository: AccountRepository,
    feature_flag_service,
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

## Best Practices

1. **Explicit Dependencies**: Make all dependencies explicit in fixture arguments
2. **Clear Docstrings**: Include informative docstrings for all fixtures
3. **Minimal Setup**: Keep fixture setup as simple as possible
4. **Proper Type Annotations**: Always include proper return type annotations
5. **Use yield Pattern**: Use `yield` pattern to ensure proper cleanup
6. **Follow SRP**: Fixtures should only do one thing and do it well

## UTC Datetime Compliance

As per ADR-011, all datetime values in fixtures must use the appropriate datetime functions:

```python
from src.utils.datetime_utils import naive_utc_now, naive_days_from_now

# Use naive_utc_now() for database fields
model = StatementHistory(
    account_id=account.id,
    statement_date=naive_utc_now(),
    statement_balance=Decimal("500.00")
)
```

## Common Anti-Patterns to Avoid

1. **No unittest.mock**: Do not use unittest.mock or MagicMock
2. **No Naive Datetimes**: Never use naive datetime objects directly
3. **No Repository Bypass**: Higher-level fixtures should use repositories, not direct DB access
4. **No Complex Fixture Chains**: Avoid creating deep dependency chains
5. **No Cross-Layer Testing in Unit Tests**: Keep unit test fixtures focused on one layer
