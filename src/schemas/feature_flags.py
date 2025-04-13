"""
Feature flag schemas for the API.

This module provides Pydantic schemas for feature flag validation and serialization
across API boundaries. It includes schemas for creating, updating, and retrieving
feature flags, with appropriate validation for different flag types.

These schemas are part of the implementation of ADR-024: Feature Flag System.
"""

from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional

from pydantic import Field, field_validator, model_validator

from src.schemas.base_schema import BaseSchemaValidator


class FeatureFlagType(str, Enum):
    """Valid feature flag types."""

    BOOLEAN = "boolean"
    PERCENTAGE = "percentage"
    USER_SEGMENT = "user_segment"
    TIME_BASED = "time_based"
    ENVIRONMENT = "environment"


class FeatureFlagBase(BaseSchemaValidator):
    """
    Base schema for feature flags with common attributes.

    This schema defines the core attributes shared by all feature flag schemas,
    including creation, update, and response schemas.
    """

    name: str = Field(
        ...,
        description="Unique identifier for the feature flag",
        # Document pattern without automatic validation
        examples=["BANKING_ACCOUNT_TYPES_ENABLED", "MULTI_CURRENCY_SUPPORT_ENABLED"],
        json_schema_extra={"pattern": "^[A-Z][A-Z0-9_]+$"},  # For documentation only
    )

    description: Optional[str] = Field(
        None,
        description="Human-readable description of the feature flag",
        max_length=500,
        examples=["Enables new banking account types from ADR-019"],
    )

    @field_validator("name")
    @classmethod
    def validate_name_format(cls, v: str) -> str:
        """Validate feature flag name format."""
        if not v[0].isupper():
            raise ValueError("Feature flag name must start with an uppercase letter")
        if not all(c.isupper() or c.isdigit() or c == "_" for c in v):
            raise ValueError(
                "Feature flag name must contain only uppercase letters, numbers, and underscores"
            )
        return v


class FeatureFlagCreate(FeatureFlagBase):
    """
    Schema for creating a new feature flag.

    This schema extends the base schema with fields required for creating a new feature flag,
    including the flag type, initial value, and optional metadata.
    """

    flag_type: FeatureFlagType = Field(
        ...,
        description="Type of feature flag",
        examples=["boolean", "percentage", "user_segment", "time_based"],
    )

    value: Any = Field(
        ...,
        description="Value of the feature flag (format depends on flag_type)",
        examples=[True, 50, ["admin", "beta"], {"start_time": "2025-04-01T00:00:00Z"}],
    )

    flag_metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional configuration data for the flag",
        examples=[{"owner": "backend-team", "jira_ticket": "DEBT-123"}],
    )

    is_system: bool = Field(
        False,
        description="Whether this is a system-defined flag (protected)",
    )

    @model_validator(mode="after")
    def validate_value_for_type(self) -> "FeatureFlagCreate":
        """Validate that value matches the expected format for the flag type."""
        if self.flag_type is None:
            return self

        flag_type_str = (
            self.flag_type.value
            if hasattr(self.flag_type, "value")
            else str(self.flag_type)
        )

        if flag_type_str == FeatureFlagType.BOOLEAN.value:
            if not isinstance(self.value, bool):
                raise ValueError("Boolean flag value must be a boolean")

        elif flag_type_str == FeatureFlagType.PERCENTAGE.value:
            if not isinstance(self.value, (int, float)):
                raise ValueError("Percentage flag value must be a number")
            if self.value < 0 or self.value > 100:
                raise ValueError("Percentage flag value must be between 0 and 100")

        elif flag_type_str == FeatureFlagType.USER_SEGMENT.value:
            if not isinstance(self.value, list):
                raise ValueError("User segment flag value must be a list of segments")

        elif flag_type_str == FeatureFlagType.TIME_BASED.value:
            if not isinstance(self.value, dict):
                raise ValueError(
                    "Time-based flag value must be a dictionary with start/end times"
                )

        elif flag_type_str == FeatureFlagType.ENVIRONMENT.value:
            if not isinstance(self.value, dict):
                raise ValueError(
                    "Environment flag value must be a dictionary with environments and default"
                )
            if not all(key in self.value for key in ("environments", "default")):
                raise ValueError(
                    "Environment flag value must contain 'environments' and 'default' keys"
                )
            if not isinstance(self.value["environments"], list):
                raise ValueError("'environments' must be a list of environment names")

        return self


