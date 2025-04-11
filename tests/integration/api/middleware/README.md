# API Middleware Tests

This directory contains tests for Debtonator API middleware components. Middleware components intercept HTTP requests and responses to perform operations like authentication, logging, and feature flag enforcement.

## Directory Structure

```
middleware/
├── README.md                             # This file
├── test_feature_flag_middleware.py       # Tests for feature flag middleware
└── test_*.py                             # Tests for other middleware components
```

## Feature Flag Middleware Testing

The feature flag middleware enforces feature flag requirements at the API layer. Tests should verify:

1. **Enforcement**: Requests for disabled features are blocked with 403 Forbidden
2. **Passthrough**: Requests for enabled features are allowed
3. **Pattern Matching**: URL pattern matching works correctly
4. **Caching**: Caching behavior performs as expected
5. **Error Handling**: Configuration errors are handled properly

## Test Structure

Each middleware test should follow this pattern:

1. **Setup**: Create test application with middleware
2. **Configure**: Set up feature flags and requirements
3. **Execute**: Send requests that should and should not trigger the middleware
4. **Verify**: Assert on responses and side effects

## Example Test

```python
async def test_feature_flag_middleware_blocks_disabled_feature(app, client, feature_flag_service):
    """Test that the middleware blocks requests when features are disabled."""
    # Configure test requirements
    config_provider = InMemoryConfigProvider({
        "TEST_FEATURE": {
            "api": {
                "/api/v1/test-endpoint": ["*"]
            }
        }
    })
    
    # Disable feature flag
    await feature_flag_service.set_enabled("TEST_FEATURE", False)
    
    # Add middleware to app
    app.add_middleware(
        FeatureFlagMiddleware,
        feature_flag_service=feature_flag_service,
        config_provider=config_provider
    )
    
    # Execute request
    response = client.get("/api/v1/test-endpoint")
    
    # Verify response
    assert response.status_code == 403
    assert response.json()["message"].startswith("Operation not available")
    assert response.json()["feature_flag"] == "TEST_FEATURE"
```

## Testing Different Path Patterns

The middleware supports various path patterns, including:

1. **Exact paths**: `/api/v1/accounts`
2. **Path parameters**: `/api/v1/accounts/{account_id}`
3. **Wildcard paths**: `/api/v1/banking/*`

Tests should cover all these pattern types:

```python
async def test_middleware_path_pattern_matching(app, client, feature_flag_service):
    """Test that the middleware correctly matches different path patterns."""
    # Configure test requirements
    config_provider = InMemoryConfigProvider({
        "TEST_FEATURE": {
            "api": {
                # Exact path
                "/api/v1/exact-path": ["*"],
                # Path parameter
                "/api/v1/accounts/{account_id}": ["*"],
                # Wildcard path
                "/api/v1/banking/*": ["*"]
            }
        }
    })
    
    # Disable feature flag
    await feature_flag_service.set_enabled("TEST_FEATURE", False)
    
    # Add middleware to app
    app.add_middleware(
        FeatureFlagMiddleware,
        feature_flag_service=feature_flag_service,
        config_provider=config_provider
    )
    
    # Test exact path
    response = client.get("/api/v1/exact-path")
    assert response.status_code == 403
    
    # Test path parameter
    response = client.get("/api/v1/accounts/123")
    assert response.status_code == 403
    
    # Test wildcard path
    response = client.get("/api/v1/banking/overview")
    assert response.status_code == 403
    
    # Test non-matching path
    response = client.get("/api/v1/non-matching-path")
    assert response.status_code != 403
```

## Testing Caching Behavior

The middleware implements caching to improve performance. Tests should verify that caching works as expected:

```python
async def test_middleware_caching(app, client, feature_flag_service):
    """Test that the middleware caches requirements and respects TTL."""
    # Set up a mock config provider that counts calls
    mock_provider = MockConfigProvider()
    
    # Add middleware with short TTL
    app.add_middleware(
        FeatureFlagMiddleware,
        feature_flag_service=feature_flag_service,
        config_provider=mock_provider,
        cache_ttl=0.1  # 100ms TTL for testing
    )
    
    # First request should load requirements
    client.get("/api/v1/test-endpoint")
    assert mock_provider.call_count == 1
    
    # Second request within TTL should use cache
    client.get("/api/v1/test-endpoint")
    assert mock_provider.call_count == 1
    
    # Wait for cache to expire
    await asyncio.sleep(0.2)
    
    # Request after TTL should reload requirements
    client.get("/api/v1/test-endpoint")
    assert mock_provider.call_count == 2
