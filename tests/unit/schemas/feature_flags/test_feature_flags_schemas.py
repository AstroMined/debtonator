"""
Unit tests for feature flags schemas.

Tests the FeatureFlag schema validation and serialization
as part of ADR-024 Feature Flags.
"""

import json

import pytest
from pydantic import ValidationError

from src.schemas.feature_flags import (
    FeatureFlagBase,
    FeatureFlagCreate,
    FeatureFlagResponse,
    FeatureFlagType,
    FeatureFlagUpdate,
)
from src.utils.datetime_utils import utc_now


def test_feature_flag_base_schema():
    """Test the base feature flag schema."""
    # Test boolean feature flag
    boolean_flag = FeatureFlagBase(
        name="enable_dark_mode",
        description="Enable dark mode UI",
        flag_type=FeatureFlagType.BOOLEAN,
        is_enabled=True,
        value_json=json.dumps(True),
    )
    assert boolean_flag.name == "enable_dark_mode"
    assert boolean_flag.description == "Enable dark mode UI"
    assert boolean_flag.flag_type == FeatureFlagType.BOOLEAN
    assert boolean_flag.is_enabled is True
    assert json.loads(boolean_flag.value_json) is True

    # Test percentage feature flag
    percentage_flag = FeatureFlagBase(
        name="new_feature_rollout",
        description="Percentage rollout of new feature",
        flag_type=FeatureFlagType.PERCENTAGE,
        is_enabled=True,
        value_json=json.dumps(25.5),  # 25.5% rollout
    )
    assert percentage_flag.name == "new_feature_rollout"
    assert percentage_flag.flag_type == FeatureFlagType.PERCENTAGE
    assert json.loads(percentage_flag.value_json) == 25.5


def test_feature_flag_name_validation():
    """Test validation of feature flag names."""
    # Test valid name
    flag = FeatureFlagBase(
        name="valid_flag_name",
        description="Valid flag",
        flag_type=FeatureFlagType.BOOLEAN,
        is_enabled=True,
        value_json=json.dumps(True),
    )
    assert flag.name == "valid_flag_name"

    # Test invalid name (with spaces)
    with pytest.raises(ValidationError, match="Flag name must be snake_case"):
        FeatureFlagBase(
            name="Invalid Flag Name",
            description="Invalid flag",
            flag_type=FeatureFlagType.BOOLEAN,
            is_enabled=True,
            value_json=json.dumps(True),
        )

    # Test invalid name (with special characters)
    with pytest.raises(ValidationError, match="Flag name must be snake_case"):
        FeatureFlagBase(
            name="invalid-flag-name",
            description="Invalid flag",
            flag_type=FeatureFlagType.BOOLEAN,
            is_enabled=True,
            value_json=json.dumps(True),
        )


def test_feature_flag_value_validation():
    """Test validation of feature flag values based on flag_type."""
    # Test invalid boolean value
    with pytest.raises(ValidationError, match="Value must be a boolean"):
        FeatureFlagBase(
            name="test_flag",
            description="Test flag",
            flag_type=FeatureFlagType.BOOLEAN,
            is_enabled=True,
            value_json=json.dumps("not_a_boolean"),  # Invalid for boolean type
        )

    # Test invalid percentage value (negative)
    with pytest.raises(ValidationError, match="must be between 0 and 100"):
        FeatureFlagBase(
            name="test_flag",
            description="Test flag",
            flag_type=FeatureFlagType.PERCENTAGE,
            is_enabled=True,
            value_json=json.dumps(-10),  # Negative percentage
        )

    # Test invalid percentage value (over 100)
    with pytest.raises(ValidationError, match="must be between 0 and 100"):
        FeatureFlagBase(
            name="test_flag",
            description="Test flag",
            flag_type=FeatureFlagType.PERCENTAGE,
            is_enabled=True,
            value_json=json.dumps(101),  # Over 100%
        )

    # Test invalid user segment value (not a list)
    with pytest.raises(
        ValidationError, match="User segments must be a list of strings"
    ):
        FeatureFlagBase(
            name="test_flag",
            description="Test flag",
            flag_type=FeatureFlagType.USER_SEGMENT,
            is_enabled=True,
            value_json=json.dumps("premium"),  # Should be ["premium"]
        )


