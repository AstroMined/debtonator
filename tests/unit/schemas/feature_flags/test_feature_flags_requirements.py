"""
Tests for feature flag requirements schemas.

This module contains tests for the schemas used to define feature flag requirements,
including RequirementsBase, RequirementsResponse, and RequirementsUpdate.
"""

import pytest
from pydantic import ValidationError

from src.schemas.feature_flags import (
    RequirementsBase,
    RequirementsResponse,
    RequirementsUpdate,
)


def test_requirements_base_schema():
    """Test the base requirements schema."""
    req = RequirementsBase(
        flag_name="TEST_FLAG",
        requirements={
            "repository": {
                "create_typed_entity": ["bnpl", "ewa"],
                "update_typed_entity": ["bnpl", "ewa"],
            },
            "service": {
                "create_account": ["bnpl", "ewa"],
            },
            "api": {
                "/api/v1/accounts": ["bnpl", "ewa"],
            },
        },
    )
    assert req.flag_name == "TEST_FLAG"
    assert "repository" in req.requirements
    assert "create_typed_entity" in req.requirements["repository"]
    assert req.requirements["repository"]["create_typed_entity"] == ["bnpl", "ewa"]
    assert "service" in req.requirements
    assert "api" in req.requirements


def test_requirements_response_schema():
    """Test the requirements response schema."""
    resp = RequirementsResponse(
        flag_name="TEST_FLAG",
        requirements={
            "repository": {
                "create_typed_entity": ["bnpl", "ewa"],
            },
            "service": {
                "create_account": ["bnpl", "ewa"],
            },
        },
    )
    assert resp.flag_name == "TEST_FLAG"
    assert "repository" in resp.requirements
    assert "service" in resp.requirements


def test_requirements_update_schema_valid():
    """Test the requirements update schema with valid input."""
    update = RequirementsUpdate(
        requirements={
            "repository": {
                "create_typed_entity": ["bnpl", "ewa", "payment_app"],
            },
            "service": {
                "create_account": ["bnpl", "ewa", "payment_app"],
            },
        },
    )
    assert "repository" in update.requirements
    assert "service" in update.requirements
    assert update.requirements["repository"]["create_typed_entity"] == [
        "bnpl",
        "ewa",
        "payment_app",
    ]


def test_requirements_update_invalid_layer():
    """Test the requirements update schema with an invalid layer."""
    with pytest.raises(ValidationError, match="Invalid layers in requirements"):
        RequirementsUpdate(
            requirements={
                "invalid_layer": {  # Not a valid layer
                    "method": ["bnpl"],
                },
            },
        )


def test_requirements_update_invalid_repository_format():
    """Test the requirements update schema with invalid repository format."""
    with pytest.raises(
        ValidationError, match="Repository requirements must be a dictionary"
    ):
        RequirementsUpdate(
            requirements={
                "repository": "not_a_dict",  # Should be a dict
            },
        )


def test_requirements_update_invalid_method_name():
    """Test the requirements update schema with an invalid method name."""
    with pytest.raises(
        ValidationError, match="Repository method names must be strings"
    ):
        RequirementsUpdate(
            requirements={
                "repository": {
                    123: ["bnpl"],  # Method name should be a string
                },
            },
        )


def test_requirements_update_invalid_account_types():
    """Test the requirements update schema with invalid account types."""
    with pytest.raises(
        ValidationError,
        match="Account types for method 'create_typed_entity' must be a list or dictionary",
    ):
        RequirementsUpdate(
            requirements={
                "repository": {
                    "create_typed_entity": "bnpl",  # Should be a list or dict
                },
            },
        )


def test_requirements_update_non_string_account_types():
    """Test the requirements update schema with non-string account types."""
    with pytest.raises(
        ValidationError,
        match="Account types for method 'create_typed_entity' must be strings",
    ):
        RequirementsUpdate(
            requirements={
                "repository": {
                    "create_typed_entity": [123, "ewa"],  # All should be strings
                },
            },
        )


def test_requirements_update_service_validation():
    """Test the requirements update schema with service validation."""
    # Valid service requirements
    update = RequirementsUpdate(
        requirements={
            "service": {
                "create_account": ["bnpl", "ewa"],
            },
        },
    )
    assert "service" in update.requirements
    assert update.requirements["service"]["create_account"] == ["bnpl", "ewa"]

    # Invalid service method type
    with pytest.raises(
        ValidationError,
        match="Account types for method 'create_account' must be a list or dictionary",
    ):
        RequirementsUpdate(
            requirements={
                "service": {
                    "create_account": 123,  # Should be a list or dict
                },
            },
        )


def test_requirements_update_api_validation():
    """Test the requirements update schema with API validation."""
    # Valid API requirements
    update = RequirementsUpdate(
        requirements={
            "api": {
                "/api/v1/accounts": ["bnpl", "ewa"],
            },
        },
    )
    assert "api" in update.requirements
    assert update.requirements["api"]["/api/v1/accounts"] == ["bnpl", "ewa"]

    # Invalid API endpoint type
    with pytest.raises(ValidationError, match="API endpoint paths must be strings"):
        RequirementsUpdate(
            requirements={
                "api": {
                    123: ["bnpl"],  # Endpoint should be a string
                },
            },
        )

    # Invalid account types format
    with pytest.raises(
        ValidationError,
        match="Account types for endpoint '/api/v1/accounts' must be a list or dictionary",
    ):
        RequirementsUpdate(
            requirements={
                "api": {
                    "/api/v1/accounts": "all",  # Should be a list or dict
                },
            },
        )


