"""
Integration tests for the feature flag service.

These tests verify that the feature flag service correctly interacts with the repository
and registry components, properly synchronizing feature flags between the database
and in-memory registry.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.feature_flags import FeatureFlag
from src.registry.feature_flags import FeatureFlagRegistry
from src.repositories.feature_flags import FeatureFlagRepository
from src.schemas.feature_flags import FeatureFlagCreate, FeatureFlagType
from src.services.feature_flags import FeatureFlagService
from src.utils.datetime_utils import utc_now


class TestFeatureFlagService:
    """Integration tests for the FeatureFlagService class."""

    @pytest.fixture
    async def registry(self):
        """Create a feature flag registry for testing."""
        return FeatureFlagRegistry()

    @pytest.fixture
    async def repository(self, db_session: AsyncSession):
        """Create a feature flag repository for testing."""
        return FeatureFlagRepository(db_session)

    @pytest.fixture
    async def service(
        self, registry: FeatureFlagRegistry, repository: FeatureFlagRepository
    ):
        """Create a feature flag service for testing."""
        service = FeatureFlagService(registry, repository)
        await service.initialize()
        return service

    @pytest.fixture
    async def sample_flags_db(self, db_session: AsyncSession):
        """Create sample feature flags in the database."""
        flags = [
            FeatureFlag(
                name="BOOLEAN_FLAG",
                flag_type=FeatureFlagType.BOOLEAN,
                value=True,
                description="Test boolean flag",
                flag_metadata={"type": "boolean"},
                is_system=False,
                created_at=utc_now(),
                updated_at=utc_now(),
            ),
            FeatureFlag(
                name="PERCENTAGE_FLAG",
                flag_type=FeatureFlagType.PERCENTAGE,
                value=50,
                description="Test percentage flag",
                flag_metadata={"type": "percentage"},
                is_system=False,
                created_at=utc_now(),
                updated_at=utc_now(),
            ),
            FeatureFlag(
                name="USER_SEGMENT_FLAG",
                flag_type=FeatureFlagType.USER_SEGMENT,
                value=["admin", "beta"],
                description="Test user segment flag",
                flag_metadata={"type": "segment"},
                is_system=False,
                created_at=utc_now(),
                updated_at=utc_now(),
            ),
        ]

        for flag in flags:
            db_session.add(flag)

        await db_session.flush()
        return flags

    async def test_initialize(
        self,
        registry: FeatureFlagRegistry,
        repository: FeatureFlagRepository,
        sample_flags_db,
    ):
        """Test initializing the service with existing flags in the database."""
        # Create service and initialize it
        service = FeatureFlagService(registry, repository)
        await service.initialize()

        # Check that flags from database were loaded into registry
        assert registry.get_flag("BOOLEAN_FLAG") is not None
        assert registry.get_flag("PERCENTAGE_FLAG") is not None
        assert registry.get_flag("USER_SEGMENT_FLAG") is not None

        # Check values are correct
        assert registry.get_value("BOOLEAN_FLAG") is True
        assert registry.get_flag("PERCENTAGE_FLAG")["value"] == 50
        assert registry.get_flag("USER_SEGMENT_FLAG")["value"] == ["admin", "beta"]

    async def test_is_enabled_boolean(self, service: FeatureFlagService):
        """Test checking if a boolean flag is enabled."""
        # Create test flags
        await service.create_flag(
            {
                "name": "ENABLED_FLAG",
                "flag_type": FeatureFlagType.BOOLEAN,
                "value": True,
            }
        )

        await service.create_flag(
            {
                "name": "DISABLED_FLAG",
                "flag_type": FeatureFlagType.BOOLEAN,
                "value": False,
            }
        )

        # Check enabled flag
        assert service.is_enabled("ENABLED_FLAG") is True

        # Check disabled flag
        assert service.is_enabled("DISABLED_FLAG") is False

        # Check nonexistent flag
        assert service.is_enabled("NONEXISTENT_FLAG") is False

    async def test_is_enabled_percentage(self, service: FeatureFlagService):
        """Test checking if a percentage flag is enabled based on context."""
        await service.create_flag(
            {
                "name": "PERCENTAGE_FLAG",
                "flag_type": FeatureFlagType.PERCENTAGE,
                "value": 50,  # 50% rollout
            }
        )

        # Without context, should be disabled
        assert service.is_enabled("PERCENTAGE_FLAG") is False

        # With context containing user_id, will depend on the hash calculation
        # We can't predict the exact outcome, but we can verify it doesn't error
        context = {"user_id": "test-user-1"}
        service.is_enabled("PERCENTAGE_FLAG", context)

        # Try another user ID
        context = {"user_id": "test-user-2"}
        service.is_enabled("PERCENTAGE_FLAG", context)

    async def test_is_enabled_user_segment(self, service: FeatureFlagService):
        """Test checking if a user segment flag is enabled based on context."""
        await service.create_flag(
            {
                "name": "SEGMENT_FLAG",
                "flag_type": FeatureFlagType.USER_SEGMENT,
                "value": ["admin", "beta"],
            }
        )

        # Without context, should be disabled
        assert service.is_enabled("SEGMENT_FLAG") is False

        # Admin user should have it enabled
        assert service.is_enabled("SEGMENT_FLAG", {"is_admin": True}) is True

        # Beta tester should have it enabled
        assert service.is_enabled("SEGMENT_FLAG", {"is_beta_tester": True}) is True

        # User in beta group should have it enabled
        assert (
            service.is_enabled("SEGMENT_FLAG", {"user_groups": ["regular", "beta"]})
            is True
        )

        # Regular user should not have it enabled
        assert service.is_enabled("SEGMENT_FLAG", {"user_groups": ["regular"]}) is False

    async def test_set_enabled(
        self, service: FeatureFlagService, repository: FeatureFlagRepository
    ):
        """Test enabling and disabling a boolean flag."""
        # Create a test flag
        await service.create_flag(
            {
                "name": "TOGGLE_FLAG",
                "flag_type": FeatureFlagType.BOOLEAN,
                "value": False,
            }
        )

        # Verify initial state
        assert service.is_enabled("TOGGLE_FLAG") is False

        # Enable the flag
        result = await service.set_enabled("TOGGLE_FLAG", True)
        assert result is True

        # Check it's enabled in both registry and repository
        assert service.is_enabled("TOGGLE_FLAG") is True
        flag_db = await repository.get("TOGGLE_FLAG")
        assert flag_db.value is True

        # Disable the flag
        result = await service.set_enabled("TOGGLE_FLAG", False)
        assert result is True

        # Check it's disabled in both registry and repository
        assert service.is_enabled("TOGGLE_FLAG") is False
        flag_db = await repository.get("TOGGLE_FLAG")
        assert flag_db.value is False

    async def test_set_enabled_non_boolean(self, service: FeatureFlagService):
        """Test that set_enabled fails for non-boolean flags."""
        # Create a percentage flag
        await service.create_flag(
            {
                "name": "PERCENTAGE_FLAG",
                "flag_type": FeatureFlagType.PERCENTAGE,
                "value": 50,
            }
        )

        # Try to use set_enabled on it
        result = await service.set_enabled("PERCENTAGE_FLAG", True)
        assert result is False  # Should fail

    async def test_create_flag(
        self, service: FeatureFlagService, repository: FeatureFlagRepository
    ):
        """Test creating a new feature flag."""
        flag_data = FeatureFlagCreate(
            name="NEW_FLAG",
            flag_type=FeatureFlagType.BOOLEAN,
            value=True,
            description="New test flag",
            flag_metadata={"owner": "test-team"},
        )

        # Create the flag
        flag = await service.create_flag(flag_data)

        # Check it exists in both registry and repository
        assert flag is not None
        assert flag.name == "NEW_FLAG"

        # Check registry
        registry_flag = service.registry.get_flag("NEW_FLAG")
        assert registry_flag is not None
        assert registry_flag["value"] is True

        # Check repository
        db_flag = await repository.get("NEW_FLAG")
        assert db_flag is not None
        assert db_flag.value is True
        assert db_flag.description == "New test flag"
        assert db_flag.flag_metadata == {"owner": "test-team"}

    async def test_update_flag(
        self, service: FeatureFlagService, repository: FeatureFlagRepository
    ):
        """Test updating an existing feature flag."""
        # Create a flag to update
        await service.create_flag(
            {
                "name": "UPDATE_FLAG",
                "flag_type": FeatureFlagType.BOOLEAN,
                "value": False,
                "description": "Original description",
            }
        )

        # Update the flag
        update_data = {
            "value": True,
            "description": "Updated description",
            "flag_metadata": {"updated": True},
        }

        updated_flag = await service.update_flag("UPDATE_FLAG", update_data)

        # Check it was updated
        assert updated_flag is not None
        assert updated_flag.value is True
        assert updated_flag.description == "Updated description"
        assert updated_flag.flag_metadata == {"updated": True}

        # Check registry was updated
        registry_flag = service.registry.get_flag("UPDATE_FLAG")
        assert registry_flag["value"] is True

        # Check repository was updated
        db_flag = await repository.get("UPDATE_FLAG")
        assert db_flag.value is True
        assert db_flag.description == "Updated description"
        assert db_flag.flag_metadata == {"updated": True}

    async def test_delete_flag(
        self, service: FeatureFlagService, repository: FeatureFlagRepository
    ):
        """Test deleting a feature flag."""
        # Create a flag to delete
        await service.create_flag(
            {
                "name": "DELETE_FLAG",
                "flag_type": FeatureFlagType.BOOLEAN,
                "value": True,
            }
        )

        # Verify it exists
        assert await repository.get("DELETE_FLAG") is not None

        # Delete the flag
        result = await service.delete_flag("DELETE_FLAG")
        assert result is True

        # Verify it's gone from the repository
        assert await repository.get("DELETE_FLAG") is None

        # Note: The registry doesn't support removing flags directly,
        # so the service maintains DB as source of truth

    async def test_delete_system_flag(
        self, service: FeatureFlagService, repository: FeatureFlagRepository
    ):
        """Test that system flags cannot be deleted."""
        # Create a system flag
        await service.create_flag(
            {
                "name": "SYSTEM_FLAG",
                "flag_type": FeatureFlagType.BOOLEAN,
                "value": True,
                "is_system": True,
            }
        )

        # Try to delete it
        result = await service.delete_flag("SYSTEM_FLAG")
        assert result is False

        # Verify it still exists
        assert await repository.get("SYSTEM_FLAG") is not None

    async def test_get_all_flags(self, service: FeatureFlagService, sample_flags_db):
        """Test retrieving all feature flags."""
        # Get all flags
        flags = await service.get_all_flags()

        # Check we got all three flags
        assert len(flags) == 3

        # Check flag names
        flag_names = {flag.name for flag in flags}
        assert "BOOLEAN_FLAG" in flag_names
        assert "PERCENTAGE_FLAG" in flag_names
        assert "USER_SEGMENT_FLAG" in flag_names

    async def test_set_value(
        self, service: FeatureFlagService, repository: FeatureFlagRepository
    ):
        """Test setting the value of different flag types."""
        # Create flags of different types
        await service.create_flag(
            {
                "name": "BOOLEAN_VALUE_FLAG",
                "flag_type": FeatureFlagType.BOOLEAN,
                "value": False,
            }
        )

        await service.create_flag(
            {
                "name": "PERCENTAGE_VALUE_FLAG",
                "flag_type": FeatureFlagType.PERCENTAGE,
                "value": 25,
            }
        )

        await service.create_flag(
            {
                "name": "SEGMENT_VALUE_FLAG",
                "flag_type": FeatureFlagType.USER_SEGMENT,
                "value": ["admin"],
            }
        )

        # Update boolean flag
        result = await service.set_value("BOOLEAN_VALUE_FLAG", True)
        assert result is True
        assert service.registry.get_flag("BOOLEAN_VALUE_FLAG")["value"] is True
        assert (await repository.get("BOOLEAN_VALUE_FLAG")).value is True

        # Update percentage flag
        result = await service.set_value("PERCENTAGE_VALUE_FLAG", 75)
        assert result is True
        assert service.registry.get_flag("PERCENTAGE_VALUE_FLAG")["value"] == 75
        assert (await repository.get("PERCENTAGE_VALUE_FLAG")).value == 75

        # Update segment flag
        result = await service.set_value("SEGMENT_VALUE_FLAG", ["admin", "beta"])
        assert result is True
        assert service.registry.get_flag("SEGMENT_VALUE_FLAG")["value"] == [
            "admin",
            "beta",
        ]
        assert (await repository.get("SEGMENT_VALUE_FLAG")).value == ["admin", "beta"]

    async def test_get_flag(self, service: FeatureFlagService, sample_flags_db):
        """Test retrieving a specific flag by name."""
        # Get an existing flag
        flag = await service.get_flag("BOOLEAN_FLAG")
        assert flag is not None
        assert flag.name == "BOOLEAN_FLAG"
        assert flag.flag_type == FeatureFlagType.BOOLEAN
        assert flag.value is True

        # Get a nonexistent flag
        flag = await service.get_flag("NONEXISTENT_FLAG")
        assert flag is None
