# Service Proxy Test Fixtures

This directory contains fixture functions for testing service proxy components in the Debtonator application. Service proxies wrap service instances to provide cross-cutting functionality like feature flag enforcement, logging, and caching.

## Related Documentation

- [Parent Service Fixtures README](../README.md)
- [Service Interceptors README](../interceptors/README.md)
- [Feature Flag System: Service Layer Implementation](/code/debtonator/docs/active_context.md#feature-flag-system)
- [System Patterns: Service Patterns](/code/debtonator/docs/system_patterns.md#service-patterns)

## Architecture

Service proxies follow the proxy design pattern, where they wrap service instances and intercept method calls:

```flow
API Layer
    │
    ▼
┌───────────────────────┐
│ ServiceProxy          │
│ ┌─────────────────┐   │
│ │ Real Service    │   │
│ └─────────────────┘   │
└───────────────────────┘
    │
    ▼
Repository Layer
```

## Implementation Patterns

### Service Proxy Pattern

The service proxy pattern creates a wrapper around service instances:

```python
class FeatureFlagServiceProxy:
    """Proxy that enforces feature flags on service operations."""
    
    def __init__(
        self, 
        service: Any,
        feature_flag_service,
        required_flag: str
    ):
        self._service = service
        self._feature_flag_service = feature_flag_service
        self._required_flag = required_flag
        
    def __getattr__(self, name):
        """Get attribute from service, checking feature flag for methods."""
        attr = getattr(self._service, name)
        
        if callable(attr) and asyncio.iscoroutinefunction(attr):
            async def wrapped(*args, **kwargs):
                await self._check_feature_flag()
                return await attr(*args, **kwargs)
            return wrapped
        return attr
```

### Dynamic Proxy Creation Pattern

Dynamic proxy creation allows for flexible proxy configurations:

```python
@pytest_asyncio.fixture
async def service_proxy_factory(
    feature_flag_service
) -> ServiceProxyFactory:
    """
    Create a ServiceProxyFactory for testing.
    
    This fixture provides a factory that creates service
    proxies with appropriate dependencies.
    """
    factory = ServiceProxyFactory(feature_flag_service=feature_flag_service)
    return factory
```

## Available Fixtures

### Feature Flag Service Proxy Fixtures

- **feature_flag_service_proxy**: Fixture for FeatureFlagServiceProxy testing
- **feature_flag_service_proxy_factory**: Factory for creating proxies

### Caching Service Proxy Fixtures

- **caching_service_proxy**: Fixture for CachingServiceProxy testing
- **cache_manager**: Test cache manager for service method caching

### Logging Service Proxy Fixtures

- **logging_service_proxy**: Fixture for LoggingServiceProxy testing
- **test_logger**: Test logger for service operation logging

## Testing Strategy

The service proxy fixtures in this directory support testing:

1. **Method Interception**: Verify proxy intercepts service methods
2. **Feature Flag Enforcement**: Test feature flag checks before service operations
3. **Caching Behavior**: Test cache hit/miss behavior for service methods
4. **Logging**: Test logging of service operations
5. **Exception Handling**: Test proxy handling of service exceptions
6. **Proxy Chaining**: Test multiple proxies applied to service instances

## Best Practices

1. **Real Services**: Use real service instances for proxies to wrap
2. **Complete Method Coverage**: Test all methods that proxies intercept
3. **Feature Flag Testing**: Test with different feature flag configurations
4. **Error Cases**: Test proxy behavior when services raise exceptions
5. **Performance Testing**: Test caching behavior for performance improvements
6. **Integration Testing**: Test proxy integration with API layer

## Example Service Proxy Test

```python
async def test_feature_flag_service_proxy(
    account_service: AccountService,
    feature_flag_service,
    feature_flag_service_proxy_factory
):
    """Test feature flag enforcement by service proxy."""
    # Create proxy for account service
    proxy = feature_flag_service_proxy_factory.create_proxy(
        service=account_service,
        required_flag="INTERNATIONAL_ACCOUNTS"
    )
    
    # Create account data
    account_data = {
        "name": "International Account",
        "account_type": "checking",
        "currency": "EUR"
    }
    
    # Disable the feature flag
    await feature_flag_service.disable_flag("INTERNATIONAL_ACCOUNTS")
    
    # Proxy should raise an exception
    with pytest.raises(FeatureFlagDisabledError):
        await proxy.create_account(account_data)
    
    # Enable the feature flag
    await feature_flag_service.enable_flag("INTERNATIONAL_ACCOUNTS")
    
    # Proxy should allow operation
    account = await proxy.create_account(account_data)
    assert account is not None
    assert account.name == "International Account"
    assert account.currency == "EUR"
```

## Known Considerations

1. **Method Signature Matching**: Proxy methods must match service method signatures
2. **Async Method Handling**: All proxy methods must handle async service methods
3. **Exception Propagation**: Proxies should properly propagate service exceptions
4. **Transparent Proxying**: Proxies should be transparent to calling code
5. **Performance Overhead**: Proxies add overhead to service operations
6. **Proxy vs. Interceptor**: Understand the difference between proxies and interceptors
   - Proxies wrap service instances directly
   - Interceptors focus on method interception and chaining
   - Both serve similar purposes with different implementation approaches
