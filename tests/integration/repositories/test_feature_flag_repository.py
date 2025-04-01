"""
Integration tests for the feature flag repository.

These tests verify that the feature flag repository correctly interacts with
the database, storing and retrieving feature flags as expected.
"""

import pytest
from datetime import datetime, timedelta

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.feature_flags import FeatureFlag
from src.repositories.feature_flags import FeatureFlagRepository
from src.schemas.feature_flags import FeatureFlagType
from src.utils.datetime_utils import utc_now, ensure_utc


class TestFeatureFlagRepository:
    """Integration tests for the FeatureFlagRepository class."""

    @pytest.fixture
    async def repository(self, db_session: AsyncSession):
        """Create a repository instance for testing."""
        return FeatureFlagRepository(db_session)

    @pytest.fixture
    async def sample_flag(self, db_session: AsyncSession):
        """Create a sample feature flag in the database."""
        flag = FeatureFlag(
            name="TEST_BOOLEAN_FLAG",
            flag_type=FeatureFlagType.BOOLEAN,
            value=True,
            description="Test boolean flag",
            metadata={"test": "metadata"},
            is_system=False,
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        db_session.add(flag)
        await db_session.flush()
        await db_session.refresh(flag)
        return flag

    async def test_create_flag(self, repository: FeatureFlagRepository):
        """Test creating a new feature flag."""
        flag_data = {
            "name": "NEW_FLAG",
            "flag_type": FeatureFlagType.BOOLEAN,
            "value": True,
            "description": "New test flag",
            "metadata": {"owner": "test-team"},
            "is_system": False,
        }

        flag = await repository.create(flag_data)

        assert flag.name == "NEW_FLAG"
        assert flag.flag_type == FeatureFlagType.BOOLEAN
        assert flag.value is True
        assert flag.description == "New test flag"
        assert flag.metadata == {"owner": "test-team"}
        assert flag.is_system is False
        assert flag.created_at is not None
        assert flag.updated_at is not None

    async def test_get_flag(self, repository: FeatureFlagRepository, sample_flag: FeatureFlag):
        """Test retrieving a feature flag by name."""
        flag = await repository.get(sample_flag.name)

        assert flag is not None
        assert flag.name == sample_flag.name
        assert flag.flag_type == sample_flag.flag_type
        assert flag.value == sample_flag.value
        assert flag.description == sample_flag.description
        assert flag.metadata == sample_flag.metadata
        assert flag.is_system == sample_flag.is_system

    async def test_get_nonexistent_flag(self, repository: FeatureFlagRepository):
        """Test retrieving a nonexistent feature flag."""
        flag = await repository.get("NONEXISTENT_FLAG")
        assert flag is None

    async def test_get_all(self, repository: FeatureFlagRepository, sample_flag: FeatureFlag):
        """Test retrieving all feature flags."""
        # Create additional flags
        await repository.create({
            "name": "SECOND_FLAG",
            "flag_type": FeatureFlagType.PERCENTAGE,
            "value": 50,
        })

        await repository.create({
            "name": "THIRD_FLAG",
            "flag_type": FeatureFlagType.USER_SEGMENT,
            "value": ["admin", "beta"],
        })

        # Retrieve all flags
        flags = await repository.get_all()

        # Check that we got all the flags
        assert len(flags) == 3
        flag_names = {flag.name for flag in flags}
        assert "TEST_BOOLEAN_FLAG" in flag_names
        assert "SECOND_FLAG" in flag_names
        assert "THIRD_FLAG" in flag_names

    async def test_update_flag(self, repository: FeatureFlagRepository, sample_flag: FeatureFlag):
        """Test updating a feature flag."""
        # Update the flag
        update_data = {
            "value": False,
            "description": "Updated description",
            "metadata": {"updated": True},
        }

        updated_flag = await repository.update(sample_flag.name, update_data)

        # Check that the update was applied
        assert updated_flag is not None
        assert updated_flag.value is False
        assert updated_flag.description == "Updated description"
        assert updated_flag.metadata == {"updated": True}
        # These should remain unchanged
        assert updated_flag.name == sample_flag.name
        assert updated_flag.flag_type == sample_flag.flag_type
        assert updated_flag.is_system == sample_flag.is_system

        # Verify by retrieving again
        retrieved_flag = await repository.get(sample_flag.name)
        assert retrieved_flag.value is False
        assert retrieved_flag.description == "Updated description"
        assert retrieved_flag.metadata == {"updated": True}

    async def test_update_nonexistent_flag(self, repository: FeatureFlagRepository):
        """Test updating a nonexistent feature flag."""
        updated_flag = await repository.update("NONEXISTENT_FLAG", {"value": True})
        assert updated_flag is None

    async def test_delete_flag(self, repository: FeatureFlagRepository, sample_flag: FeatureFlag):
        """Test deleting a feature flag."""
        # Delete the flag
        result = await repository.delete(sample_flag.name)
        assert result is True

        # Verify it's gone
        flag = await repository.get(sample_flag.name)
        assert flag is None

    async def test_delete_nonexistent_flag(self, repository: FeatureFlagRepository):
        """Test deleting a nonexistent feature flag."""
        result = await repository.delete("NONEXISTENT_FLAG")
        assert result is False

    async def test_get_all_by_type(self, repository: FeatureFlagRepository):
        """Test retrieving feature flags by type."""
        # Create flags of different types
        await repository.create({
            "name": "BOOLEAN_FLAG_1",
            "flag_type": FeatureFlagType.BOOLEAN,
            "value": True,
        })

        await repository.create({
            "name": "BOOLEAN_FLAG_2",
            "flag_type": FeatureFlagType.BOOLEAN,
            "value": False,
        })

        await repository.create({
            "name": "PERCENTAGE_FLAG",
            "flag_type": FeatureFlagType.PERCENTAGE,
            "value": 50,
        })

        # Get boolean flags
        boolean_flags = await repository.get_all_by_type(FeatureFlagType.BOOLEAN)
        assert len(boolean_flags) == 2
        for flag in boolean_flags:
            assert flag.flag_type == FeatureFlagType.BOOLEAN
            assert flag.name in {"BOOLEAN_FLAG_1", "BOOLEAN_FLAG_2"}

        # Get percentage flags
        percentage_flags = await repository.get_all_by_type(FeatureFlagType.PERCENTAGE)
        assert len(percentage_flags) == 1
        assert percentage_flags[0].flag_type == FeatureFlagType.PERCENTAGE
        assert percentage_flags[0].name == "PERCENTAGE_FLAG"

        # Get a type with no flags
        user_segment_flags = await repository.get_all_by_type(FeatureFlagType.USER_SEGMENT)
        assert len(user_segment_flags) == 0

    async def test_get_system_flags(self, repository: FeatureFlagRepository):
        """Test retrieving system-defined feature flags."""
        # Create system and non-system flags
        await repository.create({
            "name": "SYSTEM_FLAG_1",
            "flag_type": FeatureFlagType.BOOLEAN,
            "value": True,
            "is_system": True,
        })

        await repository.create({
            "name": "SYSTEM_FLAG_2",
            "flag_type": FeatureFlagType.BOOLEAN,
            "value": False,
            "is_system": True,
        })

        await repository.create({
            "name": "USER_FLAG",
            "flag_type": FeatureFlagType.BOOLEAN,
            "value": True,
            "is_system": False,
        })

        # Get system flags
        system_flags = await repository.get_system_flags()
        assert len(system_flags) == 2
        for flag in system_flags:
            assert flag.is_system is True
            assert flag.name in {"SYSTEM_FLAG_1", "SYSTEM_FLAG_2"}

    async def test_bulk_create(self, repository: FeatureFlagRepository):
        """Test creating multiple feature flags in a single transaction."""
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

        created_flags = await repository.bulk_create(flags_data)
        assert len(created_flags) == 3

        # Verify all were created
        all_flags = await repository.get_all()
        bulk_flags = [flag for flag in all_flags if flag.name.startswith("BULK_FLAG_")]
        assert len(bulk_flags) == 3

    async def test_bulk_update(self, repository: FeatureFlagRepository):
        """Test updating multiple feature flags in a single transaction."""
        # Create flags to update
        await repository.create({
            "name": "UPDATE_FLAG_1",
            "flag_type": FeatureFlagType.BOOLEAN,
            "value": True,
        })

        await repository.create({
            "name": "UPDATE_FLAG_2",
            "flag_type": FeatureFlagType.BOOLEAN,
            "value": False,
        })

        # Update both flags
        updates = [
            ("UPDATE_FLAG_1", {"value": False}),
            ("UPDATE_FLAG_2", {"value": True}),
        ]

        updated_flags = await repository.bulk_update(updates)
        assert len(updated_flags) == 2
        
        # Both should exist and be updated
        assert all(flag is not None for flag in updated_flags)
        
        # Verify updates
        flag1 = await repository.get("UPDATE_FLAG_1")
        flag2 = await repository.get("UPDATE_FLAG_2")
        
        assert flag1.value is False
        assert flag2.value is True

    async def test_count_by_type(self, repository: FeatureFlagRepository):
        """Test counting feature flags by type."""
        # Create flags of different types
        await repository.create({
            "name": "COUNT_BOOLEAN_1",
            "flag_type": FeatureFlagType.BOOLEAN,
            "value": True,
        })

        await repository.create({
            "name": "COUNT_BOOLEAN_2",
            "flag_type": FeatureFlagType.BOOLEAN,
            "value": False,
        })

        await repository.create({
            "name": "COUNT_PERCENTAGE",
            "flag_type": FeatureFlagType.PERCENTAGE,
            "value": 50,
        })

        # Get counts
        counts = await repository.count_by_type()
        
        # Check counts are accurate
        assert counts[FeatureFlagType.BOOLEAN] == 2
        assert counts[FeatureFlagType.PERCENTAGE] == 1
        assert counts[FeatureFlagType.USER_SEGMENT] == 0
        assert counts[FeatureFlagType.TIME_BASED] == 0
