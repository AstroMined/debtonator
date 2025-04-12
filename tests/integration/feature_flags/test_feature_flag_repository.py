"""
Integration tests for the feature flag repository.

These tests verify that the feature flag repository correctly interacts with
the database, storing and retrieving feature flags as expected.
"""

import pytest

from src.models.feature_flags import FeatureFlag
from src.repositories.feature_flags import FeatureFlagRepository
from src.schemas.feature_flags import FeatureFlagType

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_create_flag(feature_flag_repository: FeatureFlagRepository):
    """
    Test creating a new feature flag.

    This test verifies that the FeatureFlagRepository correctly creates
    a new feature flag with the provided data.

    Args:
        feature_flag_repository: Feature flag repository fixture
    """
    # 1. ARRANGE: Repository is provided by fixture

    # 2. SCHEMA: Create flag data (no schema factory needed for this test)
    flag_data = {
        "name": "NEW_FLAG",
        "flag_type": FeatureFlagType.BOOLEAN,
        "value": True,
        "description": "New test flag",
        "metadata": {"owner": "test-team"},
        "is_system": False,
    }

    # 3. ACT: Create the flag
    flag = await feature_flag_repository.create(flag_data)

    # 4. ASSERT: Verify the flag was created correctly
    assert flag.name == "NEW_FLAG"
    assert flag.flag_type == FeatureFlagType.BOOLEAN
    assert flag.value is True
    assert flag.description == "New test flag"
    assert flag.flag_metadata == {"owner": "test-team"}
    assert flag.is_system is False
    assert flag.created_at is not None
    assert flag.updated_at is not None


@pytest.mark.asyncio
async def test_get_flag(
    feature_flag_repository: FeatureFlagRepository, sample_flag: FeatureFlag
):
    """
    Test retrieving a feature flag by name.

    This test verifies that the FeatureFlagRepository correctly retrieves
    a feature flag by its name.

    Args:
        feature_flag_repository: Feature flag repository fixture
        sample_flag: Sample feature flag fixture
    """
    # 1. ARRANGE: Repository and sample flag are provided by fixtures

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Retrieve the flag
    flag = await feature_flag_repository.get(sample_flag.name)

    # 4. ASSERT: Verify the flag was retrieved correctly
    assert flag is not None
    assert flag.name == sample_flag.name
    assert flag.flag_type == sample_flag.flag_type
    assert flag.value == sample_flag.value
    assert flag.description == sample_flag.description
    assert flag.flag_metadata == sample_flag.flag_metadata
    assert flag.is_system == sample_flag.is_system


@pytest.mark.asyncio
async def test_get_nonexistent_flag(feature_flag_repository: FeatureFlagRepository):
    """
    Test retrieving a nonexistent feature flag.

    This test verifies that the FeatureFlagRepository correctly returns None
    when attempting to retrieve a nonexistent feature flag.

    Args:
        feature_flag_repository: Feature flag repository fixture
    """
    # 1. ARRANGE: Repository is provided by fixture

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Attempt to retrieve a nonexistent flag
    flag = await feature_flag_repository.get("NONEXISTENT_FLAG")

    # 4. ASSERT: Verify the result is None
    assert flag is None


@pytest.mark.asyncio
async def test_get_all(
    feature_flag_repository: FeatureFlagRepository, sample_flag: FeatureFlag
):
    """
    Test retrieving all feature flags.

    This test verifies that the FeatureFlagRepository correctly retrieves
    all feature flags from the database.

    Args:
        feature_flag_repository: Feature flag repository fixture
        sample_flag: Sample feature flag fixture
    """
    # 1. ARRANGE: Create additional flags
    await feature_flag_repository.create(
        {
            "name": "SECOND_FLAG",
            "flag_type": FeatureFlagType.PERCENTAGE,
            "value": 50,
        }
    )

    await feature_flag_repository.create(
        {
            "name": "THIRD_FLAG",
            "flag_type": FeatureFlagType.USER_SEGMENT,
            "value": ["admin", "beta"],
        }
    )

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Retrieve all flags
    flags = await feature_flag_repository.get_all()

    # 4. ASSERT: Verify all flags were retrieved
    assert len(flags) == 3
    flag_names = {flag.name for flag in flags}
    assert "TEST_BOOLEAN_FLAG" in flag_names
    assert "SECOND_FLAG" in flag_names
    assert "THIRD_FLAG" in flag_names


