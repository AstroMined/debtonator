"""
Fixtures for polymorphic repository testing.

This module provides fixtures for testing the polymorphic repository pattern,
including test models, registry, and repository instances.
"""

from typing import Any, Dict, Type

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.polymorphic_base_repository import PolymorphicBaseRepository
from tests.helpers.models.polymorphic_test_models import (
    TestBaseModel,
    TestTypeAModel,
    TestTypeBModel,
)


class TestTypeRegistry:
    """
    Test registry for polymorphic type lookup.
    
    This registry maps entity types to their model classes for use in
    polymorphic repository operations.
    """

    def __init__(self, models: Dict[str, Type]):
        """
        Initialize registry with model type mappings.
        
        Args:
            models: Dictionary mapping type names to model classes
        """
        self.models = models

    def get_model_class(self, entity_type: str) -> Type:
        """
        Get model class for specified entity type.
        
        Args:
            entity_type: The polymorphic type identifier
            
        Returns:
            The model class for the specified type
        """
        return self.models.get(entity_type)


class TestPolymorphicRepository(PolymorphicBaseRepository[TestBaseModel, int]):
    """
    Test repository for polymorphic entity operations.
    
    This repository implements the polymorphic repository pattern for
    test models to verify proper polymorphic entity handling.
    """

    def __init__(self, session: AsyncSession, registry: Any = None):
        """
        Initialize repository with session and registry.
        
        Args:
            session: The database session to use
            registry: Optional registry for model class lookup
        """
        self.discriminator_field = "model_type"
        self.registry = registry
        super().__init__(
            session=session,
            model_class=TestBaseModel,
            discriminator_field="model_type",
            registry=registry,
        )


@pytest_asyncio.fixture
async def test_type_registry():
    """
    Create a test type registry for polymorphic model lookup.
    
    This fixture provides a registry with mappings between type identifiers
    and model classes for use in polymorphic repository operations.
    
    Returns:
        A test registry instance with mappings for TestTypeAModel and TestTypeBModel
    """
    return TestTypeRegistry({"type_a": TestTypeAModel, "type_b": TestTypeBModel})


@pytest_asyncio.fixture
async def polymorphic_test_repository(db_session: AsyncSession, test_type_registry):
    """
    Create a polymorphic test repository instance.
    
    This fixture provides a real PolymorphicBaseRepository implementation
    connected to the test database session for integration testing without mocks.
    
    Args:
        db_session: Test database session
        test_type_registry: Registry for test model type lookup
        
    Returns:
        A TestPolymorphicRepository instance connected to the test database
    """
    repository = TestPolymorphicRepository(db_session, test_type_registry)
    return repository
