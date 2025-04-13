"""
Unit tests for feature flag schemas.

These tests verify that the feature flag schemas correctly validate input data
and enforce the constraints defined in the schema.
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
    FlagHistoryResponse,
    FlagMetricsResponse,
    RequirementsBase,
    RequirementsResponse,
    RequirementsUpdate,
)
from src.utils.datetime_utils import utc_now


# Tests for FeatureFlagType enum
def test_valid_flag_types():
    """Test that all flag types can be accessed."""
    assert FeatureFlagType.BOOLEAN == "boolean"
    assert FeatureFlagType.PERCENTAGE == "percentage"
    assert FeatureFlagType.USER_SEGMENT == "user_segment"
    assert FeatureFlagType.TIME_BASED == "time_based"
    assert FeatureFlagType.ENVIRONMENT == "environment"


def test_enum_from_string():
    """Test that string values can be converted to enum values."""
    assert FeatureFlagType("boolean") == FeatureFlagType.BOOLEAN
    assert FeatureFlagType("percentage") == FeatureFlagType.PERCENTAGE
    assert FeatureFlagType("user_segment") == FeatureFlagType.USER_SEGMENT
    assert FeatureFlagType("time_based") == FeatureFlagType.TIME_BASED
    assert FeatureFlagType("environment") == FeatureFlagType.ENVIRONMENT


def test_invalid_flag_type():
    """Test that invalid flag types raise a ValueError."""
    with pytest.raises(ValueError):
        FeatureFlagType("invalid_type")


# Tests for FeatureFlagBase schema
def test_valid_feature_flag_base():
    """Test that valid data passes validation."""
    flag = FeatureFlagBase(
        name="TEST_FLAG",
        description="Test flag description",
    )
    assert flag.name == "TEST_FLAG"
    assert flag.description == "Test flag description"


def test_name_format_validation():
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
    assert (
        "Feature flag name must contain only uppercase letters, numbers, and underscores"
        in str(exc.value)
    )

    # Invalid name - starting with number
    with pytest.raises(ValidationError) as exc:
        FeatureFlagBase(name="1TEST_FLAG")
    assert "Feature flag name must start with an uppercase letter" in str(exc.value)


def test_optional_description():
    """Test that description is optional."""
    flag = FeatureFlagBase(name="TEST_FLAG")
    assert flag.name == "TEST_FLAG"
    assert flag.description is None


# Tests for FeatureFlagCreate schema
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
    with pytest.raises(ValidationError) as exc:
        FeatureFlagCreate(
            name="TEST_ENVIRONMENT_FLAG",
            flag_type=FeatureFlagType.ENVIRONMENT,
            value={"environments": ["dev", "staging"]},  # Missing 'default' key
        )
    assert (
        "Environment flag value must contain 'environments' and 'default' keys"
        in str(exc.value)
    )

    with pytest.raises(ValidationError) as exc:
        FeatureFlagCreate(
            name="TEST_ENVIRONMENT_FLAG",
            flag_type=FeatureFlagType.ENVIRONMENT,
            value={"default": True},  # Missing 'environments' key
        )
    assert (
        "Environment flag value must contain 'environments' and 'default' keys"
        in str(exc.value)
    )


def test_invalid_environment_flag_wrong_type():
    """Test that environment flags must have the correct value types."""
    with pytest.raises(ValidationError) as exc:
        FeatureFlagCreate(
            name="TEST_ENVIRONMENT_FLAG",
            flag_type=FeatureFlagType.ENVIRONMENT,
            value={
                "environments": "dev,staging",  # String instead of list
                "default": False,
            },
        )
    assert "'environments' must be a list of environment names" in str(exc.value)


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


def test_invalid_boolean_value():
    """Test that boolean flags must have boolean values."""
    with pytest.raises(ValidationError) as exc:
        FeatureFlagCreate(
            name="TEST_BOOLEAN_FLAG",
            flag_type=FeatureFlagType.BOOLEAN,
            value="true",  # String instead of boolean
        )
    assert "Boolean flag value must be a boolean" in str(exc.value)


def test_invalid_percentage_value():
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


def test_invalid_user_segment_value():
    """Test that user segment flags must have list values."""
    with pytest.raises(ValidationError) as exc:
        FeatureFlagCreate(
            name="TEST_USER_SEGMENT_FLAG",
            flag_type=FeatureFlagType.USER_SEGMENT,
            value="admin",  # String instead of list
        )
    assert "User segment flag value must be a list of segments" in str(exc.value)


def test_invalid_time_based_value():
    """Test that time-based flags must have dictionary values."""
    with pytest.raises(ValidationError) as exc:
        FeatureFlagCreate(
            name="TEST_TIME_BASED_FLAG",
            flag_type=FeatureFlagType.TIME_BASED,
            value="2023-01-01",  # String instead of dict
        )
    assert "Time-based flag value must be a dictionary with start/end times" in str(
        exc.value
    )


# Tests for FeatureFlagUpdate schema
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


def test_validate_value_for_type():
    """Test that update values are validated against the flag type if both are provided."""
    # Valid update
    update = FeatureFlagUpdate(flag_type=FeatureFlagType.BOOLEAN, value=True)
    assert update.flag_type == FeatureFlagType.BOOLEAN
    assert update.value is True

    # Invalid update
    with pytest.raises(ValidationError) as exc:
        FeatureFlagUpdate(flag_type=FeatureFlagType.BOOLEAN, value="not-a-boolean")
    assert "Boolean flag value must be a boolean" in str(exc.value)


def test_update_environment_flag():
    """Test updating an environment flag."""
    update = FeatureFlagUpdate(
        flag_type=FeatureFlagType.ENVIRONMENT,
        value={"environments": ["dev", "staging"], "default": True},
    )
    assert update.flag_type == FeatureFlagType.ENVIRONMENT
    assert update.value["environments"] == ["dev", "staging"]
    assert update.value["default"] is True

    # Invalid update - missing required keys
    with pytest.raises(ValidationError) as exc:
        FeatureFlagUpdate(
            flag_type=FeatureFlagType.ENVIRONMENT,
            value={"environments": ["dev"]},  # Missing 'default' key
        )
    assert (
        "Environment flag value must contain 'environments' and 'default' keys"
        in str(exc.value)
    )

    # Invalid update - wrong type for environments
    with pytest.raises(ValidationError) as exc:
        FeatureFlagUpdate(
            flag_type=FeatureFlagType.ENVIRONMENT,
            value={"environments": "all", "default": False},  # Should be a list
        )
    assert "'environments' must be a list of environment names" in str(exc.value)


# Tests for FeatureFlagResponse schema
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


# Tests for FeatureFlagToggle schema
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


# Tests for FeatureFlagContext schema
def test_empty_context():
    """Test that an empty context is valid."""
    context = FeatureFlagContext()
    assert context.user_id is None
    assert context.user_groups is None
    assert context.is_admin is None
    assert context.is_beta_tester is None
    assert context.request_path is None
    assert context.client_ip is None


def test_user_context():
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


def test_request_context():
    """Test a context with request information."""
    context = FeatureFlagContext(
        request_path="/api/v1/accounts",
        client_ip="192.168.1.1",
    )
    assert context.request_path == "/api/v1/accounts"
    assert context.client_ip == "192.168.1.1"


def test_full_context():
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


# Tests for feature flag requirements schemas
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
    with pytest.raises(ValidationError) as exc:
        RequirementsUpdate(
            requirements={
                "invalid_layer": {  # Not a valid layer
                    "method": ["bnpl"],
                },
            },
        )
    assert "Invalid layers in requirements" in str(exc.value)


def test_requirements_update_invalid_repository_format():
    """Test the requirements update schema with invalid repository format."""
    with pytest.raises(ValidationError) as exc:
        RequirementsUpdate(
            requirements={
                "repository": "not_a_dict",  # Should be a dict
            },
        )
    assert "Repository requirements must be a dictionary" in str(exc.value)


def test_requirements_update_invalid_method_name():
    """Test the requirements update schema with an invalid method name."""
    with pytest.raises(ValidationError) as exc:
        RequirementsUpdate(
            requirements={
                "repository": {
                    123: ["bnpl"],  # Method name should be a string
                },
            },
        )
    assert "Repository method names must be strings" in str(exc.value)


def test_requirements_update_invalid_account_types():
    """Test the requirements update schema with invalid account types."""
    with pytest.raises(ValidationError) as exc:
        RequirementsUpdate(
            requirements={
                "repository": {
                    "create_typed_entity": "bnpl",  # Should be a list or dict
                },
            },
        )
    assert (
        "Account types for method 'create_typed_entity' must be a list or dictionary"
        in str(exc.value)
    )


def test_requirements_update_non_string_account_types():
    """Test the requirements update schema with non-string account types."""
    with pytest.raises(ValidationError) as exc:
        RequirementsUpdate(
            requirements={
                "repository": {
                    "create_typed_entity": [123, "ewa"],  # All should be strings
                },
            },
        )
    assert "Account types for method 'create_typed_entity' must be strings" in str(
        exc.value
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
    with pytest.raises(ValidationError) as exc:
        RequirementsUpdate(
            requirements={
                "service": {
                    "create_account": 123,  # Should be a list or dict
                },
            },
        )
    assert (
        "Account types for method 'create_account' must be a list or dictionary"
        in str(exc.value)
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
    with pytest.raises(ValidationError) as exc:
        RequirementsUpdate(
            requirements={
                "api": {
                    123: ["bnpl"],  # Endpoint should be a string
                },
            },
        )
    assert "API endpoint paths must be strings" in str(exc.value)

    # Invalid account types format
    with pytest.raises(ValidationError) as exc:
        RequirementsUpdate(
            requirements={
                "api": {
                    "/api/v1/accounts": "all",  # Should be a list or dict
                },
            },
        )
    assert (
        "Account types for endpoint '/api/v1/accounts' must be a list or dictionary"
        in str(exc.value)
    )


# Tests for flag history schemas
def test_flag_history_entry_schema():
    """Test the flag history entry schema."""
    now = utc_now()
    entry = FlagHistoryEntry(
        flag_name="TEST_FLAG",
        timestamp=now,
        change_type="update",
        old_value=False,
        new_value=True,
    )
    assert entry.flag_name == "TEST_FLAG"
    assert entry.timestamp == now
    assert entry.change_type == "update"
    assert entry.old_value is False
    assert entry.new_value is True


def test_flag_history_entry_create():
    """Test a history entry for flag creation."""
    now = utc_now()
    entry = FlagHistoryEntry(
        flag_name="TEST_FLAG",
        timestamp=now,
        change_type="create",
        new_value=True,
    )
    assert entry.flag_name == "TEST_FLAG"
    assert entry.timestamp == now
    assert entry.change_type == "create"
    assert entry.old_value is None
    assert entry.new_value is True


def test_flag_history_entry_delete():
    """Test a history entry for flag deletion."""
    now = utc_now()
    entry = FlagHistoryEntry(
        flag_name="TEST_FLAG",
        timestamp=now,
        change_type="delete",
        old_value=True,
    )
    assert entry.flag_name == "TEST_FLAG"
    assert entry.timestamp == now
    assert entry.change_type == "delete"
    assert entry.old_value is True
    assert entry.new_value is None


def test_flag_history_response_schema():
    """Test the flag history response schema."""
    now = utc_now()
    entry1 = FlagHistoryEntry(
        flag_name="TEST_FLAG",
        timestamp=now,
        change_type="create",
        new_value=False,
    )
    entry2 = FlagHistoryEntry(
        flag_name="TEST_FLAG",
        timestamp=now,
        change_type="update",
        old_value=False,
        new_value=True,
    )

    response = FlagHistoryResponse(
        flag_name="TEST_FLAG",
        history=[entry1, entry2],
    )
    assert response.flag_name == "TEST_FLAG"
    assert len(response.history) == 2
    assert response.history[0].change_type == "create"
    assert response.history[1].change_type == "update"


# Tests for flag metrics schema
def test_flag_metrics_response_schema():
    """Test the flag metrics response schema."""
    now = utc_now()
    metrics = FlagMetricsResponse(
        flag_name="TEST_FLAG",
        check_count=2500,
        layers={
            "repository": 1250,
            "service": 980,
            "api": 270,
        },
        last_checked=now,
    )
    assert metrics.flag_name == "TEST_FLAG"
    assert metrics.check_count == 2500
    assert metrics.layers["repository"] == 1250
    assert metrics.layers["service"] == 980
    assert metrics.layers["api"] == 270
    assert metrics.last_checked == now


def test_flag_metrics_without_last_checked():
    """Test flag metrics response without last_checked."""
    metrics = FlagMetricsResponse(
        flag_name="TEST_FLAG",
        check_count=0,
        layers={
            "repository": 0,
            "service": 0,
            "api": 0,
        },
    )
    assert metrics.flag_name == "TEST_FLAG"
    assert metrics.check_count == 0
    assert metrics.last_checked is None


def test_flag_metrics_with_missing_layer():
    """Test flag metrics response with a missing layer."""
    metrics = FlagMetricsResponse(
        flag_name="TEST_FLAG",
        check_count=1000,
        layers={
            "repository": 500,
            "api": 500,
            # 'service' layer is missing
        },
    )
    assert metrics.flag_name == "TEST_FLAG"
    assert metrics.check_count == 1000
    assert "repository" in metrics.layers
    assert "api" in metrics.layers
    assert "service" not in metrics.layers
