"""
Fixtures for service factory tests.

These fixtures provide the necessary components for testing
service factory integration with feature flags.
"""

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.providers.feature_flags import DatabaseConfigProvider
from src.repositories.feature_flags import FeatureFlagRepository
from src.registry.feature_flags_registry import FeatureFlagRegistry
from src.services.feature_flags import FeatureFlagService
from src.services.factory import ServiceFactory


@pytest_asyncio.fixture
async def factory_registry():
    """Create a feature flag registry with test flags for factory tests."""
    registry = FeatureFlagRegistry()
    
    # Register test flags
    registry.register(
        flag_name="BANKING_ACCOUNT_TYPES_ENABLED",
        flag_type="boolean",
        default_value=True,
        description="Banking account types flag",
    )
    
    return registry


@pytest_asyncio.fixture
async def factory_feature_flag_service(
    factory_registry, 
    feature_flag_repository
):
    """Create a real feature flag service with real registry and repository."""
    service = FeatureFlagService(
        registry=factory_registry,
        repository=feature_flag_repository,
    )
    
    # Create test flags in database
    await feature_flag_repository.create({
        "name": "BANKING_ACCOUNT_TYPES_ENABLED",
        "flag_type": "boolean",
        "value": True,
        "description": "Banking account types flag",
        "is_system": False,
        "requirements": {
            "service": {
                "create_account": {
                    "ewa": True,
                    "bnpl": True,
                    "payment_app": True,
                }
            }
        }
    })
    
    return service
