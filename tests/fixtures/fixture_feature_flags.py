"""
Simplified feature flag fixtures for testing.

This module provides the minimal required fixtures for feature flag testing.
Each fixture is async-compatible and properly isolated for clean tests.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.feature_flags import FeatureFlag
from src.registry.feature_flags_registry import FeatureFlagRegistry
from src.repositories.feature_flags import FeatureFlagRepository
from src.services.feature_flags import FeatureFlagService
from src.utils.datetime_utils import utc_now


@pytest_asyncio.fixture
async def feature_flag_model(db_session: AsyncSession) -> FeatureFlag:
    """
    Create a simple test feature flag.

    Args:
        db_session: Database session

    Returns:
        FeatureFlag: A test feature flag
    """
    # Use a unique name pattern for test fixture to avoid conflicts
    flag_name = f"TEST_FLAG_{utc_now().microsecond}"

    flag = FeatureFlag(
        name=flag_name,
        flag_type="boolean",
        value=True,
        description="Test feature flag",
        is_system=False,
        created_at=utc_now(),
        updated_at=utc_now(),
    )

    db_session.add(flag)
    await db_session.flush()
    await db_session.refresh(flag)

    return flag


@pytest_asyncio.fixture
async def feature_flag_registry() -> FeatureFlagRegistry:
    """
    Provide a clean feature flag registry.

    Returns:
        FeatureFlagRegistry: A fresh registry instance
    """
    registry = FeatureFlagRegistry()
    registry.reset()  # Ensure clean state
    return registry


@pytest_asyncio.fixture
async def feature_flag_repository(db_session: AsyncSession) -> FeatureFlagRepository:
    """
    Provide a feature flag repository.

    Args:
        db_session: Database session

    Returns:
        FeatureFlagRepository: Repository for feature flags
    """
    return FeatureFlagRepository(db_session)


@pytest_asyncio.fixture
async def feature_flag_service(
    feature_flag_registry: FeatureFlagRegistry,
    feature_flag_repository: FeatureFlagRepository,
) -> FeatureFlagService:
    """
    Provide a minimal feature flag service.

    This fixture creates a basic service without attempting to create
    any default flags or perform complex initialization.

    Args:
        feature_flag_registry: Registry fixture
        feature_flag_repository: Repository fixture

    Returns:
        FeatureFlagService: Basic feature flag service
    """
    service = FeatureFlagService(feature_flag_registry, feature_flag_repository)

    # Simple initialization without creating default flags
    await service.initialize()

    return service


@pytest_asyncio.fixture
async def boolean_feature_flag(
    db_session: AsyncSession, feature_flag_service: FeatureFlagService
) -> str:
    """
    Create a boolean feature flag for testing.

    Args:
        db_session: Database session
        feature_flag_service: Feature flag service

    Returns:
        str: The name of the created feature flag
    """
    # Use microseconds to ensure unique names across test runs
    flag_name = f"BOOL_FLAG_{utc_now().microsecond}"

    # Create a boolean feature flag
    flag_data = {
        "name": flag_name,
        "flag_type": "boolean",
        "value": True,
        "description": "Test boolean flag",
        "is_system": False,
    }

    await feature_flag_service.create_flag(flag_data)
    return flag_name
