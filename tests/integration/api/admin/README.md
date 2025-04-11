# Admin API Tests

This directory contains integration tests for the Debtonator Admin API endpoints. These tests verify that the administrative functionality works correctly and follows proper error handling and security patterns.

## Testing Approach

Admin API tests follow these principles:

1. **Real Components**: Tests use real services and repositories, not mocks
2. **Database Testing**: Tests interact with a real test database
3. **Feature Management**: Tests verify proper management of system features
4. **Error Handling**: Tests verify correct error responses for invalid inputs
5. **Security**: Tests validate proper enforcement of access controls

## Directory Structure

```
admin/
├── README.md                        # This file
├── test_feature_flags_admin_api.py  # Tests for feature flag management API
└── test_*.py                        # Tests for other admin endpoints
```

## Test Guidelines

### Feature Flag Admin API Tests

The feature flag admin API tests should verify:

1. **Requirements Management**: Proper getting and updating of feature flag requirements
2. **Flag Listing**: Proper listing of all feature flags
3. **Flag Details**: Correct retrieval of individual flag details
4. **Flag Updates**: Proper updating of flag values and settings
5. **Default Requirements**: Access to default requirements
6. **Error Handling**: Proper error responses for invalid inputs or non-existent flags

Note: History and metrics endpoints are placeholders in the current implementation.

### Example Test Structure

```python
async def test_update_flag_requirements(client, db_session, test_boolean_flag):
    """Test updating feature flag requirements."""
    # Prepare test data
    requirements = {
        "repository": {
            "create_typed_account": ["bnpl", "ewa", "payment_app"]
        },
        "service": {
            "create_account": ["bnpl", "ewa", "payment_app"]
        }
    }
    
    # Execute request
    response = await client.put(
        f"/api/admin/feature-flags/{test_boolean_flag.name}/requirements",
        json={"requirements": requirements}
    )
    
    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert result["flag_name"] == test_boolean_flag.name
    assert "repository" in result["requirements"]
    assert "service" in result["requirements"]
    
    # Verify database changes
    flag_repository = FeatureFlagRepository(db_session)
    flag = await flag_repository.get(test_boolean_flag.name)
    assert flag.requirements is not None
    assert flag.requirements["repository"]["create_typed_account"] == ["bnpl", "ewa", "payment_app"]
