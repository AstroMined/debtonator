"""
Banking account types feature flag configuration.

This module defines the configuration for banking-related feature flags
and initialization functions for the feature flag registry.

Implements ADR-019 Banking Account Types Expansion and 
ADR-024 Feature Flags for granular access control.
"""

from src.services.feature_flags import FeatureFlagService


def register_banking_feature_flags(feature_flag_service: FeatureFlagService) -> None:
    """
    Register banking-related feature flags with the feature flag service.

    Args:
        feature_flag_service: The feature flag service to register flags with
    """
    # Master Banking Account Types Feature Flag
    feature_flag_service.register_flag(
        name="BANKING_ACCOUNT_TYPES_ENABLED",
        default_value=True,  # Enabled by default in development
        description="Master switch for all banking account types",
        category="Banking",
    )

    # Individual Account Type Feature Flags
    feature_flag_service.register_flag(
        name="CHECKING_ACCOUNTS_ENABLED",
        default_value=True,
        description="Enable checking accounts",
        category="Banking:AccountTypes",
        depends_on="BANKING_ACCOUNT_TYPES_ENABLED",
    )

    feature_flag_service.register_flag(
        name="SAVINGS_ACCOUNTS_ENABLED",
        default_value=True,
        description="Enable savings accounts",
        category="Banking:AccountTypes",
        depends_on="BANKING_ACCOUNT_TYPES_ENABLED",
    )

    feature_flag_service.register_flag(
        name="CREDIT_ACCOUNTS_ENABLED",
        default_value=True,
        description="Enable credit card accounts",
        category="Banking:AccountTypes",
        depends_on="BANKING_ACCOUNT_TYPES_ENABLED",
    )

    feature_flag_service.register_flag(
        name="PAYMENT_APP_ACCOUNTS_ENABLED",
        default_value=True,
        description="Enable payment app accounts (PayPal, Venmo, etc.)",
        category="Banking:AccountTypes",
        depends_on="BANKING_ACCOUNT_TYPES_ENABLED",
    )

    feature_flag_service.register_flag(
        name="BNPL_ACCOUNTS_ENABLED",
        default_value=True,
        description="Enable Buy Now Pay Later accounts",
        category="Banking:AccountTypes",
        depends_on="BANKING_ACCOUNT_TYPES_ENABLED",
    )

    feature_flag_service.register_flag(
        name="EWA_ACCOUNTS_ENABLED",
        default_value=True,
        description="Enable Earned Wage Access accounts",
        category="Banking:AccountTypes",
        depends_on="BANKING_ACCOUNT_TYPES_ENABLED",
    )

    # Multi-Currency Support Feature Flag
    feature_flag_service.register_flag(
        name="MULTI_CURRENCY_SUPPORT_ENABLED",
        default_value=False,  # Disabled by default
        description="Enable multi-currency support for accounts",
        category="Banking:Features",
    )

    # International Banking Support Feature Flag
    feature_flag_service.register_flag(
        name="INTERNATIONAL_ACCOUNT_SUPPORT_ENABLED",
        default_value=False,  # Disabled by default
        description="Enable international banking fields such as IBAN, SWIFT/BIC, and sort codes",
        category="Banking:Features",
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
        from src.registry.feature_flags import FeatureFlagRegistry
        from src.repositories.feature_flags import FeatureFlagRepository
        from src.database.database import get_db_session

        # Create a new registry instance
        registry = FeatureFlagRegistry()
        
        # Get a db session
        db = next(get_db_session())
        repository = FeatureFlagRepository(db)
        feature_flag_service = FeatureFlagService(
            registry=registry, repository=repository
        )

        register_banking_feature_flags(feature_flag_service)


def is_account_type_enabled(account_type: str, feature_flag_service: FeatureFlagService) -> bool:
    """
    Check if a specific account type is enabled.

    This is a helper function to centralize the logic for determining if an account
    type is enabled based on feature flags.

    Args:
        account_type: The account type to check ("checking", "savings", etc.)
        feature_flag_service: The feature flag service to check flags with

    Returns:
        bool: True if the account type is enabled, False otherwise
    """
    # First, check if the master switch is enabled
    if not feature_flag_service.is_enabled("BANKING_ACCOUNT_TYPES_ENABLED"):
        return False

    # Map account type to its specific feature flag
    flag_mapping = {
        "checking": "CHECKING_ACCOUNTS_ENABLED",
        "savings": "SAVINGS_ACCOUNTS_ENABLED",
        "credit": "CREDIT_ACCOUNTS_ENABLED",
        "payment_app": "PAYMENT_APP_ACCOUNTS_ENABLED",
        "bnpl": "BNPL_ACCOUNTS_ENABLED",
        "ewa": "EWA_ACCOUNTS_ENABLED",
    }

    # Check if the account type has a corresponding feature flag
    if account_type in flag_mapping:
        return feature_flag_service.is_enabled(flag_mapping[account_type])

    # For unknown account types, default to disabled for safety
    return False
