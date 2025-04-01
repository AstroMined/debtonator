"""
Feature Flag Service for business logic and integration.

This module provides the FeatureFlagService class which bridges the gap between
the in-memory feature flag registry and the database-backed repository. It provides
methods for checking if flags are enabled, setting flag values, and managing the
lifecycle of feature flags.

The service is a core component of the Feature Flag System defined in ADR-024.
"""

import logging
import hashlib
from typing import Any, Dict, List, Optional, Union

from src.models.feature_flags import FeatureFlag
from src.registry.feature_flags import FeatureFlagRegistry, FeatureFlagObserver
from src.repositories.feature_flags import FeatureFlagRepository
from src.utils.datetime_utils import ensure_utc, utc_now
from src.schemas.feature_flags import (
    FeatureFlagCreate, 
    FeatureFlagResponse, 
    FeatureFlagType,
    FeatureFlagUpdate
)

logger = logging.getLogger(__name__)


class FeatureFlagService(FeatureFlagObserver):
    """
    Service for managing and evaluating feature flags.
    
    This class orchestrates the interaction between the in-memory registry and
    the database repository, ensuring that changes are properly synchronized.
    It also provides the primary API for checking flag status and modifying flags.
    
    The service implements the FeatureFlagObserver protocol to receive notifications
    when flags are changed through the registry directly.
    """
    
    def __init__(
        self, 
        registry: FeatureFlagRegistry,
        repository: FeatureFlagRepository,
    ):
        """
        Initialize the service with a registry and repository.
        
        Args:
            registry: In-memory feature flag registry
            repository: Database repository for feature flags
        """
        self.registry = registry
        self.repository = repository
        
        # Register as an observer to receive notifications of flag changes
        self.registry.add_observer(self)
        
        # Set on first initialization
        self._initialized = False
        
        logger.info("Feature flag service initialized")
    
    async def initialize(self) -> None:
        """
        Initialize the service by loading all flags from the database.
        
        This method synchronizes the in-memory registry with the database state,
        and should be called during application startup.
        """
        if self._initialized:
            logger.debug("Feature flag service already initialized")
            return
        
        logger.info("Initializing feature flag service from database")
        
        # Load all flags from the database
        flags = await self.repository.get_all()
        
        # Register each flag in the registry
        for flag in flags:
            try:
                self.registry.register(
                    flag_name=flag.name,
                    flag_type=flag.flag_type,
                    default_value=flag.value,
                    description=flag.description,
                    metadata=flag.metadata,
                    is_system=flag.is_system,
                )
            except ValueError:
                # Flag already exists in registry, update its value
                self.registry.set_value(flag.name, flag.value)
                logger.debug(f"Updated existing flag in registry: {flag.name}")
        
        self._initialized = True
        logger.info(f"Feature flag service initialized with {len(flags)} flags")
    
    def is_enabled(self, flag_name: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        Check if a feature flag is enabled.
        
        Args:
            flag_name: Name of the feature flag to check
            context: Optional context information for evaluating the flag
            
        Returns:
            True if the flag is enabled, False otherwise
            
        Note:
            If the flag doesn't exist, this returns False as a safety measure.
        """
        try:
            value = self.registry.get_value(flag_name, context)
            # For boolean flags, the value is the enabled state
            # For percentage/segment flags, the result of evaluation is the enabled state
            return bool(value)
        except ValueError:
            # If flag doesn't exist, default to disabled for safety
            logger.warning(f"Feature flag not found: {flag_name}")
            return False
    
    async def set_enabled(
        self, 
        flag_name: str, 
        enabled: bool, 
        persist: bool = True
    ) -> bool:
        """
        Enable or disable a boolean feature flag.
        
        Args:
            flag_name: Name of the feature flag to update
            enabled: Whether the flag should be enabled
            persist: Whether to persist the change to the database
            
        Returns:
            True if the operation was successful, False otherwise
        """
        flag = self.registry.get_flag(flag_name)
        if not flag:
            logger.warning(f"Cannot set enabled state for non-existent flag: {flag_name}")
            return False
        
        if flag["type"] != FeatureFlagType.BOOLEAN:
            logger.warning(f"Cannot set enabled state for non-boolean flag: {flag_name} (type: {flag['type']})")
            return False
        
        # Update the registry
        self.registry.set_value(flag_name, enabled)
        
        # Persist to database if requested
        if persist:
            await self.repository.update(flag_name, {"value": enabled})
        
        logger.info(f"Feature flag {flag_name} set to: {enabled}")
        return True
    
    async def set_value(
        self, 
        flag_name: str, 
        value: Any, 
        persist: bool = True
    ) -> bool:
        """
        Set the value of a feature flag.
        
        Args:
            flag_name: Name of the feature flag to update
            value: New value for the flag
            persist: Whether to persist the change to the database
            
        Returns:
            True if the operation was successful, False otherwise
        """
        flag = self.registry.get_flag(flag_name)
        if not flag:
            logger.warning(f"Cannot set value for non-existent flag: {flag_name}")
            return False
        
        # Validate value based on flag type
        flag_type = flag["type"]
        
        if flag_type == FeatureFlagType.BOOLEAN and not isinstance(value, bool):
            logger.warning(f"Invalid value for boolean flag: {value}")
            return False
        
        if flag_type == FeatureFlagType.PERCENTAGE:
            if not isinstance(value, (int, float)) or value < 0 or value > 100:
                logger.warning(f"Invalid percentage value: {value}")
                return False
        
        if flag_type == FeatureFlagType.USER_SEGMENT and not isinstance(value, list):
            logger.warning(f"Invalid user segment value: {value}")
            return False
        
        if flag_type == FeatureFlagType.TIME_BASED and not isinstance(value, dict):
            logger.warning(f"Invalid time-based value: {value}")
            return False
        
        # Update the registry
        self.registry.set_value(flag_name, value)
        
        # Persist to database if requested
        if persist:
            await self.repository.update(flag_name, {"value": value})
        
        logger.info(f"Feature flag {flag_name} value updated to: {value}")
        return True
    
    async def create_flag(self, flag_data: Union[Dict[str, Any], FeatureFlagCreate]) -> Optional[FeatureFlag]:
        """
        Create a new feature flag.
        
        Args:
            flag_data: Feature flag data
            
        Returns:
            The created feature flag, or None if creation failed
            
        Note:
            This method persists the flag to the database and registers it in the in-memory registry.
        """
        try:
            # Convert schema to dict if needed
            if hasattr(flag_data, "model_dump"):
                data_dict = flag_data.model_dump()
            else:
                data_dict = dict(flag_data)
                
            # Create in database first
            flag = await self.repository.create(data_dict)
            
            # Then register in registry
            flag_type = flag.flag_type
            self.registry.register(
                flag_name=flag.name,
                flag_type=flag_type,
                default_value=flag.value,
                description=flag.description,
                metadata=flag.metadata,
                is_system=flag.is_system,
            )
            
            logger.info(f"Feature flag created: {flag.name}")
            return flag
            
        except Exception as e:
            logger.error(f"Error creating feature flag: {e}")
            return None
    
    async def update_flag(
        self, 
        flag_name: str, 
        flag_data: Union[Dict[str, Any], FeatureFlagUpdate]
    ) -> Optional[FeatureFlag]:
        """
        Update an existing feature flag.
        
        Args:
            flag_name: Name of the flag to update
            flag_data: Updated flag data
            
        Returns:
            The updated feature flag, or None if update failed
            
        Note:
            This method updates both the database and the in-memory registry.
        """
        try:
            # Check if flag exists in registry
            if not self.registry.get_flag(flag_name):
                logger.warning(f"Feature flag not found in registry: {flag_name}")
                return None
                
            # Convert schema to dict if needed
            if hasattr(flag_data, "model_dump"):
                data_dict = flag_data.model_dump(exclude_unset=True)
            else:
                data_dict = dict(flag_data)
                
            # Update in database first
            updated_flag = await self.repository.update(flag_name, data_dict)
            if not updated_flag:
                logger.warning(f"Feature flag not found in database: {flag_name}")
                return None
            
            # Then update registry
            if "value" in data_dict:
                self.registry.set_value(flag_name, data_dict["value"])
            
            # Note: Updating flag_type in registry is not directly supported
            # A full registry reload would be needed for that
            
            logger.info(f"Feature flag updated: {flag_name}")
            return updated_flag
            
        except Exception as e:
            logger.error(f"Error updating feature flag: {e}")
            return None
    
    async def delete_flag(self, flag_name: str) -> bool:
        """
        Delete a feature flag.
        
        Args:
            flag_name: Name of the flag to delete
            
        Returns:
            True if deleted successfully, False otherwise
            
        Note:
            System flags (is_system=True) cannot be deleted.
        """
        try:
            # Check if this is a system flag
            flag = self.registry.get_flag(flag_name)
            if flag and flag.get("is_system", False):
                logger.warning(f"Cannot delete system feature flag: {flag_name}")
                return False
            
            # Delete from database
            deleted = await self.repository.delete(flag_name)
            if not deleted:
                logger.warning(f"Feature flag not found in database: {flag_name}")
                return False
            
            # Remove from registry
            # Note: registry doesn't have a direct method to remove flags
            # A full reload would be needed to synchronize
            
            logger.info(f"Feature flag deleted: {flag_name}")
            return True
            
        except Exception as e:
            logger.error(f"Error deleting feature flag: {e}")
            return False
    
    async def get_all_flags(self) -> List[FeatureFlagResponse]:
        """
        Get all feature flags.
        
        Returns:
            List of feature flag responses
        """
        # Get flags from database to ensure we have the full details
        db_flags = await self.repository.get_all()
        
        # Convert to response schema
        return [
            FeatureFlagResponse(
                name=flag.name,
                description=flag.description,
                flag_type=flag.flag_type,
                value=flag.value,
                metadata=flag.metadata,
                is_system=flag.is_system,
                created_at=ensure_utc(flag.created_at),
                updated_at=ensure_utc(flag.updated_at),
            )
            for flag in db_flags
        ]
    
    async def get_flag(self, flag_name: str) -> Optional[FeatureFlagResponse]:
        """
        Get a specific feature flag.
        
        Args:
            flag_name: Name of the flag to retrieve
            
        Returns:
            Feature flag response, or None if not found
        """
        # Get from database to ensure we have the full details
        db_flag = await self.repository.get(flag_name)
        if not db_flag:
            return None
        
        # Convert to response schema
        return FeatureFlagResponse(
            name=db_flag.name,
            description=db_flag.description,
            flag_type=db_flag.flag_type,
            value=db_flag.value,
            metadata=db_flag.metadata,
            is_system=db_flag.is_system,
            created_at=ensure_utc(db_flag.created_at),
            updated_at=ensure_utc(db_flag.updated_at),
        )
    
    # Implementation of FeatureFlagObserver protocol
    def flag_changed(self, flag_name: str, old_value: Any, new_value: Any) -> None:
        """
        Handle notification of a flag value change in the registry.
        
        Args:
            flag_name: Name of the flag that changed
            old_value: Previous value
            new_value: New value
            
        Note:
            This method is called by the registry when a flag value changes.
            It logs the change but does not persist it to the database, as this is
            typically called as a result of a direct registry update from set_value,
            which already handles persistence.
        """
        logger.info(f"Feature flag '{flag_name}' changed: {old_value} -> {new_value}")