@pytest.mark.asyncio
async def test_update_flag(
    feature_flag_repository: FeatureFlagRepository, sample_flag: FeatureFlag
):
    """
    Test updating a feature flag.

    This test verifies that the FeatureFlagRepository correctly updates
    a feature flag with the provided data.

    Args:
        feature_flag_repository: Feature flag repository fixture
        sample_flag: Sample feature flag fixture
    """
    # 1. ARRANGE: Repository and sample flag are provided by fixtures

    # 2. SCHEMA: Create update data (no schema factory needed for this test)
    update_data = {
        "value": False,
        "description": "Updated description",
        "metadata": {"updated": True},
    }

    # 3. ACT: Update the flag
    updated_flag = await feature_flag_repository.update(sample_flag.name, update_data)

    # 4. ASSERT: Verify the flag was updated correctly
    assert updated_flag is not None
    assert updated_flag.value is False
    assert updated_flag.description == "Updated description"
    assert updated_flag.flag_metadata == {"updated": True}
    # These should remain unchanged
    assert updated_flag.name == sample_flag.name
    assert updated_flag.flag_type == sample_flag.flag_type
    assert updated_flag.is_system == sample_flag.is_system

    # Verify by retrieving again
    retrieved_flag = await feature_flag_repository.get(sample_flag.name)
    assert retrieved_flag.value is False
    assert retrieved_flag.description == "Updated description"
    assert retrieved_flag.flag_metadata == {"updated": True}


@pytest.mark.asyncio
async def test_update_nonexistent_flag(feature_flag_repository: FeatureFlagRepository):
    """
    Test updating a nonexistent feature flag.

    This test verifies that the FeatureFlagRepository correctly returns None
    when attempting to update a nonexistent feature flag.

    Args:
        feature_flag_repository: Feature flag repository fixture
    """
    # 1. ARRANGE: Repository is provided by fixture

    # 2. SCHEMA: Create update data (no schema factory needed for this test)
    update_data = {"value": True}

    # 3. ACT: Attempt to update a nonexistent flag
    updated_flag = await feature_flag_repository.update("NONEXISTENT_FLAG", update_data)

    # 4. ASSERT: Verify the result is None
    assert updated_flag is None


@pytest.mark.asyncio
async def test_delete_flag(
    feature_flag_repository: FeatureFlagRepository, sample_flag: FeatureFlag
):
    """
    Test deleting a feature flag.

    This test verifies that the FeatureFlagRepository correctly deletes
    a feature flag from the database.

    Args:
        feature_flag_repository: Feature flag repository fixture
        sample_flag: Sample feature flag fixture
    """
    # 1. ARRANGE: Repository and sample flag are provided by fixtures

    # 2. SCHEMA: Not applicable for this operation

    # 3. ACT: Delete the flag
    result = await feature_flag_repository.delete(sample_flag.name)

    # 4. ASSERT: Verify the flag was deleted
    assert result is True

    # Verify it's gone
    flag = await feature_flag_repository.get(sample_flag.name)
    assert flag is None


@pytest.mark.asyncio
async def test_delete_nonexistent_flag(feature_flag_repository: FeatureFlagRepository):
    """
    Test deleting a nonexistent feature flag.

    This test verifies that the FeatureFlagRepository correctly returns False
    when attempting to delete a nonexistent feature flag.

    Args:
        feature_flag_repository: Feature flag repository fixture
    """
    # 1. ARRANGE: Repository is provided by fixture

    # 2. SCHEMA: Not applicable for this operation

    # 3. ACT: Attempt to delete a nonexistent flag
    result = await feature_flag_repository.delete("NONEXISTENT_FLAG")

    # 4. ASSERT: Verify the result is False
    assert result is False


