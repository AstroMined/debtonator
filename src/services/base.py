"""
Base service implementation.

This module provides a base service class that all services should inherit from.
It implements standardized repository initialization, feature flag integration,
and repository caching.

Implements ADR-014 Repository Layer Compliance with improved service-repository integration.
"""

from typing import Any, Dict, Optional, Type, TypeVar

from sqlalchemy.ext.asyncio import AsyncSession

from src.config.providers.feature_flags import (
    DatabaseConfigProvider,
    InMemoryConfigProvider,
)
from src.repositories.base_repository import BaseRepository
from src.repositories.factory import RepositoryFactory
from src.repositories.polymorphic_base_repository import PolymorphicBaseRepository
from src.repositories.proxies.feature_flag_proxy import FeatureFlagRepositoryProxy
from src.services.feature_flags import FeatureFlagService

# Type variable for repository types
RepoType = TypeVar("RepoType", bound=BaseRepository)


class BaseService:
    """
    Base class for all services with standardized repository initialization.
    
    This class provides a consistent way to instantiate and access repositories,
    with automatic feature flag integration and proper handling of polymorphic
    entities.
    
    All services should inherit from this class to ensure consistent repository
    access patterns across the application.
    """
    
    def __init__(
        self,
        session: AsyncSession,
        feature_flag_service: Optional[FeatureFlagService] = None,
        config_provider: Optional[Any] = None
    ):
        """
        Initialize base service with session and optional feature flag service.
        
        Args:
            session: SQLAlchemy async session
            feature_flag_service: Optional feature flag service for repository proxies
            config_provider: Optional config provider for feature flags
        """
        self._session = session
        self._feature_flag_service = feature_flag_service
        self._config_provider = config_provider
        
        # Dictionary to store lazy-loaded repositories
        self._repositories: Dict[str, Any] = {}
        
    async def _get_repository(
        self, 
        repository_class: Type[RepoType],
        polymorphic_type: Optional[str] = None,
        repository_key: Optional[str] = None
    ) -> RepoType:
        """
        Get or create a repository instance.
        
        For polymorphic repositories, uses the repository factory.
        For standard repositories, uses direct instantiation.
        
        Args:
            repository_class: Repository class to instantiate
            polymorphic_type: Optional polymorphic type for factory-created repositories
            repository_key: Optional custom key for repository caching
            
        Returns:
            Repository instance with optional feature flag wrapping
        """
        # Generate a key for repository caching
        key = repository_key or f"{repository_class.__name__}_{polymorphic_type or ''}"
        
        # Return cached repository if available
        if key in self._repositories:
            return self._repositories[key]
            
        # Create repository based on type
        if issubclass(repository_class, PolymorphicBaseRepository) and polymorphic_type:
            # Use factory for polymorphic repositories
            repository = await RepositoryFactory.create_account_repository(
                self._session, 
                polymorphic_type,
                self._feature_flag_service, 
                self._config_provider
            )
        else:
            # Direct instantiation for standard repositories
            repository = repository_class(self._session)
            
            # Apply feature flag proxy if needed
            if self._feature_flag_service:
                repository = await self._wrap_with_feature_flags(repository)
                
        # Cache the repository
        self._repositories[key] = repository
        return repository
        
    async def _wrap_with_feature_flags(self, repository: RepoType) -> RepoType:
        """
        Wrap repository with feature flag proxy.
        
        Args:
            repository: Repository instance to wrap
            
        Returns:
            Repository wrapped with FeatureFlagRepositoryProxy
        """
        # Create config provider if not provided
        if self._config_provider is None:
            try:
                config_provider = DatabaseConfigProvider(self._session)
            except Exception:
                config_provider = InMemoryConfigProvider()
        else:
            config_provider = self._config_provider
            
        # Create and return the proxy
        return FeatureFlagRepositoryProxy(
            repository=repository,
            feature_flag_service=self._feature_flag_service,
            config_provider=config_provider,
        )
