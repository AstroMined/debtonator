# API Test Fixtures

This directory contains fixture functions for testing the FastAPI endpoints and related API components of the Debtonator application. These fixtures support integration testing of the API layer with real services and repositories.

## Related Documentation

- [Parent Fixtures README](../README.md)
- [Service Fixtures README](../services/README.md)
- [Repository Fixtures README](../repositories/README.md)

## Architecture

The API fixtures mirror the structure of the API layer in the application:

```tree
api/
├── __init__.py
├── endpoints/         # API route handlers
├── middleware/        # FastAPI middleware components
├── dependencies/      # FastAPI dependency injection
└── schemas/          # Pydantic response/request models
```

## Implementation Patterns

### Test Client Pattern

API tests use the FastAPI TestClient to make HTTP requests to the application:

```python
@pytest_asyncio.fixture
async def test_client(app: FastAPI) -> AsyncGenerator[TestClient, None]:
    """
    Create a FastAPI TestClient for API testing.
    
    This fixture provides a test client that can make HTTP requests
    to the application endpoints.
    """
    client = TestClient(app)
    yield client
```

### Application Factory Pattern

API tests use an application factory to create a test instance of the FastAPI application:

```python
@pytest_asyncio.fixture
async def app(
    db_session: AsyncSession,
    repository_factory: RepositoryFactory,
    service_factory: ServiceFactory,
    feature_flag_service
) -> AsyncGenerator[FastAPI, None]:
    """
    Create a FastAPI application instance for testing.
    
    This fixture provides a fully configured application with
    test dependencies injected.
    """
    # Create test app with dependencies
    app = create_test_application(
        db_session=db_session,
        repository_factory=repository_factory,
        service_factory=service_factory,
        feature_flag_service=feature_flag_service
    )
    
    yield app
```

### Middleware Testing Pattern

API middleware tests use specialized fixtures to isolate and test middleware components:

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

## Available Subdirectories

### Middleware (`middleware/`)

Contains fixtures for testing FastAPI middleware components:

- Feature flag middleware
- Authentication middleware
- Logging middleware
- Error handling middleware

## Testing Strategy

The API fixtures in this directory support testing:

1. **Endpoint Functionality**: HTTP requests and responses for API endpoints
2. **Middleware Behavior**: Request/response processing by middleware components
3. **Dependency Injection**: Proper injection of dependencies into endpoints
4. **Authentication**: Authentication and authorization behavior
5. **Error Handling**: Proper error responses for various error conditions
6. **Integration Testing**: Cross-layer integration through API requests

## Best Practices

1. **Real Dependencies**: Use real service and repository instances
2. **Isolated Database**: Use a test database that resets between tests
3. **Feature Flag Testing**: Test with different feature flag configurations
4. **CRUD Testing**: Test all CRUD operations through API endpoints
5. **Status Code Verification**: Verify correct HTTP status codes for all responses
6. **Response Validation**: Validate response bodies against expected schemas
7. **Error Testing**: Test error conditions and verify proper error responses
8. **Integration Testing**: Test complete request/response flow through all layers

## Example API Test

```python
async def test_get_account_by_id(
    test_client: TestClient,
    test_checking_account: CheckingAccount
):
    """Test getting an account by ID through the API."""
    # Make API request
    response = test_client.get(f"/accounts/{test_checking_account.id}")
    
    # Verify status code
    assert response.status_code == 200
    
    # Verify response body
    data = response.json()
    assert data["id"] == test_checking_account.id
    assert data["name"] == test_checking_account.name
    assert data["account_type"] == "checking"
    assert "available_balance" in data
    assert "current_balance" in data
```

## Example Middleware Test

```python
async def test_feature_flag_middleware(
    feature_flag_middleware: FeatureFlagMiddleware,
    feature_flag_service
):
    """Test feature flag middleware enforcement."""
    # Create mock request with path that requires feature flag
    request = Request(scope={"type": "http", "path": "/api/v1/international-accounts"})
    
    # Create mock response function
    async def mock_call_next(request):
        return Response(status_code=200)
    
    # Test with feature flag disabled
    await feature_flag_service.disable_flag("INTERNATIONAL_ACCOUNTS")
    
    # Middleware should raise an exception
    with pytest.raises(FeatureFlagDisabledError):
        await feature_flag_middleware(request, mock_call_next)
    
    # Test with feature flag enabled
    await feature_flag_service.enable_flag("INTERNATIONAL_ACCOUNTS")
    
    # Middleware should allow request
    response = await feature_flag_middleware(request, mock_call_next)
    assert response.status_code == 200
```
