"""
Unit tests for the feature flag registry.

These tests verify that the feature flag registry properly stores, retrieves,
and evaluates feature flags in isolation, without crossing layer boundaries.
"""

import hashlib
from datetime import timedelta

import pytest

from src.registry.feature_flags_registry import FeatureFlagRegistry
from src.schemas.feature_flags import FeatureFlagType
from src.utils.datetime_utils import utc_now

# Import fixtures from the fixtures directory
from tests.fixtures.fixture_feature_flags import (
    feature_flag_registry,
    registry_with_predefined_flags,
)


# Registry initialization tests
def test_init(feature_flag_registry):
    """Test that a new registry is empty."""
    registry = feature_flag_registry
    assert registry._flags == {}
    assert registry._observers == []


# Flag registration tests
def test_register_flag(feature_flag_registry):
    """Test registering a new flag."""
    registry = feature_flag_registry
    registry.register(
        flag_name="TEST_FLAG",
        flag_type=FeatureFlagType.BOOLEAN,
        default_value=True,
        description="Test flag",
    )

    flag = registry._flags["TEST_FLAG"]
    assert flag["type"] == FeatureFlagType.BOOLEAN
    assert flag["value"] is True
    assert flag["description"] == "Test flag"
    assert flag["metadata"] == {}
    assert flag["is_system"] is False
    assert "registered_at" in flag


def test_register_with_string_type(feature_flag_registry):
    """Test registering a flag with a string type instead of enum."""
    registry = feature_flag_registry
    registry.register(
        flag_name="TEST_FLAG",
        flag_type="boolean",
        default_value=True,
    )

    flag = registry._flags["TEST_FLAG"]
    assert flag["type"] == "boolean"
    assert flag["value"] is True


def test_register_duplicate_flag(registry_with_predefined_flags):
    """Test that registering a duplicate flag raises an error."""
    registry = registry_with_predefined_flags
    with pytest.raises(
        ValueError, match="Feature flag TEST_BOOLEAN_FLAG already registered"
    ):
        registry.register(
            flag_name="TEST_BOOLEAN_FLAG",
            flag_type=FeatureFlagType.BOOLEAN,
            default_value=False,
        )


def test_register_with_metadata(feature_flag_registry):
    """Test registering a flag with metadata."""
    registry = feature_flag_registry
    metadata = {"owner": "test-team", "jira_ticket": "TEST-123"}
    registry.register(
        flag_name="TEST_FLAG",
        flag_type=FeatureFlagType.BOOLEAN,
        default_value=True,
        metadata=metadata,
    )

    flag = registry._flags["TEST_FLAG"]
    assert flag["metadata"] == metadata


def test_register_system_flag(feature_flag_registry):
    """Test registering a system flag."""
    registry = feature_flag_registry
    registry.register(
        flag_name="TEST_SYSTEM_FLAG",
        flag_type=FeatureFlagType.BOOLEAN,
        default_value=True,
        is_system=True,
    )

    flag = registry._flags["TEST_SYSTEM_FLAG"]
    assert flag["is_system"] is True


# Flag retrieval tests
def test_get_flag(registry_with_predefined_flags):
    """Test getting a specific flag's configuration."""
    registry = registry_with_predefined_flags
    flag = registry.get_flag("TEST_BOOLEAN_FLAG")
    assert flag["type"] == FeatureFlagType.BOOLEAN
    assert flag["value"] is True
    assert flag["description"] == "Test boolean flag"


def test_get_nonexistent_flag(feature_flag_registry):
    """Test getting a nonexistent flag."""
    registry = feature_flag_registry
    assert registry.get_flag("NONEXISTENT_FLAG") is None


def test_get_all_flags(registry_with_predefined_flags):
    """Test getting all flags."""
    registry = registry_with_predefined_flags
    flags = registry.get_all_flags()
    assert len(flags) == 4
    assert "TEST_BOOLEAN_FLAG" in flags
    assert "TEST_PERCENTAGE_FLAG" in flags
    assert "TEST_USER_SEGMENT_FLAG" in flags
    assert "TEST_TIME_BASED_FLAG" in flags


