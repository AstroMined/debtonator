# Repository Proxies Tests

This directory contains integration tests for repository proxies in the Debtonator application. Repository proxies are a core component of the Feature Flag System defined in ADR-024, providing a centralized way to enforce feature flag requirements at the repository layer.

## What are Repository Proxies?

Repository proxies intercept method calls to repositories, check if the methods are allowed based on feature flag requirements, and either pass the call through or block it with a `FeatureDisabledError`. This pattern provides:

1. **Centralized Feature Flag Enforcement**: Instead of scattered feature flag checks throughout the codebase
2. **Consistent Error Handling**: Standardized errors for disabled features
3. **Dynamic Configuration**: Feature requirements can be updated at runtime
4. **Transparent Integration**: Minimal changes to existing repository code

## Test Organization

Tests in this directory are organized by proxy type:

- `test_feature_flag_proxy_integration.py`: Tests for the `FeatureFlagRepositoryProxy`

## Testing Patterns

Repository proxy tests follow these patterns:

### 1. Test Categories

Repository proxy tests are divided into categories:

- **Basic Proxy Functionality**: Testing pass-through behavior for methods and attributes
- **Feature Flag Enforcement**: Testing blocking/allowing methods based on feature flags
- **Account Type Extraction**: Testing extraction from different parameter patterns
- **Caching and Performance**: Testing caching behavior and fallback mechanisms

### 2. Test Fixtures

Fixtures are in `tests/fixtures/repositories/proxies/` and include:

- Test repositories with known methods and attributes
- Feature flag services with pre-configured flags
- Config providers with known requirements
- Ready-to-use proxy instances with different configurations

### 3. The Four-Step Pattern

Similar to repository tests, proxy tests follow a four-step pattern:

1. **Arrange**: Set up test data, feature flags, and repositories
2. **Act**: Call methods through the proxy
3. **Assert**: Verify correct behavior (pass-through or block)
4. **Reset**: Reset state for subsequent tests where needed

## Examples

### Testing Pass-Through Behavior

```python
@pytest.mark.asyncio
async def test_proxy_passes_through_allowed_methods(feature_flag_proxy):
    """Test that the proxy correctly passes through allowed method calls."""
    # Arrange - use the proxy fixture
    
    # Act - call a method that should be allowed
    result = await feature_flag_proxy.test_method(account_type="test_account_type")
    
    # Assert - verify the method was called and returned correctly
    assert "Test method called with test_account_type" == result
```

### Testing Feature Flag Enforcement

```python
@pytest.mark.asyncio
async def test_proxy_blocks_disabled_feature(feature_flag_proxy, feature_flag_service):
    """Test that the proxy blocks methods when feature is disabled."""
    # Arrange - disable the feature
    await feature_flag_service.set_enabled("TEST_FEATURE", False)
    
    # Act & Assert - attempt to call method should raise error
    with pytest.raises(FeatureDisabledError) as exc_info:
        await feature_flag_proxy.test_method(account_type="test_account_type")
    
    # Verify error details
    assert exc_info.value.feature_name == "TEST_FEATURE"
```

## Relationship with Other Tests

Repository proxy tests complement:

- **Repository Tests**: Test the underlying repository functionality
- **Feature Flag Tests**: Test the feature flag service functionality
- **Service Tests**: Test the service layer's use of repository proxies

## Key Principles

1. **Real Objects**: Use real feature flag services and repositories
2. **Comprehensive Coverage**: Test all proxy behaviors
3. **Isolation**: Test only the proxy's behavior, not the repository's
4. **Proper Reset**: Reset feature flags after tests to avoid affecting other tests
