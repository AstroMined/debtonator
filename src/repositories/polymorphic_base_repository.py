"""
Polymorphic Base Repository

This module contains the PolymorphicBaseRepository class, which provides a specialized
base repository for polymorphic entities. This repository extends the BaseRepository
with specialized handling for polymorphic entities, ensuring proper type handling and
identity management. It enforces the use of concrete subclasses rather than base classes.

For more details on this pattern, see ADR-016.
"""

from typing import Any, ClassVar, Dict, Optional, Set, Type, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import with_polymorphic

from src.repositories.base_repository import BaseRepository

# Type variables for the polymorphic model and primary key types
PolyModelType = TypeVar("PolyModelType")
PKType = TypeVar("PKType")


class PolymorphicBaseRepository(BaseRepository[PolyModelType, PKType]):
    """
    Base repository for polymorphic entities.

    This repository extends the BaseRepository with specialized handling for
    polymorphic entities, ensuring proper type handling and identity management.
    It enforces the use of concrete subclasses rather than the base class.

    Class Attributes:
        discriminator_field: The field name used as the discriminator for polymorphic identity
        registry: The registry to use for model class lookup

    Attributes:
        session: The database session to use for operations
        model_class: The base model class for this repository
    """

    # Class variable to store the discriminator field name
    discriminator_field: ClassVar[str] = "type"

    # Registry to use for model class lookup
    registry = None

    def __init__(
        self,
        session: AsyncSession,
        model_class: Type[PolyModelType],
        discriminator_field: str = None,
        registry: Any = None,
    ):
        """
        Initialize repository with session, model class, and polymorphic configuration.

        Args:
            session: The database session to use
            model_class: The base model class for this repository
            discriminator_field: Optional override for the discriminator field name
            registry: Optional registry for model class lookup
        """
        super().__init__(session, model_class)

        if discriminator_field:
            self.discriminator_field = discriminator_field

        if registry:
            self.registry = registry

    def _needs_polymorphic_loading(self) -> bool:
        """
        Override to always enable polymorphic loading.

        Returns:
            bool: Always True for polymorphic repositories
        """
        return True

    async def create(self, obj_in: Dict[str, Any]) -> PolyModelType:
        """
        Create method is disabled for polymorphic base repository.

        This method is intentionally disabled to prevent creating instances
        with incorrect polymorphic identity. Use create_typed_entity instead.

        Args:
            obj_in: The data for the new entity

        Raises:
            NotImplementedError: Always raised to prevent direct creation
        """
        raise NotImplementedError(
            "Direct creation through base repository is disabled for polymorphic entities. "
            "Use create_typed_entity() instead to ensure proper polymorphic identity."
        )

    async def update(
        self, id: PKType, obj_in: Dict[str, Any]
    ) -> Optional[PolyModelType]:
        """
        Update method is disabled for polymorphic base repository.

        This method is intentionally disabled to prevent updating instances
        with incorrect polymorphic identity. Use update_typed_entity instead.

        Args:
            id: The ID of the entity to update
            obj_in: The data to update with

        Raises:
            NotImplementedError: Always raised to prevent direct updates
        """
        raise NotImplementedError(
            "Direct update through base repository is disabled for polymorphic entities. "
            "Use update_typed_entity() instead to ensure proper polymorphic identity."
        )

    async def create_typed_entity(
        self, entity_type: str, data: Dict[str, Any], registry: Any = None
    ) -> PolyModelType:
        """
        Create a new entity with the specified polymorphic type.

        Args:
            entity_type: The polymorphic identity for the new entity
            data: The data for the new entity
            registry: Optional registry for model class lookup, overrides the class registry

        Returns:
            The created entity with polymorphic identity loaded

        Raises:
            ValueError: If no registry is provided or no model class is found
        """
        # Use provided registry or fall back to class registry
        registry_to_use = registry or self.registry

        if not registry_to_use:
            raise ValueError(
                "No registry provided for polymorphic type lookup. "
                "Either provide a registry or set the class registry."
            )

        # Get model class from registry
        model_class = registry_to_use.get_model_class(entity_type)

        if not model_class:
            raise ValueError(
                f"No model class registered for entity type '{entity_type}'"
            )

        # Ensure discriminator field is set correctly
        data_copy = data.copy()
        data_copy[self.discriminator_field] = entity_type

        # Filter data to include only valid fields for this model class
        valid_fields = self._get_valid_fields_for_model(model_class)
        filtered_data = {
            k: v
            for k, v in data_copy.items()
            if k in valid_fields.get("all", set()) or k == self.discriminator_field
        }

        # Create instance with filtered data
        db_obj = model_class(**filtered_data)
        self.session.add(db_obj)

        # Flush to get an ID
        await self.session.flush()

        # Get ID for later query
        created_id = db_obj.id

        # Detach the object to ensure we get a fresh instance
        self.session.expunge(db_obj)

        # Query using the specific model class
        stmt = select(model_class).where(model_class.id == created_id)
        result = await self.session.execute(stmt)
        typed_entity = result.scalars().first()

        return typed_entity

    async def update_typed_entity(
        self, id: PKType, entity_type: str, data: Dict[str, Any], registry: Any = None
    ) -> Optional[PolyModelType]:
        """
        Update an entity with the specified polymorphic type.

        Args:
            id: The ID of the entity to update
            entity_type: The polymorphic identity of the entity
            data: The data to update with
            registry: Optional registry for model class lookup, overrides the class registry

        Returns:
            The updated entity with polymorphic identity loaded, or None if not found

        Raises:
            ValueError: If no registry is provided, no model class is found, or types don't match
        """
        # Use provided registry or fall back to class registry
        registry_to_use = registry or self.registry

        if not registry_to_use:
            raise ValueError(
                "No registry provided for polymorphic type lookup. "
                "Either provide a registry or set the class registry."
            )

        # Get model class from registry
        model_class = registry_to_use.get_model_class(entity_type)

        if not model_class:
            raise ValueError(
                f"No model class registered for entity type '{entity_type}'"
            )

        # Get the entity using polymorphic loading
        poly_entity = with_polymorphic(self.model_class, "*")
        result = await self.session.execute(
            select(poly_entity).where(poly_entity.id == id)
        )
        entity = result.scalars().first()

        if not entity:
            return None

        # Verify entity_type matches expected type
        if getattr(entity, self.discriminator_field) != entity_type:
            raise ValueError(
                f"Entity ID {id} is of type {getattr(entity, self.discriminator_field)}, "
                f"not {entity_type}"
            )

        # Ensure discriminator field is preserved
        filtered_data = data.copy()
        filtered_data[self.discriminator_field] = entity_type

        # Get valid fields for this model class
        valid_fields = self._get_valid_fields_for_model(model_class)

        # Update entity fields, preserving required fields
        for key, value in filtered_data.items():
            if hasattr(entity, key):
                # Skip setting required fields to NULL
                if key in valid_fields.get("required", set()) and value is None:
                    continue

                setattr(entity, key, value)

        # Save changes
        self.session.add(entity)
        await self.session.flush()
        await self.session.refresh(entity)

        return entity

    def _get_valid_fields_for_model(self, model_class: Type) -> Dict[str, Set[str]]:
        """
        Get valid fields for a model class, including required fields.

        Args:
            model_class: SQLAlchemy model class

        Returns:
            Dict with 'all' and 'required' field sets
        """
        all_fields = set()
        required_fields = set()

        # Get fields from the model class hierarchy
        current_class = model_class
        while hasattr(current_class, "__table__") and current_class != object:
            if hasattr(current_class, "__table__"):
                for column in current_class.__table__.columns:
                    all_fields.add(column.key)
                    if (
                        not column.nullable
                        and not column.default
                        and not column.server_default
                    ):
                        required_fields.add(column.key)

            current_class = current_class.__bases__[0]
            if not hasattr(current_class, "__table__"):
                break

        return {"all": all_fields, "required": required_fields}
