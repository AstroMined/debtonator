"""
Fixtures for feature flag proxy tests.

These fixtures provide the necessary components for testing
feature flag enforcement at the service layer using proxies.
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
from src.services.proxies.feature_flag_proxy import ServiceProxy


# Create a simple test service class with methods to wrap
class TestService:
    """Simple service class for testing the proxy."""
    
    def __init__(self, name="TestService"):
        self.name = name
        self.method_calls = {}
    
    async def async_method(self, param1=None, param2=None):
        """Sample async method to test proxy wrapping."""
        # Record that this method was called
        self.method_calls["async_method"] = (param1, param2)
        return f"Async method called: {param1}, {param2}"
    
    async def account_type_method(self, account_type, data=None):
        """Method with account_type parameter for testing account-specific flags."""
        # Record that this method was called
        self.method_calls["account_type_method"] = (account_type, data)
        return f"Account type method called: {account_type}"
    
    def sync_method(self, param1=None, param2=None):
        """Sample sync method to test proxy handling of non-async methods."""
        # Record that this method was called
        self.method_calls["sync_method"] = (param1, param2)
        return f"Sync method called: {param1}, {param2}"
    
    @property
    def read_only_property(self):
        """Property to test that proxy passes through non-method attributes."""
        return "property_value"


@pytest_asyncio.fixture
async def proxy_registry():
    """
    Create a feature flag registry with test flags for proxy testing.
    
    Returns:
        Initialized FeatureFlagRegistry
    """
    registry = FeatureFlagRegistry()
    
    # Register test flags
    registry.register(
        flag_name="TEST_FEATURE_FLAG",
        flag_type="boolean",
        default_value=True,
        description="Test feature flag for service proxy tests",
    )
    
    registry.register(
        flag_name="ACCOUNT_TYPE_SPECIFIC_FLAG",
        flag_type="boolean",
        default_value=True,
        description="Feature flag for specific account types",
    )
    
    return registry


@pytest_asyncio.fixture
async def proxy_feature_flag_service(
    proxy_registry, 
    feature_flag_repository
):
    """
    Create a real feature flag service with real registry and repository.
    
    Args:
        proxy_registry: Initialized registry
        feature_flag_repository: Initialized repository
        
    Returns:
        Initialized FeatureFlagService
    """
    service = FeatureFlagService(
        registry=proxy_registry,
        repository=feature_flag_repository,
    )
    
    # Create test flags in database
    await feature_flag_repository.create({
        "name": "TEST_FEATURE_FLAG",
        "flag_type": "boolean",
        "value": True,
        "description": "Test feature flag for service proxy tests",
        "is_system": False,
        "requirements": {
            "service": {
                "async_method": True,
                "sync_method": True,
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
                "account_type_method": {
                    "ewa": True,
                    "bnpl": True,
                    "checking": False  # Not controlled for checking
                }
            }
        }
    })
    
    return service


@pytest_asyncio.fixture
async def proxy_config_provider(db_session: AsyncSession, feature_flag_repository):
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
async def test_service():
    """
    Create a test service to wrap with the proxy.
    
    Returns:
        TestService instance
    """
    return TestService()


@pytest_asyncio.fixture
async def proxied_service(
    test_service,
    proxy_feature_flag_service,
    proxy_config_provider
):
    """
    Create a proxied test service.
    
    Args:
        test_service: Service to proxy
        proxy_feature_flag_service: Feature flag service
        proxy_config_provider: Config provider
        
    Returns:
        ServiceProxy wrapping the test service
    """
    return ServiceProxy(
        service=test_service,
        feature_flag_service=proxy_feature_flag_service,
        config_provider=proxy_config_provider,
    )
