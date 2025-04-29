"""
Integration tests for the PolymorphicBaseRepository class.

This module provides tests for the PolymorphicBaseRepository, ensuring proper
handling of polymorphic entities and enforcing correct type identity. It validates
core functionality including:

1. Disabled base CRUD methods to enforce proper polymorphic creation/updates
2. Type-specific entity creation and updates with proper validation
3. Field filtering and required field protection
4. Registry integration for model class lookup
"""

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from tests.fixtures.repositories.fixture_polymorphic_test_repositories import (
    TestPolymorphicRepository,
)
from tests.helpers.models.polymorphic_test_models import TestTypeAModel, TestTypeBModel
from tests.helpers.schema_factories.polymorphic_test_schema_factories import (
    create_test_type_a_schema,
    create_test_type_a_update_schema,
    create_test_type_b_schema,
    create_test_type_b_update_schema,
)

#
# Disabled Base Method Tests
#


@pytest.mark.asyncio
async def test_create_method_disabled(polymorphic_test_repository):
    """
    Test that the base create method is disabled for polymorphic repositories.

    The PolymorphicBaseRepository should raise NotImplementedError when the base
    create method is called, directing users to the create_typed_entity method.
    """
    # 1. ARRANGE: Prepare test data
    test_type_a_schema = create_test_type_a_schema()

    # 2. SCHEMA: Convert schema to dict for repository
    entity_data = test_type_a_schema.model_dump()

    # 3. ACT & 4. ASSERT: Verify the method raises NotImplementedError
    with pytest.raises(NotImplementedError) as excinfo:
        await polymorphic_test_repository.create(entity_data)

    # Verify error message guides users to the correct method
    assert "Direct creation through base repository is disabled" in str(excinfo.value)
    assert "Use create_typed_entity()" in str(excinfo.value)


@pytest.mark.asyncio
async def test_update_method_disabled(polymorphic_test_repository):
    """
    Test that the base update method is disabled for polymorphic repositories.

    The PolymorphicBaseRepository should raise NotImplementedError when the base
    update method is called, directing users to the update_typed_entity method.
    """
    # 1. ARRANGE: Prepare test data
    test_type_a_update_schema = create_test_type_a_update_schema(name="Updated Name")

    # 2. SCHEMA: Convert schema to dict for repository
    update_data = test_type_a_update_schema.model_dump()

    # 3. ACT & 4. ASSERT: Verify the method raises NotImplementedError
    with pytest.raises(NotImplementedError) as excinfo:
        await polymorphic_test_repository.update(1, update_data)

    # Verify error message guides users to the correct method
    assert "Direct update through base repository is disabled" in str(excinfo.value)
    assert "Use update_typed_entity()" in str(excinfo.value)


#
# Registry Validation Tests
#


@pytest.mark.asyncio
async def test_create_typed_entity_without_registry(db_session: AsyncSession):
    """
    Test that create_typed_entity validates registry availability.

    The create_typed_entity method should raise ValueError when no registry
    is provided for polymorphic type lookup.
    """
    # 1. ARRANGE: Create repository without registry
    repo = TestPolymorphicRepository(db_session)

    # 2. SCHEMA: Create schema for test data
    test_type_a_schema = create_test_type_a_schema()

    # 3. ACT & 4. ASSERT: Verify the method raises ValueError
    with pytest.raises(ValueError) as excinfo:
        await repo.create_typed_entity("type_a", test_type_a_schema.model_dump())

    # Verify error message explains the issue
    assert "No registry provided for polymorphic type lookup" in str(excinfo.value)


@pytest.mark.asyncio
async def test_update_typed_entity_without_registry(db_session: AsyncSession):
    """
    Test that update_typed_entity validates registry availability.

    The update_typed_entity method should raise ValueError when no registry
    is provided for polymorphic type lookup.
    """
    # 1. ARRANGE: Create repository without registry
    repo = TestPolymorphicRepository(db_session)

    # 2. SCHEMA: Create schema for test data
    test_type_a_update_schema = create_test_type_a_update_schema(name="Updated Name")

    # 3. ACT & 4. ASSERT: Verify the method raises ValueError
    with pytest.raises(ValueError) as excinfo:
        await repo.update_typed_entity(
            1, "type_a", test_type_a_update_schema.model_dump()
        )

    # Verify error message explains the issue
    assert "No registry provided for polymorphic type lookup" in str(excinfo.value)


@pytest.mark.asyncio
async def test_create_typed_entity_invalid_type(polymorphic_test_repository):
    """
    Test that create_typed_entity validates entity type existence.

    The create_typed_entity method should raise ValueError when an invalid
    entity type is provided.
    """
    # 1. ARRANGE: Prepare test data with invalid type
    test_type_a_schema = create_test_type_a_schema()

    # 2. SCHEMA: Convert schema to dict for repository
    entity_data = test_type_a_schema.model_dump()

    # 3. ACT & 4. ASSERT: Verify the method raises ValueError
    with pytest.raises(ValueError) as excinfo:
        await polymorphic_test_repository.create_typed_entity(
            "invalid_type", entity_data
        )

    # Verify error message explains the issue
    assert "No model class registered for entity type 'invalid_type'" in str(
        excinfo.value
    )


