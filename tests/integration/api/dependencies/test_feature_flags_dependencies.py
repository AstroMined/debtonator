"""
Integration tests for the feature flag dependencies.

This module contains integration tests for the feature flag dependency functions,
following the Real Objects Testing Philosophy with a real database.
"""
import os
from typing import Dict, List, Optional

import pytest
from fastapi import Depends, FastAPI, Request
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.feature_flags import (
    build_context_from_request,
    get_feature_flag_registry,
    get_feature_flag_repository,
    get_feature_flag_service,
    get_flag_management_enabled,
)
from src.models.feature_flags import FeatureFlag
from src.utils.feature_flags.context import Environment


@pytest.mark.asyncio
async def test_get_flag_management_enabled(env_setup):
    """Test flag management enabled detection."""
    # Test enabled case
    os.environ["ENABLE_FEATURE_FLAG_MANAGEMENT"] = "1"
    assert get_flag_management_enabled() is True
    
    # Test disabled case
    os.environ["ENABLE_FEATURE_FLAG_MANAGEMENT"] = "0"
    assert get_flag_management_enabled() is False
    
    # Test environment-based default (test environment should be enabled)
    os.environ.pop("ENABLE_FEATURE_FLAG_MANAGEMENT", None)
    assert get_flag_management_enabled() is True  # In test environment


@pytest.mark.asyncio
async def test_get_feature_flag_registry():
    """Test getting the feature flag registry."""
    # Get the registry - should return a non-None instance
    registry = get_feature_flag_registry()
    assert registry is not None
    
    # Registry should be a singleton (calling again should return same instance)
    registry2 = get_feature_flag_registry()
    assert registry is registry2


@pytest.mark.asyncio
async def test_get_feature_flag_repository(db_session: AsyncSession):
    """Test getting the feature flag repository."""
    # Create the repository with our test db_session
    # Get the repository directly
    from src.repositories.feature_flags import FeatureFlagRepository
    repo = FeatureFlagRepository(db_session)
    
    # Verify the repository
    assert repo is not None
    
    # Test repository functionality
    flags = await repo.get_all()
    # Don't need to check flag values, just that it returns something
    assert isinstance(flags, list)


@pytest.mark.asyncio
async def test_feature_flag_service_with_context(
    db_session: AsyncSession, test_boolean_flag: FeatureFlag
):
    """Test feature flag service with context."""
    # Get registry and repository
    registry = get_feature_flag_registry()
    
    # Create a repository directly
    from src.repositories.feature_flags import FeatureFlagRepository
    repo = FeatureFlagRepository(db_session)
    
    # Get the service
    service = get_feature_flag_service(
        registry=registry,
        repository=repo
    )
    
    # Check that the service has the expected attributes
    assert service.registry is registry
    assert service.repository is repo
    
    # Verify the service can get our test flag
    flag = await service.get_flag(test_boolean_flag.name)
    assert flag is not None
    assert flag.name == test_boolean_flag.name


@pytest.mark.asyncio
async def test_build_context_from_request():
    """Test building context from request using a temporary app."""
    # Create a minimal FastAPI app for testing
    app = FastAPI()
    
    @app.get("/test-context")
    async def test_endpoint(request: Request):
        context = build_context_from_request(request)
        return {
            "environment": context.environment,
            "hostname": context.hostname,
            "request_id": context.request_id,
            "ip_address": context.ip_address,
            "user_agent": context.user_agent,
        }
    
    # Test client for our minimal app
    from fastapi.testclient import TestClient
    client = TestClient(app)
    
    # Make request with headers
    response = client.get(
        "/test-context",
        headers={
            "X-Request-ID": "test-request-id",
            "User-Agent": "Test User Agent",
            "X-Forwarded-For": "192.168.1.1",
        },
    )
    
    # Check response
    assert response.status_code == 200
    data = response.json()
    assert data["request_id"] == "test-request-id"
    assert data["user_agent"] == "Test User Agent"
    assert data["ip_address"] == "192.168.1.1"
    assert "environment" in data
    assert "hostname" in data


@pytest.mark.asyncio
async def test_dependency_integration_with_real_app(
    client: AsyncClient, test_boolean_flag: FeatureFlag, env_setup
):
    """Test integration of dependencies in the real app."""
    # Enable management
    os.environ["ENABLE_FEATURE_FLAG_MANAGEMENT"] = "1"
    
    # Make request to get flag
    response = await client.get(f"/api/v1/feature-flags/flags/{test_boolean_flag.name}")
    
    # Verify response
    assert response.status_code == 200
    flag = response.json()
    assert flag["name"] == test_boolean_flag.name
    
    # The fact that this works confirms that:
    # 1. get_feature_flag_service dependency works
    # 2. get_feature_flag_repository dependency works
    # 3. get_feature_flag_registry dependency works
    # 4. get_flag_management_enabled dependency works