class FeatureFlagUpdate(BaseSchemaValidator):
    """
    Schema for updating an existing feature flag.

    This schema includes only the fields that can be updated for an existing feature flag.
    The flag name cannot be changed after creation.
    """

    description: Optional[str] = Field(
        None,
        description="Human-readable description of the feature flag",
        max_length=500,
    )

    value: Optional[Any] = Field(
        None,
        description="New value for the feature flag",
    )

    flag_metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Updated metadata for the flag",
    )

    flag_type: Optional[FeatureFlagType] = Field(
        None,
        description="Type of feature flag (if changing the flag type)",
    )

    @model_validator(mode="after")
    def validate_value_for_type(self) -> "FeatureFlagUpdate":
        """Validate that value matches the expected format for the flag type."""
        if self.value is None or self.flag_type is None:
            return self

        flag_type_str = (
            self.flag_type.value
            if hasattr(self.flag_type, "value")
            else str(self.flag_type)
        )

        if flag_type_str == FeatureFlagType.BOOLEAN.value:
            if not isinstance(self.value, bool):
                raise ValueError("Boolean flag value must be a boolean")

        elif flag_type_str == FeatureFlagType.PERCENTAGE.value:
            if not isinstance(self.value, (int, float)):
                raise ValueError("Percentage flag value must be a number")
            if self.value < 0 or self.value > 100:
                raise ValueError("Percentage flag value must be between 0 and 100")

        elif flag_type_str == FeatureFlagType.USER_SEGMENT.value:
            if not isinstance(self.value, list):
                raise ValueError("User segment flag value must be a list of segments")

        elif flag_type_str == FeatureFlagType.TIME_BASED.value:
            if not isinstance(self.value, dict):
                raise ValueError(
                    "Time-based flag value must be a dictionary with start/end times"
                )

        elif flag_type_str == FeatureFlagType.ENVIRONMENT.value:
            if not isinstance(self.value, dict):
                raise ValueError(
                    "Environment flag value must be a dictionary with environments and default"
                )
            if not all(key in self.value for key in ("environments", "default")):
                raise ValueError(
                    "Environment flag value must contain 'environments' and 'default' keys"
                )
            if not isinstance(self.value["environments"], list):
                raise ValueError("'environments' must be a list of environment names")

        return self


class FeatureFlagResponse(FeatureFlagBase):
    """
    Schema for feature flag API responses.

    This schema extends the base schema with all fields needed for responding to API requests,
    including the full feature flag configuration and metadata.
    """

    flag_type: FeatureFlagType = Field(
        ...,
        description="Type of feature flag",
    )

    value: Any = Field(
        ...,
        description="Current value of the feature flag",
    )

    flag_metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional configuration data for the flag",
    )

    is_system: bool = Field(
        False,
        description="Whether this is a system-defined flag (protected)",
    )

    created_at: datetime = Field(
        ...,
        description="When the feature flag was created",
    )

    updated_at: datetime = Field(
        ...,
        description="When the feature flag was last updated",
    )


class FeatureFlagToggle(BaseSchemaValidator):
    """
    Schema for toggling a boolean feature flag.

    This simplified schema is used for quickly enabling or disabling a boolean feature flag
    without needing to specify the full update payload.
    """

    enabled: bool = Field(
        ...,
        description="Whether the feature flag should be enabled",
    )


class FeatureFlagContext(BaseSchemaValidator):
    """
    Schema for feature flag context information.

    This schema defines the context that can be provided when evaluating feature flags,
    such as user information for user_segment flags or request context.
    """

    user_id: Optional[str] = Field(
        None,
        description="User ID for user-specific flag evaluation",
    )

    user_groups: Optional[List[str]] = Field(
        None,
        description="User groups/segments for segment-based flags",
    )

    is_admin: Optional[bool] = Field(
        None,
        description="Whether the user is an admin",
    )

    is_beta_tester: Optional[bool] = Field(
        None,
        description="Whether the user is a beta tester",
    )

    # Additional context fields can be added as needed
    request_path: Optional[str] = Field(
        None,
        description="Current request path for context-aware flags",
    )

    client_ip: Optional[str] = Field(
        None,
        description="Client IP address for geo-based flags",
    )


# Schemas for feature flag requirements management API


class RequirementsBase(BaseSchemaValidator):
    """
    Base schema for feature flag requirements.

    This schema defines the common structure for feature flag requirements
    across all validation layers: repository, service, and API.
    """

    flag_name: str = Field(
        ...,
        description="Name of the feature flag",
        examples=["BANKING_ACCOUNT_TYPES_ENABLED", "MULTI_CURRENCY_SUPPORT_ENABLED"],
    )

    requirements: Dict[str, Any] = Field(
        ...,
        description="Requirements mapping for repository, service, and API layers",
        examples=[
            {
                "repository": {
                    "create_typed_entity": ["bnpl", "ewa", "payment_app"],
                    "update_typed_entity": ["bnpl", "ewa", "payment_app"],
                },
                "service": {"create_account": ["bnpl", "ewa", "payment_app"]},
                "api": {"/api/v1/accounts": ["bnpl", "ewa", "payment_app"]},
            }
        ],
    )


class RequirementsResponse(RequirementsBase):
    """
    Schema for requirements API responses.

    This schema extends the base schema with response-specific fields.
    """