@pytest.mark.asyncio
async def test_update_typed_entity_invalid_type(polymorphic_test_repository):
    """
    Test that update_typed_entity validates entity type existence.

    The update_typed_entity method should raise ValueError when an invalid
    entity type is provided.
    """
    # 1. ARRANGE: Prepare test data with invalid type
    test_type_a_update_schema = create_test_type_a_update_schema(name="Updated Name")

    # 2. SCHEMA: Convert schema to dict for repository
    update_data = test_type_a_update_schema.model_dump()

    # 3. ACT & 4. ASSERT: Verify the method raises ValueError
    with pytest.raises(ValueError) as excinfo:
        await polymorphic_test_repository.update_typed_entity(
            1, "invalid_type", update_data
        )

    # Verify error message explains the issue
    assert "No model class registered for entity type 'invalid_type'" in str(
        excinfo.value
    )


#
# Field Validation Tests
#


@pytest.mark.asyncio
async def test_get_valid_fields_for_model(
    polymorphic_test_repository, test_type_registry
):
    """
    Test that _get_valid_fields_for_model correctly identifies valid fields.

    The _get_valid_fields_for_model method should return dictionaries containing
    all fields and required fields for each model class.
    """
    # 1. ARRANGE - Test classes already available

    # 2. ACT: Get field data for TypeA model
    type_a_fields = polymorphic_test_repository._get_valid_fields_for_model(
        TestTypeAModel
    )

    # 4. ASSERT: Verify correct fields for type_a
    assert "id" in type_a_fields["all"]
    assert "name" in type_a_fields["all"]
    assert "model_type" in type_a_fields["all"]
    assert "a_field" in type_a_fields["all"]

    # Verify required fields
    assert "name" in type_a_fields["required"]
    assert "a_field" not in type_a_fields["required"]

    # 3. ACT: Get field data for TypeB model
    type_b_fields = polymorphic_test_repository._get_valid_fields_for_model(
        TestTypeBModel
    )

    # 4. ASSERT: Verify correct fields for type_b
    assert "id" in type_b_fields["all"]
    assert "name" in type_b_fields["all"]
    assert "model_type" in type_b_fields["all"]
    assert "b_field" in type_b_fields["all"]

    # Verify required fields
    assert "name" in type_b_fields["required"]
    assert "b_field" in type_b_fields["required"]


#
# Create Tests
#


@pytest.mark.asyncio
async def test_create_typed_entity_success(polymorphic_test_repository):
    """
    Test successful creation of a typed entity.

    The create_typed_entity method should properly create an entity of
    the specified type with the correct polymorphic identity.
    """
    # 1. ARRANGE: Prepare test data
    test_type_a_schema = create_test_type_a_schema(
        name="Test Type A Entity", a_field="Test A Field Value"
    )

    # 2. SCHEMA: Convert schema to dict for repository
    entity_data = test_type_a_schema.model_dump()

    # 3. ACT: Create entity through repository
    entity = await polymorphic_test_repository.create_typed_entity(
        "type_a", entity_data
    )

    # 4. ASSERT: Verify entity was created with correct properties
    assert entity is not None
    assert entity.id is not None
    assert entity.name == "Test Type A Entity"
    assert entity.model_type == "type_a"  # Discriminator field set correctly
    assert entity.a_field == "Test A Field Value"
    assert isinstance(entity, TestTypeAModel)  # Correct polymorphic type

    # Verify entity was stored in database by retrieving it
    stored_entity = await polymorphic_test_repository.get(entity.id)
    assert stored_entity is not None
    assert stored_entity.id == entity.id
    assert stored_entity.name == "Test Type A Entity"
    assert stored_entity.model_type == "type_a"
    assert stored_entity.a_field == "Test A Field Value"
    assert isinstance(stored_entity, TestTypeAModel)


@pytest.mark.asyncio
async def test_create_typed_entity_with_required_field(polymorphic_test_repository):
    """
    Test creating a typed entity with a required field.

    The create_typed_entity method should properly handle entities
    with required fields.
    """
    # 1. ARRANGE: Prepare test data with required field
    test_type_b_schema = create_test_type_b_schema(
        name="Test Type B Entity", b_field="Required B Field Value"
    )

    # 2. SCHEMA: Convert schema to dict for repository
    entity_data = test_type_b_schema.model_dump()

    # 3. ACT: Create entity through repository
    entity = await polymorphic_test_repository.create_typed_entity(
        "type_b", entity_data
    )

    # 4. ASSERT: Verify entity was created with correct properties
    assert entity is not None
    assert entity.id is not None
    assert entity.name == "Test Type B Entity"
    assert entity.model_type == "type_b"  # Discriminator field set correctly
    assert entity.b_field == "Required B Field Value"
    assert isinstance(entity, TestTypeBModel)  # Correct polymorphic type


