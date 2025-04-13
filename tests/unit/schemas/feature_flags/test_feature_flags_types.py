"""
Tests for different feature flag type validations.

This module contains tests for the validation of different feature flag types,
including boolean, percentage, user segment, time-based, and environment flags.
"""

import pytest
from pydantic import ValidationError

from src.schemas.feature_flags import FeatureFlagCreate, FeatureFlagType, FeatureFlagUpdate
from src.utils.datetime_utils import utc_now


# Boolean flag tests
def test_valid_boolean_flag():
    """Test creating a valid boolean flag."""
    flag = FeatureFlagCreate(
        name="TEST_BOOLEAN_FLAG",
        flag_type=FeatureFlagType.BOOLEAN,
        value=True,
        description="Test boolean flag",
    )
    assert flag.name == "TEST_BOOLEAN_FLAG"
    assert flag.flag_type == FeatureFlagType.BOOLEAN
    assert flag.value is True
    assert flag.description == "Test boolean flag"
    assert flag.is_system is False  # Default value


def test_invalid_boolean_value():
    """Test that boolean flags must have boolean values."""
    with pytest.raises(ValidationError, match="Boolean flag value must be a boolean"):
        FeatureFlagCreate(
            name="TEST_BOOLEAN_FLAG",
            flag_type=FeatureFlagType.BOOLEAN,
            value="true",  # String instead of boolean
        )


def test_boolean_flag_update():
    """Test updating a boolean flag."""
    update = FeatureFlagUpdate(
        flag_type=FeatureFlagType.BOOLEAN,
        value=True,
    )
    assert update.flag_type == FeatureFlagType.BOOLEAN
    assert update.value is True

    # Invalid update
    with pytest.raises(ValidationError, match="Boolean flag value must be a boolean"):
        FeatureFlagUpdate(
            flag_type=FeatureFlagType.BOOLEAN,
            value="not-a-boolean",  # String instead of boolean
        )


# Percentage flag tests
def test_valid_percentage_flag():
    """Test creating a valid percentage flag."""
    flag = FeatureFlagCreate(
        name="TEST_PERCENTAGE_FLAG",
        flag_type=FeatureFlagType.PERCENTAGE,
        value=50,
        description="Test percentage flag",
    )
    assert flag.name == "TEST_PERCENTAGE_FLAG"
    assert flag.flag_type == FeatureFlagType.PERCENTAGE
    assert flag.value == 50
    assert flag.description == "Test percentage flag"


def test_invalid_percentage_value():
    """Test that percentage flags must have numeric values between 0 and 100."""
    # Test non-numeric value
    with pytest.raises(ValidationError, match="Percentage flag value must be a number"):
        FeatureFlagCreate(
            name="TEST_PERCENTAGE_FLAG",
            flag_type=FeatureFlagType.PERCENTAGE,
            value="50",  # String instead of number
        )

    # Test value out of range (negative)
    with pytest.raises(ValidationError, match="Percentage flag value must be between 0 and 100"):
        FeatureFlagCreate(
            name="TEST_PERCENTAGE_FLAG",
            flag_type=FeatureFlagType.PERCENTAGE,
            value=-10,
        )

    # Test value out of range (over 100)
    with pytest.raises(ValidationError, match="Percentage flag value must be between 0 and 100"):
        FeatureFlagCreate(
            name="TEST_PERCENTAGE_FLAG",
            flag_type=FeatureFlagType.PERCENTAGE,
            value=110,
        )


def test_percentage_flag_update():
    """Test updating a percentage flag."""
    update = FeatureFlagUpdate(
        flag_type=FeatureFlagType.PERCENTAGE,
        value=75,
    )
    assert update.flag_type == FeatureFlagType.PERCENTAGE
    assert update.value == 75

    # Invalid update - non-numeric value
    with pytest.raises(ValidationError, match="Percentage flag value must be a number"):
        FeatureFlagUpdate(
            flag_type=FeatureFlagType.PERCENTAGE,
            value="75%",  # String instead of number
        )

    # Invalid update - negative value
    with pytest.raises(ValidationError, match="Percentage flag value must be between 0 and 100"):
        FeatureFlagUpdate(
            flag_type=FeatureFlagType.PERCENTAGE,
            value=-10,
        )

    # Invalid update - value over 100
    with pytest.raises(ValidationError, match="Percentage flag value must be between 0 and 100"):
        FeatureFlagUpdate(
            flag_type=FeatureFlagType.PERCENTAGE,
            value=110,
        )


# User segment flag tests
def test_valid_user_segment_flag():
    """Test creating a valid user segment flag."""
    flag = FeatureFlagCreate(
        name="TEST_USER_SEGMENT_FLAG",
        flag_type=FeatureFlagType.USER_SEGMENT,
        value=["admin", "beta"],
        description="Test user segment flag",
    )
    assert flag.name == "TEST_USER_SEGMENT_FLAG"
    assert flag.flag_type == FeatureFlagType.USER_SEGMENT
    assert flag.value == ["admin", "beta"]
    assert flag.description == "Test user segment flag"


def test_invalid_user_segment_value():
    """Test that user segment flags must have list values."""
    with pytest.raises(ValidationError, match="User segment flag value must be a list of segments"):
        FeatureFlagCreate(
            name="TEST_USER_SEGMENT_FLAG",
            flag_type=FeatureFlagType.USER_SEGMENT,
            value="admin",  # String instead of list
        )


