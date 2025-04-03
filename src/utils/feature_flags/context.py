"""
Context utilities for feature flag evaluation.

This module provides utilities for building context information used in
feature flag evaluation. Since the application is single-tenant without
user authentication, we use environment-based contexts instead of user contexts.
"""

import hashlib
import os
import platform
import sys
from enum import Enum
from typing import Any, Dict, Optional

from pydantic import BaseModel


class Environment(str, Enum):
    """Supported application environments."""

    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    TEST = "test"


class EnvironmentContext(BaseModel):
    """
    Environment-based context for feature flag evaluation.

    This context provides information about the environment and request
    that can be used for feature flag evaluation in a single-tenant system.
    """

    environment: Environment
    hostname: str
    application_version: Optional[str] = None
    request_id: Optional[str] = None
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Dict[str, Any] = {}

    @property
    def is_development(self) -> bool:
        """Check if current environment is development."""
        return self.environment == Environment.DEVELOPMENT

    @property
    def is_staging(self) -> bool:
        """Check if current environment is staging."""
        return self.environment == Environment.STAGING

    @property
    def is_production(self) -> bool:
        """Check if current environment is production."""
        return self.environment == Environment.PRODUCTION

    @property
    def is_test(self) -> bool:
        """Check if current environment is test."""
        return self.environment == Environment.TEST


def detect_environment() -> Environment:
    """
    Detect the current environment based on environment variables.

    Uses the application settings and falls back to environment variables.
    Priority order:
    1. Explicit APP_ENV environment variable
    2. Settings from configuration
    3. Detection based on runtime context

    Returns:
        Environment: The detected environment (development, staging, production, or test)
    """
    # Check for pytest environment first for test detection
    # This ensures tests that don't set APP_ENV still get the TEST environment
    if "pytest" in sys.modules:
        # Only return TEST if not explicitly overridden by env vars
        if "APP_ENV" not in os.environ:
            return Environment.TEST

    # Check explicit environment variable
    # This takes highest priority to allow tests to override environment
    env_var = os.environ.get("APP_ENV")
    if env_var:
        env_var = env_var.lower()
        # Map environment variable to Environment enum
        if env_var in ("production", "prod"):
            return Environment.PRODUCTION
        elif env_var in ("staging", "stage"):
            return Environment.STAGING
        elif env_var == "test":
            return Environment.TEST
        elif env_var == "development":
            return Environment.DEVELOPMENT

    # Then try to get environment from settings
    from src.utils.config import settings

    env_name = getattr(settings, "APP_ENV", None)
    if env_name:
        env_name = env_name.lower()
        # Map setting to Environment enum
        if env_name in ("production", "prod"):
            return Environment.PRODUCTION
        elif env_name in ("staging", "stage"):
            return Environment.STAGING
        elif env_name == "test":
            return Environment.TEST
        elif env_name == "development":
            return Environment.DEVELOPMENT

    # Default to development if nothing else matched
    return Environment.DEVELOPMENT


def generate_hash_id(input_str: str) -> str:
    """
    Generate a deterministic hash ID from an input string.

    This is used for percentage-based rollouts to ensure consistent
    behavior for the same input (e.g., hostname).

    Args:
        input_str: The input string to hash

    Returns:
        str: A hexadecimal hash string
    """
    return hashlib.md5(input_str.encode()).hexdigest()


def is_feature_enabled_for_percentage(percentage: float, identifier: str) -> bool:
    """
    Determine if a feature should be enabled based on percentage rollout.

    Args:
        percentage: A value between 0 and 100 representing the rollout percentage
        identifier: A string identifier to hash for consistent behavior

    Returns:
        bool: True if the feature should be enabled, False otherwise
    """
    if percentage >= 100:
        return True
    if percentage <= 0:
        return False

    # Generate a hash and convert first 8 chars to integer
    hash_value = int(generate_hash_id(identifier)[:8], 16)

    # Normalize to a value between 0 and 100
    normalized_value = hash_value % 100

    # Enable if the normalized value is less than the rollout percentage
    return normalized_value < percentage


def create_environment_context(
    request_id: Optional[str] = None,
    ip_address: Optional[str] = None,
    user_agent: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None,
    application_version: Optional[str] = None,
) -> EnvironmentContext:
    """
    Create an environment context for feature flag evaluation.

    Args:
        request_id: Optional identifier for the current request
        ip_address: Optional IP address of the client
        user_agent: Optional user agent string
        metadata: Optional additional metadata
        application_version: Optional application version

    Returns:
        EnvironmentContext: Context for feature flag evaluation
    """
    from src.version import VERSION

    return EnvironmentContext(
        environment=detect_environment(),
        hostname=platform.node(),
        application_version=application_version or VERSION,
        request_id=request_id,
        ip_address=ip_address,
        user_agent=user_agent,
        metadata=metadata or {},
    )


def create_default_context() -> EnvironmentContext:
    """
    Create a default environment context with minimal information.

    Returns:
        EnvironmentContext: A minimal context for feature flag evaluation
    """
    return create_environment_context()
