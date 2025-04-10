"""
Fixtures for feature flag repository proxy tests.

This module provides fixtures for testing the FeatureFlagRepositoryProxy,
including test repositories, feature flag services, and config providers.
"""

import pytest
from typing import Dict, List, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.providers.feature_flags import (
    ConfigProvider,
    DatabaseConfigProvider,
    InMemoryConfigProvider,
)
from src.registry.feature_flags_registry import FeatureFlagRegistry
from src.repositories.feature_flags import FeatureFlagRepository
from src.repositories.proxies.feature_flag_proxy import FeatureFlagRepositoryProxy
from src.schemas.feature_flags import FeatureFlagType
from src.services.feature_flags import FeatureFlagService


class TestRepository:
    """Test repository class with methods for proxy testing."""

    def __init__(self, name: str = "test"):
        """Initialize with a name for identification."""
        self.name = name
        self.non_method_attr = "test_attribute"

    async def test_method(self, account_type: Optional[str] = None) -> str:
        """Test method that returns account type."""
        return f"Test method called with {account_type}"

    async def get_by_id(self, id: int) -> Dict[str, Any]:
        """Get entity by ID."""
        return {"id": id, "name": f"Test Entity {id}"}

    async def get_by_type(self, account_type: str) -> Dict[str, Any]:
        """Get entity by account type."""
        return {"type": account_type, "name": f"Test {account_type}"}

    async def create(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create a new entity."""
        return {"id": 1, **data}

    async def update(self, id: int, data: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing entity."""
        return {"id": id, **data}

    async def delete(self, id: int) -> bool:
        """Delete an entity."""
        return True


class TypedTestRepository(TestRepository):
    """Test repository with account type in the class name."""

    def __init__(self, account_type: str):
        """Initialize with an account type."""
        super().__init__(f"{account_type}_repository")
        self.account_type = account_type

    async def type_specific_method(self) -> str:
        """Type-specific method that returns the account type."""
        return f"Type-specific method for {self.account_type}"


@pytest.fixture
def feature_flag_registry():
    """
    Provide a feature flag registry for testing.

    Returns:
        FeatureFlagRegistry: An initialized registry
    """
    return FeatureFlagRegistry()


@pytest.fixture
def feature_flag_repository(db_session):
    """
    Provide a feature flag repository for testing.

    Args:
        db_session: SQLAlchemy async session

    Returns:
        FeatureFlagRepository: A repository instance
    """
    return FeatureFlagRepository(db_session)


@pytest.fixture
async def feature_flag_service(feature_flag_registry, feature_flag_repository):
    """
    Provide a feature flag service for testing.

    Args:
        feature_flag_registry: Feature flag registry fixture
        feature_flag_repository: Feature flag repository fixture

    Returns:
        FeatureFlagService: A configured service instance
    """
    service = FeatureFlagService(feature_flag_registry, feature_flag_repository)
    
    # Configure test flags
    await service.create_flag({
        "name": "TEST_FEATURE",
        "flag_type": FeatureFlagType.BOOLEAN, 
        "value": True,
        "description": "Test feature for proxy tests",
        "requirements": {
            "repository": {
                "test_method": ["test_account_type"],
                "get_by_id": ["*"],  # Wildcard for all account types
                "get_by_type": ["specific_type"],
            }
        }
    })
    
    # Banking account types feature
    await service.create_flag({
        "name": "BANKING_ACCOUNT_TYPES_ENABLED",
        "flag_type": FeatureFlagType.BOOLEAN, 
        "value": True,
        "description": "Enable banking account types",
        "requirements": {
            "repository": {
                "create": ["bnpl", "ewa", "payment_app"],
                "update": ["bnpl", "ewa", "payment_app"],
                "get_by_type": ["bnpl", "ewa", "payment_app"],
            }
        }
    })
    
    return service


@pytest.fixture
def test_repository():
    """
    Provide a test repository that implements common methods.

    Returns:
        TestRepository: A repository instance for testing
    """
    return TestRepository()


@pytest.fixture
def typed_test_repository():
    """
    Provide a test repository with account type in the class name.

    Returns:
        TypedTestRepository: A repository instance for testing
    """
    return TypedTestRepository("bnpl")


@pytest.fixture
def config_provider(db_session, feature_flag_repository):
    """
    Provide a database config provider for testing.

    Args:
        db_session: SQLAlchemy async session
        feature_flag_repository: Feature flag repository fixture

    Returns:
        DatabaseConfigProvider: A configured provider
    """
    return DatabaseConfigProvider(db_session)


@pytest.fixture
def in_memory_config_provider():
    """
    Provide an in-memory config provider for testing.

    Returns:
        InMemoryConfigProvider: A provider with test requirements
    """
    test_requirements = {
        "TEST_FEATURE": {
            "repository": {
                "test_method": ["test_account_type"],
                "get_by_id": ["*"]
            }
        },
        "BANKING_ACCOUNT_TYPES_ENABLED": {
            "repository": {
                "create": ["bnpl", "ewa", "payment_app"],
                "update": ["bnpl", "ewa", "payment_app"],
                "get_by_type": ["bnpl", "ewa", "payment_app"],
            }
        }
    }
    return InMemoryConfigProvider(test_requirements)


@pytest.fixture
def feature_flag_proxy(test_repository, feature_flag_service, config_provider):
    """
    Provide a feature flag repository proxy for testing.

    Args:
        test_repository: Test repository fixture
        feature_flag_service: Feature flag service fixture
        config_provider: Config provider fixture

    Returns:
        FeatureFlagRepositoryProxy: A configured proxy instance
    """
    return FeatureFlagRepositoryProxy(
        repository=test_repository,
        feature_flag_service=feature_flag_service,
        config_provider=config_provider
    )


@pytest.fixture
def typed_feature_flag_proxy(typed_test_repository, feature_flag_service, config_provider):
    """
    Provide a feature flag repository proxy for a typed repository.

    Args:
        typed_test_repository: Typed test repository fixture
        feature_flag_service: Feature flag service fixture
        config_provider: Config provider fixture

    Returns:
        FeatureFlagRepositoryProxy: A configured proxy instance
    """
    return FeatureFlagRepositoryProxy(
        repository=typed_test_repository,
        feature_flag_service=feature_flag_service,
        config_provider=config_provider
    )


@pytest.fixture
def memory_config_proxy(test_repository, feature_flag_service, in_memory_config_provider):
    """
    Provide a feature flag repository proxy with in-memory config provider.

    Args:
        test_repository: Test repository fixture
        feature_flag_service: Feature flag service fixture
        in_memory_config_provider: In-memory config provider fixture

    Returns:
        FeatureFlagRepositoryProxy: A configured proxy instance
    """
    return FeatureFlagRepositoryProxy(
        repository=test_repository,
        feature_flag_service=feature_flag_service,
        config_provider=in_memory_config_provider
    )
