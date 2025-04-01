"""
Feature flag schemas for the API.

This module provides Pydantic schemas for feature flag validation and serialization
across API boundaries. It includes schemas for creating, updating, and retrieving
feature flags, with appropriate validation for different flag types.

These schemas are part of the implementation of ADR-024: Feature Flag System.
"""

from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional, Union, Literal

from pydantic import Field, field_validator

from src.schemas.base_schema import BaseSchemaValidator


class FeatureFlagType(str, Enum):
    """Valid feature flag types."""
    
    BOOLEAN = "boolean"
    PERCENTAGE = "percentage" 
    USER_SEGMENT = "user_segment"
    TIME_BASED = "time_based"


class FeatureFlagBase(BaseSchemaValidator):
    """
    Base schema for feature flags with common attributes.
    
    This schema defines the core attributes shared by all feature flag schemas,
    including creation, update, and response schemas.
    """
    
    name: str = Field(
        ...,
        description="Unique identifier for the feature flag",
        pattern=r"^[A-Z][A-Z0-9_]+$",  # UPPERCASE_WITH_UNDERSCORES
        examples=["BANKING_ACCOUNT_TYPES_ENABLED", "MULTI_CURRENCY_SUPPORT_ENABLED"],
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
        if not all(c.isupper() or c.isdigit() or c == '_' for c in v):
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
    
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Additional configuration data for the flag",
        examples=[{"owner": "backend-team", "jira_ticket": "DEBT-123"}],
    )
    
    is_system: bool = Field(
        False,
        description="Whether this is a system-defined flag (protected)",
    )
    
    @field_validator("value")
    @classmethod
    def validate_value_for_type(cls, v: Any, info) -> Any:
        """Validate that the value matches the expected format for the flag type."""
        values = info.data
        flag_type = values.get("flag_type")
        
        if not flag_type:
            return v
            
        if flag_type == FeatureFlagType.BOOLEAN and not isinstance(v, bool):
            raise ValueError("Boolean flag value must be a boolean")
            
        if flag_type == FeatureFlagType.PERCENTAGE:
            if not isinstance(v, int) and not isinstance(v, float):
                raise ValueError("Percentage flag value must be a number")
            if v < 0 or v > 100:
                raise ValueError("Percentage flag value must be between 0 and 100")
                
        if flag_type == FeatureFlagType.USER_SEGMENT and not isinstance(v, list):
            raise ValueError("User segment flag value must be a list of segments")
            
        if flag_type == FeatureFlagType.TIME_BASED and not isinstance(v, dict):
            raise ValueError("Time-based flag value must be a dictionary with start/end times")
            
        return v


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
    
    metadata: Optional[Dict[str, Any]] = Field(
        None,
        description="Updated metadata for the flag",
    )
    
    flag_type: Optional[FeatureFlagType] = Field(
        None,
        description="Type of feature flag (if changing the flag type)",
    )
    
    @field_validator("value")
    @classmethod
    def validate_update_value(cls, v: Any, info) -> Any:
        """Validate updated value against flag_type if both are provided."""
        values = info.data
        flag_type = values.get("flag_type")
        
        if v is None or flag_type is None:
            return v
            
        # Reuse the same validation logic from FeatureFlagCreate
        # This is a simplified version - in a real implementation, you might
        # want to extract this to a shared function
        if flag_type == FeatureFlagType.BOOLEAN and not isinstance(v, bool):
            raise ValueError("Boolean flag value must be a boolean")
            
        if flag_type == FeatureFlagType.PERCENTAGE:
            if not isinstance(v, int) and not isinstance(v, float):
                raise ValueError("Percentage flag value must be a number")
            if v < 0 or v > 100:
                raise ValueError("Percentage flag value must be between 0 and 100")
                
        if flag_type == FeatureFlagType.USER_SEGMENT and not isinstance(v, list):
            raise ValueError("User segment flag value must be a list of segments")
            
        if flag_type == FeatureFlagType.TIME_BASED and not isinstance(v, dict):
            raise ValueError("Time-based flag value must be a dictionary with start/end times")
            
        return v


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
    
    metadata: Optional[Dict[str, Any]] = Field(
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
