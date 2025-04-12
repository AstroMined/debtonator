"""
Integration tests for the Service Factory with Feature Flag integration.

These tests verify that the ServiceFactory correctly creates services with
feature flag proxy applied when needed.
"""

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.providers.feature_flags import DatabaseConfigProvider
from src.services.factory import ServiceFactory
from src.services.proxies.feature_flag_proxy import ServiceProxy


class TestServiceFactoryFeatureFlags:
    """Tests for the service factory's integration with feature flags."""

    async def test_factory_creates_proxied_service_with_feature_flags(
        self,
        db_session: AsyncSession,
        factory_feature_flag_service,
    ):
        """Test that factory creates proxied services when feature flags are provided."""
        # Act - create service with feature flags
        account_service = await ServiceFactory.create_account_service(
            session=db_session,
            feature_flag_service=factory_feature_flag_service,
            apply_proxy=True,  # explicitly request proxy
        )

        # Assert - service should be wrapped in a proxy
        assert isinstance(account_service, ServiceProxy)
        assert account_service._feature_flag_service == factory_feature_flag_service

    async def test_factory_creates_regular_service_without_feature_flags(
        self,
        db_session: AsyncSession,
    ):
        """Test that factory creates regular services when feature flags aren't provided."""
        # Act - create service without feature flags
        account_service = await ServiceFactory.create_account_service(
            session=db_session,
            feature_flag_service=None,
        )

        # Assert - service should not be a proxy
        assert not isinstance(account_service, ServiceProxy)

    async def test_factory_respects_apply_proxy_flag(
        self,
        db_session: AsyncSession,
        factory_feature_flag_service,
    ):
        """Test that factory respects the apply_proxy flag."""
        # Act - create service with feature flags but disable proxy
        account_service = await ServiceFactory.create_account_service(
            session=db_session,
            feature_flag_service=factory_feature_flag_service,
            apply_proxy=False,  # disable proxy
        )

        # Assert - service should not be a proxy despite having feature flags
        assert not isinstance(account_service, ServiceProxy)

    async def test_factory_creates_config_provider(
        self,
        db_session: AsyncSession,
    ):
        """Test that factory correctly creates config provider."""
        # Directly test the _get_config_provider method
        config_provider = await ServiceFactory._get_config_provider(db_session)

        # Assert - should be a DatabaseConfigProvider
        assert isinstance(config_provider, DatabaseConfigProvider)
