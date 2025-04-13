"""
Additional unit tests for feature flag schemas.

These tests focus on improving coverage for the feature_flags.py schema file,
targeting specific validators and edge cases that aren't covered by the existing tests.
"""

import pytest
from pydantic import ValidationError

from src.schemas.feature_flags import (
    FeatureFlagBase,
    FeatureFlagContext,
    FeatureFlagCreate,
    FeatureFlagResponse,
    FeatureFlagToggle,
    FeatureFlagType,
    FeatureFlagUpdate,
    FlagHistoryEntry,
    FlagMetricsResponse,
    RequirementsUpdate,
)
from src.utils.datetime_utils import utc_now


def test_feature_flag_base_name_validation_edge_cases():
    """Test edge cases for feature flag name validation."""
    # Valid name with numbers
    flag = FeatureFlagBase(name="TEST_FLAG_123")
    assert flag.name == "TEST_FLAG_123"

    # Valid name with underscores
    flag = FeatureFlagBase(name="TEST_FLAG_WITH_UNDERSCORES")
    assert flag.name == "TEST_FLAG_WITH_UNDERSCORES"

    # Invalid name starting with number
    with pytest.raises(
        ValidationError, match="Feature flag name must start with an uppercase letter"
    ):
        FeatureFlagBase(name="1TEST_FLAG")

    # Invalid name with lowercase letters
    with pytest.raises(
        ValidationError, match="Feature flag name must contain only uppercase letters"
    ):
        FeatureFlagBase(name="TEST_flag")

    # Invalid name with special characters
    with pytest.raises(
        ValidationError, match="Feature flag name must contain only uppercase letters"
    ):
        FeatureFlagBase(name="TEST-FLAG")

    # Invalid name with spaces
    with pytest.raises(
        ValidationError, match="Feature flag name must contain only uppercase letters"
    ):
        FeatureFlagBase(name="TEST FLAG")


def test_feature_flag_create_with_complex_values():
    """Test creating feature flags with complex nested values."""
    # Test environment flag with complex nested structure
    flag = FeatureFlagCreate(
        name="COMPLEX_ENV_FLAG",
        flag_type=FeatureFlagType.ENVIRONMENT,
        value={
            "environments": ["dev", "staging", "prod", "test"],
            "default": False,
            "overrides": {"dev": True, "staging": True},
        },
        description="Complex environment flag",
    )
    assert flag.name == "COMPLEX_ENV_FLAG"
    assert flag.flag_type == FeatureFlagType.ENVIRONMENT
    assert flag.value["environments"] == ["dev", "staging", "prod", "test"]
    assert flag.value["default"] is False
    assert flag.value["overrides"]["dev"] is True

    # Test time-based flag with complex structure
    now = utc_now()
    flag = FeatureFlagCreate(
        name="COMPLEX_TIME_FLAG",
        flag_type=FeatureFlagType.TIME_BASED,
        value={
            "start_time": now.isoformat(),
            "end_time": (now.replace(hour=23, minute=59, second=59)).isoformat(),
            "timezone": "UTC",
            "active_days": ["Monday", "Wednesday", "Friday"],
        },
        description="Complex time-based flag",
    )
    assert flag.name == "COMPLEX_TIME_FLAG"
    assert flag.flag_type == FeatureFlagType.TIME_BASED
    assert "start_time" in flag.value
    assert "end_time" in flag.value
    assert flag.value["timezone"] == "UTC"
    assert flag.value["active_days"] == ["Monday", "Wednesday", "Friday"]


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


def test_feature_flag_context_with_all_fields():
    """Test feature flag context with all fields populated."""
    context = FeatureFlagContext(
        user_id="user-123",
        user_groups=["admin", "beta", "premium"],
        is_admin=True,
        is_beta_tester=True,
        request_path="/api/v1/accounts",
        client_ip="192.168.1.1",
    )
    assert context.user_id == "user-123"
    assert context.user_groups == ["admin", "beta", "premium"]
    assert context.is_admin is True
    assert context.is_beta_tester is True
    assert context.request_path == "/api/v1/accounts"
    assert context.client_ip == "192.168.1.1"


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

    # Test with invalid layer structure (non-dictionary)
    with pytest.raises(
        ValidationError, match="Repository requirements must be a dictionary"
    ):
        RequirementsUpdate(
            requirements={"repository": ["method1", "method2"]}  # Should be a dict
        )

    # Test with invalid method name type
    with pytest.raises(
        ValidationError, match="Repository method names must be strings"
    ):
        RequirementsUpdate(
            requirements={"repository": {123: ["bnpl"]}}  # Non-string key
        )


def test_flag_history_entry_with_complex_values():
    """Test flag history entries with complex values."""
    now = utc_now()

    # Test with boolean value
    entry = FlagHistoryEntry(
        flag_name="TEST_FLAG",
        timestamp=now,
        change_type="update",
        old_value=False,
        new_value=True,
    )
    assert entry.flag_name == "TEST_FLAG"
    assert entry.change_type == "update"
    assert entry.old_value is False
    assert entry.new_value is True

    # Test with percentage value
    entry = FlagHistoryEntry(
        flag_name="PERCENTAGE_FLAG",
        timestamp=now,
        change_type="update",
        old_value=25,
        new_value=50,
    )
    assert entry.old_value == 25
    assert entry.new_value == 50

    # Test with user segment value
    entry = FlagHistoryEntry(
        flag_name="USER_SEGMENT_FLAG",
        timestamp=now,
        change_type="update",
        old_value=["admin"],
        new_value=["admin", "beta"],
    )
    assert entry.old_value == ["admin"]
    assert entry.new_value == ["admin", "beta"]

    # Test with environment value
    entry = FlagHistoryEntry(
        flag_name="ENV_FLAG",
        timestamp=now,
        change_type="update",
        old_value={"environments": ["dev"], "default": False},
        new_value={"environments": ["dev", "staging"], "default": True},
    )
    assert entry.old_value["environments"] == ["dev"]
    assert entry.new_value["environments"] == ["dev", "staging"]
    assert entry.old_value["default"] is False
    assert entry.new_value["default"] is True


def test_flag_metrics_response_with_partial_data():
    """Test flag metrics response with partial data."""
    # Test with minimal data
    metrics = FlagMetricsResponse(
        flag_name="TEST_FLAG",
        check_count=0,
        layers={},
    )
    assert metrics.flag_name == "TEST_FLAG"
    assert metrics.check_count == 0
    assert metrics.layers == {}
    assert metrics.last_checked is None

    # Test with partial layer data
    metrics = FlagMetricsResponse(
        flag_name="TEST_FLAG",
        check_count=500,
        layers={
            "repository": 500,
            # Missing service and api layers
        },
    )
    assert metrics.flag_name == "TEST_FLAG"
    assert metrics.check_count == 500
    assert metrics.layers["repository"] == 500
    assert "service" not in metrics.layers
    assert "api" not in metrics.layers

    # Test with all layers but zero counts
    metrics = FlagMetricsResponse(
        flag_name="UNUSED_FLAG",
        check_count=0,
        layers={
            "repository": 0,
            "service": 0,
            "api": 0,
        },
    )
    assert metrics.flag_name == "UNUSED_FLAG"
    assert metrics.check_count == 0
    assert metrics.layers["repository"] == 0
    assert metrics.layers["service"] == 0
    assert metrics.layers["api"] == 0


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
