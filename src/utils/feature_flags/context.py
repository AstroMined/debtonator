"""
Context utilities for feature flag evaluation.

This module provides utilities for building context information used in
feature flag evaluation. Since the application is single-tenant without
user authentication, we use environment-based contexts instead of user contexts.
"""
from enum import Enum
import hashlib
import os
import platform
import sys
from pathlib import Path
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
    
    Returns:
        Environment: The detected environment (development, staging, production, or test)
    """
    from src.utils.config import settings
    
    # First try to get environment from settings
    env_name = getattr(settings, "APP_ENV", None)
    
    # Fall back to environment variable if not in settings
    if not env_name:
        env_name = os.environ.get("APP_ENV", "development")
        
    env_name = env_name.lower()
    
    if env_name == "test" or "pytest" in sys.modules:
        return Environment.TEST
    elif env_name == "production" or env_name == "prod":
        return Environment.PRODUCTION
    elif env_name == "staging" or env_name == "stage":
        return Environment.STAGING
    else:
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


def is_feature_enabled_for_percentage(
    percentage: float,
    identifier: str
) -> bool:
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
    application_version: Optional[str] = None
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
        metadata=metadata or {}
    )


def create_default_context() -> EnvironmentContext:
    """
    Create a default environment context with minimal information.
    
    Returns:
        EnvironmentContext: A minimal context for feature flag evaluation
    """
    return create_environment_context()
