"""
Integration tests for the feature flag API endpoints.

This module contains integration tests for the feature flag API endpoints,
following the Real Objects Testing Philosophy with a real database.
"""
import os
from typing import Dict, List, Optional

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.feature_flags import FeatureFlag
from src.utils.datetime_utils import naive_utc_now


@pytest.mark.asyncio
async def test_feature_flag_management_enabled(
    client: AsyncClient, test_boolean_flag: FeatureFlag, env_setup
):
    """Test enabling feature flag management with environment variables."""
    # Set environment variable to enable feature flag management
    os.environ["ENABLE_FEATURE_FLAG_MANAGEMENT"] = "1"
    
    # Make request to list flags
    response = await client.get("/api/v1/feature-flags/flags")
    
    # Verify access is allowed
    assert response.status_code == 200
    flags = response.json()
    assert len(flags) >= 1
    assert any(flag["name"] == test_boolean_flag.name for flag in flags)


@pytest.mark.asyncio
async def test_feature_flag_management_disabled(
    client: AsyncClient, test_boolean_flag: FeatureFlag, env_setup
):
    """Test disabling feature flag management with environment variables."""
    # Set environment variable to disable feature flag management
    os.environ["ENABLE_FEATURE_FLAG_MANAGEMENT"] = "0"
    
    # Make request to list flags
    response = await client.get("/api/v1/feature-flags/flags")
    
    # Verify access is denied
    assert response.status_code == 403
    assert "disabled" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_list_feature_flags(
    client: AsyncClient, test_multiple_flags: List[FeatureFlag], env_setup
):
    """Test listing all feature flags."""
    # Enable management
    os.environ["ENABLE_FEATURE_FLAG_MANAGEMENT"] = "1"
    
    # Make request to list flags
    response = await client.get("/api/v1/feature-flags/flags")
    
    # Verify response
    assert response.status_code == 200
    flags = response.json()
    assert len(flags) >= len(test_multiple_flags)
    
    # Check that all test flags are in the response
    flag_names = [flag["name"] for flag in flags]
    for test_flag in test_multiple_flags:
        assert test_flag.name in flag_names


@pytest.mark.asyncio
async def test_list_feature_flags_with_filter(
    client: AsyncClient, test_multiple_flags: List[FeatureFlag], env_setup
):
    """Test listing feature flags with filtering."""
    # Enable management
    os.environ["ENABLE_FEATURE_FLAG_MANAGEMENT"] = "1"
    
    # Make request to list flags with prefix filter
    response = await client.get("/api/v1/feature-flags/flags?prefix=FEATURE_")
    
    # Verify filtered response
    assert response.status_code == 200
    flags = response.json()
    assert len(flags) >= 1
    for flag in flags:
        assert flag["name"].startswith("FEATURE_")
    
    # Make request to list only enabled flags (value=True for boolean flags)
    response = await client.get("/api/v1/feature-flags/flags?enabled_only=true")
    
    # Verify filtered response
    assert response.status_code == 200
    flags = response.json()
    for flag in flags:
        # For boolean flags, value should be True
        # For other flag types, the API should filter them properly
        if flag["flag_type"] == "boolean":
            assert flag["value"] is True


@pytest.mark.asyncio
async def test_get_feature_flag(
    client: AsyncClient, test_boolean_flag: FeatureFlag, env_setup
):
    """Test getting a specific feature flag."""
    # Enable management
    os.environ["ENABLE_FEATURE_FLAG_MANAGEMENT"] = "1"
    
    # Make request to get a specific flag
    response = await client.get(f"/api/v1/feature-flags/flags/{test_boolean_flag.name}")
    
    # Verify response
    assert response.status_code == 200
    flag = response.json()
    assert flag["name"] == test_boolean_flag.name
    assert flag["value"] == test_boolean_flag.value
    assert flag["flag_type"] == test_boolean_flag.flag_type


@pytest.mark.asyncio
async def test_get_feature_flag_not_found(client: AsyncClient, env_setup):
    """Test getting a non-existent feature flag."""
    # Enable management
    os.environ["ENABLE_FEATURE_FLAG_MANAGEMENT"] = "1"
    
    # Make request to get a non-existent flag
    response = await client.get("/api/v1/feature-flags/flags/NON_EXISTENT_FLAG")
    
    # Verify response
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_feature_flag(
    client: AsyncClient, test_boolean_flag: FeatureFlag, env_setup
):
    """Test updating a feature flag."""
    # Enable management
    os.environ["ENABLE_FEATURE_FLAG_MANAGEMENT"] = "1"
    
    # Create update data (value replaces enabled for boolean flags)
    update_data = {
        "value": not test_boolean_flag.value,
        "description": "Updated description",
        "flag_metadata": {"environment": "test", "new_key": "new_value"}
    }
    
    # Make request to update the flag
    response = await client.put(
        f"/api/v1/feature-flags/flags/{test_boolean_flag.name}",
        json=update_data
    )
    
    # Verify response
    assert response.status_code == 200
    flag = response.json()
    assert flag["name"] == test_boolean_flag.name
    assert flag["value"] == update_data["value"]
    assert flag["description"] == update_data["description"]
    assert flag["flag_metadata"]["environment"] == "test"
    assert flag["flag_metadata"]["new_key"] == "new_value"
    
    # Verify database was updated (by getting the flag again)
    response = await client.get(f"/api/v1/feature-flags/flags/{test_boolean_flag.name}")
    flag = response.json()
    assert flag["value"] == update_data["value"]
    assert flag["description"] == update_data["description"]


