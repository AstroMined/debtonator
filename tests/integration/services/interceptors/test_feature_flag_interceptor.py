"""
Integration tests for the Service Interceptor for feature flag enforcement.

These tests verify that the ServiceInterceptor correctly enforces feature flag
requirements at the service layer boundary.
"""

import asyncio

import pytest

from src.errors.feature_flags import FeatureDisabledError


class TestServiceInterceptor:
    """Tests for the service interceptor functionality."""

    async def test_interceptor_allows_method_when_feature_enabled(
        self,
        service_interceptor,
        feature_flag_repository,
    ):
        """Test that interceptor allows methods when features are enabled."""
        # Arrange - ensure flag is enabled
        await feature_flag_repository.update("TEST_FEATURE_FLAG", {"value": True})

        # Act/Assert - Should not raise an exception
        await service_interceptor.intercept(
            service_class="TestService", method_name="test_method", args=(), kwargs={}
        )

    async def test_interceptor_blocks_method_when_feature_disabled(
        self,
        service_interceptor,
        feature_flag_repository,
    ):
        """Test that interceptor blocks methods when features are disabled."""
        # Arrange - disable the flag in the database
        await feature_flag_repository.update("TEST_FEATURE_FLAG", {"value": False})

        # Act/Assert - Should raise FeatureDisabledError
        with pytest.raises(FeatureDisabledError) as excinfo:
            await service_interceptor.intercept(
                service_class="TestService",
                method_name="test_method",
                args=(),
                kwargs={},
            )

        # Verify error details are correct
        assert excinfo.value.feature_name == "TEST_FEATURE_FLAG"
        assert excinfo.value.entity_type == "service_method"
        assert excinfo.value.entity_id == "test_method"
        assert "TestService.test_method" in str(excinfo.value)

    async def test_interceptor_handles_account_type_specific_requirements(
        self,
        service_interceptor,
        feature_flag_repository,
    ):
        """Test that interceptor handles account-type-specific requirements."""
        # CASE 1: Testing with a controlled account type (ewa)
        # Arrange - ensure flag is enabled initially
        await feature_flag_repository.update(
            "ACCOUNT_TYPE_SPECIFIC_FLAG", {"value": True}
        )

        # Act/Assert - Method with ewa account type should work
        await service_interceptor.intercept(
            service_class="TestService",
            method_name="test_method_with_account_type",
            args=(),
            kwargs={"account_type": "ewa"},
        )

        # Arrange - disable the flag
        await feature_flag_repository.update(
            "ACCOUNT_TYPE_SPECIFIC_FLAG", {"value": False}
        )

        # Act/Assert - Method with ewa should now be blocked
        with pytest.raises(FeatureDisabledError) as excinfo:
            await service_interceptor.intercept(
                service_class="TestService",
                method_name="test_method_with_account_type",
                args=(),
                kwargs={"account_type": "ewa"},
            )

        # CASE 2: Testing with a non-controlled account type (checking)
        # Should work even when flag is disabled
        await service_interceptor.intercept(
            service_class="TestService",
            method_name="test_method_with_account_type",
            args=(),
            kwargs={"account_type": "checking"},
        )

    async def test_interceptor_extracts_account_type_from_different_patterns(
        self,
        service_interceptor,
    ):
        """Test that interceptor extracts account type from different argument patterns."""
        # Note: manually call the protected method for testing

        # CASE 1: Direct account_type keyword argument
        account_type = service_interceptor._extract_account_type(
            args=(), kwargs={"account_type": "savings"}
        )
        assert account_type == "savings"

        # CASE 2: Account type in data dictionary
        account_type = service_interceptor._extract_account_type(
            args=(), kwargs={"data": {"account_type": "checking"}}
        )
        assert account_type == "checking"

        # CASE 3: Account type in first positional argument
        account_type = service_interceptor._extract_account_type(
            args=("credit",), kwargs={}
        )
        assert account_type == "credit"

        # CASE 4: Account type in pydantic-like object with attribute
        class MockSchema:
            def __init__(self, account_type):
                self.account_type = account_type

        account_type = service_interceptor._extract_account_type(
            args=(), kwargs={"schema": MockSchema("bnpl")}
        )
        assert account_type == "bnpl"

        # CASE 5: Account type in pydantic-like object with model_dump
        class MockSchemaWithDump:
            def __init__(self, account_type):
                self._account_type = account_type

            def model_dump(self):
                return {"account_type": self._account_type}

        account_type = service_interceptor._extract_account_type(
            args=(), kwargs={"schema": MockSchemaWithDump("ewa")}
        )
        assert account_type == "ewa"

    async def test_interceptor_pattern_matching(self, service_interceptor):
        """Test that interceptor correctly matches method patterns."""
        # Note: manually call the protected method for testing

        # Exact match
        assert (
            service_interceptor._matches_pattern("test_method", "test_method") is True
        )

        # Glob pattern match
        assert (
            service_interceptor._matches_pattern("test_create_account", "test_*")
            is True
        )
        assert (
            service_interceptor._matches_pattern(
                "create_checking_account", "create_*_account"
            )
            is True
        )
        assert (
            service_interceptor._matches_pattern("update_ewa_account", "*_ewa_*")
            is True
        )

        # Non-matches
        assert (
            service_interceptor._matches_pattern("test_method", "other_method") is False
        )
        assert (
            service_interceptor._matches_pattern("test_method", "test_*_suffix")
            is False
        )

    async def test_interceptor_caching_behavior(
        self,
        service_interceptor,
        feature_flag_repository,
        db_session,
    ):
        """Test that interceptor correctly caches requirements."""
        # Arrange - ensure flag is enabled initially
        await feature_flag_repository.update("TEST_FEATURE_FLAG", {"value": True})

        # First call should work and cache the result
        await service_interceptor.intercept(
            service_class="TestService", method_name="test_method", args=(), kwargs={}
        )

        # Disable flag in database
        await feature_flag_repository.update("TEST_FEATURE_FLAG", {"value": False})

        # Second call should still work due to caching
        await service_interceptor.intercept(
            service_class="TestService", method_name="test_method", args=(), kwargs={}
        )

        # Wait for cache to expire (TTL is 1 second)
        await asyncio.sleep(1.1)

        # Now the operation should be blocked with updated requirements
        with pytest.raises(FeatureDisabledError):
            await service_interceptor.intercept(
                service_class="TestService",
                method_name="test_method",
                args=(),
                kwargs={},
            )

        # Re-enable flag
        await feature_flag_repository.update("TEST_FEATURE_FLAG", {"value": True})

        # Call should work again after re-enabling
        await service_interceptor.intercept(
            service_class="TestService", method_name="test_method", args=(), kwargs={}
        )

    async def test_interceptor_cache_invalidation(
        self,
        service_interceptor,
        feature_flag_repository,
    ):
        """Test that interceptor cache can be manually invalidated."""
        # Arrange - ensure flag is enabled initially
        await feature_flag_repository.update("TEST_FEATURE_FLAG", {"value": True})

        # First call should work and cache the result
        await service_interceptor.intercept(
            service_class="TestService", method_name="test_method", args=(), kwargs={}
        )

        # Disable flag in database
        await feature_flag_repository.update("TEST_FEATURE_FLAG", {"value": False})

        # Manually invalidate cache
        await service_interceptor.invalidate_cache()

        # Now the operation should be blocked
        with pytest.raises(FeatureDisabledError):
            await service_interceptor.intercept(
                service_class="TestService",
                method_name="test_method",
                args=(),
                kwargs={},
            )