def test_user_segment_flag_update():
    """Test updating a user segment flag."""
    update = FeatureFlagUpdate(
        flag_type=FeatureFlagType.USER_SEGMENT,
        value=["admin", "beta", "premium"],
    )
    assert update.flag_type == FeatureFlagType.USER_SEGMENT
    assert update.value == ["admin", "beta", "premium"]

    # Invalid update
    with pytest.raises(ValidationError, match="User segment flag value must be a list of segments"):
        FeatureFlagUpdate(
            flag_type=FeatureFlagType.USER_SEGMENT,
            value="admin",  # String instead of list
        )


# Time-based flag tests
def test_valid_time_based_flag():
    """Test creating a valid time-based flag."""
    start_time = utc_now()
    flag = FeatureFlagCreate(
        name="TEST_TIME_BASED_FLAG",
        flag_type=FeatureFlagType.TIME_BASED,
        value={"start_time": start_time.isoformat()},
        description="Test time-based flag",
    )
    assert flag.name == "TEST_TIME_BASED_FLAG"
    assert flag.flag_type == FeatureFlagType.TIME_BASED
    assert flag.value["start_time"] == start_time.isoformat()
    assert flag.description == "Test time-based flag"


def test_invalid_time_based_value():
    """Test that time-based flags must have dictionary values."""
    with pytest.raises(ValidationError, match="Time-based flag value must be a dictionary"):
        FeatureFlagCreate(
            name="TEST_TIME_BASED_FLAG",
            flag_type=FeatureFlagType.TIME_BASED,
            value="2025-01-01",  # String instead of dict
        )


def test_time_based_flag_update():
    """Test updating a time-based flag."""
    now = utc_now()
    update = FeatureFlagUpdate(
        flag_type=FeatureFlagType.TIME_BASED,
        value={
            "start_time": now.isoformat(),
            "end_time": (now.replace(hour=23, minute=59, second=59)).isoformat(),
        },
    )
    assert update.flag_type == FeatureFlagType.TIME_BASED
    assert update.value["start_time"] == now.isoformat()

    # Invalid update
    with pytest.raises(ValidationError, match="Time-based flag value must be a dictionary"):
        FeatureFlagUpdate(
            flag_type=FeatureFlagType.TIME_BASED,
            value="2025-01-01",  # String instead of dict
        )


# Environment flag tests
def test_valid_environment_flag():
    """Test creating a valid environment flag."""
    flag = FeatureFlagCreate(
        name="TEST_ENVIRONMENT_FLAG",
        flag_type=FeatureFlagType.ENVIRONMENT,
        value={"environments": ["dev", "staging", "prod"], "default": False},
        description="Test environment flag",
    )
    assert flag.name == "TEST_ENVIRONMENT_FLAG"
    assert flag.flag_type == FeatureFlagType.ENVIRONMENT
    assert flag.value["environments"] == ["dev", "staging", "prod"]
    assert flag.value["default"] is False
    assert flag.description == "Test environment flag"


def test_invalid_environment_flag_missing_keys():
    """Test that environment flags must have required keys."""
    with pytest.raises(ValidationError, match="Environment flag value must contain 'environments' and 'default' keys"):
        FeatureFlagCreate(
            name="TEST_ENVIRONMENT_FLAG",
            flag_type=FeatureFlagType.ENVIRONMENT,
            value={"environments": ["dev", "staging"]},  # Missing 'default' key
        )

    with pytest.raises(ValidationError, match="Environment flag value must contain 'environments' and 'default' keys"):
        FeatureFlagCreate(
            name="TEST_ENVIRONMENT_FLAG",
            flag_type=FeatureFlagType.ENVIRONMENT,
            value={"default": True},  # Missing 'environments' key
        )


def test_invalid_environment_flag_wrong_type():
    """Test that environment flags must have the correct value types."""
    with pytest.raises(ValidationError, match="'environments' must be a list of environment names"):
        FeatureFlagCreate(
            name="TEST_ENVIRONMENT_FLAG",
            flag_type=FeatureFlagType.ENVIRONMENT,
            value={
                "environments": "dev,staging",  # String instead of list
                "default": False,
            },
        )


def test_environment_flag_update():
    """Test updating an environment flag."""
    update = FeatureFlagUpdate(
        flag_type=FeatureFlagType.ENVIRONMENT,
        value={"environments": ["dev", "staging"], "default": True},
    )
    assert update.flag_type == FeatureFlagType.ENVIRONMENT
    assert update.value["environments"] == ["dev", "staging"]
    assert update.value["default"] is True

    # Invalid update - missing required keys
    with pytest.raises(ValidationError, match="Environment flag value must contain 'environments' and 'default' keys"):
        FeatureFlagUpdate(
            flag_type=FeatureFlagType.ENVIRONMENT,
            value={"environments": ["dev"]},  # Missing 'default' key
        )

    # Invalid update - wrong type for environments
    with pytest.raises(ValidationError, match="'environments' must be a list of environment names"):
        FeatureFlagUpdate(
            flag_type=FeatureFlagType.ENVIRONMENT,
            value={"environments": "all", "default": False},  # Should be a list
        )


def test_complex_environment_flag():
    """Test creating an environment flag with complex nested structure."""
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


def test_complex_time_based_flag():
    """Test creating a time-based flag with complex structure."""
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
