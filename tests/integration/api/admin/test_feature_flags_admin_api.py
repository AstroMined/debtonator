"""
Integration tests for the feature flag admin API endpoints.

This module contains integration tests for the feature flag admin API endpoints,
including requirements management, flag operations, and error handling.
"""

import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.feature_flags import FeatureFlag
from src.repositories.feature_flags import FeatureFlagRepository
from src.utils.feature_flags.requirements import get_default_requirements


@pytest.mark.asyncio
async def test_list_feature_flags(
    client: AsyncClient, test_multiple_flags: list[FeatureFlag]
):
    """Test listing all feature flags through the admin API."""
    # Make request to list flags
    response = await client.get("/api/admin/feature-flags")

    # Verify response
    assert response.status_code == 200
    flags = response.json()
    assert len(flags) >= len(test_multiple_flags)

    # Check that all test flags are in the response
    flag_names = [flag["name"] for flag in flags]
    for test_flag in test_multiple_flags:
        assert test_flag.name in flag_names


@pytest.mark.asyncio
async def test_get_feature_flag(client: AsyncClient, test_boolean_flag: FeatureFlag):
    """Test getting a specific feature flag through the admin API."""
    # Make request to get a specific flag
    response = await client.get(f"/api/admin/feature-flags/{test_boolean_flag.name}")

    # Verify response
    assert response.status_code == 200
    flag = response.json()
    assert flag["name"] == test_boolean_flag.name
    assert flag["value"] == test_boolean_flag.value
    assert flag["flag_type"] == test_boolean_flag.flag_type


@pytest.mark.asyncio
async def test_get_feature_flag_not_found(client: AsyncClient):
    """Test getting a non-existent feature flag through the admin API."""
    # Make request to get a non-existent flag
    response = await client.get("/api/admin/feature-flags/NON_EXISTENT_FLAG")

    # Verify response
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_feature_flag(client: AsyncClient, test_boolean_flag: FeatureFlag):
    """Test updating a feature flag through the admin API."""
    # Create update data
    update_data = {
        "value": not test_boolean_flag.value,
        "description": "Updated through admin API",
        "flag_metadata": {"environment": "test", "updated_via": "admin_api"},
    }

    # Make request to update the flag
    response = await client.put(
        f"/api/admin/feature-flags/{test_boolean_flag.name}",
        json=update_data,
    )

    # Verify response
    assert response.status_code == 200
    flag = response.json()
    assert flag["name"] == test_boolean_flag.name
    assert flag["value"] == update_data["value"]
    assert flag["description"] == update_data["description"]
    assert flag["flag_metadata"]["environment"] == "test"
    assert flag["flag_metadata"]["updated_via"] == "admin_api"

    # Verify database was updated (by getting the flag again)
    response = await client.get(f"/api/admin/feature-flags/{test_boolean_flag.name}")
    flag = response.json()
    assert flag["value"] == update_data["value"]
    assert flag["description"] == update_data["description"]


@pytest.mark.asyncio
async def test_get_flag_requirements(
    client: AsyncClient, test_boolean_flag: FeatureFlag, db_session: AsyncSession
):
    """Test getting requirements for a feature flag."""
    # Set up initial requirements
    repository = FeatureFlagRepository(db_session)

    test_requirements = {
        "repository": {
            "create_typed_entity": ["bnpl", "ewa", "payment_app"],
        },
        "service": {
            "create_account": ["bnpl", "ewa", "payment_app"],
        },
    }

    await repository.update_requirements(test_boolean_flag.name, test_requirements)
    await db_session.commit()

    # Make request to get requirements
    response = await client.get(
        f"/api/admin/feature-flags/{test_boolean_flag.name}/requirements"
    )

    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert result["flag_name"] == test_boolean_flag.name
    assert "repository" in result["requirements"]
    assert "service" in result["requirements"]
    assert result["requirements"]["repository"]["create_typed_entity"] == [
        "bnpl",
        "ewa",
        "payment_app",
    ]


