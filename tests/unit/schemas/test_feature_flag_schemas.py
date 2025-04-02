"""
Unit tests for feature flag schemas.

These tests verify that the feature flag schemas correctly validate input data
and enforce the constraints defined in the schema.
"""

import pytest
from datetime import datetime
from pydantic import ValidationError
from typing import Dict, Any, List

from src.schemas.feature_flags import (
    FeatureFlagType,
    FeatureFlagBase,
    FeatureFlagCreate,
    FeatureFlagUpdate,
    FeatureFlagResponse,
    FeatureFlagToggle,
    FeatureFlagContext,
)
from src.utils.datetime_utils import utc_now


class TestFeatureFlagType:
    """Tests for the FeatureFlagType enum."""

    def test_valid_flag_types(self):
        """Test that all flag types can be accessed."""
        assert FeatureFlagType.BOOLEAN == "boolean"
        assert FeatureFlagType.PERCENTAGE == "percentage"
        assert FeatureFlagType.USER_SEGMENT == "user_segment"
        assert FeatureFlagType.TIME_BASED == "time_based"

    def test_enum_from_string(self):
        """Test that string values can be converted to enum values."""
        assert FeatureFlagType("boolean") == FeatureFlagType.BOOLEAN
        assert FeatureFlagType("percentage") == FeatureFlagType.PERCENTAGE
        assert FeatureFlagType("user_segment") == FeatureFlagType.USER_SEGMENT
        assert FeatureFlagType("time_based") == FeatureFlagType.TIME_BASED

    def test_invalid_flag_type(self):
        """Test that invalid flag types raise a ValueError."""
        with pytest.raises(ValueError):
            FeatureFlagType("invalid_type")


class TestFeatureFlagBase:
    """Tests for the FeatureFlagBase schema."""

    def test_valid_feature_flag_base(self):
        """Test that valid data passes validation."""
        flag = FeatureFlagBase(
            name="TEST_FLAG",
            description="Test flag description",
        )
        assert flag.name == "TEST_FLAG"
        assert flag.description == "Test flag description"

    def test_name_format_validation(self):
        """Test that flag names must be in uppercase with underscores."""
        # Valid name
        flag = FeatureFlagBase(name="TEST_FLAG_123")
        assert flag.name == "TEST_FLAG_123"

        # Invalid name - lowercase
        with pytest.raises(ValidationError) as exc:
            FeatureFlagBase(name="test_flag")
        assert "Feature flag name must start with an uppercase letter" in str(exc.value)

        # Invalid name - special characters
        with pytest.raises(ValidationError) as exc:
            FeatureFlagBase(name="TEST-FLAG")
        assert "Feature flag name must contain only uppercase letters, numbers, and underscores" in str(exc.value)

        # Invalid name - starting with number
        with pytest.raises(ValidationError) as exc:
            FeatureFlagBase(name="1TEST_FLAG")
        assert "Feature flag name must start with an uppercase letter" in str(exc.value)

    def test_optional_description(self):
        """Test that description is optional."""
        flag = FeatureFlagBase(name="TEST_FLAG")
        assert flag.name == "TEST_FLAG"
        assert flag.description is None


class TestFeatureFlagCreate:
    """Tests for the FeatureFlagCreate schema."""

    def test_valid_boolean_flag(self):
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

    def test_valid_percentage_flag(self):
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

    def test_valid_user_segment_flag(self):
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

    def test_valid_time_based_flag(self):
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

    def test_create_with_metadata(self):
        """Test creating a flag with metadata."""
        flag = FeatureFlagCreate(
            name="TEST_BOOLEAN_FLAG",
            flag_type=FeatureFlagType.BOOLEAN,
            value=True,
            flag_metadata={"owner": "test-team", "jira_ticket": "TEST-123"},
        )
        assert flag.flag_metadata == {"owner": "test-team", "jira_ticket": "TEST-123"}

    def test_create_system_flag(self):
        """Test creating a system flag."""
        flag = FeatureFlagCreate(
            name="TEST_SYSTEM_FLAG",
            flag_type=FeatureFlagType.BOOLEAN,
            value=True,
            is_system=True,
        )
        assert flag.is_system is True

    def test_invalid_boolean_value(self):
        """Test that boolean flags must have boolean values."""
        with pytest.raises(ValidationError) as exc:
            FeatureFlagCreate(
                name="TEST_BOOLEAN_FLAG",
                flag_type=FeatureFlagType.BOOLEAN,
                value="true",  # String instead of boolean
            )
        assert "Boolean flag value must be a boolean" in str(exc.value)

    def test_invalid_percentage_value(self):
        """Test that percentage flags must have numeric values between 0 and 100."""
        # Test non-numeric value
        with pytest.raises(ValidationError) as exc:
            FeatureFlagCreate(
                name="TEST_PERCENTAGE_FLAG",
                flag_type=FeatureFlagType.PERCENTAGE,
                value="50",  # String instead of number
            )
        assert "Percentage flag value must be a number" in str(exc.value)

        # Test value out of range (negative)
        with pytest.raises(ValidationError) as exc:
            FeatureFlagCreate(
                name="TEST_PERCENTAGE_FLAG",
                flag_type=FeatureFlagType.PERCENTAGE,
                value=-10,
            )
        assert "Percentage flag value must be between 0 and 100" in str(exc.value)

        # Test value out of range (over 100)
        with pytest.raises(ValidationError) as exc:
            FeatureFlagCreate(
                name="TEST_PERCENTAGE_FLAG",
                flag_type=FeatureFlagType.PERCENTAGE,
                value=110,
            )
        assert "Percentage flag value must be between 0 and 100" in str(exc.value)

    def test_invalid_user_segment_value(self):
        """Test that user segment flags must have list values."""
        with pytest.raises(ValidationError) as exc:
            FeatureFlagCreate(
                name="TEST_USER_SEGMENT_FLAG",
                flag_type=FeatureFlagType.USER_SEGMENT,
                value="admin",  # String instead of list
            )
        assert "User segment flag value must be a list of segments" in str(exc.value)

    def test_invalid_time_based_value(self):
        """Test that time-based flags must have dictionary values."""
        with pytest.raises(ValidationError) as exc:
            FeatureFlagCreate(
                name="TEST_TIME_BASED_FLAG",
                flag_type=FeatureFlagType.TIME_BASED,
                value="2023-01-01",  # String instead of dict
            )
        assert "Time-based flag value must be a dictionary with start/end times" in str(exc.value)


