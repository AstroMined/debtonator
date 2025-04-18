"""
Feature Flag Configuration

This module provides functions for initializing the feature flag system with
default flag values. It registers the standard feature flags defined in ADR-024
and provides a function to configure the feature flag system during app startup.

This implementation includes the database-driven feature flag requirements as
defined in ADR-024 implementation.
"""

import logging

from src.registry.feature_flags_registry import FeatureFlagRegistry
from src.repositories.feature_flags import FeatureFlagRepository
from src.schemas.feature_flags import FeatureFlagType
from src.services.feature_flags import FeatureFlagService
from src.utils.feature_flags.requirements import get_default_requirements

logger = logging.getLogger(__name__)

# Global registry instance (singleton)
_REGISTRY: FeatureFlagRegistry = None


def get_registry() -> FeatureFlagRegistry:
    """
    Get the global FeatureFlagRegistry instance.

    This function implements the singleton pattern, ensuring that
    all parts of the application use the same registry instance.

    Returns:
        FeatureFlagRegistry: The global feature flag registry instance
    """
    global _REGISTRY

    if _REGISTRY is None:
        logger.debug("Creating new FeatureFlagRegistry instance")
        _REGISTRY = FeatureFlagRegistry()

    return _REGISTRY


# Get the default requirements for feature flags
DEFAULT_REQUIREMENTS = get_default_requirements()

# Default feature flags as defined in ADR-024
DEFAULT_FEATURE_FLAGS = [
    {
        "name": "BANKING_ACCOUNT_TYPES_ENABLED",
        "flag_type": FeatureFlagType.BOOLEAN,
        "value": False,
        "description": "Enable new banking account types from ADR-019",
        "is_system": True,
        "flag_metadata": {"adr": "019", "owner": "backend-team"},
        "requirements": DEFAULT_REQUIREMENTS.get("BANKING_ACCOUNT_TYPES_ENABLED", {}),
    },
    {
        "name": "MULTI_CURRENCY_SUPPORT_ENABLED",
        "flag_type": FeatureFlagType.BOOLEAN,
        "value": False,
        "description": "Enable multi-currency support for accounts",
        "is_system": True,
        "flag_metadata": {"adr": "019", "owner": "backend-team"},
        "requirements": DEFAULT_REQUIREMENTS.get("MULTI_CURRENCY_SUPPORT_ENABLED", {}),
    },
    {
        "name": "INTERNATIONAL_ACCOUNT_SUPPORT_ENABLED",
        "flag_type": FeatureFlagType.BOOLEAN,
        "value": False,
        "description": "Enable international account support (IBAN, SWIFT, etc.)",
        "is_system": True,
        "flag_metadata": {"adr": "019", "owner": "backend-team"},
        "requirements": DEFAULT_REQUIREMENTS.get(
            "INTERNATIONAL_ACCOUNT_SUPPORT_ENABLED", {}
        ),
    },
    {
        "name": "BNPL_ACCOUNTS_ENABLED",
        "flag_type": FeatureFlagType.BOOLEAN,
        "value": False,
        "description": "Enable Buy Now Pay Later account type",
        "is_system": True,
        "flag_metadata": {"adr": "019", "owner": "backend-team"},
        "requirements": DEFAULT_REQUIREMENTS.get("BNPL_ACCOUNTS_ENABLED", {}),
    },
    {
        "name": "EWA_ACCOUNTS_ENABLED",
        "flag_type": FeatureFlagType.BOOLEAN,
        "value": False,
        "description": "Enable Early Wage Access account type",
        "is_system": True,
        "flag_metadata": {"adr": "019", "owner": "backend-team"},
        "requirements": DEFAULT_REQUIREMENTS.get("EWA_ACCOUNTS_ENABLED", {}),
    },
    {
        "name": "PAYMENT_APP_ACCOUNTS_ENABLED",
        "flag_type": FeatureFlagType.BOOLEAN,
        "value": False,
        "description": "Enable Payment App account type",
        "is_system": True,
        "flag_metadata": {"adr": "019", "owner": "backend-team"},
        "requirements": DEFAULT_REQUIREMENTS.get("PAYMENT_APP_ACCOUNTS_ENABLED", {}),
    },
]


async def configure_feature_flags(
    registry: FeatureFlagRegistry, repository: FeatureFlagRepository
) -> FeatureFlagService:
    """
    Configure the feature flag system with default flags.

    This function creates a FeatureFlagService instance, registers default feature flags,
    and initializes the service from the database. It should be called during application
    startup.

    Args:
        registry: The feature flag registry
        repository: The feature flag repository

    Returns:
        FeatureFlagService: The configured feature flag service
    """
    # Create the service
    service = FeatureFlagService(registry, repository)

    # Create default feature flags in DB if they don't exist
    for flag_config in DEFAULT_FEATURE_FLAGS:
        # Check if flag exists in database
        flag = await repository.get(flag_config["name"])
        if not flag:
            logger.info(f"Creating default feature flag: {flag_config['name']}")
            await service.create_flag(flag_config)
        else:
            logger.debug(f"Feature flag already exists: {flag_config['name']}")

    # Initialize service (loads all flags from DB)
    await service.initialize()

    logger.info("Feature flag system configured")
    return service


async def configure_development_defaults(service: FeatureFlagService) -> None:
    """
    Configure development-specific feature flag defaults.

    This function sets development-specific values for feature flags.
    It should only be called in development environments.

    Args:
        service: The feature flag service
    """
    # In development, enable all feature flags by default for testing
    dev_flags = {
        "BANKING_ACCOUNT_TYPES_ENABLED": True,
        "MULTI_CURRENCY_SUPPORT_ENABLED": True,
        "INTERNATIONAL_ACCOUNT_SUPPORT_ENABLED": True,
        "BNPL_ACCOUNTS_ENABLED": True,
        "EWA_ACCOUNTS_ENABLED": True,
        "PAYMENT_APP_ACCOUNTS_ENABLED": True,
    }

    for flag_name, enabled in dev_flags.items():
        await service.set_enabled(flag_name, enabled)

    logger.info("Development feature flag defaults configured")
