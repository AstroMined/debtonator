"""
Integration tests for the feature flag service.

These tests verify that the feature flag service correctly interacts with the repository
and registry components, properly synchronizing feature flags between the database
and in-memory registry.
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.feature_flags import FeatureFlag
from src.schemas.feature_flags import FeatureFlagCreate, FeatureFlagType
from src.services.feature_flags import FeatureFlagService
from src.utils.datetime_utils import utc_now


@pytest_asyncio.fixture
async def test_flags(db_session: AsyncSession):
    """
    Create sample feature flags in the database for testing.

    Args:
        db_session: Database session

    Returns:
        Dict mapping flag types to their unique names
    """
    # Create unique names using timestamp microseconds
    now = utc_now()
    boolean_name = f"BOOL_FLAG_{now.microsecond}_1"
    percentage_name = f"PCT_FLAG_{now.microsecond}_2"
    segment_name = f"SEG_FLAG_{now.microsecond}_3"

    flags = [
        FeatureFlag(
            name=boolean_name,
            flag_type=FeatureFlagType.BOOLEAN,
            value=True,
            description="Test boolean flag",
            flag_metadata={"type": "boolean"},
            is_system=False,
            created_at=now,
            updated_at=now,
        ),
        FeatureFlag(
            name=percentage_name,
            flag_type=FeatureFlagType.PERCENTAGE,
            value=50,
            description="Test percentage flag",
            flag_metadata={"type": "percentage"},
            is_system=False,
            created_at=now,
            updated_at=now,
        ),
        FeatureFlag(
            name=segment_name,
            flag_type=FeatureFlagType.USER_SEGMENT,
            value=["admin", "beta"],
            description="Test user segment flag",
            flag_metadata={"type": "segment"},
            is_system=False,
            created_at=now,
            updated_at=now,
        ),
    ]

    for flag in flags:
        db_session.add(flag)

    await db_session.flush()

    # Return a dict mapping flag types to names for easy reference in tests
    return {
        "boolean": boolean_name,
        "percentage": percentage_name,
        "segment": segment_name,
    }


@pytest.mark.asyncio
async def test_service_initialize_with_existing_flags(
    feature_flag_registry,
    feature_flag_repository,
    test_flags,
):
    """Test initializing the service with existing flags in the database."""
    # Create service and initialize it
    service = FeatureFlagService(feature_flag_registry, feature_flag_repository)
    await service.initialize()

    # Check that flags from database were loaded into registry
    boolean_flag = test_flags["boolean"]
    percentage_flag = test_flags["percentage"]
    segment_flag = test_flags["segment"]

    assert feature_flag_registry.get_flag(boolean_flag) is not None
    assert feature_flag_registry.get_flag(percentage_flag) is not None
    assert feature_flag_registry.get_flag(segment_flag) is not None

    # Check values are correct
    assert feature_flag_registry.get_value(boolean_flag) is True
    assert feature_flag_registry.get_flag(percentage_flag)["value"] == 50
    assert feature_flag_registry.get_flag(segment_flag)["value"] == ["admin", "beta"]


@pytest.mark.asyncio
async def test_service_create_flag(feature_flag_service, feature_flag_repository):
    """Test creating a new feature flag."""
    # Use unique name with microseconds to avoid conflicts
    flag_name = f"NEW_FLAG_{utc_now().microsecond}"

    flag_data = FeatureFlagCreate(
        name=flag_name,
        flag_type=FeatureFlagType.BOOLEAN,
        value=True,
        description="New test flag",
        flag_metadata={"owner": "test-team"},
    )

    # Create the flag
    flag = await feature_flag_service.create_flag(flag_data)

    # Check it exists in both registry and repository
    assert flag is not None
    assert flag.name == flag_name

    # Check registry
    registry_flag = feature_flag_service.registry.get_flag(flag_name)
    assert registry_flag is not None
    assert registry_flag["value"] is True

    # Check repository
    db_flag = await feature_flag_repository.get(flag_name)
    assert db_flag is not None
    assert db_flag.value is True
    assert db_flag.description == "New test flag"
    assert db_flag.flag_metadata == {"owner": "test-team"}
