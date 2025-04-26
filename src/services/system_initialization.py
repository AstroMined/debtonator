"""
System initialization service.

This module provides services for initializing and ensuring required system data
exists in the database during application startup.

Implements ADR-014 Repository Layer Compliance by using BaseService for repository access.
Provides methods for initializing system categories and feature flags.
"""

import logging
from typing import Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.categories import CategoryRepository
from src.repositories.feature_flags import FeatureFlagRepository
from src.schemas.feature_flags import FeatureFlagType
from src.services.base import BaseService
from src.services.feature_flags import FeatureFlagService

logger = logging.getLogger(__name__)


class SystemInitializationService(BaseService):
    """
    Service for initializing system data during application startup.

    This service is responsible for ensuring required system data exists in the database,
    such as system categories, default feature flags, and other required system data.

    It follows the repository pattern by inheriting from BaseService and using
    _get_repository() for standardized repository access.
    """

    def __init__(
        self,
        session: AsyncSession,
        feature_flag_service: Optional[FeatureFlagService] = None,
        config_provider: Optional[Any] = None,
    ):
        """
        Initialize system initialization service.

        Args:
            session: SQLAlchemy async session
            feature_flag_service: Optional feature flag service
            config_provider: Optional config provider
        """
        super().__init__(session, feature_flag_service, config_provider)
        logger.info("System initialization service created")

    async def ensure_system_categories(self) -> None:
        """
        Ensure system categories exist - called during initialization.

        This leverages the repository layer to check for and create the default
        category if needed, maintaining architectural consistency.
        """
        # Get the category repository through standardized method
        category_repo = await self._get_repository(CategoryRepository)

        # This already handles creation if needed and ensures it's marked as a system category
        await category_repo.get_default_category_id()
        logger.info("Default system categories initialized")

        # Future system categories could be added here
        # For example: await category_repo.get_or_create_system_category("Bills", "Default bills category")

    async def ensure_system_feature_flags(self) -> None:
        """
        Ensure system feature flags exist - called during initialization.

        This method ensures that all required system feature flags exist in the database.
        If a flag does not exist, it is created with default values. If it already exists,
        its system status is verified and updated if needed.

        It uses the repository pattern by accessing the repository through BaseService.
        """
        logger.info("Ensuring system feature flags exist")

        # Get repository using BaseService pattern
        repository = await self._get_repository(FeatureFlagRepository)

        # Define required system flags with their default values
        system_flags = [
            {
                "name": "SYSTEM_INITIALIZED",
                "description": "Indicates that the system has been initialized",
                "flag_type": FeatureFlagType.BOOLEAN,
                "value": True,
                "is_system": True,
            },
            {
                "name": "FEATURE_FLAGS_ENABLED",
                "description": "Master switch for the feature flag system",
                "flag_type": FeatureFlagType.BOOLEAN,
                "value": True,
                "is_system": True,
            },
            {
                "name": "ACCOUNT_TYPES_ENABLED",
                "description": "Enables support for multiple account types",
                "flag_type": FeatureFlagType.BOOLEAN,
                "value": True,
                "is_system": True,
            },
            {
                "name": "BILLING_V2_ENABLED",
                "description": "Enables version 2 of the billing system",
                "flag_type": FeatureFlagType.BOOLEAN,
                "value": True,
                "is_system": True,
            },
        ]

        # Check and create/update each system flag
        for flag_data in system_flags:
            # Try to get existing flag
            flag_name = flag_data["name"]
            existing_flag = await repository.get(flag_name)

            if existing_flag:
                # Flag exists, ensure it's marked as system flag
                if not existing_flag.is_system:
                    await repository.update(flag_name, {"is_system": True})
                    logger.info("Updated flag %s to be a system flag", flag_name)
            else:
                # Flag doesn't exist, create it
                await repository.create(flag_data)
                logger.info("Created system flag: %s", flag_name)

        logger.info("System feature flags initialization complete")

    async def initialize_system(self) -> None:
        """
        Initialize all required system data.

        This method orchestrates the initialization of all required system data,
        including categories, feature flags, and other required data.
        """
        logger.info("Initializing system data")

        # Initialize system categories
        await self.ensure_system_categories()

        # Initialize system feature flags
        await self.ensure_system_feature_flags()

        logger.info("System data initialization complete")