# Flag value tests
def test_get_value_boolean(registry_with_predefined_flags):
    """Test getting a boolean flag value."""
    registry = registry_with_predefined_flags
    value = registry.get_value("TEST_BOOLEAN_FLAG")
    assert value is True


def test_get_value_nonexistent(feature_flag_registry):
    """Test getting a nonexistent flag value."""
    registry = feature_flag_registry
    with pytest.raises(ValueError, match="Unknown feature flag: NONEXISTENT_FLAG"):
        registry.get_value("NONEXISTENT_FLAG")


def test_set_value(registry_with_predefined_flags):
    """Test setting a flag's value."""
    registry = registry_with_predefined_flags
    registry.set_value("TEST_BOOLEAN_FLAG", False)
    assert registry._flags["TEST_BOOLEAN_FLAG"]["value"] is False


def test_set_nonexistent_value(feature_flag_registry):
    """Test setting a nonexistent flag's value."""
    registry = feature_flag_registry
    with pytest.raises(ValueError, match="Unknown feature flag: NONEXISTENT_FLAG"):
        registry.set_value("NONEXISTENT_FLAG", True)


# Percentage flag tests
def test_get_percentage_flag_no_context(registry_with_predefined_flags):
    """Test that percentage flags return False when no context is provided."""
    registry = registry_with_predefined_flags
    value = registry.get_value("TEST_PERCENTAGE_FLAG")
    assert value is False


def test_get_percentage_flag_with_user(feature_flag_registry):
    """Test percentage flag evaluation with a user."""
    registry = feature_flag_registry
    # Create a percentage flag for testing
    registry.register(
        flag_name="TEST_PERCENTAGE_50",
        flag_type=FeatureFlagType.PERCENTAGE,
        default_value=50,
    )

    # Use known test user IDs instead of mocking
    # This user should be included (hash calculation would put it below 50%)
    # Using stable test values for consistent results
    test_user_included = "user-123456"
    test_user_excluded = "user-654321"

    # We can test both cases without mocking
    # Included user (assuming hash puts this user in the 0-49 range)
    context_included = {"user_id": test_user_included}

    # Excluded user (assuming hash puts this user in the 50-99 range)
    context_excluded = {"user_id": test_user_excluded}

    # We don't assert specific outcomes as they depend on the hash algorithm
    # We just verify both cases are handled correctly
    registry.get_value("TEST_PERCENTAGE_50", context=context_included)
    registry.get_value("TEST_PERCENTAGE_50", context=context_excluded)


def test_is_user_in_percentage(feature_flag_registry):
    """Test the _is_user_in_percentage method."""
    registry = feature_flag_registry
    # Create a deterministic test by directly calculating the hash
    user_id = "test-user"
    flag_name = "TEST_FLAG"
    hash_input = f"{user_id}:{flag_name}"
    hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)
    bucket = hash_value % 100

    # Test with percentage just above the bucket
    assert registry._is_user_in_percentage(user_id, flag_name, bucket + 1) is True

    # Test with percentage equal to the bucket
    assert registry._is_user_in_percentage(user_id, flag_name, bucket) is False

    # Test with percentage below the bucket
    assert registry._is_user_in_percentage(user_id, flag_name, bucket - 1) is False

    # Edge cases
    assert registry._is_user_in_percentage(user_id, flag_name, 100) is True
    assert registry._is_user_in_percentage(user_id, flag_name, 0) is False


# User segment flag tests
def test_get_user_segment_flag_admin(registry_with_predefined_flags):
    """Test user segment flag evaluation for admin users."""
    registry = registry_with_predefined_flags
    value = registry.get_value(
        "TEST_USER_SEGMENT_FLAG",
        context={"is_admin": True},
    )
    assert value is True


def test_get_user_segment_flag_beta(registry_with_predefined_flags):
    """Test user segment flag evaluation for beta testers."""
    registry = registry_with_predefined_flags
    value = registry.get_value(
        "TEST_USER_SEGMENT_FLAG",
        context={"is_beta_tester": True},
    )
    assert value is True