class TestFeatureFlagUpdate:
    """Tests for the FeatureFlagUpdate schema."""

    def test_update_value(self):
        """Test updating a flag's value."""
        update = FeatureFlagUpdate(value=False)
        assert update.value is False

    def test_update_description(self):
        """Test updating a flag's description."""
        update = FeatureFlagUpdate(description="Updated description")
        assert update.description == "Updated description"

    def test_update_metadata(self):
        """Test updating a flag's metadata."""
        update = FeatureFlagUpdate(flag_metadata={"owner": "new-team"})
        assert update.flag_metadata == {"owner": "new-team"}

    def test_update_flag_type(self):
        """Test updating a flag's type."""
        update = FeatureFlagUpdate(flag_type=FeatureFlagType.PERCENTAGE)
        assert update.flag_type == FeatureFlagType.PERCENTAGE

    def test_update_multiple_fields(self):
        """Test updating multiple fields at once."""
        update = FeatureFlagUpdate(
            value=False,
            description="Updated description",
            flag_metadata={"owner": "new-team"},
        )
        assert update.value is False
        assert update.description == "Updated description"
        assert update.flag_metadata == {"owner": "new-team"}

    def test_empty_update(self):
        """Test that an empty update is valid."""
        update = FeatureFlagUpdate()
        assert update.value is None
        assert update.description is None
        assert update.flag_metadata is None
        assert update.flag_type is None

    def test_validate_value_for_type(self):
        """Test that update values are validated against the flag type if both are provided."""
        # Valid update
        update = FeatureFlagUpdate(flag_type=FeatureFlagType.BOOLEAN, value=True)
        assert update.flag_type == FeatureFlagType.BOOLEAN
        assert update.value is True

        # Invalid update
        with pytest.raises(ValidationError) as exc:
            FeatureFlagUpdate(flag_type=FeatureFlagType.BOOLEAN, value="not-a-boolean")
        assert "Boolean flag value must be a boolean" in str(exc.value)


class TestFeatureFlagResponse:
    """Tests for the FeatureFlagResponse schema."""

    def test_valid_response(self):
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

    def test_response_with_minimal_fields(self):
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


class TestFeatureFlagToggle:
    """Tests for the FeatureFlagToggle schema."""

    def test_valid_toggle(self):
        """Test a valid feature flag toggle."""
        toggle = FeatureFlagToggle(enabled=True)
        assert toggle.enabled is True

        toggle = FeatureFlagToggle(enabled=False)
        assert toggle.enabled is False

    def test_required_enabled_field(self):
        """Test that the enabled field is required."""
        with pytest.raises(ValidationError):
            FeatureFlagToggle()


class TestFeatureFlagContext:
    """Tests for the FeatureFlagContext schema."""

    def test_empty_context(self):
        """Test that an empty context is valid."""
        context = FeatureFlagContext()
        assert context.user_id is None
        assert context.user_groups is None
        assert context.is_admin is None
        assert context.is_beta_tester is None
        assert context.request_path is None
        assert context.client_ip is None

    def test_user_context(self):
        """Test a context with user information."""
        context = FeatureFlagContext(
            user_id="user-123",
            user_groups=["admin", "beta"],
            is_admin=True,
            is_beta_tester=True,
        )
        assert context.user_id == "user-123"
        assert context.user_groups == ["admin", "beta"]
        assert context.is_admin is True
        assert context.is_beta_tester is True

    def test_request_context(self):
        """Test a context with request information."""
        context = FeatureFlagContext(
            request_path="/api/v1/accounts",
            client_ip="192.168.1.1",
        )
        assert context.request_path == "/api/v1/accounts"
        assert context.client_ip == "192.168.1.1"

    def test_full_context(self):
        """Test a context with all information."""
        context = FeatureFlagContext(
            user_id="user-123",
            user_groups=["admin", "beta"],
            is_admin=True,
            is_beta_tester=True,
            request_path="/api/v1/accounts",
            client_ip="192.168.1.1",
        )
        assert context.user_id == "user-123"
        assert context.user_groups == ["admin", "beta"]
        assert context.is_admin is True
        assert context.is_beta_tester is True
        assert context.request_path == "/api/v1/accounts"
        assert context.client_ip == "192.168.1.1"
