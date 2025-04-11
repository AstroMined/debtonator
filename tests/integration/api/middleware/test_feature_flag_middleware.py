"""
Integration tests for the Feature Flag Middleware.

This module tests the FeatureFlagMiddleware component that enforces
feature flag requirements at the API layer. The tests verify that
requests for disabled features are blocked with 403 Forbidden responses,
while requests for enabled features are allowed.
"""

import asyncio
import pytest

from src.api.middleware.feature_flags import FeatureFlagMiddleware
from src.config.providers.feature_flags import InMemoryConfigProvider


@pytest.mark.asyncio
async def test_middleware_allows_non_feature_flagged_routes(
    test_app, test_client, feature_flag_service, api_requirements
):
    """Test that non-feature-flagged routes are not affected by the middleware."""
    # Arrange
    # Create provider with empty requirements for this test
    config_provider = InMemoryConfigProvider({})
    
    # Disable all features
    await feature_flag_service.set_enabled("TEST_FEATURE", False)
    await feature_flag_service.set_enabled("BANKING_ACCOUNT_TYPES_ENABLED", False)
    
    # Add middleware to app
    test_app.add_middleware(
        FeatureFlagMiddleware,
        feature_flag_service=feature_flag_service,
        config_provider=config_provider
    )
    
    # Act - Request to a non-flagged endpoint should succeed
    response = await test_client.get("/api/v1/non-feature-flagged")
    
    # Assert - Should get 404 (not found), not 403 (forbidden)
    assert response.status_code == 404
    assert "FEATURE_DISABLED" not in response.text


@pytest.mark.asyncio
async def test_middleware_blocks_disabled_features(
    test_app, test_client, feature_flag_service, api_requirements
):
    """Test that the middleware blocks requests for disabled features."""
    # Arrange
    config_provider = InMemoryConfigProvider(api_requirements)
    
    # Disable the test feature
    await feature_flag_service.set_enabled("TEST_FEATURE", False)
    
    # Add middleware to app
    test_app.add_middleware(
        FeatureFlagMiddleware,
        feature_flag_service=feature_flag_service,
        config_provider=config_provider
    )
    
    # Act - Request to the test endpoint
    response = await test_client.get("/api/v1/test-endpoint")
    
    # Assert - Should be forbidden
    assert response.status_code == 403
    assert response.json()["code"] == "FEATURE_DISABLED"
    assert response.json()["feature_flag"] == "TEST_FEATURE"
    assert response.json()["entity_type"] == "api_endpoint"


@pytest.mark.asyncio
async def test_middleware_allows_enabled_features(
    test_app, test_client, feature_flag_service, api_requirements
):
    """Test that the middleware allows requests for enabled features."""
    # Arrange
    config_provider = InMemoryConfigProvider(api_requirements)
    
    # Enable the test feature
    await feature_flag_service.set_enabled("TEST_FEATURE", True)
    
    # Add middleware to app
    test_app.add_middleware(
        FeatureFlagMiddleware,
        feature_flag_service=feature_flag_service,
        config_provider=config_provider
    )
    
    # Act - Request to the test endpoint
    response = await test_client.get("/api/v1/test-endpoint")
    
    # Assert - Should succeed
    assert response.status_code == 200
    assert response.json()["message"] == "success"


@pytest.mark.asyncio
async def test_middleware_path_pattern_matching(
    test_app, test_client, feature_flag_service, api_requirements
):
    """Test that the middleware correctly matches different path patterns."""
    # Arrange
    config_provider = InMemoryConfigProvider(api_requirements)
    
    # Disable banking account types
    await feature_flag_service.set_enabled("BANKING_ACCOUNT_TYPES_ENABLED", False)
    
    # Add middleware to app
    test_app.add_middleware(
        FeatureFlagMiddleware,
        feature_flag_service=feature_flag_service,
        config_provider=config_provider
    )
    
    # Act & Assert - Test path parameter matching
    response = await test_client.get("/api/v1/accounts/123")
    assert response.status_code == 403
    assert response.json()["feature_flag"] == "BANKING_ACCOUNT_TYPES_ENABLED"
    
    # Act & Assert - Test wildcard path matching
    response = await test_client.get("/api/v1/banking/overview")
    assert response.status_code == 403
    assert response.json()["feature_flag"] == "BANKING_ACCOUNT_TYPES_ENABLED"
    
    # Now enable the feature
    await feature_flag_service.set_enabled("BANKING_ACCOUNT_TYPES_ENABLED", True)
    
    # Request should succeed now
    response = await test_client.get("/api/v1/accounts/123")
    assert response.status_code == 200
    
    response = await test_client.get("/api/v1/banking/overview")
    assert response.status_code == 200


@pytest.mark.asyncio
async def test_middleware_caching(
    test_app, test_client, feature_flag_service, api_requirements, app_with_counting_middleware
):
    """Test that the middleware caches requirements and respects TTL."""
    # Arrange - Get the counting provider from the fixture
    _, counting_provider = app_with_counting_middleware
    
    # Act & Assert
    # First request should load requirements
    await test_client.get("/api/v1/test-endpoint")
    assert counting_provider.call_count == 1
    
    # Second request within TTL should use cache
    await test_client.get("/api/v1/test-endpoint")
    assert counting_provider.call_count == 1
    
    # Wait for cache to expire
    await asyncio.sleep(0.2)
    
    # Request after TTL should reload requirements
    await test_client.get("/api/v1/test-endpoint")
    assert counting_provider.call_count == 2
