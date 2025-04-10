"""
Fixtures for service instances.

This module provides fixtures for service objects including feature flags.
All fixtures follow the Real Objects Testing Philosophy without mocks.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.feature_flags import FeatureFlagRepository
from src.services.feature_flags import FeatureFlagService
from src.utils.feature_flags.feature_flags import DEFAULT_FEATURE_FLAGS, get_registry


@pytest_asyncio.fixture
async def feature_flag_service(
    feature_flag_repository: FeatureFlagRepository,
) -> FeatureFlagService:
    """
    Create and initialize a feature flag service for testing.

    This fixture creates a real feature flag service, initializes it with
    default flags, and enables banking account types for testing.
    
    Args:
        feature_flag_repository: Repository for feature flags
        
    Returns:
        FeatureFlagService: Service for managing feature flags
    """
    # Get registry singleton
    registry = get_registry()

    # Create service
    service = FeatureFlagService(registry, feature_flag_repository)

    # Create default flags in database
    for flag_config in DEFAULT_FEATURE_FLAGS:
        # Check if flag exists in database to avoid duplicates
        flag = await feature_flag_repository.get(flag_config["name"])
        if not flag:
            await service.create_flag(flag_config)

    # Initialize service (loads flags from database)
    await service.initialize()

    # Enable banking account types for testing
    await service.set_enabled("BANKING_ACCOUNT_TYPES_ENABLED", True)

    return service
