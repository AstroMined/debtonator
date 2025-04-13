"""
Base repository implementation for CRUD operations.

This module provides a generic base repository class that handles standard CRUD operations,
allowing model-specific repositories to inherit common functionality while focusing on
their unique requirements.
"""

from contextlib import asynccontextmanager
from typing import (
    Any,
    AsyncContextManager,
    Dict,
    Generic,
    List,
    Optional,
    Tuple,
    Type,
    TypeVar,
)

from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.database.base import Base
from src.utils.datetime_utils import naive_utc_now

ModelType = TypeVar("ModelType", bound=Base)
PKType = TypeVar("PKType")


class BaseRepository(Generic[ModelType, PKType]):
    """
    Generic base repository for CRUD operations.

    This class provides standard database operations for SQLAlchemy models,
    using generic type parameters to ensure type safety.

    Attributes:
        session (AsyncSession): The SQLAlchemy async session for database operations
        model_class (Type[ModelType]): The SQLAlchemy model class this repository manages
    """

    def __init__(self, session: AsyncSession, model_class: Type[ModelType]):
        """
        Initialize repository with session and model class.

        Args:
            session (AsyncSession): AsyncSession for database operations
            model_class (Type[ModelType]): Model class this repository manages
        """
        self.session = session
        self.model_class = model_class

    async def create(self, obj_in: Dict[str, Any]) -> ModelType:
        """
        Create a new database record.

        Args:
            obj_in (Dict[str, Any]): Dictionary of attributes for the new object

        Returns:
            ModelType: Created database object
        """
        # Filter input to only include valid model attributes
        model_fields = set()

        # Add column attributes (including foreign keys)
        if hasattr(self.model_class, "__table__") and hasattr(
            self.model_class.__table__, "columns"
        ):
            model_fields.update(c.key for c in self.model_class.__table__.columns)

        # Add relationship attributes
        if hasattr(self.model_class, "__mapper__") and hasattr(
            self.model_class.__mapper__, "relationships"
        ):
            model_fields.update(self.model_class.__mapper__.relationships.keys())

        # Add foreign key fields explicitly
        if hasattr(self.model_class, "__mapper__") and hasattr(
            self.model_class.__mapper__, "relationships"
        ):
            for relationship in self.model_class.__mapper__.relationships.values():
                # Extract foreign key column names if available
                if hasattr(relationship, "local_columns"):
                    for column in relationship.local_columns:
                        if hasattr(column, "key"):
                            model_fields.add(column.key)

        # Add any fields that start with valid column names (for foreign keys that might be named differently)
        column_prefixes = {
            c.key.replace("_id", "")
            for c in self.model_class.__table__.columns
            if c.key.endswith("_id")
        }
        for key in obj_in.keys():
            if key.endswith("_id") and key.replace("_id", "") in column_prefixes:
                model_fields.add(key)

        # Filter out fields that don't exist in the model
        filtered_obj_in = {k: v for k, v in obj_in.items() if k in model_fields}

        # Create the object with filtered data
        db_obj = self.model_class(**filtered_obj_in)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    def _needs_polymorphic_loading(self) -> bool:
        """
        Determine if this repository's model requires polymorphic loading.

        Can be overridden by subclasses to enable polymorphic loading.

        Returns:
            bool: True if polymorphic loading should be used, False otherwise
        """
        return False

    async def get(self, id: PKType) -> Optional[ModelType]:
        """
        Get a single record by primary key.

        Args:
            id (PKType): Primary key value

        Returns:
            Optional[ModelType]: Found object or None
        """
        if self._needs_polymorphic_loading():
            # Use polymorphic loading for models with inheritance
            from sqlalchemy.orm import with_polymorphic

            poly_model = with_polymorphic(self.model_class, "*")
            result = await self.session.execute(
                select(poly_model).where(poly_model.id == id)
            )
        else:
            # Standard loading for non-polymorphic models
            result = await self.session.execute(
                select(self.model_class).where(self.model_class.id == id)
            )

        return result.scalars().first()

    async def get_with_joins(
        self, id: PKType, relationships: List[str] = None
    ) -> Optional[ModelType]:
        """
        Get a single record with joined relationships.

        Args:
            id (PKType): Primary key value
            relationships (List[str], optional): Relationships to join-load

        Returns:
            Optional[ModelType]: Found object with loaded relationships or None
        """
        query = select(self.model_class).where(self.model_class.id == id)

        if relationships:
            for relationship in relationships:
                if hasattr(self.model_class, relationship):
                    query = query.options(
                        joinedload(getattr(self.model_class, relationship))
                    )

        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
    ) -> List[ModelType]:
        """
        Get multiple records with optional filtering.

        Args:
            skip (int, optional): Number of records to skip (offset)
            limit (int, optional): Maximum number of records to return
            filters (Dict[str, Any], optional): Field-value pairs for filtering

        Returns:
            List[ModelType]: List of found objects
        """
        query = select(self.model_class).offset(skip).limit(limit)

        if filters:
            for field, value in filters.items():
                if hasattr(self.model_class, field):
                    query = query.where(getattr(self.model_class, field) == value)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_paginated(
        self,
        *,
        page: int = 1,
        items_per_page: int = 20,
        filters: Optional[Dict[str, Any]] = None,
    ) -> Tuple[List[ModelType], int]:
        """
        Get paginated records with optional filtering.

        Args:
            page (int): Page number (1-based)
            items_per_page (int): Items per page
            filters (Dict[str, Any], optional): Field-value pairs for filtering

        Returns:
            Tuple[List[ModelType], int]: Tuple of (items, total_count)
        """
        # Calculate offset
        skip = (page - 1) * items_per_page

        # Get total count
        count_query = select(func.count(1)).select_from(
            self.model_class
        )  # Use func.count(1) for SQL COUNT(*) equivalent
        if filters:
            for field, value in filters.items():
                if hasattr(self.model_class, field):
                    count_query = count_query.where(
                        getattr(self.model_class, field) == value
                    )

        total_result = await self.session.execute(count_query)
        total = total_result.scalar_one()

        # Get items
        items = await self.get_multi(skip=skip, limit=items_per_page, filters=filters)

        return items, total

    async def update(self, id: PKType, obj_in: Dict[str, Any]) -> Optional[ModelType]:
        """
        Update an existing record.

        Args:
            id (PKType): Primary key of record to update
            obj_in (Dict[str, Any]): Dictionary of attributes to update

        Returns:
            Optional[ModelType]: Updated object or None if not found
        """
        # Retrieve the ORM instance
        query = select(self.model_class).where(self.model_class.id == id)
        result = await self.session.execute(query)
        db_obj = result.scalars().first()
        if not db_obj:
            return None

        # Filter out None values for relationships and required columns
        filtered_obj_in = {}
        for key, value in obj_in.items():
            # Skip None values for relationship fields or non-nullable columns
            if key in db_obj.__mapper__.relationships:
                if value is not None:
                    filtered_obj_in[key] = value
            elif (
                value is not None
                or key not in db_obj.__table__.columns
                or db_obj.__table__.columns[key].nullable
            ):
                filtered_obj_in[key] = value

        # Update fields; the ORM will trigger the onupdate for updated_at
        for key, value in filtered_obj_in.items():
            setattr(db_obj, key, value)

        # Force updated_at to refresh with a new timestamp
        # This ensures updated_at changes even if SQLAlchemy doesn't detect field changes
        if hasattr(db_obj, "updated_at"):
            # Explicitly set to current time
            setattr(db_obj, "updated_at", naive_utc_now())

        # Explicitly mark as modified to ensure SQLAlchemy tracks changes
        self.session.add(db_obj)

        # Flush changes so that onupdate is applied
        await self.session.flush()
        await self.session.refresh(db_obj)

        return db_obj

    async def delete(self, id: PKType) -> bool:
        """
        Delete a record by primary key.

        Args:
            id (PKType): Primary key of record to delete

        Returns:
            bool: True if deleted, False if not found
        """
        result = await self.session.execute(
            delete(self.model_class).where(self.model_class.id == id)
        )
        return result.rowcount > 0

    async def bulk_create(self, objects: List[Dict[str, Any]]) -> List[ModelType]:
        """
        Create multiple records in a single transaction.

        Args:
            objects (List[Dict[str, Any]]): List of attribute dictionaries

        Returns:
            List[ModelType]: List of created objects
        """
        db_objects = []
        for obj in objects:
            db_obj = self.model_class(**obj)
            self.session.add(db_obj)
            db_objects.append(db_obj)

        await self.session.flush()

        # Refresh all objects
        for obj in db_objects:
            await self.session.refresh(obj)

        return db_objects

    async def bulk_update(
        self, ids: List[PKType], obj_in: Dict[str, Any]
    ) -> List[Optional[ModelType]]:
        """
        Bulk update records identified by their primary keys.

        Args:
            ids (List[PKType]): List of primary keys to update
            obj_in (Dict[str, Any]): Dictionary containing fields to update

        Returns:
            List[Optional[ModelType]]: List of updated model instances (None for any IDs not found)
        """
        results = []
        for id in ids:
            result = await self.update(id, obj_in)
            results.append(result)

        return results

    @asynccontextmanager
    async def transaction(
        self,
    ) -> AsyncContextManager["BaseRepository[ModelType, PKType]"]:
        """
        Begin a transaction and return a repository instance with the same session.

        If a transaction is already in progress, creates a savepoint (nested transaction).

        Usage:
            async with repo.transaction() as tx_repo:
                # Operations within transaction
                await tx_repo.create(...)
                await tx_repo.update(...)

        Returns:
            BaseRepository: A repository instance with the transaction-bound session
        """
        # Check if a transaction is already active on this session
        if self.session.in_transaction():
            # Use nested transaction (savepoint) if a transaction is already in progress
            async with self.session.begin_nested():
                # Create a new repository instance with the same session
                repo = self.__class__(self.session, self.model_class)
                try:
                    yield repo
                    # Savepoint auto-commits unless an exception occurs
                except Exception as e:
                    # Savepoint auto-rollbacks on exception
                    raise e
        else:
            # No active transaction, start a new one
            async with self.session.begin():
                # Create a new repository instance with the same session
                repo = self.__class__(self.session, self.model_class)
                try:
                    yield repo
                    # Transaction auto-commits unless an exception occurs
                except Exception as e:
                    # Transaction auto-rollbacks on exception
                    raise e