def test_feature_flag_time_based_validation():
    """Test validation of time-based feature flags."""
    # Valid time-based configuration
    valid_time_config = {
        "start": "2025-04-01T00:00:00Z",
        "end": "2025-04-30T23:59:59Z",
    }

    flag = FeatureFlagBase(
        name="valid_time_flag",
        description="Valid time-based flag",
        flag_type=FeatureFlagType.TIME_BASED,
        is_enabled=True,
        value_json=json.dumps(valid_time_config),
    )
    assert flag.name == "valid_time_flag"

    # Invalid time-based configuration (end before start)
    invalid_time_config = {
        "start": "2025-04-30T00:00:00Z",
        "end": "2025-04-01T23:59:59Z",  # Before start date
    }

    with pytest.raises(ValidationError, match="End date must be after start date"):
        FeatureFlagBase(
            name="invalid_time_flag",
            description="Invalid time-based flag",
            flag_type=FeatureFlagType.TIME_BASED,
            is_enabled=True,
            value_json=json.dumps(invalid_time_config),
        )


def test_feature_flag_complex_validation():
    """Test validation of complex feature flags."""
    # Complex configuration with nested structure
    complex_config = {
        "version": "1.0",
        "settings": {"min_balance": "1000.00", "threshold": 500, "notification": True},
        "eligibility": ["premium", "business"],
        "regions": {"us": True, "eu": False},
    }

    flag = FeatureFlagBase(
        name="complex_flag",
        description="Complex configuration flag",
        flag_type=FeatureFlagType.COMPLEX,
        is_enabled=True,
        value_json=json.dumps(complex_config),
    )
    assert flag.name == "complex_flag"
    loaded_value = json.loads(flag.value_json)
    assert loaded_value["version"] == "1.0"
    assert loaded_value["settings"]["min_balance"] == "1000.00"
    assert loaded_value["eligibility"] == ["premium", "business"]


def test_feature_flag_create_schema():
    """Test the feature flag create schema."""
    flag_create = FeatureFlagCreate(
        name="new_feature",
        description="A new feature flag",
        flag_type=FeatureFlagType.BOOLEAN,
        is_enabled=True,
        value_json=json.dumps(True),
        category="ui",
    )
    assert flag_create.name == "new_feature"
    assert flag_create.category == "ui"


def test_feature_flag_update_schema():
    """Test the feature flag update schema."""
    # Test partial update (only description)
    flag_update = FeatureFlagUpdate(
        description="Updated description",
    )
    assert flag_update.description == "Updated description"
    assert flag_update.is_enabled is None  # Not updated

    # Test update with all fields
    flag_update = FeatureFlagUpdate(
        description="Fully updated flag",
        is_enabled=False,
        value_json=json.dumps(False),
        category="updated_category",
    )
    assert flag_update.description == "Fully updated flag"
    assert flag_update.is_enabled is False
    assert json.loads(flag_update.value_json) is False
    assert flag_update.category == "updated_category"


def test_feature_flag_response_schema():
    """Test the feature flag response schema."""
    now = utc_now()

    flag_response = FeatureFlagResponse(
        id=1,
        name="test_flag",
        description="Test flag",
        flag_type=FeatureFlagType.BOOLEAN,
        is_enabled=True,
        value_json=json.dumps(True),
        category="test",
        created_at=now,
        updated_at=now,
    )
    assert flag_response.id == 1
    assert flag_response.name == "test_flag"
    assert flag_response.flag_type == FeatureFlagType.BOOLEAN
    assert flag_response.category == "test"
    assert flag_response.created_at == now
    assert flag_response.updated_at == now


def test_feature_flag_banking_category():
    """Test banking-specific feature flags."""
    # Banking account types flag
    banking_flag = FeatureFlagCreate(
        name="enable_new_account_types",
        description="Enable new banking account types",
        flag_type=FeatureFlagType.USER_SEGMENT,
        is_enabled=True,
        value_json=json.dumps(["beta_testers", "premium"]),
        category="banking",
    )
    assert banking_flag.name == "enable_new_account_types"
    assert banking_flag.category == "banking"
    assert json.loads(banking_flag.value_json) == ["beta_testers", "premium"]
