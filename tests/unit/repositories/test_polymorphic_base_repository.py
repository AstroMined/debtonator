"""
Tests for the PolymorphicBaseRepository class.

This module provides tests for the PolymorphicBaseRepository, ensuring proper
handling of polymorphic entities and enforcing correct type identity.
"""

from typing import Any

import pytest
from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.ext.asyncio import AsyncSession

from src.database.base import Base
from src.repositories.polymorphic_base_repository import PolymorphicBaseRepository


# Simple registry mock class for testing
class MockRegistry:
    def __init__(self, models):
        self.models = models

    def get_model_class(self, entity_type):
        return self.models.get(entity_type)


# Test models for polymorphic repository testing
class TestBaseModel(Base):
    __tablename__ = "test_base_models"
    __mapper_args__ = {"polymorphic_on": "model_type", "polymorphic_identity": "base"}

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    model_type = Column(String, nullable=False)


class TestTypeAModel(TestBaseModel):
    __tablename__ = "test_type_a_models"
    __mapper_args__ = {"polymorphic_identity": "type_a"}

    id = Column(Integer, ForeignKey("test_base_models.id"), primary_key=True)
    a_field = Column(String, nullable=True)


class TestTypeBModel(TestBaseModel):
    __tablename__ = "test_type_b_models"
    __mapper_args__ = {"polymorphic_identity": "type_b"}

    id = Column(Integer, ForeignKey("test_base_models.id"), primary_key=True)
    b_field = Column(String, nullable=False)  # Required field


# Test repository class
class TestPolymorphicRepository(PolymorphicBaseRepository[TestBaseModel, int]):
    def __init__(self, session: AsyncSession, registry: Any = None):
        self.discriminator_field = "model_type"
        self.registry = registry
        super().__init__(
            session=session,
            model_class=TestBaseModel,
            discriminator_field="model_type",
            registry=registry,
        )


@pytest.fixture
def mock_registry():
    """Create a mock registry for testing."""
    return MockRegistry({"type_a": TestTypeAModel, "type_b": TestTypeBModel})


@pytest.mark.asyncio
async def test_create_method_disabled(db_session):
    """Test that the create method is disabled and raises NotImplementedError."""
    repo = TestPolymorphicRepository(db_session)

    with pytest.raises(NotImplementedError) as excinfo:
        await repo.create({"name": "Test", "model_type": "type_a"})

    assert "Direct creation through base repository is disabled" in str(excinfo.value)
    assert "Use create_typed_entity()" in str(excinfo.value)


@pytest.mark.asyncio
async def test_update_method_disabled(db_session):
    """Test that the update method is disabled and raises NotImplementedError."""
    repo = TestPolymorphicRepository(db_session)

    with pytest.raises(NotImplementedError) as excinfo:
        await repo.update(1, {"name": "Updated Test"})

    assert "Direct update through base repository is disabled" in str(excinfo.value)
    assert "Use update_typed_entity()" in str(excinfo.value)


@pytest.mark.asyncio
async def test_create_typed_entity_without_registry(db_session):
    """Test that create_typed_entity raises an error when no registry is provided."""
    repo = TestPolymorphicRepository(db_session)

    with pytest.raises(ValueError) as excinfo:
        await repo.create_typed_entity("type_a", {"name": "Test"})

    assert "No registry provided for polymorphic type lookup" in str(excinfo.value)


@pytest.mark.asyncio
async def test_update_typed_entity_without_registry(db_session):
    """Test that update_typed_entity raises an error when no registry is provided."""
    repo = TestPolymorphicRepository(db_session)

    with pytest.raises(ValueError) as excinfo:
        await repo.update_typed_entity(1, "type_a", {"name": "Updated Test"})

    assert "No registry provided for polymorphic type lookup" in str(excinfo.value)


@pytest.mark.asyncio
async def test_create_typed_entity_invalid_type(db_session, mock_registry):
    """Test that create_typed_entity raises an error for invalid entity types."""
    repo = TestPolymorphicRepository(db_session, mock_registry)

    with pytest.raises(ValueError) as excinfo:
        await repo.create_typed_entity("invalid_type", {"name": "Test"})

    assert "No model class registered for entity type 'invalid_type'" in str(
        excinfo.value
    )


@pytest.mark.asyncio
async def test_update_typed_entity_invalid_type(db_session, mock_registry):
    """Test that update_typed_entity raises an error for invalid entity types."""
    repo = TestPolymorphicRepository(db_session, mock_registry)

    with pytest.raises(ValueError) as excinfo:
        await repo.update_typed_entity(1, "invalid_type", {"name": "Updated Test"})

    assert "No model class registered for entity type 'invalid_type'" in str(
        excinfo.value
    )