class RequirementsUpdate(BaseSchemaValidator):
    """
    Schema for updating feature flag requirements.

    This schema is used for updating the requirements of an existing feature flag,
    with validation to ensure a proper structure.
    """

    requirements: Dict[str, Any] = Field(
        ...,
        description="Updated requirements mapping for repository, service, and API layers",
    )

    @model_validator(mode="after")
    def validate_requirements_structure(self) -> "RequirementsUpdate":
        """Validate that requirements follows the expected structure."""
        requirements = self.requirements

        # Check top-level keys
        valid_layers = {"repository", "service", "api"}
        actual_layers = set(requirements.keys())

        if not actual_layers.issubset(valid_layers):
            invalid_layers = actual_layers - valid_layers
            raise ValueError(
                f"Invalid layers in requirements: {invalid_layers}. "
                f"Valid layers are: {valid_layers}"
            )

        # Check repository requirements
        if "repository" in requirements:
            repo_reqs = requirements["repository"]
            if not isinstance(repo_reqs, dict):
                raise ValueError(
                    "Repository requirements must be a dictionary mapping methods to account types"
                )

            for method, account_types in repo_reqs.items():
                if not isinstance(method, str):
                    raise ValueError("Repository method names must be strings")

                if not isinstance(account_types, list) and not isinstance(
                    account_types, dict
                ):
                    raise ValueError(
                        f"Account types for method '{method}' must be a list or dictionary"
                    )

                if isinstance(account_types, list):
                    if not all(isinstance(t, str) for t in account_types):
                        raise ValueError(
                            f"Account types for method '{method}' must be strings"
                        )

        # Check service requirements
        if "service" in requirements:
            service_reqs = requirements["service"]
            if not isinstance(service_reqs, dict):
                raise ValueError(
                    "Service requirements must be a dictionary mapping methods to account types"
                )

            for method, account_types in service_reqs.items():
                if not isinstance(method, str):
                    raise ValueError("Service method names must be strings")

                if not isinstance(account_types, list) and not isinstance(
                    account_types, dict
                ):
                    raise ValueError(
                        f"Account types for method '{method}' must be a list or dictionary"
                    )

                if isinstance(account_types, list):
                    if not all(isinstance(t, str) for t in account_types):
                        raise ValueError(
                            f"Account types for method '{method}' must be strings"
                        )

        # Check API requirements
        if "api" in requirements:
            api_reqs = requirements["api"]
            if not isinstance(api_reqs, dict):
                raise ValueError(
                    "API requirements must be a dictionary mapping endpoints to account types"
                )

            for endpoint, account_types in api_reqs.items():
                if not isinstance(endpoint, str):
                    raise ValueError("API endpoint paths must be strings")

                if not isinstance(account_types, list) and not isinstance(
                    account_types, dict
                ):
                    raise ValueError(
                        f"Account types for endpoint '{endpoint}' must be a list or dictionary"
                    )

                if isinstance(account_types, list):
                    if not all(isinstance(t, str) for t in account_types):
                        raise ValueError(
                            f"Account types for endpoint '{endpoint}' must be strings"
                        )

        return self


class FlagHistoryEntry(BaseSchemaValidator):
    """
    Schema for a single feature flag history entry.

    This schema represents a single change to a feature flag,
    including what was changed and when.
    """

    flag_name: str = Field(
        ...,
        description="Name of the feature flag",
    )

    timestamp: datetime = Field(
        ...,
        description="When the change occurred",
    )

    change_type: str = Field(
        ...,
        description="Type of change (create, update, delete)",
        examples=["create", "update", "delete"],
    )

    old_value: Optional[Any] = Field(
        None,
        description="Previous value (for updates)",
    )

    new_value: Optional[Any] = Field(
        None,
        description="New value (for creates and updates)",
    )


class FlagHistoryResponse(BaseSchemaValidator):
    """
    Schema for flag history API responses.

    This schema is used for returning the history of changes to a feature flag.
    """

    flag_name: str = Field(
        ...,
        description="Name of the feature flag",
    )

    history: List[FlagHistoryEntry] = Field(
        ...,
        description="List of history entries, newest first",
    )


class FlagMetricsResponse(BaseSchemaValidator):
    """
    Schema for feature flag metrics API responses.

    This schema is used for returning usage metrics for a feature flag,
    such as how many times it has been checked and in which layers.
    """

    flag_name: str = Field(
        ...,
        description="Name of the feature flag",
    )

    check_count: int = Field(
        ...,
        description="Total number of times the flag has been checked",
    )

    layers: Dict[str, int] = Field(
        ...,
        description="Check counts by layer (repository, service, api)",
        examples=[{"repository": 1250, "service": 980, "api": 430}],
    )

    last_checked: Optional[datetime] = Field(
        None,
        description="When the flag was last checked",
    )
