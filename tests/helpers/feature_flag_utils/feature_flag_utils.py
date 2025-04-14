"""
Feature flag testing utilities.

This module provides helpers for testing with feature flags, including
solutions for cache-related issues that can occur in test environments.
"""

from typing import Any, Dict

from src.config.providers.feature_flags import InMemoryConfigProvider


class ZeroTTLConfigProvider(InMemoryConfigProvider):
    """
    Config provider with zero TTL for testing purposes.

    This provider disables caching, ensuring that changes to feature flags
    take effect immediately. This is particularly useful in test environments
    where multiple operations need to reflect flag changes without delays.

    Usage:
        config_provider = ZeroTTLConfigProvider({
            "FLAG_NAME": {
                "repository": {
                    "method_name": ["account_type1", "account_type2"]
                }
            }
        })
    """

    def __init__(self, requirements: Dict[str, Any]):
        """
        Initialize the provider with given requirements.

        Args:
            requirements: Feature flag requirements mapping
        """
        super().__init__(requirements)
        # Override the TTL to be 0 seconds for testing
        self._cache_ttl = 0


def create_test_requirements(flag_name: str, account_type: str) -> Dict[str, Any]:
    """
    Create standardized test requirements for a feature flag.

    This helper creates a properly formatted requirements structure that will
    be recognized by the FeatureFlagRepositoryProxy.

    Args:
        flag_name: Name of the feature flag
        account_type: Account type to include in requirements

    Returns:
        Dictionary with properly formatted requirements structure
    """
    return {
        flag_name: {
            "repository": {
                "create_typed_entity": [account_type],
                "update_typed_entity": [account_type],
                "get_by_type": [account_type],
            }
        }
    }


def clear_config_provider_cache(config_provider: InMemoryConfigProvider) -> None:
    """
    Manually clear a config provider's cache.

    This function provides a standardized way to clear the cache when using
    a provider with non-zero TTL.

    Args:
        config_provider: The config provider to clear cache for
    """
    config_provider._cache = {}
    config_provider._cache_expiry = 0


async def set_flag_and_clear_cache(
    feature_flag_service, flag_name: str, enabled: bool, repository_proxy=None
) -> None:
    """
    Set a feature flag and clear the repository proxy cache.

    This helper ensures flag changes are immediately reflected in tests by combining
    the flag update and cache clearing in one call.

    Args:
        feature_flag_service: The feature flag service to use
        flag_name: Name of the feature flag to update
        enabled: Whether the flag should be enabled
        repository_proxy: Repository proxy to clear cache for (optional)
    """
    await feature_flag_service.set_enabled(flag_name, enabled, proxy=repository_proxy)

    # Fallback if proxy not provided or doesn't have the method
    if repository_proxy and not hasattr(repository_proxy, "clear_feature_check_cache"):
        # Log a warning about missing method
        import logging

        logger = logging.getLogger(__name__)
        logger.warning(
            f"Repository proxy does not have clear_feature_check_cache method. "
            f"Flag changes for {flag_name} may not take effect immediately."
        )
