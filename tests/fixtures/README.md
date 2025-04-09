# Debtonator Test Fixtures

This directory contains fixture functions for creating test instances of various components in the Debtonator application. These fixtures follow the "Real Objects Testing Philosophy" established in ADR-014, which prohibits mocking and emphasizes integration testing with real components.

## Overall Philosophy

Fixtures in Debtonator adhere to these core principles:

1. **No Mocks**: We strictly avoid using mocks, stubs, or other test doubles
2. **Real Components**: All fixtures instantiate real objects that interact with other real objects
3. **Integration-First**: Fixtures support our integration-first testing approach
4. **Real Database**: Tests use a real SQLite database that resets between tests
5. **Single Responsibility**: Each fixture has a single clear purpose and responsibility
6. **Directory Mirroring**: Fixture organization mirrors the source code directory structure
7. **Proper Isolation**: Tests maintain proper isolation despite using real objects

## Directory Structure

```
fixtures/
├── __init__.py
├── fixture_repositories.py  (Repository fixtures)
├── fixture_services.py      (Service fixtures)
└── models/                  (Model fixtures)
    ├── __init__.py
    ├── fixture_accounts_models.py
    ├── fixture_balance_models.py
    ├── ...
    └── account_types/
        ├── __init__.py
        ├── banking/
        │   ├── __init__.py
        │   ├── fixture_checking_models.py
        │   ├── ...
```

## Fixture Categories

This directory contains fixtures for the following component types:

### Models

Model fixtures create SQLAlchemy model instances for testing. See the [models README](./models/README.md) for detailed guidelines on creating model fixtures, including handling complex relationships, polymorphic models, and edge cases.

### Repositories

Repository fixtures create real repository objects connected to the test database. See the [repositories README](./fixture_repositories.py) for detailed guidelines on creating repository fixtures, including factory patterns and specialized repositories.

### Services

Service fixtures create service objects with real repository dependencies. See the [services README](./fixture_services.py) for detailed guidelines on creating service fixtures, including dependency management, circular dependency resolution, and feature flag integration.

## Registration in conftest.py

All fixture files must be registered in the `pytest_plugins` list in `tests/conftest.py` to make them available across the test suite. This registration happens automatically for the existing fixtures, but must be done manually when adding new fixture files.

## UTC Datetime Compliance

As per ADR-011, all datetime values in tests must use timezone-aware UTC datetime objects. The pytest hooks in conftest.py will warn you about naive datetime usage in tests that run successfully.

Always use datetime functions from `src/utils/datetime_utils.py` when working with datetime values in fixtures.

## Best Practices

1. **Explicit Dependencies**: Make all dependencies explicit in fixture arguments
2. **Clear Docstrings**: Include informative docstrings for all fixtures
3. **Minimal Setup**: Keep fixture setup as simple as possible
4. **Proper Type Annotations**: Always include proper return type annotations for fixtures
5. **Use yield Pattern**: Use `yield` pattern to ensure proper cleanup of fixtures
6. **Follow SRP**: Fixtures should only do one thing and do it well

## Common Anti-Patterns to Avoid

1. **No unittest.mock**: Do not use unittest.mock or MagicMock
2. **No Naive Datetimes**: Never use naive datetime objects
3. **No Repository Bypass at Service Layer**: Higher-level tests should use repositories, not direct DB access
4. **No Complex Fixture Chains**: Avoid creating deep dependency chains
5. **No Cross-Layer Testing in Unit Tests**: Keep unit tests focused on one layer

> **Note on Direct Database Access**: Model fixtures legitimately interact directly with the database — this is appropriate for model-level tests. Direct database access is only discouraged for service-layer and API-layer testing, where repository abstractions should be used instead.

## Learn More

For detailed guidelines on creating fixtures for specific component types, refer to the README.md files in the subdirectories:

- [Model Fixtures](./models/README.md)
- [Repository Fixtures](./fixture_repositories.py) (documentation at top of file)
- [Service Fixtures](./fixture_services.py) (documentation at top of file)
