"""
Integration tests for the FeatureFlagRepositoryProxy.

This module tests the feature flag repository proxy that intercepts repository
method calls and enforces feature flag requirements. It verifies:

1. Basic proxy functionality (passing through methods)
2. Feature flag enforcement (allowing/blocking based on flags)
3. Account type extraction (from different parameter patterns)
4. Caching behavior (performance optimization)
"""

import pytest
import time
from typing import Dict, List, Any, Optional

from src.config.providers.feature_flags import InMemoryConfigProvider
from src.errors.feature_flags import FeatureDisabledError
from src.repositories.proxies.feature_flag_proxy import FeatureFlagRepositoryProxy
from src.schemas.feature_flags import FeatureFlagCreate, FeatureFlagType


pytestmark = pytest.mark.asyncio


# Basic proxy functionality tests
async def test_proxy_passes_through_allowed_methods(feature_flag_proxy):
    """
    Test that the proxy correctly passes through allowed method calls.
    
    The proxy should pass through methods that are allowed by feature flags,
    returning the same result as the underlying repository.
    """
    # Arrange - use the proxy fixture
    
    # Act - call a method that should be allowed
    result = await feature_flag_proxy.test_method(account_type="test_account_type")
    
    # Assert - verify the method was called and returned correctly
    assert "Test method called with test_account_type" == result


@pytest.mark.asyncio
async def test_proxy_passes_non_method_attributes(feature_flag_proxy, test_repository):
    """
    Test that the proxy passes through non-method attributes.
    
    The proxy should return the same value as the underlying repository
    for non-method attributes.
    """
    # Arrange - proxy and repository fixtures
    
    # Act - access a non-method attribute
    attr_value = feature_flag_proxy.non_method_attr
    
    # Assert - verify the attribute access works correctly
    assert attr_value == test_repository.non_method_attr
    assert attr_value == "test_attribute"


@pytest.mark.asyncio
async def test_proxy_works_with_any_account_type_using_wildcard(feature_flag_proxy):
    """
    Test that the proxy allows methods with any account type using wildcard.
    
    Methods with wildcard requirements should allow any account type.
    """
    # Arrange - proxy fixture
    
    # Act - call a method that has a wildcard requirement
    result = await feature_flag_proxy.get_by_id(1)
    
    # Assert - verify the method was allowed
    assert result["id"] == 1
    assert result["name"] == "Test Entity 1"


# Feature flag enforcement tests
@pytest.mark.asyncio
async def test_proxy_blocks_disabled_feature(feature_flag_proxy, feature_flag_service):
    """
    Test that the proxy blocks methods when feature is disabled.
    
    Methods that require a disabled feature should raise FeatureDisabledError.
    """
    # Arrange - disable the feature
    await feature_flag_service.set_enabled("TEST_FEATURE", False)
    
    # Act & Assert - attempt to call method should raise error
    with pytest.raises(FeatureDisabledError) as exc_info:
        await feature_flag_proxy.test_method(account_type="test_account_type")
    
    # Verify error details
    assert exc_info.value.feature_name == "TEST_FEATURE"
    assert exc_info.value.entity_type == "account"
    assert exc_info.value.operation == "test_method"
    
    # Re-enable the feature for other tests
    await feature_flag_service.set_enabled("TEST_FEATURE", True)


@pytest.mark.asyncio
async def test_proxy_account_type_whitelist(feature_flag_proxy, feature_flag_service):
    """
    Test that the proxy respects account type whitelist.
    
    When a feature has an account type whitelist, only those types
    should be allowed.
    """
    # Arrange - set account type whitelist
    await feature_flag_service.set_account_types_whitelist("TEST_FEATURE", ["allowed_type"])
    
    # Act & Assert - attempt with non-whitelisted type should raise error
    with pytest.raises(FeatureDisabledError):
        await feature_flag_proxy.test_method(account_type="test_account_type")
    
    # But allowed type should work
    result = await feature_flag_proxy.test_method(account_type="allowed_type")
    assert "Test method called with allowed_type" in result
    
    # Reset whitelist for other tests
    await feature_flag_service.set_account_types_whitelist("TEST_FEATURE", [])


@pytest.mark.asyncio
async def test_proxy_allows_specific_account_types(feature_flag_proxy):
    """
    Test that the proxy allows specific account types based on requirements.
    
    Methods that require specific account types should only be allowed
    for those types.
    """
    # Arrange - proxy fixture
    
    # Act & Assert - attempt with non-matching type should raise error
    with pytest.raises(FeatureDisabledError):
        await feature_flag_proxy.get_by_type(account_type="non_specific_type")
    
    # But specific type should work
    result = await feature_flag_proxy.get_by_type(account_type="specific_type")
    assert result["type"] == "specific_type"


@pytest.mark.asyncio
async def test_proxy_with_banking_account_types(feature_flag_proxy, feature_flag_service):
    """
    Test that the proxy enforces banking account types feature flag.
    
    The BANKING_ACCOUNT_TYPES_ENABLED flag should control access to
    banking account type methods.
    """
    # Arrange - disable the banking account types feature
    await feature_flag_service.set_enabled("BANKING_ACCOUNT_TYPES_ENABLED", False)
    
    # Act & Assert - attempt with banking account type should raise error
    with pytest.raises(FeatureDisabledError) as exc_info:
        await feature_flag_proxy.create({"account_type": "bnpl", "name": "Test BNPL"})
    
    # Verify error details
    assert exc_info.value.feature_name == "BANKING_ACCOUNT_TYPES_ENABLED"
    
    # Re-enable the feature
    await feature_flag_service.set_enabled("BANKING_ACCOUNT_TYPES_ENABLED", True)
    
    # Now it should work
    result = await feature_flag_proxy.create({"account_type": "bnpl", "name": "Test BNPL"})
    assert result["account_type"] == "bnpl"


