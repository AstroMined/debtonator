"""
Repository factory for dependency injection.

This module provides a factory class that creates and caches repository instances,
simplifying dependency injection and ensuring consistent repository usage across services.
"""

from typing import Any, Dict, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.base_repository import BaseRepository

T = TypeVar("T", bound=BaseRepository)


class RepositoryFactory:
    """
    Factory for creating and caching repository instances.

    This class manages repository instances, creating them as needed and
    caching them for reuse within the same session scope.

    Attributes:
        session (AsyncSession): The SQLAlchemy async session for database operations
        _repositories (Dict): Cache of repository instances
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize factory with database session.

        Args:
            session (AsyncSession): SQLAlchemy async session to use for all repositories
        """
        self.session = session
        self._repositories: Dict[Type[BaseRepository], BaseRepository] = {}

    def get_repository(self, repository_class: Type[T]) -> T:
        """
        Get or create a repository instance of the specified class.

        Args:
            repository_class (Type[T]): Repository class to instantiate

        Returns:
            T: Instance of the requested repository class
        """
        if repository_class not in self._repositories:
            self._repositories[repository_class] = repository_class(self.session)
        return self._repositories[repository_class]
