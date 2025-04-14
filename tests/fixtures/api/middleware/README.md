# API Middleware Test Fixtures

This directory contains fixture functions for testing middleware components in the FastAPI application of the Debtonator project. Middleware components intercept HTTP requests and responses and provide cross-cutting functionality.

## Related Documentation

- [Parent API Fixtures README](../README.md)
- [Service Fixtures README](../../services/README.md)
- [Feature Flag System: Middleware Pattern](../../../../docs/system_patterns.md#feature-flag-system)

## Architecture

Middleware components in FastAPI follow a standard pattern where they intercept requests before they reach route handlers and can also modify responses:

```flow
HTTP Request
    │
    ▼
┌────────────────┐
│  Middleware 1  │
└────────────────┘
    │
    ▼
┌────────────────┐
│  Middleware 2  │
└────────────────┘
    │
    ▼
┌────────────────┐
│  Route Handler │
└────────────────┘
    │
    ▼
HTTP Response
```

## Implementation Patterns

### Middleware Test Pattern

Middleware tests directly instantiate middleware classes and test their behavior with mock requests and response handlers:

```python
@pytest_asyncio.fixture
async def feature_flag_middleware(
    feature_flag_service
) -> FeatureFlagMiddleware:
    """
    Create a FeatureFlagMiddleware instance for testing.
    
    This fixture provides an isolated middleware component for
    testing feature flag enforcement.
    """
    return FeatureFlagMiddleware(feature_flag_service=feature_flag_service)
```

### Request Factory Pattern

Tests create mock requests to test middleware behavior:

```python
@pytest_asyncio.fixture
def test_request_factory():
    """
    Factory function for creating test requests.
    
    This fixture provides a function to create test requests with
    specific paths, headers, and other attributes.
    """
    def _create_request(path: str, headers: dict = None, **kwargs):
        scope = {
            "type": "http",
            "path": path,
            "headers": [(k.encode(), v.encode()) for k, v in (headers or {}).items()],
            **kwargs
        }
        return Request(scope=scope)
    
    return _create_request
```

### Response Factory Pattern

Tests create mock response handlers to test middleware behavior:

```python
@pytest_asyncio.fixture
def test_response_factory():
    """
    Factory function for creating test response handlers.
    
    This fixture provides a function to create test response handlers
    with specific status codes and response bodies.
    """
    def _create_response_handler(status_code: int = 200, body: dict = None):
        async def call_next(request):
            return JSONResponse(
                status_code=status_code,
                content=body or {}
            )
        return call_next
    
    return _create_response_handler
```

## Available Fixtures

### Feature Flag Middleware Fixtures

- **feature_flag_middleware**: FeatureFlagMiddleware instance for testing
- **feature_flag_test_requests**: Predefined requests for feature flag tests
- **feature_flag_path_patterns**: Path patterns for feature flag enforcement

### Authentication Middleware Fixtures

- **auth_middleware**: AuthMiddleware instance for testing
- **auth_test_requests**: Predefined requests for authentication tests
- **auth_test_tokens**: Test tokens for authentication tests

### Logging Middleware Fixtures

- **logging_middleware**: LoggingMiddleware instance for testing
- **logging_test_requests**: Predefined requests for logging tests
- **test_logger**: Test logger for logging assertions

### Error Handling Middleware Fixtures

- **error_middleware**: ErrorHandlingMiddleware instance for testing
- **error_test_requests**: Predefined requests for error handling tests
- **error_generators**: Functions that generate specific errors for testing

## Testing Strategy

The middleware fixtures in this directory support testing:

1. **Request Interception**: Middleware handling of incoming requests
2. **Response Modification**: Middleware modification of responses
3. **Error Handling**: Middleware handling of errors during request processing
4. **Feature Flag Enforcement**: Enforcement of feature flags on protected paths
5. **Authentication**: Verification of authentication tokens and permissions
6. **Logging**: Proper logging of requests and responses
7. **Cross-Cutting Concerns**: Other cross-cutting functionality implemented by middleware

## Best Practices

1. **Isolated Testing**: Test middleware components in isolation
2. **Real Dependencies**: Use real service instances for middleware dependencies
3. **Mock Requests**: Use mock requests to test different request scenarios
4. **Complete Flow**: Test the entire request/response flow through middleware
5. **Error Cases**: Test middleware behavior with error conditions
6. **Feature Flag Testing**: Test with different feature flag configurations
7. **Path Pattern Testing**: Test middleware path matching patterns
8. **Header Testing**: Test middleware header handling

## Example Middleware Test

```python
async def test_feature_flag_middleware_disabled_flag(
    feature_flag_middleware: FeatureFlagMiddleware,
    feature_flag_service,
    test_request_factory,
    test_response_factory
):
    """Test feature flag middleware blocks request when flag is disabled."""
    # Create test request for a path that requires a feature flag
    request = test_request_factory("/api/v1/international-accounts")
    
    # Create mock response handler
    response_handler = test_response_factory(200, {"message": "Success"})
    
    # Disable the feature flag
    await feature_flag_service.disable_flag("INTERNATIONAL_ACCOUNTS")
    
    # Middleware should raise an exception
    with pytest.raises(FeatureFlagDisabledError):
        await feature_flag_middleware(request, response_handler)
    
    # Enable the feature flag
    await feature_flag_service.enable_flag("INTERNATIONAL_ACCOUNTS")
    
    # Middleware should allow request
    response = await feature_flag_middleware(request, response_handler)
    assert response.status_code == 200
    
    # Response body should be unchanged
    body = json.loads(await response.body())
    assert body == {"message": "Success"}
```

## Known Considerations

1. **Request Scope**: Request objects must have a valid scope dictionary
2. **Response Handling**: Response handling functions must be async
3. **Exception Propagation**: Middleware may raise exceptions that need to be caught
4. **Order Dependence**: Middleware execution order can affect behavior
5. **Stateful Middleware**: Some middleware may be stateful and require cleanup
6. **Path Pattern Matching**: Path patterns use regex-style matching rules
