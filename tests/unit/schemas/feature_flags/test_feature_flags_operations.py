"""
Tests for feature flag operation schemas.

This module contains tests for the schemas used in CRUD operations on feature flags,
including FeatureFlagCreate, FeatureFlagUpdate, FeatureFlagToggle, and FeatureFlagResponse.
"""

import pytest
from pydantic import ValidationError

from src.schemas.feature_flags import (
    FeatureFlagCreate,
    FeatureFlagResponse,
    FeatureFlagToggle,
    FeatureFlagType,
    FeatureFlagUpdate,
)
from src.utils.datetime_utils import utc_now


# FeatureFlagCreate tests
def test_create_with_metadata():
    """Test creating a flag with metadata."""
    flag = FeatureFlagCreate(
        name="TEST_BOOLEAN_FLAG",
        flag_type=FeatureFlagType.BOOLEAN,
        value=True,
        flag_metadata={"owner": "test-team", "jira_ticket": "TEST-123"},
    )
    assert flag.flag_metadata == {"owner": "test-team", "jira_ticket": "TEST-123"}


def test_create_system_flag():
    """Test creating a system flag."""
    flag = FeatureFlagCreate(
        name="TEST_SYSTEM_FLAG",
        flag_type=FeatureFlagType.BOOLEAN,
        value=True,
        is_system=True,
    )
    assert flag.is_system is True


def test_feature_flag_create_validation_edge_cases():
    """Test edge cases for feature flag create validation."""
    # Test with None flag_type
    with pytest.raises(ValidationError):
        FeatureFlagCreate(
            name="TEST_FLAG",
            flag_type=None,
            value=True,
        )

    # Test with string flag_type
    flag = FeatureFlagCreate(
        name="STRING_TYPE_FLAG",
        flag_type="boolean",  # String instead of enum
        value=True,
    )
    assert flag.flag_type == FeatureFlagType.BOOLEAN
    assert flag.value is True


# FeatureFlagUpdate tests
def test_update_value():
    """Test updating a flag's value."""
    update = FeatureFlagUpdate(value=False)
    assert update.value is False


def test_update_description():
    """Test updating a flag's description."""
    update = FeatureFlagUpdate(description="Updated description")
    assert update.description == "Updated description"


def test_update_metadata():
    """Test updating a flag's metadata."""
    update = FeatureFlagUpdate(flag_metadata={"owner": "new-team"})
    assert update.flag_metadata == {"owner": "new-team"}


def test_update_flag_type():
    """Test updating a flag's type."""
    update = FeatureFlagUpdate(flag_type=FeatureFlagType.PERCENTAGE)
    assert update.flag_type == FeatureFlagType.PERCENTAGE


def test_update_multiple_fields():
    """Test updating multiple fields at once."""
    update = FeatureFlagUpdate(
        value=False,
        description="Updated description",
        flag_metadata={"owner": "new-team"},
    )
    assert update.value is False
    assert update.description == "Updated description"
    assert update.flag_metadata == {"owner": "new-team"}


def test_empty_update():
    """Test that an empty update is valid."""
    update = FeatureFlagUpdate()
    assert update.value is None
    assert update.description is None
    assert update.flag_metadata is None
    assert update.flag_type is None


def test_feature_flag_update_with_type_change():
    """Test updating a feature flag with a type change."""
    # Update from boolean to percentage
    update = FeatureFlagUpdate(
        flag_type=FeatureFlagType.PERCENTAGE,
        value=50,
        description="Updated to percentage flag",
    )
    assert update.flag_type == FeatureFlagType.PERCENTAGE
    assert update.value == 50
    assert update.description == "Updated to percentage flag"

    # Update from boolean to user_segment
    update = FeatureFlagUpdate(
        flag_type=FeatureFlagType.USER_SEGMENT,
        value=["admin", "beta", "premium"],
        description="Updated to user segment flag",
    )
    assert update.flag_type == FeatureFlagType.USER_SEGMENT
    assert update.value == ["admin", "beta", "premium"]
    assert update.description == "Updated to user segment flag"

    # Update with invalid value for new type
    with pytest.raises(ValidationError, match="Percentage flag value must be a number"):
        FeatureFlagUpdate(
            flag_type=FeatureFlagType.PERCENTAGE,
            value=["admin"],  # List instead of number
        )


