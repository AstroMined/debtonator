# Repository Proxy Test Fixtures

This directory contains fixture functions for testing repository proxy components in the Debtonator application. Repository proxies intercept calls to repositories to provide cross-cutting functionality like feature flag enforcement.

## Related Documentation

- [Parent Repository Fixtures README](../README.md)
- [Feature Flag System: Repository Layer Implementation](/code/debtonator/docs/active_context.md#feature-flag-system)
- [System Patterns: Repository Patterns](/code/debtonator/docs/system_patterns.md#repository-patterns)

## Architecture

Repository proxies follow the proxy design pattern, where they wrap a real repository instance and intercept method calls:

```flow
Service Layer
    │
    ▼
┌───────────────────────┐
│ RepositoryProxy       │
│ ┌─────────────────┐   │
│ │ Real Repository │   │
│ └─────────────────┘   │
└───────────────────────┘
    │
    ▼
Database Layer
```

## Implementation Patterns

### Repository Proxy Pattern

The repository proxy pattern allows for interception of repository method calls:

```python
class FeatureFlagRepositoryProxy:
    """Proxy that enforces feature flags on repository operations."""
    
    def __init__(
        self, 
        repository: BaseRepository,
        feature_flag_service
    ):
        self._repository = repository
        self._feature_flag_service = feature_flag_service
        
    async def create(self, obj_in):
        """Check feature flag before creating entity."""
        await self._check_feature_flag()
        return await self._repository.create(obj_in)
```

### Repository Proxy Factory Pattern

Repository proxy factories create proxy instances for repositories:

```python
@pytest_asyncio.fixture
async def repository_proxy_factory(
    feature_flag_service
) -> RepositoryProxyFactory:
    """
    Create a RepositoryProxyFactory for testing.
    
    This fixture provides a factory that creates repository
    proxies with appropriate dependencies.
    """
    factory = RepositoryProxyFactory(feature_flag_service=feature_flag_service)
    return factory
```

## Available Fixtures

### Feature Flag Repository Proxy Fixtures

- **feature_flag_repository_proxy**: Fixture for FeatureFlagRepositoryProxy testing
- **feature_flag_repository_proxy_factory**: Factory for creating proxies

### Caching Repository Proxy Fixtures

- **caching_repository_proxy**: Fixture for CachingRepositoryProxy testing
- **cache_manager**: Test cache manager for repository caching

### Logging Repository Proxy Fixtures

- **logging_repository_proxy**: Fixture for LoggingRepositoryProxy testing
- **test_logger**: Test logger for repository operation logging

## Testing Strategy

The repository proxy fixtures in this directory support testing:

1. **Method Interception**: Verify proxy intercepts repository methods
2. **Feature Flag Enforcement**: Test feature flag checks before repository operations
3. **Caching Behavior**: Test cache hit/miss behavior for repository methods
4. **Logging**: Test logging of repository operations
5. **Exception Handling**: Test proxy handling of repository exceptions

## Best Practices

1. **Real Repositories**: Use real repository instances for proxies to wrap
2. **Complete Method Coverage**: Test all methods that the proxy intercepts
3. **Feature Flag Testing**: Test with different feature flag configurations
4. **Error Cases**: Test proxy behavior when repositories raise exceptions
5. **Performance Testing**: Test caching behavior for performance improvements
6. **Integration Testing**: Test proxy integration with service layer

## Example Repository Proxy Test

```python
async def test_feature_flag_repository_proxy(
    account_repository: AccountRepository,
    feature_flag_service,
    feature_flag_repository_proxy_factory
):
    """Test feature flag enforcement by repository proxy."""
    # Create proxy for account repository
    proxy = feature_flag_repository_proxy_factory.create_proxy(
        repository=account_repository,
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
        await proxy.create_typed_entity("checking", account_data)
    
    # Enable the feature flag
    await feature_flag_service.enable_flag("INTERNATIONAL_ACCOUNTS")
    
    # Proxy should allow operation
    account = await proxy.create_typed_entity("checking", account_data)
    assert account is not None
    assert account.name == "International Account"
    assert account.currency == "EUR"
```

## Known Considerations

1. **Method Signature Matching**: Proxy methods must match repository method signatures
2. **Async Method Handling**: All proxy methods must be async if repository methods are async
3. **Exception Propagation**: Proxies should properly propagate repository exceptions
4. **Transparent Proxying**: Proxies should be transparent to calling code
5. **Performance Overhead**: Proxies add overhead to repository operations
6. **Proxy Chaining**: Multiple proxies can be chained together