#
# Update Tests
#


@pytest.mark.asyncio
async def test_update_typed_entity_success(polymorphic_test_repository):
    """
    Test successful update of a typed entity.

    The update_typed_entity method should properly update an entity
    while preserving its polymorphic identity.
    """
    # 1. ARRANGE: First create an entity
    create_schema = create_test_type_b_schema(
        name="Test Type B", b_field="Original Value"
    )
    entity = await polymorphic_test_repository.create_typed_entity(
        "type_b", create_schema.model_dump()
    )

    # 2. SCHEMA: Create update schema
    update_schema = create_test_type_b_update_schema(
        name="Updated Type B", b_field="New Value"
    )

    # 3. ACT: Update entity through repository
    updated_entity = await polymorphic_test_repository.update_typed_entity(
        entity.id, "type_b", update_schema.model_dump()
    )

    # 4. ASSERT: Verify entity was updated correctly
    assert updated_entity is not None
    assert updated_entity.id == entity.id
    assert updated_entity.name == "Updated Type B"
    assert updated_entity.model_type == "type_b"  # Discriminator field preserved
    assert updated_entity.b_field == "New Value"
    assert isinstance(updated_entity, TestTypeBModel)  # Correct polymorphic type

    # Verify entity was updated in database
    stored_entity = await polymorphic_test_repository.get(entity.id)
    assert stored_entity is not None
    assert stored_entity.name == "Updated Type B"
    assert stored_entity.b_field == "New Value"


@pytest.mark.asyncio
async def test_field_filtering_for_required_fields(polymorphic_test_repository):
    """
    Test that setting required fields to NULL is prevented.

    The update_typed_entity method should prevent setting required fields
    to NULL by preserving their original values.
    """
    # 1. ARRANGE: First create an entity with a required field
    create_schema = create_test_type_b_schema(
        name="Test Type B", b_field="Required Value"
    )
    entity = await polymorphic_test_repository.create_typed_entity(
        "type_b", create_schema.model_dump()
    )

    # 2. SCHEMA: Create update schema that attempts to set required field to None
    update_schema = create_test_type_b_update_schema(
        name="Updated Type B", b_field=None
    )

    # 3. ACT: Update entity through repository
    updated_entity = await polymorphic_test_repository.update_typed_entity(
        entity.id, "type_b", update_schema.model_dump()
    )

    # 4. ASSERT: Verify required field was preserved
    assert updated_entity is not None
    assert updated_entity.name == "Updated Type B"  # Name was updated
    assert (
        updated_entity.b_field == "Required Value"
    )  # b_field preserved original value


@pytest.mark.asyncio
async def test_update_typed_entity_wrong_type(polymorphic_test_repository):
    """
    Test that updating an entity with the wrong type is prevented.

    The update_typed_entity method should validate that the entity being
    updated matches the specified polymorphic type.
    """
    # 1. ARRANGE: First create a Type A entity
    create_schema = create_test_type_a_schema(name="Test Type A", a_field="Test Value")
    entity = await polymorphic_test_repository.create_typed_entity(
        "type_a", create_schema.model_dump()
    )

    # 2. SCHEMA: Create update schema for wrong type
    update_schema = create_test_type_b_update_schema(name="Updated Name")

    # 3. ACT & 4. ASSERT: Verify the method raises ValueError
    with pytest.raises(ValueError) as excinfo:
        await polymorphic_test_repository.update_typed_entity(
            entity.id, "type_b", update_schema.model_dump()
        )

    # Verify error message explains the type mismatch
    assert f"Entity ID {entity.id} is of type type_a, not type_b" in str(excinfo.value)


@pytest.mark.asyncio
async def test_partial_update_preserves_fields(polymorphic_test_repository):
    """
    Test that partial updates only modify specified fields.

    The update_typed_entity method should only update the fields specified
    in the update data, preserving all other fields.
    """
    # 1. ARRANGE: Create entity with all fields set
    create_schema = create_test_type_a_schema(
        name="Original Name", a_field="Original A Field"
    )
    entity = await polymorphic_test_repository.create_typed_entity(
        "type_a", create_schema.model_dump()
    )

    # 2. SCHEMA: Create partial update with only name field
    update_schema = create_test_type_a_update_schema(
        name="Updated Name"
        # a_field not included
    )

    # 3. ACT: Update entity through repository
    updated_entity = await polymorphic_test_repository.update_typed_entity(
        entity.id, "type_a", update_schema.model_dump()
    )

    # 4. ASSERT: Verify only specified fields were updated
    assert updated_entity is not None
    assert updated_entity.name == "Updated Name"  # This field was updated
    assert updated_entity.a_field == "Original A Field"  # This field was preserved
