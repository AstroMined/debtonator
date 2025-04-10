"""
Feature Flag Config Provider implementation.

This module provides interfaces and implementations for feature flag configuration providers,
specifically focusing on loading feature requirements from the database. It includes:

1. A base ConfigProvider interface
2. An implementation that loads requirements from the database
3. Caching mechanisms to improve performance
4. Fallback to default requirements if database access fails

This is part of the implementation of ADR-024: Feature Flag System.
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Set, Tuple, Union

from sqlalchemy.ext.asyncio import AsyncSession

from src.errors.feature_flags import FeatureConfigurationError
from src.repositories.feature_flags import FeatureFlagRepository
from src.utils.feature_flags.requirements import get_default_requirements

# Configure logger
logger = logging.getLogger(__name__)

# Type aliases for better readability
Requirements = Dict[str, Dict[str, List[str]]]
LayerRequirements = Dict[str, List[str]]
CacheEntry = Tuple[float, Requirements]  # (timestamp, data)


class ConfigProvider(ABC):
    """
    Base interface for feature flag configuration providers.
    
    This abstract class defines the interface that all feature flag configuration
    providers must implement, ensuring consistent behavior across different providers.
    """
    
    @abstractmethod
    async def get_repository_requirements(self, feature_name: str) -> LayerRequirements:
        """
        Get repository method requirements for a given feature flag.
        
        Args:
            feature_name: Name of the feature flag
            
        Returns:
            Dictionary mapping repository methods to required account types
            
        Raises:
            FeatureConfigurationError: If requirements are missing or invalid
        """
        pass
    
    @abstractmethod
    async def get_service_requirements(self, feature_name: str) -> LayerRequirements:
        """
        Get service method requirements for a given feature flag.
        
        Args:
            feature_name: Name of the feature flag
            
        Returns:
            Dictionary mapping service methods to required account types
            
        Raises:
            FeatureConfigurationError: If requirements are missing or invalid
        """
        pass
    
    @abstractmethod
    async def get_api_requirements(self, feature_name: str) -> LayerRequirements:
        """
        Get API endpoint requirements for a given feature flag.
        
        Args:
            feature_name: Name of the feature flag
            
        Returns:
            Dictionary mapping API endpoints to required account types
            
        Raises:
            FeatureConfigurationError: If requirements are missing or invalid
        """
        pass
    
    @abstractmethod
    async def get_all_requirements(self) -> Requirements:
        """
        Get all requirements for all features.
        
        Returns:
            Dictionary mapping feature names to layer requirements
            
        Raises:
            FeatureConfigurationError: If requirements are missing or invalid
        """
        pass
    
    @abstractmethod
    async def invalidate_cache(self, feature_name: Optional[str] = None) -> None:
        """
        Invalidate the cache for a specific feature or all features.
        
        Args:
            feature_name: Name of the feature flag to invalidate, or None for all
        """
        pass


class DatabaseConfigProvider(ConfigProvider):
    """
    Database-driven implementation of ConfigProvider.
    
    This provider loads feature requirements from the database and includes
    a caching mechanism to reduce database access. It falls back to default
    requirements if database access fails.
    """
    
    def __init__(
        self,
        session: AsyncSession,
        cache_ttl: int = 300,  # 5 minutes by default
    ):
        """
        Initialize the database config provider.
        
        Args:
            session: SQLAlchemy async session for database access
            cache_ttl: Cache time-to-live in seconds
        """
        self.session = session
        self.repository = FeatureFlagRepository(session)
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, CacheEntry] = {}
        self._all_cache: Optional[CacheEntry] = None
    
    async def get_repository_requirements(self, feature_name: str) -> LayerRequirements:
        """
        Get repository method requirements for a given feature flag.
        
        Args:
            feature_name: Name of the feature flag
            
        Returns:
            Dictionary mapping repository methods to required account types
            
        Raises:
            FeatureConfigurationError: If requirements are missing or invalid
        """
        requirements = await self._get_feature_requirements(feature_name)
        
        if not requirements or "repository" not in requirements:
            # Fall back to default requirements
            defaults = get_default_requirements()
            if feature_name in defaults and "repository" in defaults[feature_name]:
                return defaults[feature_name]["repository"]
            
            # If no defaults, return empty dict to avoid None checks
            return {}
        
        return requirements["repository"]
    
    async def get_service_requirements(self, feature_name: str) -> LayerRequirements:
        """
        Get service method requirements for a given feature flag.
        
        Args:
            feature_name: Name of the feature flag
            
        Returns:
            Dictionary mapping service methods to required account types
            
        Raises:
            FeatureConfigurationError: If requirements are missing or invalid
        """
        requirements = await self._get_feature_requirements(feature_name)
        
        if not requirements or "service" not in requirements:
            # Fall back to default requirements
            defaults = get_default_requirements()
            if feature_name in defaults and "service" in defaults[feature_name]:
                return defaults[feature_name]["service"]
            
            # If no defaults, return empty dict to avoid None checks
            return {}
        
        return requirements["service"]
    
    async def get_api_requirements(self, feature_name: str) -> LayerRequirements:
        """
        Get API endpoint requirements for a given feature flag.
        
        Args:
            feature_name: Name of the feature flag
            
        Returns:
            Dictionary mapping API endpoints to required account types
            
        Raises:
            FeatureConfigurationError: If requirements are missing or invalid
        """
        requirements = await self._get_feature_requirements(feature_name)
        
        if not requirements or "api" not in requirements:
            # Fall back to default requirements
            defaults = get_default_requirements()
            if feature_name in defaults and "api" in defaults[feature_name]:
                return defaults[feature_name]["api"]
            
            # If no defaults, return empty dict to avoid None checks
            return {}
        
        return requirements["api"]
    
    async def get_all_requirements(self) -> Requirements:
        """
        Get all requirements for all features.
        
        Returns:
            Dictionary mapping feature names to layer requirements
            
        Raises:
            FeatureConfigurationError: If requirements are missing or invalid
        """
        # Check if we have a valid cache
        if self._all_cache and time.time() - self._all_cache[0] < self.cache_ttl:
            return self._all_cache[1]
        
        # Load from database
        try:
            all_flags = await self.repository.get_all()
            
            result: Requirements = {}
            for flag in all_flags:
                if flag.requirements:
                    result[flag.name] = flag.requirements
            
            # Cache the result
            self._all_cache = (time.time(), result)
            
            # If result is empty, use defaults
            if not result:
                logger.warning("No feature requirements found in database, using defaults")
                result = get_default_requirements()
            
            return result
            
        except Exception as e:
            # Log error and fall back to defaults
            logger.error(f"Error loading feature requirements from database: {e}")
            return get_default_requirements()
    
    async def invalidate_cache(self, feature_name: Optional[str] = None) -> None:
        """
        Invalidate the cache for a specific feature or all features.
        
        Args:
            feature_name: Name of the feature flag to invalidate, or None for all
        """
        if feature_name:
            if feature_name in self._cache:
                del self._cache[feature_name]
        else:
            self._cache.clear()
            self._all_cache = None
    
    async def _get_feature_requirements(self, feature_name: str) -> Dict[str, LayerRequirements]:
        """
        Get requirements for a specific feature flag.
        
        Args:
            feature_name: Name of the feature flag
            
        Returns:
            Dictionary with repository, service, and API requirements
            
        Raises:
            FeatureConfigurationError: If requirements cannot be loaded
        """
        # Check if we have a valid cache
        if (
            feature_name in self._cache 
            and time.time() - self._cache[feature_name][0] < self.cache_ttl
        ):
            return self._cache[feature_name][1]
        
        # Load from database
        try:
            flag = await self.repository.get(feature_name)
            
            if not flag:
                raise FeatureConfigurationError(
                    feature_name=feature_name,
                    config_issue="Feature flag not found in database"
                )
            
            # Get requirements from flag or use empty dict
            requirements = flag.requirements or {}
            
            # Cache the result
            self._cache[feature_name] = (time.time(), requirements)
            
            return requirements
            
        except FeatureConfigurationError:
            # Re-raise configuration errors
            raise
        except Exception as e:
            # Log other errors and fall back to defaults
            logger.error(f"Error loading feature {feature_name} requirements: {e}")
            
            # Try defaults
            defaults = get_default_requirements()
            if feature_name in defaults:
                return defaults[feature_name]
            
            # If no defaults, return empty dict to avoid None checks
            return {}


class InMemoryConfigProvider(ConfigProvider):
    """
    In-memory implementation of ConfigProvider.
    
    This provider is primarily used for testing and local development where
    database access might not be available. It loads requirements from a
    provided dictionary or from default requirements.
    """
    
    def __init__(self, requirements: Optional[Requirements] = None):
        """
        Initialize the in-memory config provider.
        
        Args:
            requirements: Dictionary of feature requirements or None to use defaults
        """
        self.requirements = requirements or get_default_requirements()
    
    async def get_repository_requirements(self, feature_name: str) -> LayerRequirements:
        """
        Get repository method requirements for a given feature flag.
        
        Args:
            feature_name: Name of the feature flag
            
        Returns:
            Dictionary mapping repository methods to required account types
        """
        if feature_name not in self.requirements:
            return {}
        
        return self.requirements.get(feature_name, {}).get("repository", {})
    
    async def get_service_requirements(self, feature_name: str) -> LayerRequirements:
        """
        Get service method requirements for a given feature flag.
        
        Args:
            feature_name: Name of the feature flag
            
        Returns:
            Dictionary mapping service methods to required account types
        """
        if feature_name not in self.requirements:
            return {}
        
        return self.requirements.get(feature_name, {}).get("service", {})
    
    async def get_api_requirements(self, feature_name: str) -> LayerRequirements:
        """
        Get API endpoint requirements for a given feature flag.
        
        Args:
            feature_name: Name of the feature flag
            
        Returns:
            Dictionary mapping API endpoints to required account types
        """
        if feature_name not in self.requirements:
            return {}
        
        return self.requirements.get(feature_name, {}).get("api", {})
    
    async def get_all_requirements(self) -> Requirements:
        """
        Get all requirements for all features.
        
        Returns:
            Dictionary mapping feature names to layer requirements
        """
        return self.requirements
    
    async def invalidate_cache(self, feature_name: Optional[str] = None) -> None:
        """
        Invalidate the cache - no-op for in-memory provider.
        
        Args:
            feature_name: Name of the feature flag to invalidate (unused)
        """
        # No-op for in-memory provider
        pass
    
    def update_requirements(self, new_requirements: Requirements) -> None:
        """
        Update the in-memory requirements.
        
        Args:
            new_requirements: New requirements to use
        """
        self.requirements = new_requirements
