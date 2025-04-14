# Feature Flag Testing Utilities

This document provides information about the feature flag testing utilities in the `feature_flag_utils.py` module. These utilities help create a consistent testing environment for feature flags across the Debtonator application.

## Purpose

The feature flag testing utilities serve several important purposes:

1. **Consistent Testing Environment**: Provide a standard approach for testing with feature flags
2. **Cache Control**: Solve caching-related issues that occur in test environments
3. **Test Data Creation**: Simplify creating test data for feature flag tests
4. **Immediate Flag Updates**: Ensure feature flag changes take effect immediately in tests

## Key Components

### ZeroTTLConfigProvider

A specialized config provider that disables caching to ensure feature flag changes take effect immediately in tests:

```python
from tests.helpers.feature_flag_utils import ZeroTTLConfigProvider

# Create provider with zero TTL
config_provider = ZeroTTLConfigProvider({
    "BANKING_ACCOUNT_TYPES": {
        "repository": {
            "create_typed_entity": ["checking", "savings"]
        }
    }
})

# Use in test setup
feature_flag_service = FeatureFlagService(config_provider=config_provider)
```

### Feature Flag Test Helpers

Functions to simplify common testing tasks:

#### `create_test_requirements(flag_name, account_type)`

Creates standardized test requirements for a feature flag:

```python
from tests.helpers.feature_flag_utils import create_test_requirements

# Create standardized requirements
requirements = create_test_requirements("CHECKING_ACCOUNTS", "checking")

# Use in test setup
config_provider = ZeroTTLConfigProvider(requirements)
```

#### `clear_config_provider_cache(config_provider)`

Manually clears a config provider's cache:

```python
from tests.helpers.feature_flag_utils import clear_config_provider_cache

# Clear cache to ensure changes take effect
clear_config_provider_cache(config_provider)
```

#### `set_flag_and_clear_cache(feature_flag_service, flag_name, enabled, repository_proxy=None)`

Sets a feature flag and clears the repository proxy cache in one operation:

```python
from tests.helpers.feature_flag_utils import set_flag_and_clear_cache

# Set flag and clear cache in one operation
await set_flag_and_clear_cache(
    feature_flag_service, 
    "CHECKING_ACCOUNTS", 
    True,
    repository_proxy
)
```

## Usage Examples

### Basic Feature Flag Testing

```python
import pytest
from tests.helpers.feature_flag_utils import ZeroTTLConfigProvider, create_test_requirements

@pytest.fixture
async def feature_flag_config():
    """Create a zero-TTL config provider for testing."""
    # Create requirements for checking accounts
    requirements = create_test_requirements("CHECKING_ACCOUNTS", "checking")
    
    # Create provider with zero TTL
    return ZeroTTLConfigProvider(requirements)

@pytest.fixture
async def feature_flag_service(feature_flag_config):
    """Create a feature flag service with test configuration."""
    return FeatureFlagService(config_provider=feature_flag_config)

async def test_feature_flag_enforcement(
    account_repository, feature_flag_service, db_session
):
    """Test that feature flags properly control access to account types."""
    # Disable checking accounts
    await feature_flag_service.set_enabled("CHECKING_ACCOUNTS", False)
    
    # Create checking account schema
    checking_schema = create_checking_account_schema(name="Test Checking")
    
    # Attempt to create checking account (should raise FeatureDisabledException)
    with pytest.raises(FeatureDisabledException):
        await account_repository.create_typed_entity(
            "checking", checking_schema.model_dump()
        )
    
    # Enable checking accounts
    await feature_flag_service.set_enabled("CHECKING_ACCOUNTS", True)
    
    # Now creation should succeed
    account = await account_repository.create_typed_entity(
        "checking", checking_schema.model_dump()
    )
    
    # Verify account was created
    assert account is not None
    assert account.name == "Test Checking"
    assert account.account_type == "checking"
```

### Testing with Repository Proxy

```python
from tests.helpers.feature_flag_utils import set_flag_and_clear_cache

async def test_repository_proxy_integration(
    account_repository_proxy, feature_flag_service
):
    """Test integration with repository proxy."""
    # Set flag and clear cache in one operation
    await set_flag_and_clear_cache(
        feature_flag_service,
        "CHECKING_ACCOUNTS",
        True,
        account_repository_proxy
    )
    
    # Now proxy should allow operation
    checking_schema = create_checking_account_schema(name="Test Checking")
    account = await account_repository_proxy.create_typed_entity(
        "checking", checking_schema.model_dump()
    )
    
    # Verify account was created
    assert account is not None
```

## Best Practices

1. **Use ZeroTTLConfigProvider**: Always use ZeroTTLConfigProvider for tests to avoid caching issues
2. **Clear Cache After Flag Changes**: Clear cache after changing flags to ensure immediate effect
3. **Use set_flag_and_clear_cache**: Combines setting flag and clearing cache in one operation
4. **Create Standardized Requirements**: Use create_test_requirements for consistent test data
5. **Test Both Enabled and Disabled States**: Always test both states for comprehensive coverage

## Related Documentation

- [Feature Flag System](../../../../docs/adr/021-feature-flag-system.md)
- [Feature Flag Service Tests](../../unit/services/feature_flags/test_feature_flag_service.py)
- [Repository Proxy Tests](../../integration/repositories/test_factory.py)
