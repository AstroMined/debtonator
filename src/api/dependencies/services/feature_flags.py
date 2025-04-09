"""
Feature Flag service dependencies.

This module provides dependencies for injecting feature flag services
into FastAPI route handlers. It leverages FastAPI's dependency injection system
to create and provide service instances with all their required dependencies.

Implements the Feature Flag System defined in ADR-024.
"""

from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.api.dependencies.database import get_session
from src.registry.feature_flags_registry import feature_flag_registry
from src.repositories.feature_flags import FeatureFlagRepository
from src.services.feature_flags import FeatureFlagService
from src.utils.feature_flags.context import EnvironmentContext

# Singleton instances for performance reasons
_context = EnvironmentContext()
_service_instance = None


async def get_feature_flag_service(
    session: AsyncSession = Depends(get_session),
) -> FeatureFlagService:
    """
    Get an instance of FeatureFlagService with all required dependencies.

    This dependency creates or returns a cached FeatureFlagService instance
    with proper repository dependencies and context. The service is initialized
    on first use to load flags from the database.

    Args:
        session: Database session from FastAPI dependency

    Returns:
        FeatureFlagService: Fully configured feature flag service instance
    """
    global _service_instance

    # Create a new service instance if needed
    if _service_instance is None:
        repository = FeatureFlagRepository(session)
        _service_instance = FeatureFlagService(
            registry=feature_flag_registry,
            repository=repository,
            context=_context,
        )
        # Initialize the service with database values
        await _service_instance.initialize()

    # Update the session in the repository (sessions are not thread-safe)
    _service_instance.repository._session = session

    return _service_instance
