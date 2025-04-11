"""
Fixtures for feature flag interceptor tests.

These fixtures provide the necessary components for testing
feature flag enforcement at the service layer boundary.
"""

import asyncio
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.providers.feature_flags import DatabaseConfigProvider
from src.models.feature_flags import FeatureFlag
from src.repositories.feature_flags import FeatureFlagRepository
from src.registry.feature_flags_registry import FeatureFlagRegistry
from src.services.feature_flags import FeatureFlagService
from src.services.interceptors.feature_flag_interceptor import ServiceInterceptor


@pytest_asyncio.fixture
async def interceptor_registry():
    """
    Create a feature flag registry with test flags.
    
    Returns:
        Initialized FeatureFlagRegistry
    """
    registry = FeatureFlagRegistry()
    
    # Register test flags
    registry.register(
        flag_name="TEST_FEATURE_FLAG",
        flag_type="boolean",
        default_value=True,
        description="Test feature flag for service interceptor tests",
    )
    
    registry.register(
        flag_name="ACCOUNT_TYPE_SPECIFIC_FLAG",
        flag_type="boolean",
        default_value=True,
        description="Feature flag for specific account types",
    )
    
    return registry


@pytest_asyncio.fixture
async def interceptor_feature_flag_service(
    interceptor_registry, 
    feature_flag_repository
):
    """
    Create a real feature flag service with real registry and repository.
    
    Args:
        interceptor_registry: Initialized registry
        feature_flag_repository: Initialized repository
        
    Returns:
        Initialized FeatureFlagService
    """
    service = FeatureFlagService(
        registry=interceptor_registry,
        repository=feature_flag_repository,
    )
    
    # Create test flags in database
    await feature_flag_repository.create({
        "name": "TEST_FEATURE_FLAG",
        "flag_type": "boolean",
        "value": True,
        "description": "Test feature flag for service interceptor tests",
        "is_system": False,
        "requirements": {
            "service": {
                "test_method": True
            }
        }
    })
    
    await feature_flag_repository.create({
        "name": "ACCOUNT_TYPE_SPECIFIC_FLAG",
        "flag_type": "boolean",
        "value": True,
        "description": "Feature flag for specific account types",
        "is_system": False,
        "requirements": {
            "service": {
                "test_method_with_account_type": {
                    "ewa": True,
                    "bnpl": True,
                    "checking": False  # Not controlled for checking
                }
            }
        }
    })
    
    return service


@pytest_asyncio.fixture
async def interceptor_config_provider(db_session: AsyncSession, feature_flag_repository):
    """
    Create a real database config provider.
    
    Args:
        db_session: Database session
        feature_flag_repository: Initialized repository
        
    Returns:
        DatabaseConfigProvider instance
    """
    return DatabaseConfigProvider(db_session)


@pytest_asyncio.fixture
async def service_interceptor(
    interceptor_feature_flag_service,
    interceptor_config_provider
):
    """
    Create a service interceptor with real dependencies.
    
    Args:
        interceptor_feature_flag_service: Initialized service
        interceptor_config_provider: Initialized provider
        
    Returns:
        ServiceInterceptor instance
    """
    return ServiceInterceptor(
        feature_flag_service=interceptor_feature_flag_service,
        config_provider=interceptor_config_provider,
        cache_ttl=1  # 1 second TTL for faster testing
    )
