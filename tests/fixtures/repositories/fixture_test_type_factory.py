"""
Fixtures for test type repository factory.

This module provides pytest fixtures for testing the repository factory
using generic test models rather than domain-specific models.
"""

import importlib
import inspect
from typing import Any, Callable, Dict, Optional

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from tests.fixtures.repositories.fixture_polymorphic_test_repositories import (
    TestPolymorphicRepository,
    TestTypeRegistry,
)


class TestRepositoryFactory:
    """
    Test factory for creating repositories with specialized functionality.

    This class implements a simplified version of the repository factory pattern
    for testing purposes, specifically focused on the dynamic module loading and
    function binding capabilities.
    """

    # Cache for loaded repository modules
    _module_cache: Dict[str, Any] = {}

    @classmethod
    async def create_test_repository(
        cls,
        session: AsyncSession,
        entity_type: Optional[str] = None,
        registry: Optional[Any] = None,
    ) -> TestPolymorphicRepository:
        """
        Create a test repository with specialized functionality based on entity type.

        Args:
            session: SQLAlchemy async session
            entity_type: Optional entity type to determine specialized functionality
            registry: Optional registry for polymorphic type lookup

        Returns:
            TestPolymorphicRepository with specialized functionality for the given type
        """
        # Create the base repository
        base_repo = TestPolymorphicRepository(session, registry)

        # If no entity type is specified, return the base repository
        if not entity_type:
            return base_repo

        # Get the module path for the entity type
        module_path = cls._get_module_path(entity_type)
        if not module_path:
            return base_repo

        # Get the specialized module
        module = cls._get_or_load_module(module_path)
        if not module:
            return base_repo

        # Bind specialized functions to the base repository
        cls._bind_module_functions(base_repo, module, session)

        return base_repo

    @classmethod
    def _get_module_path(cls, entity_type: str) -> Optional[str]:
        """
        Get the module path for a given entity type.

        Args:
            entity_type: Entity type identifier

        Returns:
            Module path or None if not found
        """
        # Map entity types to module paths
        type_to_module = {
            "type_a": "tests.helpers.repositories.test_types.type_a",
            "type_b": "tests.helpers.repositories.test_types.type_b",
        }

        return type_to_module.get(entity_type)

    @classmethod
    def _get_or_load_module(cls, module_path: str) -> Optional[Any]:
        """
        Get a cached module or load it if not cached.

        Args:
            module_path: Module path to load

        Returns:
            Loaded module or None if loading fails
        """
        # Return cached module if available
        if module_path in cls._module_cache:
            return cls._module_cache[module_path]

        # Try to import the module
        try:
            module = importlib.import_module(module_path)
            cls._module_cache[module_path] = module
            return module
        except ImportError:
            return None

    @classmethod
    def _bind_module_functions(
        cls,
        repo: TestPolymorphicRepository,
        module: Any,
        session: AsyncSession,
    ) -> None:
        """
        Bind functions from the module to the repository instance.

        Args:
            repo: Repository instance to bind functions to
            module: Module containing functions to bind
            session: SQLAlchemy async session to pass to the bound functions
        """
        # Find all async functions in the module that take a session as first parameter
        for name, func in inspect.getmembers(module, inspect.iscoroutinefunction):
            if name.startswith("_"):
                continue

            # Create a bound method that passes the session to the function
            async def bound_method(*args, _func=func, **kwargs):
                return await _func(session, *args, **kwargs)

            # Set the bound method's name and docstring
            bound_method.__name__ = name
            bound_method.__doc__ = func.__doc__

            # Bind the method to the repository instance
            setattr(repo, name, bound_method)


@pytest_asyncio.fixture
async def test_repository_factory(db_session: AsyncSession, test_type_registry):
    """
    Create a test repository factory function.

    This fixture provides a factory function for creating test repositories with
    specialized functionality based on entity type.

    Args:
        db_session: Database session fixture
        test_type_registry: Registry for test types

    Returns:
        Function: Factory function for creating test repositories
    """

    async def factory(entity_type=None):
        return await TestRepositoryFactory.create_test_repository(
            db_session, entity_type, test_type_registry
        )

    return factory


@pytest_asyncio.fixture
async def test_type_a_entity(polymorphic_test_repository, test_type_registry):
    """
    Create a test Type A entity for repository tests.

    This fixture provides a test entity that can be used in repository factory tests
    to verify that specialized repository functions work correctly with the entity.

    Args:
        polymorphic_test_repository: Test repository fixture
        test_type_registry: Registry for test types

    Returns:
        TestTypeAModel: Test entity with Type A polymorphic identity
    """
    entity = await polymorphic_test_repository.create_typed_entity(
        "type_a",
        {
            "name": "Test Type A Entity",
            "a_field": "Test A Field Value",
        },
    )
    return entity


@pytest_asyncio.fixture
async def test_type_b_entity(polymorphic_test_repository, test_type_registry):
    """
    Create a test Type B entity for repository tests.

    This fixture provides a test entity that can be used in repository factory tests
    to verify that specialized repository functions work correctly with the entity.

    Args:
        polymorphic_test_repository: Test repository fixture
        test_type_registry: Registry for test types

    Returns:
        TestTypeBModel: Test entity with Type B polymorphic identity
    """
    entity = await polymorphic_test_repository.create_typed_entity(
        "type_b",
        {
            "name": "Test Type B Entity",
            "b_field": "Required B Field Value",
        },
    )
    return entity
