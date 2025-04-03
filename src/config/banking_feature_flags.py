"""
Banking account types feature flag configuration.

This module defines the configuration for banking-related feature flags
and initialization functions for the feature flag registry.

Implemented as part of ADR-019 Banking Account Types Expansion.
"""

from src.services.feature_flags import FeatureFlagService


def register_banking_feature_flags(feature_flag_service: FeatureFlagService) -> None:
    """
    Register banking-related feature flags with the feature flag service.

    Args:
        feature_flag_service: The feature flag service to register flags with
    """
    # Banking Account Types Feature Flag
    feature_flag_service.register_flag(
        name="BANKING_ACCOUNT_TYPES_ENABLED",
        default_value=True,  # Enabled by default in development
        description="Enable banking account types including checking, savings, credit, payment app, BNPL, and EWA accounts",
        category="Banking",
    )

    # Multi-Currency Support Feature Flag
    feature_flag_service.register_flag(
        name="MULTI_CURRENCY_SUPPORT_ENABLED",
        default_value=False,  # Disabled by default
        description="Enable multi-currency support for accounts",
        category="Banking",
    )

    # International Banking Support Feature Flag
    feature_flag_service.register_flag(
        name="INTERNATIONAL_ACCOUNT_SUPPORT_ENABLED",
        default_value=False,  # Disabled by default
        description="Enable international banking fields such as IBAN, SWIFT/BIC, and sort codes",
        category="Banking",
    )


def initialize_banking_feature_flags(app=None) -> None:
    """
    Initialize banking feature flags during application startup.

    Args:
        app: The FastAPI application instance (optional)
    """
    # If app is provided, get the feature flag service from app state
    if app:
        feature_flag_service = app.state.feature_flag_service
        register_banking_feature_flags(feature_flag_service)
    else:
        # For testing or CLI usage when app is not available
        # Create a standalone feature flag service
        from src.registry.feature_flags import feature_flag_registry
        from src.repositories.feature_flags import FeatureFlagRepository
        from src.utils.db import get_db

        db = next(get_db())
        repository = FeatureFlagRepository(db)
        feature_flag_service = FeatureFlagService(
            registry=feature_flag_registry, repository=repository
        )

        register_banking_feature_flags(feature_flag_service)
