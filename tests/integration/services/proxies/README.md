# Repository Proxies Tests

## Purpose

This directory contains tests for repository proxies in Debtonator. These tests validate the functionality of repository proxies, which provide cross-cutting concerns like feature flag enforcement at the repository layer boundary.

## Related Documentation

- [Services Integration Tests](../README.md)
- [Interceptors Tests](../interceptors/README.md)
- [ADR-024: Feature Flag System](/code/debtonator/docs/adr/feature_flags/adr024-feature-flag-system.md)

## Architecture

Repository proxies implement the proxy pattern to provide cross-cutting concerns at the repository layer boundary. The primary proxy is the FeatureFlagRepositoryProxy, which enforces feature flag requirements before allowing repository operations to execute.

## Implementation Patterns

### Testing Feature Flag Repository Proxy

Tests for the feature flag repository proxy verify that feature flags are correctly enforced:

```python
async def test_feature_flag_repository_proxy(db_session, feature_flag_service):
    """Test feature flag repository proxy enforces feature flags."""
    # Create a feature flag service with test configuration
    feature_flag_service = FeatureFlagService(db_session)
    
    # Create a repository with the proxy
    repository = FeatureFlagRepositoryProxy(
        AccountRepository(db_session),
        feature_flag_service
    )
    
    # Set up test data
    account_data = {
        "name": "Test Account",
        "account_type": "ewa",  # Feature-controlled account type
        # Other required fields...
    }
    
    # Disable the feature flag
    await feature_flag_service.update_feature_flag(
        feature_name="BANKING_ACCOUNT_TYPES_ENABLED",
        value=False
    )
    
    # Operation should be blocked
    with pytest.raises(FeatureDisabledError) as excinfo:
        await repository.create_typed_entity("ewa", account_data)
    
    # Verify error details
    assert excinfo.value.feature_name == "BANKING_ACCOUNT_TYPES_ENABLED"
    assert excinfo.value.entity_type == "account_type"
    assert excinfo.value.entity_id == "ewa"
        
    # Enable the feature flag
    await feature_flag_service.update_feature_flag(
        feature_name="BANKING_ACCOUNT_TYPES_ENABLED",
        value=True
    )
    
    # Operation should now succeed
    result = await repository.create_typed_entity("ewa", account_data)
    assert result is not None
    assert result.account_type == "ewa"
```

## Testing Focus Areas

### Feature Flag Enforcement

Test that proxies correctly enforce feature flags:

1. **Method-Level Enforcement**: Verify that feature flags are enforced at method boundaries
2. **Type-Based Requirements**: Test requirements based on polymorphic entity types
3. **Error Handling**: Verify appropriate errors are raised when features are disabled
4. **Caching**: Test that proxy caching of feature flag values works correctly

### Proxy Transparency

Test that proxies are transparent to service layer code:

```python
async def test_proxy_transparency(db_session, feature_flag_service):
    """Test proxy is transparent to service layer code."""
    # Create a repository and wrap it with proxy
    base_repo = AccountRepository(db_session)
    proxied_repo = FeatureFlagRepositoryProxy(base_repo, feature_flag_service)
    
    # Verify proxy has same methods as base repository
    for method_name in dir(base_repo):
        if not method_name.startswith("_") and callable(getattr(base_repo, method_name)):
            assert hasattr(proxied_repo, method_name)
            assert callable(getattr(proxied_repo, method_name))
    
    # Verify proxy delegates to base repository when feature is enabled
    await feature_flag_service.update_feature_flag(
        feature_name="BANKING_ACCOUNT_TYPES_ENABLED",
        value=True
    )
    
    # Create test account through proxy
    account_data = {
        "name": "Test Account",
        "account_type": "checking",
        # Other required fields...
    }
    
    # Operation should succeed and return same result as base repository would
    result = await proxied_repo.create_typed_entity("checking", account_data)
    assert result is not None
    assert result.account_type == "checking"
```

## Best Practices

1. **Isolation**: Test proxies in isolation from business logic
2. **Real Objects**: Use real repositories and database sessions
3. **Error Handling**: Verify appropriate errors are raised when feature flags are disabled
4. **Transparency**: Test that proxies are transparent to service layer code
5. **Caching**: Test that proxy caching works correctly

## Testing Guidelines

When testing repository proxies:

1. Create a repository and wrap it with the proxy
2. Test that feature flags are correctly enforced
3. Test error handling when feature flags are disabled
4. Test proxy transparency to service layer code
5. Test caching behavior of the proxy
6. Test integration with other components of the feature flag system

## Important Note

While this directory contains tests for the general proxy functionality, specific tests for how feature flags affect repositories are found in a separate test suite. The tests here focus only on the proxy mechanism itself, not on how feature flags affect repository business logic.