def test_feature_flag_update_validation_edge_cases():
    """Test edge cases for feature flag update validation."""
    # Test with no fields set
    update = FeatureFlagUpdate()
    assert update.description is None
    assert update.value is None
    assert update.flag_metadata is None
    assert update.flag_type is None

    # Test with only description
    update = FeatureFlagUpdate(description="Updated description")
    assert update.description == "Updated description"
    assert update.value is None
    assert update.flag_metadata is None
    assert update.flag_type is None

    # Test with only value
    update = FeatureFlagUpdate(value=True)
    assert update.description is None
    assert update.value is True
    assert update.flag_metadata is None
    assert update.flag_type is None

    # Test with only flag_metadata
    update = FeatureFlagUpdate(flag_metadata={"owner": "test-team"})
    assert update.description is None
    assert update.value is None
    assert update.flag_metadata == {"owner": "test-team"}
    assert update.flag_type is None

    # Test with only flag_type
    update = FeatureFlagUpdate(flag_type=FeatureFlagType.BOOLEAN)
    assert update.description is None
    assert update.value is None
    assert update.flag_metadata is None
    assert update.flag_type == FeatureFlagType.BOOLEAN

    # Test with value but no flag_type (should not validate value)
    update = FeatureFlagUpdate(value="not a boolean")
    assert update.value == "not a boolean"
    assert update.flag_type is None

    # Test with flag_type but no value (should not validate value)
    update = FeatureFlagUpdate(flag_type=FeatureFlagType.BOOLEAN)
    assert update.value is None
    assert update.flag_type == FeatureFlagType.BOOLEAN


# FeatureFlagToggle tests
def test_valid_toggle():
    """Test a valid feature flag toggle."""
    toggle = FeatureFlagToggle(enabled=True)
    assert toggle.enabled is True

    toggle = FeatureFlagToggle(enabled=False)
    assert toggle.enabled is False


def test_required_enabled_field():
    """Test that the enabled field is required."""
    with pytest.raises(ValidationError):
        FeatureFlagToggle()


def test_feature_flag_toggle_validation():
    """Test validation for feature flag toggle."""
    # Valid toggle (enabled)
    toggle = FeatureFlagToggle(enabled=True)
    assert toggle.enabled is True

    # Valid toggle (disabled)
    toggle = FeatureFlagToggle(enabled=False)
    assert toggle.enabled is False

    # Missing required field - use model_validate with empty dict
    # This is the correct way to test missing required fields in Pydantic v2
    with pytest.raises(ValidationError):
        FeatureFlagToggle.model_validate({})

    # Invalid type for enabled field
    with pytest.raises(ValidationError):
        FeatureFlagToggle.model_validate(
            {"enabled": "true"}
        )  # String instead of boolean


def test_feature_flag_toggle_validation_comprehensive():
    """Test comprehensive validation for feature flag toggle with various input types."""
    # Valid boolean values
    toggle = FeatureFlagToggle(enabled=True)
    assert toggle.enabled is True

    toggle = FeatureFlagToggle(enabled=False)
    assert toggle.enabled is False

    # String values - should all fail with type validation
    with pytest.raises(ValidationError, match="enabled must be a boolean value"):
        FeatureFlagToggle.model_validate({"enabled": "true"})

    with pytest.raises(ValidationError, match="enabled must be a boolean value"):
        FeatureFlagToggle.model_validate({"enabled": "false"})

    with pytest.raises(ValidationError, match="enabled must be a boolean value"):
        FeatureFlagToggle.model_validate({"enabled": "yes"})

    with pytest.raises(ValidationError, match="enabled must be a boolean value"):
        FeatureFlagToggle.model_validate({"enabled": "no"})

    with pytest.raises(ValidationError, match="enabled must be a boolean value"):
        FeatureFlagToggle.model_validate({"enabled": "1"})

    with pytest.raises(ValidationError, match="enabled must be a boolean value"):
        FeatureFlagToggle.model_validate({"enabled": "0"})

    # Numeric values - should fail with type validation
    with pytest.raises(ValidationError, match="enabled must be a boolean value"):
        FeatureFlagToggle.model_validate({"enabled": 1})

    with pytest.raises(ValidationError, match="enabled must be a boolean value"):
        FeatureFlagToggle.model_validate({"enabled": 0})

    with pytest.raises(ValidationError, match="enabled must be a boolean value"):
        FeatureFlagToggle.model_validate({"enabled": 1.0})

    with pytest.raises(ValidationError, match="enabled must be a boolean value"):
        FeatureFlagToggle.model_validate({"enabled": 0.0})

    # Collection values - should fail with type validation
    with pytest.raises(ValidationError, match="enabled must be a boolean value"):
        FeatureFlagToggle.model_validate({"enabled": []})

    with pytest.raises(ValidationError, match="enabled must be a boolean value"):
        FeatureFlagToggle.model_validate({"enabled": [True]})

    with pytest.raises(ValidationError, match="enabled must be a boolean value"):
        FeatureFlagToggle.model_validate({"enabled": {}})

    with pytest.raises(ValidationError, match="enabled must be a boolean value"):
        FeatureFlagToggle.model_validate({"enabled": {"value": True}})

    # None value - should fail with type validation
    with pytest.raises(ValidationError, match="enabled must be a boolean value"):
        FeatureFlagToggle.model_validate({"enabled": None})

    # Missing field - should fail with field required validation
    with pytest.raises(ValidationError):
        FeatureFlagToggle.model_validate({})

    # Extra fields - should be ignored
    toggle = FeatureFlagToggle.model_validate({"enabled": True, "extra_field": "value"})
    assert toggle.enabled is True
    assert not hasattr(toggle, "extra_field")


