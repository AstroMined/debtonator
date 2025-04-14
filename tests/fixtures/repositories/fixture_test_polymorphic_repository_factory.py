"""
Fixtures for test polymorphic repository factory.

This module provides pytest fixtures for working with test repositories
that follow the polymorphic pattern, specifically designed for testing
the repository factory's ability to load type-specific modules.
"""

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.factory import RepositoryFactory
from tests.helpers.models.polymorphic_test_models import TestBaseModel
from tests.fixtures.repositories.fixture_polymorphic_test_repositories import (
    TestPolymorphicRepository,
    TestTypeRegistry,
)


@pytest_asyncio.fixture
async def test_polymorphic_repository_factory(db_session: AsyncSession, test_type_registry):
    """
    Create a repository factory for polymorphic test repositories.

    This fixture provides a factory function that creates repositories for
    different test entity types, simulating how the real RepositoryFactory works
    with account types but using generic test models instead.

    Args:
        db_session: Database session fixture
        test_type_registry: Registry for test types

    Returns:
        Function: Factory function for creating test repositories
    """
    async def factory(entity_type=None):
        # Create the base repository
        base_repo = TestPolymorphicRepository(db_session)
        base_repo.registry = test_type_registry
        
        # Return the base repository if no entity type specified
        if not entity_type:
            return base_repo
            
        return base_repo
        
    return factory
