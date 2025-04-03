"""
Integration tests for feature flag configuration.

These tests verify that the feature flag configuration correctly initializes
the feature flag system with default flags and properly integrates with the
application startup process.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.registry.feature_flags import FeatureFlagRegistry
from src.repositories.feature_flags import FeatureFlagRepository
from src.services.feature_flags import FeatureFlagService
from src.utils.feature_flags.feature_flags import (
    DEFAULT_FEATURE_FLAGS,
    configure_development_defaults,
    configure_feature_flags,
)


class TestFeatureFlagConfig:
    """Integration tests for feature flag configuration."""

    @pytest.fixture
    async def registry(self):
        """Create a feature flag registry for testing."""
        return FeatureFlagRegistry()

    @pytest.fixture
    async def repository(self, db_session: AsyncSession):
        """Create a feature flag repository for testing."""
        return FeatureFlagRepository(db_session)

    async def test_configure_feature_flags(
        self, registry: FeatureFlagRegistry, repository: FeatureFlagRepository
    ):
        """Test that configure_feature_flags properly initializes the feature flag system."""
        # Configure the feature flag system
        service = await configure_feature_flags(registry, repository)

        # Check that the service was created
        assert isinstance(service, FeatureFlagService)

        # Check that default flags were registered
        for flag_config in DEFAULT_FEATURE_FLAGS:
            flag_name = flag_config["name"]

            # Check registry
            registry_flag = registry.get_flag(flag_name)
            assert registry_flag is not None
            assert registry_flag["value"] == flag_config["value"]
            assert registry_flag["description"] == flag_config["description"]
            assert registry_flag["is_system"] == flag_config["is_system"]

            # Check repository
            db_flag = await repository.get(flag_name)
            assert db_flag is not None
            assert db_flag.value == flag_config["value"]
            assert db_flag.description == flag_config["description"]
            assert db_flag.is_system == flag_config["is_system"]

    async def test_configure_development_defaults(
        self, registry: FeatureFlagRegistry, repository: FeatureFlagRepository
    ):
        """Test that development defaults properly enable all feature flags."""
        # First configure the feature flag system
        service = await configure_feature_flags(registry, repository)

        # Initially, all flags should be disabled
        for flag_config in DEFAULT_FEATURE_FLAGS:
            flag_name = flag_config["name"]
            # Verify initial state (all flags start as disabled)
            assert service.is_enabled(flag_name) is False

        # Apply development defaults
        await configure_development_defaults(service)

        # Now all flags should be enabled
        for flag_config in DEFAULT_FEATURE_FLAGS:
            flag_name = flag_config["name"]
            # Verify enabled state
            assert service.is_enabled(flag_name) is True

    async def test_idempotent_initialization(
        self, registry: FeatureFlagRegistry, repository: FeatureFlagRepository
    ):
        """Test that configuring feature flags is idempotent and can be called multiple times."""
        # Configure once
        service1 = await configure_feature_flags(registry, repository)

        # Configure again
        service2 = await configure_feature_flags(registry, repository)

        # Should be the same service (in terms of behavior, not necessarily the same instance)
        assert isinstance(service1, FeatureFlagService)
        assert isinstance(service2, FeatureFlagService)

        # Default flags should still be configured correctly
        for flag_config in DEFAULT_FEATURE_FLAGS:
            flag_name = flag_config["name"]
            assert registry.get_flag(flag_name) is not None
            assert (await repository.get(flag_name)) is not None

    async def test_flag_values_preserved(
        self, registry: FeatureFlagRegistry, repository: FeatureFlagRepository
    ):
        """Test that existing flag values are preserved when reconfiguring."""
        # Configure initially
        service = await configure_feature_flags(registry, repository)

        # Change a flag value
        flag_name = DEFAULT_FEATURE_FLAGS[0]["name"]
        await service.set_enabled(flag_name, True)

        # The flag should now be enabled
        assert service.is_enabled(flag_name) is True

        # Reconfigure
        service = await configure_feature_flags(registry, repository)

        # The flag value should be preserved
        assert service.is_enabled(flag_name) is True
