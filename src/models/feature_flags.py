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

from typing import Any, Dict, Optional

from sqlalchemy import JSON, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base_model import BaseDBModel


class FeatureFlag(BaseDBModel):
    """
    Database model for feature flags.

    Feature flags control the visibility and availability of features
    across the application. Each flag has a name (identifier), type,
    value, description, optional metadata, and method requirements.

    Attributes:
        name (str): Unique identifier for the feature flag (primary key)
        flag_type (str): Type of flag (boolean, percentage, user_segment, time_based)
        value (JSON): Current value of the flag (format depends on flag_type)
        description (str): Human-readable description of the feature flag
        flag_metadata (JSON): Additional configuration data for the flag
        is_system (bool): Whether this is a system-defined flag (protected)
        requirements (JSON): Method requirements for repository, service, and API methods
                             that should be enforced by the feature flag system
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

    value: Mapped[Any] = mapped_column(
        JSON,
        nullable=False,
        doc="Current value of the flag (format depends on flag_type)",
    )

    description: Mapped[str] = mapped_column(
        String(500),
        nullable=True,
        doc="Human-readable description of the feature flag",
    )

    flag_metadata: Mapped[Optional[Dict[str, Any]]] = mapped_column(
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
    
    requirements: Mapped[Optional[Dict[str, Any]]] = mapped_column(
        JSON,
        nullable=True,
        doc="Method requirements mapping for repository, service, and API layers",
    )

    def __repr__(self) -> str:
        """String representation of the feature flag."""
        return (
            f"<FeatureFlag name={self.name} type={self.flag_type} value={self.value}>"
        )
