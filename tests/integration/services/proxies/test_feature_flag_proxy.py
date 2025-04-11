"""
Integration tests for the Service Proxy for feature flag enforcement.

These tests verify that the ServiceProxy correctly wraps service objects and
enforces feature flag requirements by intercepting method calls.
"""

import asyncio
import pytest

from src.errors.feature_flags import FeatureDisabledError


class TestServiceProxy:
    """Tests for the service proxy functionality."""

    async def test_proxy_passes_through_non_method_attributes(
        self,
        proxied_service,
        test_service,
    ):
        """Test that proxy passes through non-method attributes."""
        # Attribute access should work directly
        assert proxied_service.name == test_service.name
        
        # Property access should work
        assert proxied_service.read_only_property == "property_value"
        
    async def test_proxy_forwards_async_methods_when_feature_enabled(
        self,
        proxied_service,
        test_service,
        feature_flag_repository,
    ):
        """Test that proxy forwards async method calls when feature is enabled."""
        # Arrange - ensure flag is enabled
        await feature_flag_repository.update(
            "TEST_FEATURE_FLAG", 
            {"value": True}
        )
        
        # Act - call async method through proxy
        result = await proxied_service.async_method("value1", "value2")
        
        # Assert - method should be called on underlying service
        assert "Async method called: value1, value2" == result
        assert test_service.method_calls["async_method"] == ("value1", "value2")
        
    async def test_proxy_forwards_sync_methods_when_feature_enabled(
        self,
        proxied_service,
        test_service,
        feature_flag_repository,
    ):
        """Test that proxy forwards sync method calls when feature is enabled."""
        # Arrange - ensure flag is enabled
        await feature_flag_repository.update(
            "TEST_FEATURE_FLAG", 
            {"value": True}
        )
        
        # Act - call sync method through proxy
        result = proxied_service.sync_method("value1", "value2")
        
        # Assert - method should be called on underlying service
        assert "Sync method called: value1, value2" == result
        assert test_service.method_calls["sync_method"] == ("value1", "value2")
        
    async def test_proxy_blocks_async_methods_when_feature_disabled(
        self,
        proxied_service,
        test_service,
        feature_flag_repository,
    ):
        """Test that proxy blocks async method calls when feature is disabled."""
        # Arrange - disable the flag
        await feature_flag_repository.update(
            "TEST_FEATURE_FLAG", 
            {"value": False}
        )
        
        # Act/Assert - method call should be blocked
        with pytest.raises(FeatureDisabledError) as excinfo:
            await proxied_service.async_method("value1", "value2")
        
        # Verify error details are correct
        assert excinfo.value.feature_name == "TEST_FEATURE_FLAG"
        assert excinfo.value.entity_type == "service_method"
        assert excinfo.value.entity_id == "async_method"
        
        # Method should not have been called on underlying service
        assert "async_method" not in test_service.method_calls
        
    async def test_proxy_blocks_sync_methods_when_feature_disabled(
        self,
        proxied_service,
        test_service,
        feature_flag_repository,
    ):
        """Test that proxy blocks sync method calls when feature is disabled."""
        # Arrange - disable the flag
        await feature_flag_repository.update(
            "TEST_FEATURE_FLAG", 
            {"value": False}
        )
        
        # Act/Assert - method call should be blocked
        with pytest.raises(FeatureDisabledError) as excinfo:
            proxied_service.sync_method("value1", "value2")
        
        # Verify error details are correct
        assert excinfo.value.feature_name == "TEST_FEATURE_FLAG"
        
        # Method should not have been called on underlying service
        assert "sync_method" not in test_service.method_calls
        
    async def test_proxy_handles_account_type_specific_requirements(
        self,
        proxied_service,
        test_service,
        feature_flag_repository,
    ):
        """Test that proxy handles account-type-specific requirements."""
        # CASE 1: Testing with a controlled account type (ewa)
        # Arrange - ensure flag is enabled initially
        await feature_flag_repository.update(
            "ACCOUNT_TYPE_SPECIFIC_FLAG", 
            {"value": True}
        )
        
        # Act - call with ewa account type
        result = await proxied_service.account_type_method("ewa", {"some": "data"})
        
        # Assert - method should work
        assert "Account type method called: ewa" == result
        assert test_service.method_calls["account_type_method"][0] == "ewa"
        
        # Clear call record for next test
        test_service.method_calls = {}
        
        # Arrange - disable the flag
        await feature_flag_repository.update(
            "ACCOUNT_TYPE_SPECIFIC_FLAG", 
            {"value": False}
        )
        
        # Act/Assert - method call with ewa should be blocked
        with pytest.raises(FeatureDisabledError):
            await proxied_service.account_type_method("ewa", {"some": "data"})
        
        # Method should not have been called
        assert "account_type_method" not in test_service.method_calls
        
        # CASE 2: Testing with a non-controlled account type (checking)
        # Should work even when flag is disabled
        result = await proxied_service.account_type_method("checking", {"some": "data"})
        
        # Assert - method should work for checking
        assert "Account type method called: checking" == result
        assert test_service.method_calls["account_type_method"][0] == "checking"
        
    async def test_proxy_caching_behavior(
        self,
        proxied_service,
        test_service,
        feature_flag_repository,
    ):
        """Test that proxy caches requirements."""
        # Arrange - ensure flag is enabled initially
        await feature_flag_repository.update(
            "TEST_FEATURE_FLAG", 
            {"value": True}
        )
        
        # First call should work and cache the result
        await proxied_service.async_method("test")
        
        # Clear call record for next test
        test_service.method_calls = {}
        
        # Disable flag in database
        await feature_flag_repository.update(
            "TEST_FEATURE_FLAG", 
            {"value": False}
        )
        
        # Second call should still work due to caching
        await proxied_service.async_method("cache test")
        
        # Method should have been called (cache still has enabled value)
        assert "async_method" in test_service.method_calls
        
        # Wait for cache to expire
        await asyncio.sleep(1.1)
        
        # Clear call record for next test
        test_service.method_calls = {}
        
        # Now the operation should be blocked
        with pytest.raises(FeatureDisabledError):
            await proxied_service.async_method("after cache expired")
        
        # Method should not have been called
        assert "async_method" not in test_service.method_calls
        
    async def test_proxy_cache_invalidation(
        self,
        proxied_service,
        test_service,
        feature_flag_repository,
    ):
        """Test that proxy cache can be manually invalidated."""
        # Arrange - ensure flag is enabled initially
        await feature_flag_repository.update(
            "TEST_FEATURE_FLAG", 
            {"value": True}
        )
        
        # First call should work and cache the result
        await proxied_service.async_method("initial call")
        
        # Clear call record for next test
        test_service.method_calls = {}
        
        # Disable flag in database
        await feature_flag_repository.update(
            "TEST_FEATURE_FLAG", 
            {"value": False}
        )
        
        # Manually invalidate cache
        proxied_service.invalidate_cache()
        
        # Now the operation should be blocked
        with pytest.raises(FeatureDisabledError):
            await proxied_service.async_method("after cache invalidation")
        
        # Method should not have been called
        assert "async_method" not in test_service.method_calls
