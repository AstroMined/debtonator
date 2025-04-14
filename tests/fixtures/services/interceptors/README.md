# Service Interceptor Test Fixtures

This directory contains fixture functions for testing service interceptor components in the Debtonator application. Service interceptors provide a mechanism to enforce cross-cutting concerns like feature flags at the service layer.

## Related Documentation

- [Parent Service Fixtures README](../README.md)
- [Feature Flag System: Service Layer Implementation](/code/debtonator/docs/active_context.md#feature-flag-system)
- [System Patterns: Service Patterns](/code/debtonator/docs/system_patterns.md#service-patterns)

## Architecture

Service interceptors follow the interceptor design pattern, where they intercept method calls on service objects:

```flow
API Layer
    │
    ▼
┌──────────────────────┐
│ ServiceInterceptor   │
│ ┌────────────────┐   │
│ │ Real Service   │   │
│ └────────────────┘   │
└──────────────────────┘
    │
    ▼
Repository Layer
```

## Implementation Patterns

### Service Interceptor Pattern

The service interceptor pattern allows for interception of service method calls:

```python
class FeatureFlagServiceInterceptor:
    """Interceptor that enforces feature flags on service operations."""
    
    def __init__(
        self, 
        service: Any,
        feature_flag_service,
        required_flag: str
    ):
        self._service = service
        self._feature_flag_service = feature_flag_service
        self._required_flag = required_flag
        
    async def __call__(self, method_name: str, *args, **kwargs):
        """Intercept method call and check feature flag."""
        await self._check_feature_flag()
        method = getattr(self._service, method_name)
        return await method(*args, **kwargs)
```

### Service Proxy Pattern

Service proxies use interceptors to provide a transparent wrapper around services:

```python
class ServiceProxy:
    """Proxy that uses interceptors for service method calls."""
    
    def __init__(
        self, 
        service: Any,
        interceptors: List[Callable]
    ):
        self._service = service
        self._interceptors = interceptors
        
    def __getattr__(self, name):
        """Get attribute from service, wrapping methods with interceptors."""
        attr = getattr(self._service, name)
        
        if callable(attr) and asyncio.iscoroutinefunction(attr):
            async def intercepted(*args, **kwargs):
                # Apply interceptors in order
                for interceptor in self._interceptors:
                    await interceptor(name, *args, **kwargs)
                return await attr(*args, **kwargs)
            return intercepted
        return attr
```

## Available Fixtures

### Feature Flag Service Interceptor Fixtures

- **feature_flag_service_interceptor**: Fixture for FeatureFlagServiceInterceptor testing
- **feature_flag_service_interceptor_factory**: Factory for creating interceptors

### Logging Service Interceptor Fixtures

- **logging_service_interceptor**: Fixture for LoggingServiceInterceptor testing
- **test_logger**: Test logger for service operation logging

### Authentication Service Interceptor Fixtures

- **auth_service_interceptor**: Fixture for AuthServiceInterceptor testing
- **test_auth_context**: Test authentication context for service operations

## Testing Strategy

The service interceptor fixtures in this directory support testing:

1. **Method Interception**: Verify interceptors handle service method calls
2. **Feature Flag Enforcement**: Test feature flag checks before service operations
3. **Logging**: Test logging of service operations
4. **Authentication**: Test authentication checks for service operations
5. **Exception Handling**: Test interceptor handling of service exceptions
6. **Interceptor Chaining**: Test multiple interceptors applied to service methods

## Best Practices

1. **Real Services**: Use real service instances for interceptors to wrap
2. **Complete Method Coverage**: Test all methods that interceptors handle
3. **Feature Flag Testing**: Test with different feature flag configurations
4. **Error Cases**: Test interceptor behavior when services raise exceptions
5. **Interceptor Order**: Test interceptor application order
6. **Integration Testing**: Test interceptor integration with API layer

## Example Service Interceptor Test

```python
async def test_feature_flag_service_interceptor(
    account_service: AccountService,
    feature_flag_service,
    feature_flag_service_interceptor_factory
):
    """Test feature flag enforcement by service interceptor."""
    # Create interceptor for account service
    interceptor = feature_flag_service_interceptor_factory.create_interceptor(
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
    
    # Interceptor should raise an exception
    with pytest.raises(FeatureFlagDisabledError):
        await interceptor("create_account", account_data)
    
    # Enable the feature flag
    await feature_flag_service.enable_flag("INTERNATIONAL_ACCOUNTS")
    
    # Interceptor should allow operation
    account = await interceptor("create_account", account_data)
    assert account is not None
    assert account.name == "International Account"
    assert account.currency == "EUR"
```

## Known Considerations

1. **Method Signature Matching**: Interceptors must handle service method signatures
2. **Async Method Handling**: Interceptors must handle async service methods
3. **Exception Propagation**: Interceptors should properly propagate service exceptions
4. **Transparent Wrapping**: Interceptors should be transparent to calling code
5. **Performance Overhead**: Interceptors add overhead to service operations
6. **Dynamic Method Access**: Interceptors need to handle dynamic method access
