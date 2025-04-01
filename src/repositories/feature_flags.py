"""
Feature Flag Repository for database operations.

This module provides the FeatureFlagRepository class which handles database
operations for feature flags. It extends the BaseRepository class and implements
specific methods for feature flag management.

The repository is a core component of the Feature Flag System defined in ADR-024.
"""

from typing import Any, Dict, List, Optional, Tuple, Union

from src.utils.datetime_utils import ensure_utc, utc_now

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, update, delete
from sqlalchemy.sql import text

from src.models.feature_flags import FeatureFlag
from src.repositories.base_repository import BaseRepository
from src.schemas.feature_flags import (
    FeatureFlagCreate,
    FeatureFlagUpdate,
    FeatureFlagType,
)


class FeatureFlagRepository(BaseRepository[FeatureFlag, str]):
    """
    Repository for managing feature flags in the database.
    
    This class extends BaseRepository to provide feature flag-specific operations,
    including loading flags at startup, creating/updating flags, and filtering
    flags by type or system status.
    
    The repository uses the name field as the primary key instead of an id
    field, aligning with the FeatureFlag model's design.
    """
    
    def __init__(self, session: AsyncSession):
        """Initialize with a database session."""
        super().__init__(session, FeatureFlag)
    
    async def get(self, name: str) -> Optional[FeatureFlag]:
        """
        Get a feature flag by name.
        
        Args:
            name: Name (primary key) of the feature flag
            
        Returns:
            FeatureFlag or None if not found
        """
        result = await self.session.execute(
            select(self.model_class).where(self.model_class.name == name)
        )
        return result.scalars().first()
    
    async def get_all(self) -> List[FeatureFlag]:
        """
        Get all feature flags.
        
        Returns:
            List of all feature flags
        """
        result = await self.session.execute(select(self.model_class))
        return result.scalars().all()
    
    async def get_all_by_type(self, flag_type: Union[str, FeatureFlagType]) -> List[FeatureFlag]:
        """
        Get all feature flags of a specific type.
        
        Args:
            flag_type: Type of feature flags to retrieve
            
        Returns:
            List of feature flags of the specified type
        """
        # Convert enum to string if needed
        if isinstance(flag_type, FeatureFlagType):
            flag_type = flag_type.value
            
        result = await self.session.execute(
            select(self.model_class).where(self.model_class.flag_type == flag_type)
        )
        return result.scalars().all()
    
    async def get_system_flags(self) -> List[FeatureFlag]:
        """
        Get all system-defined feature flags.
        
        Returns:
            List of system-defined feature flags
        """
        result = await self.session.execute(
            select(self.model_class).where(self.model_class.is_system == True)
        )
        return result.scalars().all()
    
    async def create(self, data: Union[Dict[str, Any], FeatureFlagCreate]) -> FeatureFlag:
        """
        Create a new feature flag.
        
        Args:
            data: Feature flag data (dict or FeatureFlagCreate schema)
            
        Returns:
            The created feature flag
            
        Raises:
            ValueError: If the flag_type is invalid
        """
        # Convert schema to dict if needed
        if hasattr(data, "model_dump"):
            data_dict = data.model_dump(exclude_unset=True)
        else:
            data_dict = dict(data)
        
        # Ensure we have the correct field name
        if "flag_type" not in data_dict and "type" in data_dict:
            data_dict["flag_type"] = data_dict.pop("type")
        
        # Validate flag_type
        if "flag_type" in data_dict:
            try:
                # Validate using Enum
                flag_type = data_dict["flag_type"]
                if not isinstance(flag_type, str):
                    flag_type = flag_type.value
                FeatureFlagType(flag_type)
            except ValueError:
                valid_types = ", ".join([t.value for t in FeatureFlagType])
                raise ValueError(
                    f"Invalid flag_type: {data_dict['flag_type']}. "
                    f"Must be one of: {valid_types}"
                )
        
        # Create the feature flag
        flag = FeatureFlag(**data_dict)
        self.session.add(flag)
        await self.session.flush()
        await self.session.refresh(flag)
        return flag
    
    async def update(
        self, name: str, data: Union[Dict[str, Any], FeatureFlagUpdate]
    ) -> Optional[FeatureFlag]:
        """
        Update an existing feature flag.
        
        Args:
            name: Name of the feature flag to update
            data: Updated feature flag data
            
        Returns:
            Updated feature flag or None if not found
        """
        # Convert schema to dict if needed
        if hasattr(data, "model_dump"):
            data_dict = data.model_dump(exclude_unset=True)
        else:
            data_dict = dict(data)
        
        # Ensure we have the correct field name
        if "flag_type" not in data_dict and "type" in data_dict:
            data_dict["flag_type"] = data_dict.pop("type")
        
        # Get the existing flag
        flag = await self.get(name)
        if not flag:
            return None
        
        # Validate flag_type if present
        if "flag_type" in data_dict:
            try:
                # Validate using Enum
                flag_type = data_dict["flag_type"]
                if not isinstance(flag_type, str):
                    flag_type = flag_type.value
                FeatureFlagType(flag_type)
            except ValueError:
                valid_types = ", ".join([t.value for t in FeatureFlagType])
                raise ValueError(
                    f"Invalid flag_type: {data_dict['flag_type']}. "
                    f"Must be one of: {valid_types}"
                )
        
        # Update fields
        for key, value in data_dict.items():
            setattr(flag, key, value)
        
        # Add to session and flush
        self.session.add(flag)
        await self.session.flush()
        await self.session.refresh(flag)
        
        return flag
    
    async def delete(self, name: str) -> bool:
        """
        Delete a feature flag.
        
        Args:
            name: Name of the feature flag to delete
            
        Returns:
            True if deleted, False if not found
        """
        result = await self.session.execute(
            delete(self.model_class).where(self.model_class.name == name)
        )
        return result.rowcount > 0
    
    async def bulk_create(self, flags: List[Dict[str, Any]]) -> List[FeatureFlag]:
        """
        Create multiple feature flags in a single transaction.
        
        Args:
            flags: List of feature flag data dictionaries
            
        Returns:
            List of created feature flags
        """
        created_flags = []
        for flag_data in flags:
            flag = await self.create(flag_data)
            created_flags.append(flag)
        
        return created_flags
    
    async def bulk_update(self, updates: List[Tuple[str, Dict[str, Any]]]) -> List[Optional[FeatureFlag]]:
        """
        Update multiple feature flags in a single transaction.
        
        Args:
            updates: List of tuples (flag_name, update_data)
            
        Returns:
            List of updated feature flags (None for flags not found)
        """
        updated_flags = []
        for name, data in updates:
            flag = await self.update(name, data)
            updated_flags.append(flag)
        
        return updated_flags
    
    async def count_by_type(self) -> Dict[str, int]:
        """
        Count feature flags by type.
        
        Returns:
            Dictionary mapping flag types to counts
        """
        result = await self.session.execute(
            select(
                self.model_class.flag_type,
                func.count(self.model_class.name).label("count")
            ).group_by(self.model_class.flag_type)
        )
        
        counts = {row[0]: row[1] for row in result.all()}
        
        # Ensure all types have an entry
        for flag_type in FeatureFlagType:
            if flag_type.value not in counts:
                counts[flag_type.value] = 0
                
        return counts
