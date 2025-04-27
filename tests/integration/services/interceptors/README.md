# Service Interceptors Tests

## Purpose

This directory contains tests for service interceptors in Debtonator. These tests validate the functionality of service interceptors, which provide cross-cutting concerns like feature flag enforcement at the service layer boundary.

## Related Documentation

- [Services Integration Tests](../README.md)
- [Proxies Tests](../proxies/README.md)
- [ADR-024: Feature Flag System](/code/debtonator/docs/adr/feature_flags/adr024-feature-flag-system.md)

## Architecture

Service interceptors implement the interceptor pattern to provide cross-cutting concerns at the service layer boundary. The primary interceptor is the FeatureFlagInterceptor, which enforces feature flag requirements before allowing service methods to execute.

## Implementation Patterns

### Testing Feature Flag Interceptor

Tests for the feature flag interceptor verify that feature flags are correctly enforced:

```python
async def test_feature_flag_interceptor(db_session, feature_flag_service):
    """Test feature flag interceptor enforces feature flags."""
    # Create a feature flag service with test configuration
    feature_flag_service = FeatureFlagService(db_session)
    
    # Create a service with the feature flag service
    service = SomeService(
        session=db_session,
        feature_flag_service=feature_flag_service
    )
    
    # Set up test data
    test_data = {...}
    
    # Disable the feature flag
    await feature_flag_service.update_feature_flag(
        feature_name="SOME_FEATURE_FLAG",
        value=False
    )
    
    # Operation should be blocked
    with pytest.raises(FeatureDisabledError) as excinfo:
        await service.some_operation(test_data)
    
    # Verify error details
    assert excinfo.value.feature_name == "SOME_FEATURE_FLAG"
        
    # Enable the feature flag
    await feature_flag_service.update_feature_flag(
        feature_name="SOME_FEATURE_FLAG",
        value=True
    )
    
    # Operation should now succeed
    result = await service.some_operation(test_data)
    assert result is not None
```

## Testing Focus Areas

### Feature Flag Enforcement

Test that interceptors correctly enforce feature flags:

1. **Method-Level Enforcement**: Verify that feature flags are enforced at method boundaries
2. **Parameter-Based Requirements**: Test requirements based on input parameters
3. **Error Handling**: Verify appropriate errors are raised when features are disabled
4. **Propagation**: Test that feature flag changes propagate correctly

### Interceptor Configuration

Test that interceptors are correctly configured and attached to services:

```python
async def test_interceptor_configuration(db_session):
    """Test interceptor is correctly configured on service."""
    # Create service with feature flag service
    service = SomeService(
        session=db_session,
        feature_flag_service=FeatureFlagService(db_session)
    )
    
    # Verify service has interceptor
    assert hasattr(service, "_interceptor")
    assert isinstance(service._interceptor, FeatureFlagInterceptor)
    
    # Verify interceptor has feature flag service
    assert hasattr(service._interceptor, "_feature_flag_service")
    assert isinstance(service._interceptor._feature_flag_service, FeatureFlagService)
```

## Best Practices

1. **Isolation**: Test interceptors in isolation from business logic
2. **Real Objects**: Use real feature flag services and database sessions
3. **Error Handling**: Verify appropriate errors are raised when feature flags are disabled
4. **Configuration**: Test that interceptors are correctly configured and attached to services
5. **Performance**: Test any performance-related aspects like caching

## Testing Guidelines

When testing service interceptors:

1. Create a service with the appropriate feature flag service
2. Test that feature flags are correctly enforced
3. Test error handling when feature flags are disabled
4. Test configuration and attachment of interceptors
5. Test integration with other components of the feature flag system

## Important Note

While this directory contains tests for the general interceptor functionality, specific tests for how feature flags affect services are found in a separate test suite. The tests here focus only on the interceptor mechanism itself, not on how feature flags affect service business logic.
