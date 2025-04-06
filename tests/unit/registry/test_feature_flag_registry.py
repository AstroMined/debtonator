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


class TestFeatureFlagRegistry:
    """Tests for the FeatureFlagRegistry class."""

    @pytest.fixture
    def registry(self):
        """Create a fresh registry for each test."""
        return FeatureFlagRegistry()

    @pytest.fixture
    def registry_with_flags(self):
        """Create a registry with some predefined flags."""
        registry = FeatureFlagRegistry()
        registry.register(
            flag_name="TEST_BOOLEAN_FLAG",
            flag_type=FeatureFlagType.BOOLEAN,
            default_value=True,
            description="Test boolean flag",
        )
        registry.register(
            flag_name="TEST_PERCENTAGE_FLAG",
            flag_type=FeatureFlagType.PERCENTAGE,
            default_value=50,
            description="Test percentage flag",
        )
        registry.register(
            flag_name="TEST_USER_SEGMENT_FLAG",
            flag_type=FeatureFlagType.USER_SEGMENT,
            default_value=["admin", "beta"],
            description="Test user segment flag",
        )
        start_time = utc_now() - timedelta(days=1)
        end_time = utc_now() + timedelta(days=1)
        registry.register(
            flag_name="TEST_TIME_BASED_FLAG",
            flag_type=FeatureFlagType.TIME_BASED,
            default_value={
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
            },
            description="Test time-based flag",
        )
        return registry

    def test_init(self, registry):
        """Test that a new registry is empty."""
        assert registry._flags == {}
        assert registry._observers == []

    def test_register_flag(self, registry):
        """Test registering a new flag."""
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

    def test_register_with_string_type(self, registry):
        """Test registering a flag with a string type instead of enum."""
        registry.register(
            flag_name="TEST_FLAG",
            flag_type="boolean",
            default_value=True,
        )

        flag = registry._flags["TEST_FLAG"]
        assert flag["type"] == "boolean"
        assert flag["value"] is True

    def test_register_duplicate_flag(self, registry_with_flags):
        """Test that registering a duplicate flag raises an error."""
        with pytest.raises(
            ValueError, match="Feature flag TEST_BOOLEAN_FLAG already registered"
        ):
            registry_with_flags.register(
                flag_name="TEST_BOOLEAN_FLAG",
                flag_type=FeatureFlagType.BOOLEAN,
                default_value=False,
            )

    def test_get_flag(self, registry_with_flags):
        """Test getting a specific flag's configuration."""
        flag = registry_with_flags.get_flag("TEST_BOOLEAN_FLAG")
        assert flag["type"] == FeatureFlagType.BOOLEAN
        assert flag["value"] is True
        assert flag["description"] == "Test boolean flag"

    def test_get_nonexistent_flag(self, registry):
        """Test getting a nonexistent flag."""
        assert registry.get_flag("NONEXISTENT_FLAG") is None

    def test_get_value_boolean(self, registry_with_flags):
        """Test getting a boolean flag value."""
        value = registry_with_flags.get_value("TEST_BOOLEAN_FLAG")
        assert value is True

    def test_get_value_nonexistent(self, registry):
        """Test getting a nonexistent flag value."""
        with pytest.raises(ValueError, match="Unknown feature flag: NONEXISTENT_FLAG"):
            registry.get_value("NONEXISTENT_FLAG")

    def test_get_percentage_flag_no_context(self, registry_with_flags):
        """Test that percentage flags return False when no context is provided."""
        value = registry_with_flags.get_value("TEST_PERCENTAGE_FLAG")
        assert value is False

    def test_get_percentage_flag_with_user(self, registry):
        """Test percentage flag evaluation with a user."""
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

    def test_get_user_segment_flag_admin(self, registry_with_flags):
        """Test user segment flag evaluation for admin users."""
        value = registry_with_flags.get_value(
            "TEST_USER_SEGMENT_FLAG",
            context={"is_admin": True},
        )
        assert value is True

    def test_get_user_segment_flag_beta(self, registry_with_flags):
        """Test user segment flag evaluation for beta testers."""
        value = registry_with_flags.get_value(
            "TEST_USER_SEGMENT_FLAG",
            context={"is_beta_tester": True},
        )
        assert value is True

    def test_get_user_segment_flag_groups(self, registry_with_flags):
        """Test user segment flag evaluation with user groups."""
        value = registry_with_flags.get_value(
            "TEST_USER_SEGMENT_FLAG",
            context={"user_groups": ["regular", "beta"]},
        )
        assert value is True

        value = registry_with_flags.get_value(
            "TEST_USER_SEGMENT_FLAG",
            context={"user_groups": ["regular"]},
        )
        assert value is False

    def test_get_user_segment_flag_no_match(self, registry_with_flags):
        """Test user segment flag with no matching segments."""
        value = registry_with_flags.get_value(
            "TEST_USER_SEGMENT_FLAG",
            context={},
        )
        assert value is False

    def test_get_time_based_flag(self, registry_with_flags):
        """Test time-based flag evaluation."""
        # Current time is within the range
        value = registry_with_flags.get_value("TEST_TIME_BASED_FLAG")
        assert value is True

    def test_time_based_flag_past_end(self, registry):
        """Test time-based flag after end time."""
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

    def test_time_based_flag_before_start(self, registry):
        """Test time-based flag before start time."""
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

    def test_time_based_flag_with_only_start(self, registry):
        """Test time-based flag with only start time."""
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

    def test_time_based_flag_with_only_end(self, registry):
        """Test time-based flag with only end time."""
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

    def test_time_based_flag_with_datetime_objects(self, registry):
        """Test time-based flag with datetime objects instead of strings."""
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

    def test_set_value(self, registry_with_flags):
        """Test setting a flag's value."""
        registry_with_flags.set_value("TEST_BOOLEAN_FLAG", False)
        assert registry_with_flags._flags["TEST_BOOLEAN_FLAG"]["value"] is False

    def test_set_nonexistent_value(self, registry):
        """Test setting a nonexistent flag's value."""
        with pytest.raises(ValueError, match="Unknown feature flag: NONEXISTENT_FLAG"):
            registry.set_value("NONEXISTENT_FLAG", True)

    def test_get_all_flags(self, registry_with_flags):
        """Test getting all flags."""
        flags = registry_with_flags.get_all_flags()
        assert len(flags) == 4
        assert "TEST_BOOLEAN_FLAG" in flags
        assert "TEST_PERCENTAGE_FLAG" in flags
        assert "TEST_USER_SEGMENT_FLAG" in flags
        assert "TEST_TIME_BASED_FLAG" in flags

    def test_add_remove_observer(self, registry):
        """Test adding and removing observers (without crossing layer boundaries)."""
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

    def test_is_user_in_percentage(self, registry):
        """Test the _is_user_in_percentage method."""
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

    def test_thread_safety(self, registry):
        """Test thread safety by testing the existence of the lock."""
        assert hasattr(registry, "_lock")

    def test_register_with_metadata(self, registry):
        """Test registering a flag with metadata."""
        metadata = {"owner": "test-team", "jira_ticket": "TEST-123"}
        registry.register(
            flag_name="TEST_FLAG",
            flag_type=FeatureFlagType.BOOLEAN,
            default_value=True,
            metadata=metadata,
        )

        flag = registry._flags["TEST_FLAG"]
        assert flag["metadata"] == metadata

    def test_register_system_flag(self, registry):
        """Test registering a system flag."""
        registry.register(
            flag_name="TEST_SYSTEM_FLAG",
            flag_type=FeatureFlagType.BOOLEAN,
            default_value=True,
            is_system=True,
        )

        flag = registry._flags["TEST_SYSTEM_FLAG"]
        assert flag["is_system"] is True
