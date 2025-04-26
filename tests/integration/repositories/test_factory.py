"""
Integration tests for the repository factory with dynamic module loading.

This module tests the core functionality of repository factories with a focus on:
1. Dynamic module loading
2. Function binding to repository instances
3. Session propagation
4. Fallback behavior for unknown types

Rather than using domain-specific account types, these tests use generic test models
to ensure the tests focus on factory functionality rather than domain-specific behavior.
Following the "Real Objects Testing Philosophy" with no mocks.
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.helpers.models.polymorphic_test_models import TestTypeAModel, TestTypeBModel
from tests.helpers.schema_factories.polymorphic_test_schema_factories import (
    create_test_type_a_schema,
    create_test_type_b_schema,
)

pytestmark = pytest.mark.asyncio


#
# Core Factory Functionality Tests
#


@pytest.mark.asyncio
async def test_create_repository_with_type(
    test_repository_factory,
):
    """
    Test creating repository for specific entity types.

    This test verifies that a repository factory correctly creates specialized
    repositories for different entity types with dynamically bound type-specific
    methods.

    Args:
        test_repository_factory: Repository factory fixture for test entities
    """
    # 1. ARRANGE: Repository factory is provided by fixture

    # 2. SCHEMA: Not applicable for this test

    # 3. ACT: Create repositories for different entity types
    type_a_repo = await test_repository_factory(entity_type="type_a")
    type_b_repo = await test_repository_factory(entity_type="type_b")

    # 4. ASSERT: Verify the repositories were created with type-specific methods
    assert type_a_repo is not None
    assert type_b_repo is not None

    # Verify type-specific methods are bound
    assert hasattr(type_a_repo, "get_type_a_entities_with_field_value")
    assert hasattr(type_a_repo, "count_type_a_entities")
    assert hasattr(type_b_repo, "get_type_b_entities_with_required_field")
    assert hasattr(type_b_repo, "find_type_b_by_name_pattern")


@pytest.mark.asyncio
async def test_dynamic_method_binding_type_a(
    test_repository_factory, test_type_a_entity
):
    """
    Test that dynamically bound methods work correctly for Type A.

    This test verifies that methods dynamically bound to repositories
    by the factory work correctly when called.

    Args:
        test_repository_factory: Repository factory fixture
        test_type_a_entity: Test entity fixture
    """
    # 1. ARRANGE: Repository factory and test entity are provided by fixtures

    # 2. SCHEMA: Not applicable for this test

    # 3. ACT: Create repository and use dynamically bound methods
    repo = await test_repository_factory(entity_type="type_a")

    # Count entities
    count = await repo.count_type_a_entities()

    # Get entities with specific field value
    entities = await repo.get_type_a_entities_with_field_value(
        field_value="Test A Field Value"
    )

    # 4. ASSERT: Verify the methods work correctly
    assert count >= 1
    assert len(entities) >= 1
    assert test_type_a_entity.id in [e.id for e in entities]
    assert all(isinstance(e, TestTypeAModel) for e in entities)
    assert all(e.a_field == "Test A Field Value" for e in entities)


@pytest.mark.asyncio
async def test_dynamic_method_binding_type_b(
    test_repository_factory, test_type_b_entity
):
    """
    Test that dynamically bound methods work correctly for Type B.

    This test verifies that methods dynamically bound to repositories
    by the factory work correctly when called.

    Args:
        test_repository_factory: Repository factory fixture
        test_type_b_entity: Test entity fixture
    """
    # 1. ARRANGE: Repository factory and test entity are provided by fixtures

    # 2. SCHEMA: Not applicable for this test

    # 3. ACT: Create repository and use dynamically bound methods
    repo = await test_repository_factory(entity_type="type_b")

    # Get entities with required field
    entities = await repo.get_type_b_entities_with_required_field(
        field_value="Required B Field Value"
    )

    # Find entities by name pattern
    entities_by_name = await repo.find_type_b_by_name_pattern(
        name_pattern="Test Type B"
    )

    # 4. ASSERT: Verify the methods work correctly
    assert len(entities) >= 1
    assert test_type_b_entity.id in [e.id for e in entities]
    assert all(isinstance(e, TestTypeBModel) for e in entities)
    assert all(e.b_field == "Required B Field Value" for e in entities)

    assert len(entities_by_name) >= 1
    assert test_type_b_entity.id in [e.id for e in entities_by_name]


@pytest.mark.asyncio
async def test_fallback_behavior_for_unknown_type(
    test_repository_factory,
):
    """
    Test graceful fallback when module not found.

    This test verifies that a repository factory gracefully falls back to
    the base repository when a module for an unknown entity type is not found.

    Args:
        test_repository_factory: Repository factory fixture
    """
    # 1. ARRANGE: Repository factory is provided by fixture

    # 2. SCHEMA: Not applicable for this test

    # 3. ACT: Create repository for unknown entity type
    repo = await test_repository_factory(entity_type="unknown_type")

    # 4. ASSERT: Verify fallback behavior
    assert repo is not None
    # Should fall back to base repository without specialized methods
    assert not hasattr(repo, "get_type_a_entities_with_field_value")
    assert not hasattr(repo, "count_type_a_entities")
    assert not hasattr(repo, "get_type_b_entities_with_required_field")
    assert not hasattr(repo, "find_type_b_by_name_pattern")


@pytest.mark.asyncio
async def test_session_propagation(test_repository_factory, db_session: AsyncSession):
    """
    Test that session is properly propagated to created repositories.

    This test verifies that the database session is properly propagated
    to repositories created by the factory.

    Args:
        test_repository_factory: Repository factory fixture
        db_session: Database session fixture
    """
    # 1. ARRANGE: Repository factory and database session are provided by fixtures

    # 2. SCHEMA: Create and validate through schema factory
    entity_data = create_test_type_a_schema(
        name="Session Test Entity",
        a_field="Session Test Value",
    )

    # 3. ACT: Create repository and perform database operations
    repo = await test_repository_factory(entity_type="type_a")

    # 4. ASSERT: Verify session propagation
    assert repo.session is db_session

    # Test that operations using the session work
    entity = await repo.create_typed_entity("type_a", entity_data.model_dump())

    # Use the repository to fetch the entity
    fetched = await repo.get(entity.id)
    assert fetched is not None
    assert fetched.id == entity.id
    assert fetched.name == "Session Test Entity"
    assert fetched.a_field == "Session Test Value"


@pytest.mark.asyncio
async def test_no_type_repository_creation(
    test_repository_factory,
):
    """
    Test creating a repository without specifying an entity type.

    This test verifies that a repository factory correctly creates
    a basic repository when no entity type is specified.

    Args:
        test_repository_factory: Repository factory fixture
    """
    # 1. ARRANGE: Repository factory is provided by fixture

    # 2. SCHEMA: Not applicable for this test

    # 3. ACT: Create repository without specifying an entity type
    repo = await test_repository_factory()

    # 4. ASSERT: Verify the repository was created
    assert repo is not None

    # Should not have specialized methods
    assert not hasattr(repo, "get_type_a_entities_with_field_value")
    assert not hasattr(repo, "count_type_a_entities")
    assert not hasattr(repo, "get_type_b_entities_with_required_field")
    assert not hasattr(repo, "find_type_b_by_name_pattern")


#
# Polymorphic Entity Creation Tests
#


@pytest.mark.asyncio
async def test_create_typed_entity_through_factory(
    test_repository_factory,
):
    """
    Test creating a typed entity through a factory-created repository.

    This test verifies that a repository created by a factory can properly
    create polymorphic entities with the correct type.

    Args:
        test_repository_factory: Repository factory fixture
    """
    # 1. ARRANGE: Repository factory is provided by fixture

    # 2. SCHEMA: Create and validate through schema factory
    entity_data = create_test_type_b_schema(
        name="Factory Created Entity",
        b_field="Factory Test Value",
    )

    # 3. ACT: Create repository and use it to create an entity
    repo = await test_repository_factory(entity_type="type_b")
    entity = await repo.create_typed_entity("type_b", entity_data.model_dump())

    # 4. ASSERT: Verify the entity was created with correct type
    assert entity is not None
    assert entity.id is not None
    assert entity.name == "Factory Created Entity"
    assert entity.b_field == "Factory Test Value"
    assert entity.model_type == "type_b"
    assert isinstance(entity, TestTypeBModel)

    # Verify entity was stored properly
    stored = await repo.get(entity.id)
    assert stored is not None
    assert stored.id == entity.id
    assert stored.name == "Factory Created Entity"
    assert stored.model_type == "type_b"


@pytest.mark.asyncio
async def test_update_typed_entity_through_factory(
    test_repository_factory,
):
    """
    Test updating a typed entity through a factory-created repository.

    This test verifies that a repository created by a factory can properly
    update polymorphic entities with the correct type.

    Args:
        test_repository_factory: Repository factory fixture
    """
    # 1. ARRANGE: Create repository and entity
    repo = await test_repository_factory(entity_type="type_a")

    # 2. SCHEMA: Create entity and update schemas
    create_data = create_test_type_a_schema(
        name="Original Name",
        a_field="Original Value",
    )

    # Create entity to update
    entity = await repo.create_typed_entity("type_a", create_data.model_dump())

    # 3. ACT: Update the entity
    updated = await repo.update_typed_entity(
        entity.id,
        "type_a",
        {
            "name": "Updated Name",
            "a_field": "Updated Value",
        },
    )

    # 4. ASSERT: Verify the entity was updated correctly
    assert updated is not None
    assert updated.id == entity.id
    assert updated.name == "Updated Name"
    assert updated.a_field == "Updated Value"
    assert updated.model_type == "type_a"

    # Verify entity was updated in database
    stored = await repo.get(entity.id)
    assert stored is not None
    assert stored.name == "Updated Name"
    assert stored.a_field == "Updated Value"


@pytest.mark.asyncio
async def test_combining_repository_and_type_specific_functions(
    test_repository_factory, test_type_b_entity
):
    """
    Test using both repository base methods and type-specific functions.

    This test verifies that repositories created by the factory correctly
    combine base repository methods with dynamically bound type-specific methods.

    Args:
        test_repository_factory: Repository factory fixture
        test_type_b_entity: Test entity fixture
    """
    # 1. ARRANGE: Repository factory and test entity provided by fixtures

    # 2. SCHEMA: Create data for a new entity
    create_data = create_test_type_b_schema(
        name="Combined Test Entity",
        b_field="Combined Test Value",
    )

    # 3. ACT: Create repository and use both base and specific methods
    repo = await test_repository_factory(entity_type="type_b")

    # Use base repository method to create entity
    entity = await repo.create_typed_entity("type_b", create_data.model_dump())

    # Use type-specific method to find entities
    entities_by_name = await repo.find_type_b_by_name_pattern("Combined")

    # Use base repository method to delete entity
    deleted = await repo.delete(entity.id)

    # 4. ASSERT: Verify both sets of methods work correctly
    assert entity.id is not None
    assert entity.name == "Combined Test Entity"

    assert len(entities_by_name) >= 1
    assert entity.id in [e.id for e in entities_by_name]

    assert deleted is True
    assert await repo.get(entity.id) is None
