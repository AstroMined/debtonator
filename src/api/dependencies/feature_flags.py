"""
Dependencies for feature flag-related functionality.

This module provides FastAPI dependency functions for the feature flag service
and context building from requests.
"""

import os
from typing import Optional

from fastapi import Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.repositories import get_repository
from src.database.database import get_db
from src.registry.feature_flags import FeatureFlagRegistry
from src.repositories.feature_flags import FeatureFlagRepository
from src.services.feature_flags import FeatureFlagService
from src.utils.config import settings
from src.utils.feature_flags.context import (
    Environment,
    EnvironmentContext,
    create_environment_context,
    detect_environment,
)
from src.utils.feature_flags.feature_flags import get_registry


def get_flag_management_enabled() -> bool:
    """
    Check if feature flag management is enabled based on environment.

    This function determines whether feature flag management endpoints
    should be accessible based on the current environment configuration.

    Returns:
        bool: True if feature flag management is enabled, False otherwise
    """

    # First check environment variable (highest priority)
    env_value = os.environ.get("ENABLE_FEATURE_FLAG_MANAGEMENT")
    if env_value is not None:
        # Handle string values properly
        if env_value == "0" or env_value.lower() in ("false", "no", "n", "f"):
            return False
        elif env_value == "1" or env_value.lower() in ("true", "yes", "y", "t"):
            return True

    # Then check settings
    settings_value = getattr(settings, "ENABLE_FEATURE_FLAG_MANAGEMENT", None)
    if settings_value is not None:
        # Handle potential string values in settings
        if isinstance(settings_value, str):
            if settings_value == "0" or settings_value.lower() in (
                "false",
                "no",
                "n",
                "f",
            ):
                return False
            elif settings_value == "1" or settings_value.lower() in (
                "true",
                "yes",
                "y",
                "t",
            ):
                return True
        # Handle boolean values
        elif isinstance(settings_value, bool):
            return settings_value
        # Handle integer values
        elif isinstance(settings_value, int):
            return settings_value != 0

    # Default based on environment
    environment = detect_environment()

    # Enable management in development and test environments by default
    # Disable in staging and production for safety
    return environment in (Environment.DEVELOPMENT, Environment.TEST)


def build_context_from_request(request: Request) -> EnvironmentContext:
    """
    Build an environment context from a FastAPI request.

    This function extracts relevant information from the request
    to create a context for feature flag evaluation.

    Args:
        request: The FastAPI request object

    Returns:
        EnvironmentContext: Context for feature flag evaluation
    """
    # Extract request information
    request_id = request.headers.get("X-Request-ID")
    user_agent = request.headers.get("User-Agent")

    # Get client IP address, handling potential proxies
    ip_address = request.client.host if request.client else None
    forwarded_for = request.headers.get("X-Forwarded-For")
    if forwarded_for:
        # Use the first IP if there are multiple in X-Forwarded-For
        ip_address = forwarded_for.split(",")[0].strip()

    # Extract metadata from request
    metadata = {
        "path": request.url.path,
        "method": request.method,
        "query_params": dict(request.query_params),
        "headers": {
            k: v
            for k, v in request.headers.items()
            if k.lower() not in ("authorization", "cookie", "x-api-key")
        },  # Exclude sensitive headers
    }

    return create_environment_context(
        request_id=request_id,
        ip_address=ip_address,
        user_agent=user_agent,
        metadata=metadata,
    )


def get_feature_flag_registry() -> FeatureFlagRegistry:
    """
    Get the application's feature flag registry.

    This function returns the global feature flag registry instance.

    Returns:
        FeatureFlagRegistry: The application's feature flag registry
    """

    return get_registry()


def get_feature_flag_repository(db: AsyncSession = Depends(get_db)):
    """
    Get the feature flag repository.

    This function returns a feature flag repository instance.

    Args:
        db: Database session from dependency injection

    Returns:
        FeatureFlagRepository: The feature flag repository
    """
    return get_repository(FeatureFlagRepository, db)


async def get_feature_flag_service(
    registry: FeatureFlagRegistry = Depends(get_feature_flag_registry),
    repository=Depends(get_feature_flag_repository),
    request: Request = None,
    context: Optional[EnvironmentContext] = None,
) -> FeatureFlagService:
    """
    Get the feature flag service with context.

    This function creates a feature flag service with the appropriate context.
    If a request is provided, context will be built from it. Otherwise, an
    existing context can be provided, or a default one will be created.

    The service is automatically initialized to ensure the registry is in sync
    with the database, preventing "flag not found" errors.

    Args:
        registry: The feature flag registry
        repository: The feature flag repository
        request: Optional FastAPI request
        context: Optional explicit context

    Returns:
        FeatureFlagService: The feature flag service with context
    """
    # Build context if request is provided
    if request and not context:
        context = build_context_from_request(request)
    # Use provided context or create a default one
    elif not context:
        context = create_environment_context()

    # Create service with context
    service = FeatureFlagService(
        registry=registry, repository=repository, context=context
    )

    # Initialize service to ensure registry is synced with database
    # This is necessary both in the main app and in tests
    await service.initialize()

    return service
