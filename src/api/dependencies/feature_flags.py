"""
Dependencies for feature flag-related functionality.

This module provides FastAPI dependency functions for the feature flag service
and context building from requests.
"""
from typing import Optional

from fastapi import Depends, Request

from src.registry.feature_flags import FeatureFlagRegistry
from src.services.feature_flags import FeatureFlagService
from src.utils.feature_flags.context import EnvironmentContext, create_environment_context


def get_flag_management_enabled() -> bool:
    """
    Check if feature flag management is enabled based on environment.
    
    This function determines whether feature flag management endpoints
    should be accessible based on the current environment configuration.
    
    Returns:
        bool: True if feature flag management is enabled, False otherwise
    """
    from src.utils.config import settings
    
    # Get from settings if available
    enabled = getattr(settings, "ENABLE_FEATURE_FLAG_MANAGEMENT", None)
    
    # If not in settings, default based on environment
    if enabled is None:
        from src.utils.feature_flags.context import detect_environment, Environment
        environment = detect_environment()
        
        # Enable management in development and test environments by default
        # Disable in staging and production for safety
        enabled = environment in (Environment.DEVELOPMENT, Environment.TEST)
    
    return bool(enabled)


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
        "headers": {k: v for k, v in request.headers.items() if k.lower() not in 
                   ("authorization", "cookie", "x-api-key")},  # Exclude sensitive headers
    }
    
    return create_environment_context(
        request_id=request_id,
        ip_address=ip_address,
        user_agent=user_agent,
        metadata=metadata
    )


def get_feature_flag_registry() -> FeatureFlagRegistry:
    """
    Get the application's feature flag registry.
    
    This function returns the global feature flag registry instance.
    
    Returns:
        FeatureFlagRegistry: The application's feature flag registry
    """
    # Import at function level to avoid circular imports
    from src.config.feature_flags import get_registry
    
    return get_registry()


def get_feature_flag_repository():
    """
    Get the feature flag repository.
    
    This function returns a feature flag repository instance.
    
    Returns:
        FeatureFlagRepository: The feature flag repository
    """
    # Import at function level to avoid circular imports
    from src.api.dependencies.repositories import get_repository
    from src.repositories.feature_flags import FeatureFlagRepository
    
    return get_repository(FeatureFlagRepository)


def get_feature_flag_service(
    registry: FeatureFlagRegistry = Depends(get_feature_flag_registry),
    repository = Depends(get_feature_flag_repository),
    request: Request = None,
    context: Optional[EnvironmentContext] = None
) -> FeatureFlagService:
    """
    Get the feature flag service with context.
    
    This function creates a feature flag service with the appropriate context.
    If a request is provided, context will be built from it. Otherwise, an
    existing context can be provided, or a default one will be created.
    
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
    
    return FeatureFlagService(registry=registry, repository=repository, context=context)