@pytest.mark.asyncio
async def test_get_all_by_type(feature_flag_repository: FeatureFlagRepository):
    """
    Test retrieving feature flags by type.

    This test verifies that the FeatureFlagRepository correctly retrieves
    feature flags filtered by their type.

    Args:
        feature_flag_repository: Feature flag repository fixture
    """
    # 1. ARRANGE: Create flags of different types
    await feature_flag_repository.create(
        {
            "name": "BOOLEAN_FLAG_1",
            "flag_type": FeatureFlagType.BOOLEAN,
            "value": True,
        }
    )

    await feature_flag_repository.create(
        {
            "name": "BOOLEAN_FLAG_2",
            "flag_type": FeatureFlagType.BOOLEAN,
            "value": False,
        }
    )

    await feature_flag_repository.create(
        {
            "name": "PERCENTAGE_FLAG",
            "flag_type": FeatureFlagType.PERCENTAGE,
            "value": 50,
        }
    )

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Get flags by type
    boolean_flags = await feature_flag_repository.get_all_by_type(
        FeatureFlagType.BOOLEAN
    )
    percentage_flags = await feature_flag_repository.get_all_by_type(
        FeatureFlagType.PERCENTAGE
    )
    user_segment_flags = await feature_flag_repository.get_all_by_type(
        FeatureFlagType.USER_SEGMENT
    )

    # 4. ASSERT: Verify the flags were retrieved correctly
    assert len(boolean_flags) == 2
    for flag in boolean_flags:
        assert flag.flag_type == FeatureFlagType.BOOLEAN
        assert flag.name in {"BOOLEAN_FLAG_1", "BOOLEAN_FLAG_2"}

    assert len(percentage_flags) == 1
    assert percentage_flags[0].flag_type == FeatureFlagType.PERCENTAGE
    assert percentage_flags[0].name == "PERCENTAGE_FLAG"

    assert len(user_segment_flags) == 0


@pytest.mark.asyncio
async def test_get_system_flags(feature_flag_repository: FeatureFlagRepository):
    """
    Test retrieving system-defined feature flags.

    This test verifies that the FeatureFlagRepository correctly retrieves
    feature flags that are marked as system flags.

    Args:
        feature_flag_repository: Feature flag repository fixture
    """
    # 1. ARRANGE: Create system and non-system flags
    await feature_flag_repository.create(
        {
            "name": "SYSTEM_FLAG_1",
            "flag_type": FeatureFlagType.BOOLEAN,
            "value": True,
            "is_system": True,
        }
    )

    await feature_flag_repository.create(
        {
            "name": "SYSTEM_FLAG_2",
            "flag_type": FeatureFlagType.BOOLEAN,
            "value": False,
            "is_system": True,
        }
    )

    await feature_flag_repository.create(
        {
            "name": "USER_FLAG",
            "flag_type": FeatureFlagType.BOOLEAN,
            "value": True,
            "is_system": False,
        }
    )

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Get system flags
    system_flags = await feature_flag_repository.get_system_flags()

    # 4. ASSERT: Verify the system flags were retrieved correctly
    assert len(system_flags) == 2
    for flag in system_flags:
        assert flag.is_system is True
        assert flag.name in {"SYSTEM_FLAG_1", "SYSTEM_FLAG_2"}