@pytest.mark.asyncio
async def test_get_valid_fields_for_model(db_session):
    """Test that _get_valid_fields_for_model correctly identifies fields and required fields."""
    # Create a repository instance for testing
    repo = TestPolymorphicRepository(db_session)

    # Test fields for TypeA model
    type_a_fields = repo._get_valid_fields_for_model(TestTypeAModel)
    assert "id" in type_a_fields["all"]
    assert "name" in type_a_fields["all"]
    assert "model_type" in type_a_fields["all"]
    assert "a_field" in type_a_fields["all"]

    # name should be required but a_field should not
    assert "name" in type_a_fields["required"]
    assert "a_field" not in type_a_fields["required"]

    # Test fields for TypeB model
    type_b_fields = repo._get_valid_fields_for_model(TestTypeBModel)
    assert "id" in type_b_fields["all"]
    assert "name" in type_b_fields["all"]
    assert "model_type" in type_b_fields["all"]
    assert "b_field" in type_b_fields["all"]

    # name and b_field should be required
    assert "name" in type_b_fields["required"]
    assert "b_field" in type_b_fields["required"]


@pytest.mark.asyncio
async def test_create_typed_entity_success(db_session, mock_registry):
    """Test successful creation of a typed entity."""
    repo = TestPolymorphicRepository(db_session, mock_registry)

    # Create a type A entity
    entity_data = {"name": "Test Type A", "a_field": "test value"}
    entity = await repo.create_typed_entity("type_a", entity_data)

    # Verify entity was created correctly
    assert entity is not None
    assert entity.id is not None
    assert entity.name == "Test Type A"
    assert entity.model_type == "type_a"  # Discriminator field set correctly
    assert entity.a_field == "test value"
    assert isinstance(entity, TestTypeAModel)  # Correct polymorphic type

    # Verify entity was stored in database
    stored_entity = await repo.get(entity.id)
    assert stored_entity is not None
    assert stored_entity.id == entity.id
    assert stored_entity.name == "Test Type A"
    assert stored_entity.model_type == "type_a"
    assert stored_entity.a_field == "test value"
    assert isinstance(stored_entity, TestTypeAModel)


@pytest.mark.asyncio
async def test_update_typed_entity_success(db_session, mock_registry):
    """Test successful update of a typed entity."""
    repo = TestPolymorphicRepository(db_session, mock_registry)

    # First create an entity
    entity_data = {"name": "Test Type B", "b_field": "required value"}
    entity = await repo.create_typed_entity("type_b", entity_data)

    # Now update it
    update_data = {"name": "Updated Type B", "b_field": "new value"}
    updated_entity = await repo.update_typed_entity(entity.id, "type_b", update_data)

    # Verify entity was updated correctly
    assert updated_entity is not None
    assert updated_entity.id == entity.id
    assert updated_entity.name == "Updated Type B"
    assert updated_entity.model_type == "type_b"  # Discriminator field preserved
    assert updated_entity.b_field == "new value"
    assert isinstance(updated_entity, TestTypeBModel)  # Correct polymorphic type

    # Verify entity was updated in database
    stored_entity = await repo.get(entity.id)
    assert stored_entity is not None
    assert stored_entity.name == "Updated Type B"
    assert stored_entity.b_field == "new value"


@pytest.mark.asyncio
async def test_field_filtering_for_required_fields(db_session, mock_registry):
    """Test that setting required fields to NULL is prevented."""
    repo = TestPolymorphicRepository(db_session, mock_registry)

    # Create a type B entity with a required b_field
    entity_data = {"name": "Test Type B", "b_field": "required value"}
    entity = await repo.create_typed_entity("type_b", entity_data)

    # Try to update and set b_field to NULL
    update_data = {"name": "Updated Type B", "b_field": None}
    updated_entity = await repo.update_typed_entity(entity.id, "type_b", update_data)

    # Verify b_field was not changed to NULL since it's required
    assert updated_entity is not None
    assert updated_entity.name == "Updated Type B"  # Name was updated
    assert (
        updated_entity.b_field == "required value"
    )  # b_field preserved original value


@pytest.mark.asyncio
async def test_update_typed_entity_wrong_type(db_session, mock_registry):
    """Test attempting to update an entity with the wrong type."""
    repo = TestPolymorphicRepository(db_session, mock_registry)

    # Create a type A entity
    entity_data = {"name": "Test Type A", "a_field": "test value"}
    entity = await repo.create_typed_entity("type_a", entity_data)

    # Try to update it with type B
    with pytest.raises(ValueError) as excinfo:
        await repo.update_typed_entity(entity.id, "type_b", {"name": "Updated"})

    assert f"Entity ID {entity.id} is of type type_a, not type_b" in str(excinfo.value)