def test_requirements_update_complex_validation():
    """Test complex validation scenarios for requirements update."""
    # Test with nested dictionary values instead of lists
    update = RequirementsUpdate(
        requirements={
            "repository": {
                "create_typed_entity": {"bnpl": True, "ewa": True, "payment_app": False}
            },
            "service": {"create_account": {"bnpl": True, "ewa": True}},
        }
    )
    assert "repository" in update.requirements
    assert "create_typed_entity" in update.requirements["repository"]
    assert update.requirements["repository"]["create_typed_entity"]["bnpl"] is True

    # Test with mixed list and dictionary values
    update = RequirementsUpdate(
        requirements={
            "repository": {
                "create_typed_entity": ["bnpl", "ewa"],
                "update_typed_entity": {"bnpl": True, "ewa": True},
            }
        }
    )
    assert update.requirements["repository"]["create_typed_entity"] == ["bnpl", "ewa"]
    assert update.requirements["repository"]["update_typed_entity"]["bnpl"] is True


def test_requirements_update_validation_comprehensive():
    """Test comprehensive validation for requirements update."""
    # Test with empty requirements
    update = RequirementsUpdate(requirements={})
    assert update.requirements == {}

    # Test with invalid top-level keys
    with pytest.raises(ValidationError, match="Invalid layers in requirements"):
        RequirementsUpdate(requirements={"invalid_layer": {}})

    # Test with multiple invalid top-level keys
    with pytest.raises(ValidationError, match="Invalid layers in requirements"):
        RequirementsUpdate(
            requirements={
                "repository": {},
                "invalid_layer1": {},
                "invalid_layer2": {},
            }
        )

    # Test with non-dictionary service requirements
    with pytest.raises(
        ValidationError, match="Service requirements must be a dictionary"
    ):
        RequirementsUpdate(
            requirements={"service": ["method1", "method2"]}  # Should be a dict
        )

    # Test with invalid service method name type
    with pytest.raises(ValidationError, match="Service method names must be strings"):
        RequirementsUpdate(requirements={"service": {123: ["admin"]}})  # Non-string key

    # Test with non-list/dict account types in service
    with pytest.raises(
        ValidationError,
        match="Account types for method 'create_account' must be a list or dictionary",
    ):
        RequirementsUpdate(
            requirements={
                "service": {"create_account": "bnpl"}  # String instead of list/dict
            }
        )

    # Test with non-string account types in service list
    with pytest.raises(
        ValidationError,
        match="Account types for method 'create_account' must be strings",
    ):
        RequirementsUpdate(
            requirements={
                "service": {"create_account": [123, 456]}  # Non-string values
            }
        )

    # Test with non-dictionary API requirements
    with pytest.raises(ValidationError, match="API requirements must be a dictionary"):
        RequirementsUpdate(
            requirements={"api": ["endpoint1", "endpoint2"]}  # Should be a dict
        )

    # Test with invalid API endpoint path type
    with pytest.raises(ValidationError, match="API endpoint paths must be strings"):
        RequirementsUpdate(requirements={"api": {123: ["admin"]}})  # Non-string key

    # Test with non-list/dict account types in API
    with pytest.raises(
        ValidationError,
        match="Account types for endpoint '/api/v1/accounts' must be a list or dictionary",
    ):
        RequirementsUpdate(
            requirements={
                "api": {"/api/v1/accounts": "bnpl"}  # String instead of list/dict
            }
        )

    # Test with non-string account types in API list
    with pytest.raises(
        ValidationError,
        match="Account types for endpoint '/api/v1/accounts' must be strings",
    ):
        RequirementsUpdate(
            requirements={"api": {"/api/v1/accounts": [123, 456]}}  # Non-string values
        )

    # Test with valid complex structure
    update = RequirementsUpdate(
        requirements={
            "repository": {
                "create_typed_entity": ["bnpl", "ewa"],
                "update_typed_entity": {"bnpl": True, "ewa": False},
            },
            "service": {
                "create_account": ["bnpl", "ewa"],
                "update_account": {
                    "bnpl": {"enabled": True},
                    "ewa": {"enabled": False},
                },
            },
            "api": {
                "/api/v1/accounts": ["bnpl", "ewa"],
                "/api/v1/accounts/{id}": {
                    "bnpl": {"methods": ["PUT", "DELETE"]},
                    "ewa": {"methods": ["GET"]},
                },
            },
        }
    )
    assert "repository" in update.requirements
    assert "service" in update.requirements
    assert "api" in update.requirements
    assert update.requirements["repository"]["create_typed_entity"] == ["bnpl", "ewa"]
    assert update.requirements["service"]["create_account"] == ["bnpl", "ewa"]
    assert update.requirements["api"]["/api/v1/accounts"] == ["bnpl", "ewa"]
