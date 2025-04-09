# Feature Flags Testing

## Integration Test Candidates

The following functions in `feature_flags.py` require database interactions and should be tested with integration tests rather than unit tests with mocks:

1. `get_registry()` - Tests should verify the singleton pattern works correctly.

2. `configure_feature_flags(db: AsyncSession) -> None`
   - Tests should verify that feature flags from the database are correctly loaded into the registry.
   - Should test with various database states (empty, with flags, with conflicting flags).

3. `configure_development_defaults() -> None`
   - Tests should verify that development defaults are correctly set in the registry.
   - Should test the interaction with the registry singleton.

## Testing Philosophy

These functions interact with external systems (database) and maintain global state (registry singleton). Following best practices:

- We avoid using mocks for these tests as they would not provide meaningful coverage.
- Integration tests that use a real (test) database are more appropriate.
- The tests should be placed in the `tests/integration/` directory.

## Current Coverage

Current coverage for `src/utils/feature_flags/feature_flags.py` is 30%, with the following lines missing:

```
34-38, 88-104, 118-127
```

These lines correspond to the functions mentioned above that require integration tests.