@pytest.mark.asyncio
async def test_get_flag_requirements_not_found(client: AsyncClient):
    """Test getting requirements for a non-existent feature flag."""
    # Make request to get requirements for a non-existent flag
    response = await client.get(
        "/api/admin/feature-flags/NON_EXISTENT_FLAG/requirements"
    )

    # Verify response
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_update_flag_requirements(
    client: AsyncClient, test_boolean_flag: FeatureFlag, db_session: AsyncSession
):
    """Test updating requirements for a feature flag."""
    # Create update data
    update_data = {
        "requirements": {
            "repository": {
                "create_typed_entity": ["bnpl", "ewa", "payment_app"],
                "update_typed_entity": ["bnpl", "ewa", "payment_app"],
            },
            "service": {
                "create_account": ["bnpl", "ewa", "payment_app"],
            },
            "api": {
                "/api/v1/accounts": ["bnpl", "ewa", "payment_app"],
            },
        }
    }

    # Make request to update requirements
    response = await client.put(
        f"/api/admin/feature-flags/{test_boolean_flag.name}/requirements",
        json=update_data,
    )

    # Verify response
    assert response.status_code == 200
    result = response.json()
    assert result["flag_name"] == test_boolean_flag.name
    assert "repository" in result["requirements"]
    assert "service" in result["requirements"]
    assert "api" in result["requirements"]

    # Verify database was updated
    repository = FeatureFlagRepository(db_session)
    flag = await repository.get(test_boolean_flag.name)
    assert flag.requirements is not None
    assert "repository" in flag.requirements
    assert "service" in flag.requirements
    assert "api" in flag.requirements
    assert flag.requirements["repository"]["create_typed_entity"] == [
        "bnpl",
        "ewa",
        "payment_app",
    ]


@pytest.mark.asyncio
async def test_update_flag_requirements_invalid_structure(
    client: AsyncClient, test_boolean_flag: FeatureFlag
):
    """Test updating requirements with an invalid structure."""
    # Create invalid update data
    update_data = {
        "requirements": {
            "invalid_layer": {  # Invalid layer
                "create_typed_entity": ["bnpl", "ewa", "payment_app"],
            },
        }
    }

    # Make request to update requirements
    response = await client.put(
        f"/api/admin/feature-flags/{test_boolean_flag.name}/requirements",
        json=update_data,
    )

    # Verify response
    assert response.status_code == 422  # Validation error
    assert "invalid" in response.json()["detail"][0]["msg"].lower()


@pytest.mark.asyncio
async def test_update_flag_requirements_not_found(client: AsyncClient):
    """Test updating requirements for a non-existent feature flag."""
    # Create update data
    update_data = {
        "requirements": {
            "repository": {
                "create_typed_entity": ["bnpl", "ewa", "payment_app"],
            },
        }
    }

    # Make request to update requirements for a non-existent flag
    response = await client.put(
        "/api/admin/feature-flags/NON_EXISTENT_FLAG/requirements",
        json=update_data,
    )

    # Verify response
    assert response.status_code == 404
    assert "not found" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_flag_history(client: AsyncClient, test_boolean_flag: FeatureFlag):
    """Test getting history for a feature flag."""
    # Make request to get history
    response = await client.get(
        f"/api/admin/feature-flags/{test_boolean_flag.name}/history"
    )

    # Verify response (should be not implemented)
    assert response.status_code == 501
    assert "not implemented" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_flag_metrics(client: AsyncClient, test_boolean_flag: FeatureFlag):
    """Test getting metrics for a feature flag."""
    # Make request to get metrics
    response = await client.get(
        f"/api/admin/feature-flags/{test_boolean_flag.name}/metrics"
    )

    # Verify response (should be not implemented)
    assert response.status_code == 501
    assert "not implemented" in response.json()["detail"].lower()


@pytest.mark.asyncio
async def test_get_default_requirements(client: AsyncClient):
    """Test getting default requirements."""
    # Make request to get default requirements
    response = await client.get("/api/admin/feature-flags/default-requirements")

    # Verify response
    assert response.status_code == 200
    default_requirements = response.json()

    # Check structure matches the utility function
    expected_requirements = get_default_requirements()
    assert default_requirements == expected_requirements

    # Check basic structure for key flags
    assert "BANKING_ACCOUNT_TYPES_ENABLED" in default_requirements
    assert "repository" in default_requirements["BANKING_ACCOUNT_TYPES_ENABLED"]
    assert "service" in default_requirements["BANKING_ACCOUNT_TYPES_ENABLED"]
    assert "api" in default_requirements["BANKING_ACCOUNT_TYPES_ENABLED"]