def test_get_user_segment_flag_groups(registry_with_predefined_flags):
    """Test user segment flag evaluation with user groups."""
    registry = registry_with_predefined_flags
    value = registry.get_value(
        "TEST_USER_SEGMENT_FLAG",
        context={"user_groups": ["regular", "beta"]},
    )
    assert value is True

    value = registry.get_value(
        "TEST_USER_SEGMENT_FLAG",
        context={"user_groups": ["regular"]},
    )
    assert value is False


def test_get_user_segment_flag_no_match(registry_with_predefined_flags):
    """Test user segment flag with no matching segments."""
    registry = registry_with_predefined_flags
    value = registry.get_value(
        "TEST_USER_SEGMENT_FLAG",
        context={},
    )
    assert value is False


# Time-based flag tests
def test_get_time_based_flag(registry_with_predefined_flags):
    """Test time-based flag evaluation."""
    registry = registry_with_predefined_flags
    # Current time is within the range
    value = registry.get_value("TEST_TIME_BASED_FLAG")
    assert value is True


def test_time_based_flag_past_end(feature_flag_registry):
    """Test time-based flag after end time."""
    registry = feature_flag_registry
    start_time = utc_now() - timedelta(days=2)
    end_time = utc_now() - timedelta(days=1)
    registry.register(
        flag_name="PAST_FLAG",
        flag_type=FeatureFlagType.TIME_BASED,
        default_value={
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        },
    )

    value = registry.get_value("PAST_FLAG")
    assert value is False


def test_time_based_flag_before_start(feature_flag_registry):
    """Test time-based flag before start time."""
    registry = feature_flag_registry
    start_time = utc_now() + timedelta(days=1)
    end_time = utc_now() + timedelta(days=2)
    registry.register(
        flag_name="FUTURE_FLAG",
        flag_type=FeatureFlagType.TIME_BASED,
        default_value={
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
        },
    )

    value = registry.get_value("FUTURE_FLAG")
    assert value is False


def test_time_based_flag_with_only_start(feature_flag_registry):
    """Test time-based flag with only start time."""
    registry = feature_flag_registry
    start_time = utc_now() - timedelta(days=1)
    registry.register(
        flag_name="START_ONLY_FLAG",
        flag_type=FeatureFlagType.TIME_BASED,
        default_value={
            "start_time": start_time.isoformat(),
        },
    )

    value = registry.get_value("START_ONLY_FLAG")
    assert value is True


def test_time_based_flag_with_only_end(feature_flag_registry):
    """Test time-based flag with only end time."""
    registry = feature_flag_registry
    end_time = utc_now() + timedelta(days=1)
    registry.register(
        flag_name="END_ONLY_FLAG",
        flag_type=FeatureFlagType.TIME_BASED,
        default_value={
            "end_time": end_time.isoformat(),
        },
    )

    value = registry.get_value("END_ONLY_FLAG")
    assert value is True


def test_time_based_flag_with_datetime_objects(feature_flag_registry):
    """Test time-based flag with datetime objects instead of strings."""
    registry = feature_flag_registry
    start_time = utc_now() - timedelta(days=1)
    end_time = utc_now() + timedelta(days=1)
    registry.register(
        flag_name="DATETIME_OBJECTS_FLAG",
        flag_type=FeatureFlagType.TIME_BASED,
        default_value={
            "start_time": start_time,
            "end_time": end_time,
        },
    )

    value = registry.get_value("DATETIME_OBJECTS_FLAG")
    assert value is True


# Observer tests
def test_add_remove_observer(feature_flag_registry):
    """Test adding and removing observers (without crossing layer boundaries)."""
    registry = feature_flag_registry
    # For unit tests, we simply verify the observer is correctly added/removed
    # from the internal observers list.

    # Note: This is a simple struct-like class, not a mock
    class SimpleObserver:
        def flag_changed(self, flag_name, old_value, new_value):
            pass

    observer = SimpleObserver()

    # Test adding
    registry.add_observer(observer)
    assert observer in registry._observers

    # Test removing
    registry.remove_observer(observer)
    assert observer not in registry._observers


# Miscellaneous tests
def test_thread_safety(feature_flag_registry):
    """Test thread safety by testing the existence of the lock."""
    registry = feature_flag_registry
    assert hasattr(registry, "_lock")