# FeatureFlagResponse tests
def test_valid_response():
    """Test a valid feature flag response."""
    now = utc_now()
    response = FeatureFlagResponse(
        name="TEST_FLAG",
        flag_type=FeatureFlagType.BOOLEAN,
        value=True,
        description="Test flag",
        flag_metadata={"owner": "test-team"},
        is_system=False,
        created_at=now,
        updated_at=now,
    )
    assert response.name == "TEST_FLAG"
    assert response.flag_type == FeatureFlagType.BOOLEAN
    assert response.value is True
    assert response.description == "Test flag"
    assert response.flag_metadata == {"owner": "test-team"}
    assert response.is_system is False
    assert response.created_at == now
    assert response.updated_at == now


def test_response_with_minimal_fields():
    """Test a response with only required fields."""
    now = utc_now()
    response = FeatureFlagResponse(
        name="TEST_FLAG",
        flag_type=FeatureFlagType.BOOLEAN,
        value=True,
        created_at=now,
        updated_at=now,
    )
    assert response.name == "TEST_FLAG"
    assert response.flag_type == FeatureFlagType.BOOLEAN
    assert response.value is True
    assert response.description is None
    assert response.flag_metadata is None
    assert response.is_system is False
    assert response.created_at == now
    assert response.updated_at == now


def test_environment_flag_response():
    """Test a response with an environment flag."""
    now = utc_now()
    response = FeatureFlagResponse(
        name="ENV_FLAG",
        flag_type=FeatureFlagType.ENVIRONMENT,
        value={"environments": ["dev", "staging", "prod"], "default": False},
        created_at=now,
        updated_at=now,
    )
    assert response.name == "ENV_FLAG"
    assert response.flag_type == FeatureFlagType.ENVIRONMENT
    assert response.value["environments"] == ["dev", "staging", "prod"]
    assert response.value["default"] is False
    assert response.created_at == now
    assert response.updated_at == now


def test_feature_flag_response_with_all_fields():
    """Test feature flag response with all fields populated."""
    now = utc_now()

    # Test with all fields for a boolean flag
    response = FeatureFlagResponse(
        name="COMPLETE_FLAG",
        flag_type=FeatureFlagType.BOOLEAN,
        value=True,
        description="Complete flag with all fields",
        flag_metadata={
            "owner": "test-team",
            "jira_ticket": "TEST-123",
            "priority": "high",
            "category": "experimental",
        },
        is_system=True,
        created_at=now,
        updated_at=now,
    )
    assert response.name == "COMPLETE_FLAG"
    assert response.flag_type == FeatureFlagType.BOOLEAN
    assert response.value is True
    assert response.description == "Complete flag with all fields"
    assert response.flag_metadata["owner"] == "test-team"
    assert response.flag_metadata["jira_ticket"] == "TEST-123"
    assert response.flag_metadata["priority"] == "high"
    assert response.flag_metadata["category"] == "experimental"
    assert response.is_system is True
    assert response.created_at == now
    assert response.updated_at == now
