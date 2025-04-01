"""
Feature flag model for controlling feature availability.

This module defines the database model for feature flags that will be used
to enable or disable functionality across the application. This is part of the
implementation of ADR-024: Feature Flag System.

Feature flags allow for:
- Controlled rollout of new features
- A/B testing and experimentation
- Quick disabling of problematic features
- Environment-specific feature availability
"""

from datetime import datetime
from typing import Dict, Any, Optional

from sqlalchemy import Column, String, JSON, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base_model import BaseDBModel
from src.utils.datetime_utils import naive_utc_now


class FeatureFlag(BaseDBModel):
    """
    Database model for feature flags.
    
    Feature flags control the visibility and availability of features
    across the application. Each flag has a name (identifier), type,
    value, description, and optional metadata.
    
    Attributes:
        name (str): Unique identifier for the feature flag (primary key)
        flag_type (str): Type of flag (boolean, percentage, user_segment, time_based)
        value (JSON): Current value of the flag (format depends on flag_type)
        description (str): Human-readable description of the feature flag
        metadata (JSON): Additional configuration data for the flag
        is_system (bool): Whether this is a system-defined flag (protected)
    """

    __tablename__ = "feature_flags"

    # Use name as the primary key (instead of id)
    name: Mapped[str] = mapped_column(
        String(255),
        primary_key=True,
        nullable=False,
        index=True,
        doc="Unique identifier for the feature flag",
    )
    
    flag_type: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        doc="Type of flag (boolean, percentage, user_segment, time_based)",
    )
    
    value: Mapped[Dict[str, Any]] = mapped_column(
        JSON,
        nullable=False,
        doc="Current value of the flag (format depends on flag_type)",
    )
    
    description: Mapped[str] = mapped_column(
        String(500),
        nullable=True,
        doc="Human-readable description of the feature flag",
    )
    
    metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        doc="Additional configuration data for the flag",
    )
    
    is_system: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        doc="Whether this is a system-defined flag (protected)",
    )
    
    def __repr__(self) -> str:
        """String representation of the feature flag."""
        return f"<FeatureFlag name={self.name} type={self.flag_type} value={self.value}>"