@pytest.mark.asyncio
async def test_create_feature_flag(client: AsyncClient, db_session: AsyncSession, env_setup):
    """Test creating a new feature flag."""
    # Enable management
    os.environ["ENABLE_FEATURE_FLAG_MANAGEMENT"] = "1"
    
    # Create flag data with value instead of enabled
    flag_data = {
        "name": "NEW_TEST_FLAG",
        "description": "New test flag",
        "value": True,  # For boolean flags
        "flag_type": "boolean",
        "flag_metadata": {"environment": "development"}
    }
    
    # Make request to create the flag
    response = await client.post("/api/v1/feature-flags/flags", json=flag_data)
    
    # Verify response
    assert response.status_code == 201
    flag = response.json()
    assert flag["name"] == flag_data["name"]
    assert flag["value"] == flag_data["value"]
    assert flag["description"] == flag_data["description"]
    assert flag["flag_type"] == flag_data["flag_type"]
    assert flag["flag_metadata"]["environment"] == "development"
    
    # Verify database was updated (by getting the flag)
    response = await client.get(f"/api/v1/feature-flags/flags/{flag_data['name']}")
    assert response.status_code == 200
    flag = response.json()
    assert flag["name"] == flag_data["name"]
    
    # Clean up - delete the flag from the database
    from src.repositories.feature_flags import FeatureFlagRepository
    repo = FeatureFlagRepository(db_session)
    await repo.delete(flag_data["name"])
    await db_session.commit()


@pytest.mark.asyncio
async def test_create_duplicate_feature_flag(
    client: AsyncClient, test_boolean_flag: FeatureFlag, env_setup
):
    """Test creating a duplicate feature flag."""
    # Enable management
    os.environ["ENABLE_FEATURE_FLAG_MANAGEMENT"] = "1"
    
    # Create flag data with an existing name
    flag_data = {
        "name": test_boolean_flag.name,  # Use existing name
        "description": "Duplicate flag",
        "value": True,  # Using value instead of enabled
        "flag_type": "boolean",
        "flag_metadata": {"environment": "development"}
    }
    
    # Make request to create the flag
    response = await client.post("/api/v1/feature-flags/flags", json=flag_data)
    
    # Verify response
    assert response.status_code == 409
    assert "already exists" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_bulk_update_feature_flags(
    client: AsyncClient, test_multiple_flags: List[FeatureFlag], env_setup
):
    """Test bulk updating multiple feature flags."""
    # Enable management
    os.environ["ENABLE_FEATURE_FLAG_MANAGEMENT"] = "1"
    
    # Create update data for multiple flags (using value instead of enabled)
    updates = {
        test_multiple_flags[0].name: {
            "value": not test_multiple_flags[0].value,
            "description": "Updated flag A"
        },
        test_multiple_flags[1].name: {
            "value": not test_multiple_flags[1].value,
            "description": "Updated flag B"
        }
    }
    
    # Make request to bulk update flags
    response = await client.post("/api/v1/feature-flags/flags/bulk", json=updates)
    
    # Verify response
    assert response.status_code == 200
    results = response.json()
    
    # Check that both flags were updated
    for name, update in updates.items():
        assert name in results
        assert results[name]["value"] == update["value"]
        assert results[name]["description"] == update["description"]
    
    # Verify database was updated (by getting the flags again)
    for name in updates.keys():
        response = await client.get(f"/api/v1/feature-flags/flags/{name}")
        assert response.status_code == 200
        flag = response.json()
        assert flag["value"] == updates[name]["value"]
        assert flag["description"] == updates[name]["description"]


@pytest.mark.asyncio
async def test_empty_bulk_update(client: AsyncClient, env_setup):
    """Test bulk update with empty updates."""
    # Enable management
    os.environ["ENABLE_FEATURE_FLAG_MANAGEMENT"] = "1"
    
    # Make request with empty updates
    response = await client.post("/api/v1/feature-flags/flags/bulk", json={})
    
    # Verify response
    assert response.status_code == 400
    assert "no updates" in response.json()["detail"].lower()
