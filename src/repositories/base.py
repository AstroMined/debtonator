"""
Base repository implementation for CRUD operations.

This module provides a generic base repository class that handles standard CRUD operations,
allowing model-specific repositories to inherit common functionality while focusing on
their unique requirements.
"""

from contextlib import asynccontextmanager
from typing import (Any, AsyncContextManager, Dict, Generic, List, Optional,
                    Tuple, Type, TypeVar, Union)

from sqlalchemy import delete, func, select, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.database.base import Base

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
        db_obj = self.model_class(**obj_in)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def get(self, id: PKType) -> Optional[ModelType]:
        """
        Get a single record by primary key.

        Args:
            id (PKType): Primary key value

        Returns:
            Optional[ModelType]: Found object or None
        """
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
        count_query = select(func.count()).select_from(
            self.model_class
        )  # This is correct SQLAlchemy usage, ignore Pylint
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

        # Update fields; the ORM will trigger the onupdate for updated_at
        for key, value in obj_in.items():
            setattr(db_obj, key, value)

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