# Account type extraction tests
@pytest.mark.asyncio
async def test_account_type_extraction_from_method_name(feature_flag_proxy):
    """
    Test that the proxy extracts account type from the method name.
    
    When the method name contains the account type, the proxy should
    extract it correctly.
    """
    # Arrange - create a method with account type in the name
    async def create_bnpl_account(data):
        return {"account_type": "bnpl", **data}
    
    setattr(feature_flag_proxy._repository, "create_bnpl_account", create_bnpl_account)
    
    # Act - call the method
    result = await feature_flag_proxy.create_bnpl_account({"name": "Test BNPL"})
    
    # Assert - verify the method was allowed (no error raised)
    assert result["account_type"] == "bnpl"
    assert result["name"] == "Test BNPL"


@pytest.mark.asyncio
async def test_account_type_extraction_from_kwargs(feature_flag_proxy):
    """
    Test that the proxy extracts account type from kwargs.
    
    When account_type is passed as a keyword argument, the proxy should
    extract it correctly.
    """
    # Arrange - proxy fixture
    
    # Act - call a method with account_type as kwarg
    result = await feature_flag_proxy.test_method(account_type="bnpl")
    
    # Assert - verify the method was allowed (no error raised)
    assert "Test method called with bnpl" == result


@pytest.mark.asyncio
async def test_account_type_extraction_from_repository_class(typed_feature_flag_proxy):
    """
    Test that the proxy extracts account type from the repository class name.
    
    When the repository class name contains the account type, the proxy should
    extract it correctly.
    """
    # Arrange - proxy with typed repository
    
    # Act - call a type-specific method
    result = await typed_feature_flag_proxy.type_specific_method()
    
    # Assert - verify the method was allowed (no error raised)
    assert "Type-specific method for bnpl" == result


# Caching tests
@pytest.mark.asyncio
async def test_proxy_caches_feature_checks(
    test_repository, feature_flag_service, in_memory_config_provider
):
    """
    Test that the proxy caches feature flag checks.
    
    The proxy should cache feature flag check results to avoid
    repeated database queries.
    """
    # Arrange - create a proxy with a short cache TTL for testing
    proxy = FeatureFlagRepositoryProxy(
        repository=test_repository,
        feature_flag_service=feature_flag_service,
        config_provider=in_memory_config_provider,
    )
    
    # Patch the _is_feature_enabled method to count calls
    original_method = proxy._is_feature_enabled
    call_count = {"value": 0}
    
    async def counting_method(*args, **kwargs):
        call_count["value"] += 1
        return await original_method(*args, **kwargs)
    
    proxy._is_feature_enabled = counting_method
    
    # Act - call the same method multiple times
    for _ in range(5):
        await proxy.test_method(account_type="test_account_type")
    
    # Assert - verify the _is_feature_enabled method was called only once
    assert call_count["value"] == 1
    
    # Restore the original method
    proxy._is_feature_enabled = original_method


@pytest.mark.asyncio
async def test_in_memory_config_provider_fallback(memory_config_proxy):
    """
    Test that the proxy works with in-memory config provider.
    
    The proxy should work correctly with the InMemoryConfigProvider
    as a fallback when database access is not available.
    """
    # Arrange - proxy with in-memory config provider
    
    # Act - call a method that should be allowed
    result = await memory_config_proxy.test_method(account_type="test_account_type")
    
    # Assert - verify the method was allowed
    assert "Test method called with test_account_type" == result


@pytest.mark.asyncio
async def test_proxy_passes_through_methods_without_account_type(feature_flag_proxy):
    """
    Test that the proxy passes through methods that don't have account type.
    
    Methods that don't have an account type and aren't in the requirements
    should be allowed.
    """
    # Arrange - proxy fixture
    
    # Act - call a method that doesn't have an account type
    result = await feature_flag_proxy.delete(1)
    
    # Assert - verify the method was allowed
    assert result is True


@pytest.mark.asyncio
async def test_create_proxy_with_null_service(test_repository, config_provider):
    """
    Test creating a proxy with null feature flag service.
    
    The proxy should allow all methods when the feature flag service is null.
    """
    # Arrange - create a proxy with null feature flag service
    proxy = FeatureFlagRepositoryProxy(
        repository=test_repository,
        feature_flag_service=None,
        config_provider=config_provider,
    )
    
    # Act - call a method that would normally be checked
    result = await proxy.test_method(account_type="test_account_type")
    
    # Assert - verify the method was allowed (no error raised)
    assert "Test method called with test_account_type" == result


@pytest.mark.asyncio
async def test_updating_feature_requirements(feature_flag_service, memory_config_proxy):
    """
    Test updating feature requirements at runtime.
    
    When feature requirements change, the proxy should respect the new requirements.
    """
    # Arrange - in-memory config provider for easy updates
    provider = memory_config_proxy._config_provider
    
    # Update the requirements
    new_requirements = {
        "TEST_FEATURE": {
            "repository": {
                "test_method": ["new_account_type"],  # Change allowed type
                "get_by_id": ["*"]
            }
        }
    }
    provider.update_requirements(new_requirements)
    await provider.invalidate_cache()  # Clear cache to use new requirements
    
    # Act & Assert - old account type should be blocked
    with pytest.raises(FeatureDisabledError):
        await memory_config_proxy.test_method(account_type="test_account_type")
    
    # New account type should work
    result = await memory_config_proxy.test_method(account_type="new_account_type")
    assert "Test method called with new_account_type" == result
