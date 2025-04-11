# API Integration Tests

This directory contains integration tests for the Debtonator API layer. These tests verify that the API endpoints correctly integrate with the service layer and apply proper validation, error handling, and feature flag enforcement.

## Directory Structure

```
api/
├── README.md              # This file
├── middleware/            # Tests for API middleware components
│   ├── README.md          # Middleware testing guidelines
│   └── test_*.py          # Tests for specific middleware
├── admin/                 # Tests for admin API endpoints
│   └── test_*.py          # Tests for admin endpoints
└── v1/                    # Tests for v1 API endpoints
    └── test_*.py          # Tests for v1 endpoints
```

## Testing Approach

API integration tests follow these principles:

1. **End-to-End Testing**: Tests include the entire request/response cycle
2. **Real Components**: Tests use real services and repositories, not mocks
3. **Database Testing**: Tests interact with a real test database
4. **Feature Flag Testing**: Tests verify behavior with both enabled and disabled features
5. **Error Case Testing**: Tests verify proper error responses for invalid inputs

## Test Structure

Each API test should follow this structure:

1. **Setup**: Initialize test client and required dependencies
2. **Prepare Data**: Create any necessary database fixtures
3. **Execute Request**: Send HTTP request to the endpoint
4. **Verify Response**: Assert on response status code and content
5. **Verify Side Effects**: Check database changes if applicable
6. **Cleanup**: Reset any state changes

## Example API Test

```python
async def test_create_account_valid_data(client, db_session):
    """Test creating a valid account through the API."""
    # Prepare data
    account_data = {
        "name": "Test Account",
        "account_type": "checking",
        "available_balance": "1000.00",
        "current_balance": "1000.00"
    }
    
    # Execute request
    response = client.post("/api/v1/accounts", json=account_data)
    
    # Verify response
    assert response.status_code == 201
    result = response.json()
    assert result["name"] == "Test Account"
    assert result["account_type"] == "checking"
    
    # Verify database changes
    account_repository = AccountRepository(db_session)
    account = await account_repository.get_by_id(result["id"])
    assert account is not None
    assert account.name == "Test Account"
```

## Testing Feature Flags

For feature flag testing, each endpoint should have tests for both enabled and disabled states:

```python
async def test_create_ewa_account_feature_disabled(client, feature_flag_service):
    """Test creating an EWA account when the feature is disabled."""
    # Disable the feature flag
    await feature_flag_service.set_enabled("BANKING_ACCOUNT_TYPES_ENABLED", False)
    
    # Prepare data
    account_data = {
        "name": "Test EWA Account",
        "account_type": "ewa",
        "available_balance": "1000.00",
        "current_balance": "1000.00",
        "provider": "DailyPay"
    }
    
    # Execute request
    response = client.post("/api/v1/accounts", json=account_data)
    
    # Verify feature flag error
    assert response.status_code == 403
    assert response.json()["message"].startswith("Operation not available")
    assert "BANKING_ACCOUNT_TYPES_ENABLED" in response.json()["feature_flag"]
