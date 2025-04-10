"""
Fixtures for feature flag testing.

This module provides test fixtures for feature flag models and related objects.
All fixtures follow the Real Objects Testing Philosophy without mocks.
"""

import os
from typing import Dict, List, Optional

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.feature_flags import FeatureFlag
from src.utils.datetime_utils import days_ago, days_from_now


@pytest_asyncio.fixture
async def test_boolean_flag(db_session: AsyncSession) -> FeatureFlag:
    """
    Create a boolean feature flag for testing.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        FeatureFlag: Created boolean feature flag
    """
    feature_flag = FeatureFlag(
        name="TEST_FEATURE_BOOLEAN",
        description="Test boolean feature flag",
        value=True,  # Boolean flags have a simple boolean value
        flag_type="boolean",
        flag_metadata={"environment": "development"},
    )

    db_session.add(feature_flag)
    await db_session.flush()
    await db_session.refresh(feature_flag)

    return feature_flag


@pytest_asyncio.fixture
async def test_percentage_flag(db_session: AsyncSession) -> FeatureFlag:
    """
    Create a percentage rollout feature flag for testing.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        FeatureFlag: Created percentage rollout feature flag
    """
    feature_flag = FeatureFlag(
        name="TEST_FEATURE_PERCENTAGE",
        description="Test percentage rollout feature flag",
        value=50,  # Percentage value between 0-100
        flag_type="percentage",
        flag_metadata={"environment": "development"},
    )

    db_session.add(feature_flag)
    await db_session.flush()
    await db_session.refresh(feature_flag)

    return feature_flag


@pytest_asyncio.fixture
async def test_environment_flag(db_session: AsyncSession) -> FeatureFlag:
    """
    Create an environment-specific feature flag for testing.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        FeatureFlag: Created environment-specific feature flag
    """
    feature_flag = FeatureFlag(
        name="TEST_FEATURE_ENVIRONMENT",
        description="Test environment-specific feature flag",
        value={"environments": ["development", "test"], "default": False},
        flag_type="environment",
        flag_metadata={"environment": "development"},
    )

    db_session.add(feature_flag)
    await db_session.flush()
    await db_session.refresh(feature_flag)

    return feature_flag


@pytest_asyncio.fixture
async def test_time_based_flag(db_session: AsyncSession) -> FeatureFlag:
    """
    Create a time-based feature flag for testing.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        FeatureFlag: Created time-based feature flag
    """
    # Set start time to yesterday and end time to tomorrow
    yesterday = days_ago(1).isoformat()
    tomorrow = days_from_now(1).isoformat()

    feature_flag = FeatureFlag(
        name="TEST_FEATURE_TIME_BASED",
        description="Test time-based feature flag",
        value={"start_time": yesterday, "end_time": tomorrow},
        flag_type="time_based",
        flag_metadata={"environment": "development"},
    )

    db_session.add(feature_flag)
    await db_session.flush()
    await db_session.refresh(feature_flag)

    return feature_flag


@pytest_asyncio.fixture
async def test_multiple_flags(db_session: AsyncSession) -> List[FeatureFlag]:
    """
    Create multiple feature flags of different types for testing.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        List[FeatureFlag]: List of created feature flags of different types
    """
    flags = [
        FeatureFlag(
            name="FEATURE_A",
            description="Feature A - Boolean",
            value=True,
            flag_type="boolean",
            flag_metadata={"environment": "development"},
        ),
        FeatureFlag(
            name="FEATURE_B",
            description="Feature B - Boolean (disabled)",
            value=False,
            flag_type="boolean",
            flag_metadata={"environment": "development"},
        ),
        FeatureFlag(
            name="FEATURE_C",
            description="Feature C - Percentage",
            value=75,
            flag_type="percentage",
            flag_metadata={"environment": "development"},
        ),
        FeatureFlag(
            name="FEATURE_D",
            description="Feature D - Environment",
            value={"environments": ["production", "staging"], "default": False},
            flag_type="environment",
            flag_metadata={"environment": "development"},
        ),
    ]

    for flag in flags:
        db_session.add(flag)

    await db_session.flush()

    # Refresh all entries to ensure they reflect what's in the database
    for flag in flags:
        await db_session.refresh(flag)

    return flags


@pytest_asyncio.fixture
async def sample_flag(db_session: AsyncSession) -> FeatureFlag:
    """
    Create a sample feature flag for repository testing.
    
    This fixture creates a boolean feature flag with metadata for
    testing the feature flag repository.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        FeatureFlag: Created sample feature flag
    """
    flag = FeatureFlag(
        name="TEST_BOOLEAN_FLAG",
        flag_type="boolean",
        value=True,
        description="Test boolean flag",
        flag_metadata={"test": "metadata"},
        is_system=False,
        created_at=days_ago(0),  # today
        updated_at=days_ago(0),  # today
    )
    db_session.add(flag)
    await db_session.flush()
    await db_session.refresh(flag)
    return flag


@pytest_asyncio.fixture
async def env_setup():
    """
    Setup and teardown for environment variable tests.
    
    This fixture preserves the original environment variables and
    restores them after the test completes.
    
    Returns:
        None: This fixture yields control to the test
    """
    # Store original environment
    original_env = os.environ.copy()

    # Yield control to test
    yield

    # Restore original environment
    os.environ.clear()
    os.environ.update(original_env)


@pytest_asyncio.fixture
async def environment_context_fixture(db_session: AsyncSession):
    """
    Create an environment context with test data.
    
    This fixture creates a context without using mocks by setting
    actual environment variables.
    
    Args:
        db_session: Database session fixture
        
    Returns:
        Dict: Created environment context
    """
    from src.utils.feature_flags.context import create_environment_context

    # Create with real data and a test request ID
    context = create_environment_context(
        request_id="test-request-id",
        ip_address="127.0.0.1",
        user_agent="Test User Agent",
        metadata={"test_key": "test_value"},
    )

    return context