@pytest.mark.asyncio
async def test_bulk_create(feature_flag_repository: FeatureFlagRepository):
    """
    Test creating multiple feature flags in a single transaction.

    This test verifies that the FeatureFlagRepository correctly creates
    multiple feature flags in a single transaction.

    Args:
        feature_flag_repository: Feature flag repository fixture
    """
    # 1. ARRANGE: Repository is provided by fixture

    # 2. SCHEMA: Create flag data (no schema factory needed for this test)
    flags_data = [
        {
            "name": "BULK_FLAG_1",
            "flag_type": FeatureFlagType.BOOLEAN,
            "value": True,
        },
        {
            "name": "BULK_FLAG_2",
            "flag_type": FeatureFlagType.PERCENTAGE,
            "value": 25,
        },
        {
            "name": "BULK_FLAG_3",
            "flag_type": FeatureFlagType.USER_SEGMENT,
            "value": ["admin"],
        },
    ]

    # 3. ACT: Create the flags in bulk
    created_flags = await feature_flag_repository.bulk_create(flags_data)

    # 4. ASSERT: Verify the flags were created correctly
    assert len(created_flags) == 3

    # Verify all were created
    all_flags = await feature_flag_repository.get_all()
    bulk_flags = [flag for flag in all_flags if flag.name.startswith("BULK_FLAG_")]
    assert len(bulk_flags) == 3


@pytest.mark.asyncio
async def test_bulk_update(feature_flag_repository: FeatureFlagRepository):
    """
    Test updating multiple feature flags in a single transaction.

    This test verifies that the FeatureFlagRepository correctly updates
    multiple feature flags in a single transaction.

    Args:
        feature_flag_repository: Feature flag repository fixture
    """
    # 1. ARRANGE: Create flags to update
    await feature_flag_repository.create(
        {
            "name": "UPDATE_FLAG_1",
            "flag_type": FeatureFlagType.BOOLEAN,
            "value": True,
        }
    )

    await feature_flag_repository.create(
        {
            "name": "UPDATE_FLAG_2",
            "flag_type": FeatureFlagType.BOOLEAN,
            "value": False,
        }
    )

    # 2. SCHEMA: Create update data (no schema factory needed for this test)
    updates = [
        ("UPDATE_FLAG_1", {"value": False}),
        ("UPDATE_FLAG_2", {"value": True}),
    ]

    # 3. ACT: Update the flags in bulk
    updated_flags = await feature_flag_repository.bulk_update(updates)

    # 4. ASSERT: Verify the flags were updated correctly
    assert len(updated_flags) == 2

    # Both should exist and be updated
    assert all(flag is not None for flag in updated_flags)

    # Verify updates
    flag1 = await feature_flag_repository.get("UPDATE_FLAG_1")
    flag2 = await feature_flag_repository.get("UPDATE_FLAG_2")

    assert flag1.value is False
    assert flag2.value is True


@pytest.mark.asyncio
async def test_count_by_type(feature_flag_repository: FeatureFlagRepository):
    """
    Test counting feature flags by type.

    This test verifies that the FeatureFlagRepository correctly counts
    feature flags grouped by their type.

    Args:
        feature_flag_repository: Feature flag repository fixture
    """
    # 1. ARRANGE: Create flags of different types
    await feature_flag_repository.create(
        {
            "name": "COUNT_BOOLEAN_1",
            "flag_type": FeatureFlagType.BOOLEAN,
            "value": True,
        }
    )

    await feature_flag_repository.create(
        {
            "name": "COUNT_BOOLEAN_2",
            "flag_type": FeatureFlagType.BOOLEAN,
            "value": False,
        }
    )

    await feature_flag_repository.create(
        {
            "name": "COUNT_PERCENTAGE",
            "flag_type": FeatureFlagType.PERCENTAGE,
            "value": 50,
        }
    )

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Get counts by type
    counts = await feature_flag_repository.count_by_type()

    # 4. ASSERT: Verify the counts are accurate
    assert counts[FeatureFlagType.BOOLEAN] == 2
    assert counts[FeatureFlagType.PERCENTAGE] == 1
    assert counts[FeatureFlagType.USER_SEGMENT] == 0
    assert counts[FeatureFlagType.TIME_BASED] == 0
