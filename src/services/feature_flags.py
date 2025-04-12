"""
Feature Flag Service for business logic and integration.

This module provides the FeatureFlagService class which bridges the gap between
the in-memory feature flag registry and the database-backed repository. It provides
methods for checking if flags are enabled, setting flag values, and managing the
lifecycle of feature flags.

The service is a core component of the Feature Flag System defined in ADR-024.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from src.registry.feature_flags_registry import FeatureFlagObserver, FeatureFlagRegistry
from src.repositories.feature_flags import FeatureFlagRepository
from src.schemas.feature_flags import (
    FeatureFlagCreate,
    FeatureFlagResponse,
    FeatureFlagType,
    FeatureFlagUpdate,
)
from src.utils.datetime_utils import ensure_utc
from src.utils.feature_flags.context import EnvironmentContext

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
        context: Optional[EnvironmentContext] = None,
    ):
        """
        Initialize the service with a registry, repository and optional context.

        Args:
            registry: In-memory feature flag registry
            repository: Database repository for feature flags
            context: Optional environment context for flag evaluation
        """
        self.registry = registry
        self.repository = repository
        self.context = context

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
                    metadata=flag.flag_metadata,  # Changed field name
                    is_system=flag.is_system,
                )
            except ValueError:
                # Flag already exists in registry, update its value
                self.registry.set_value(flag.name, flag.value)
                logger.debug(f"Updated existing flag in registry: {flag.name}")

        self._initialized = True
        logger.info(f"Feature flag service initialized with {len(flags)} flags")

    async def is_enabled(
        self, flag_name: str, context: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Check if a feature flag is enabled.

        This method evaluates the flag based on its type and the provided context:
        - Boolean flags: Returns the flag's value directly
        - Percentage flags: Determines if the user falls within the rollout percentage
        - User segment flags: Checks if the user belongs to an enabled segment
        - Time-based flags: Verifies if current time is within the enabled timeframe

        Args:
            flag_name: Name of the feature flag to check
            context: Optional context information for evaluating the flag, such as:
              - user_id: Identifier for percentage-based flags
              - is_admin, is_beta_tester: Status flags for segment-based targeting
              - user_groups: List of user groups for segment-based targeting

        Returns:
            True if the flag is enabled for the given context, False otherwise

        Examples:
            # Check a simple boolean flag
            is_feature_enabled = await service.is_enabled("NEW_DASHBOARD_ENABLED")

            # Check a percentage rollout flag with user context
            is_enabled_for_user = await service.is_enabled(
                "GRADUAL_ROLLOUT_FEATURE",
                context={"user_id": "user-123"}
            )

            # Check a user segment flag
            is_enabled_for_admin = await service.is_enabled(
                "ADMIN_ONLY_FEATURE",
                context={"is_admin": True}
            )

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
        self, flag_name: str, enabled: bool, persist: bool = True, proxy = None
    ) -> bool:
        """
        Enable or disable a boolean feature flag.

        Args:
            flag_name: Name of the feature flag to update
            enabled: Whether the flag should be enabled
            persist: Whether to persist the change to the database
            proxy: Optional repository proxy to clear cache for

        Returns:
            True if the operation was successful, False otherwise
        """
        flag = self.registry.get_flag(flag_name)
        if not flag:
            logger.warning(
                f"Cannot set enabled state for non-existent flag: {flag_name}"
            )
            return False

        if flag["type"] != FeatureFlagType.BOOLEAN:
            logger.warning(
                f"Cannot set enabled state for non-boolean flag: {flag_name} (type: {flag['type']})"
            )
            return False

        # Update the registry
        self.registry.set_value(flag_name, enabled)

        # Persist to database if requested
        if persist:
            await self.repository.update(flag_name, {"value": enabled})
            
        # Clear proxy cache if provided
        if proxy and hasattr(proxy, 'clear_feature_check_cache'):
            proxy.clear_feature_check_cache()
            logger.debug(f"Cleared cache for proxy after setting {flag_name} to {enabled}")

        logger.info(f"Feature flag {flag_name} set to: {enabled}")
        return True

    async def set_value(self, flag_name: str, value: Any, persist: bool = True) -> bool:
        """
        Set the value of a feature flag.

        This method validates the value based on the flag type and updates
        both the in-memory registry and (optionally) the database.

        Args:
            flag_name: Name of the feature flag to update
            value: New value for the flag, format depends on flag_type:
                - BOOLEAN: Boolean true/false
                - PERCENTAGE: Integer or float (0-100)
                - USER_SEGMENT: List of segment names
                - TIME_BASED: Dict with start_time/end_time keys
            persist: Whether to persist the change to the database

        Returns:
            True if the operation was successful, False otherwise

        Examples:
            # Set a boolean flag
            await service.set_value("FEATURE_X_ENABLED", True)

            # Set a percentage rollout
            await service.set_value("FEATURE_Y_ROLLOUT", 25)  # 25% of users

            # Set user segments
            await service.set_value("ADMIN_FEATURE", ["admin", "staff"])

            # Set time-based availability
            await service.set_value(
                "HOLIDAY_FEATURE",
                {
                    "start_time": "2025-12-01T00:00:00Z",
                    "end_time": "2026-01-01T00:00:00Z"
                }
            )
        """
        flag = self.registry.get_flag(flag_name)
        if not flag:
            logger.warning(f"Cannot set value for non-existent flag: {flag_name}")
            return False

        # Validate value based on flag type
        flag_type = flag["type"]

        if flag_type == FeatureFlagType.BOOLEAN and not isinstance(value, bool):
            logger.warning(
                f"Invalid value for boolean flag: {value} (type: {type(value).__name__}). "
                f"Expected boolean value."
            )
            return False

        if flag_type == FeatureFlagType.PERCENTAGE:
            if not isinstance(value, (int, float)):
                logger.warning(
                    f"Invalid percentage value: {value} (type: {type(value).__name__}). "
                    f"Expected number between 0 and 100."
                )
                return False
            if value < 0 or value > 100:
                logger.warning(
                    f"Invalid percentage value: {value}. "
                    f"Value must be between 0 and 100."
                )
                return False

        if flag_type == FeatureFlagType.USER_SEGMENT and not isinstance(value, list):
            logger.warning(
                f"Invalid user segment value: {value} (type: {type(value).__name__}). "
                f"Expected list of segment names."
            )
            return False

        if flag_type == FeatureFlagType.TIME_BASED:
            if not isinstance(value, dict):
                logger.warning(
                    f"Invalid time-based value: {value} (type: {type(value).__name__}). "
                    f"Expected dictionary with start_time/end_time keys."
                )
                return False

            # Validate datetime values in time-based flags
            if isinstance(value, dict):
                from datetime import datetime

                for key, val in value.items():
                    if isinstance(val, datetime):
                        value[key] = ensure_utc(val)
                    elif isinstance(val, str) and "T" in val:  # Likely ISO datetime
                        try:
                            dt = datetime.fromisoformat(val.replace("Z", "+00:00"))
                            value[key] = ensure_utc(dt).isoformat()
                        except ValueError:
                            logger.warning(
                                f"Invalid datetime string in time-based flag: {val}. "
                                f"Expected ISO format (YYYY-MM-DDThh:mm:ssZ)"
                            )
                            # Continue with original value

        # Update the registry
        self.registry.set_value(flag_name, value)

        # Persist to database if requested
        if persist:
            await self.repository.update(flag_name, {"value": value})

        logger.info(f"Feature flag {flag_name} value updated to: {value}")
        return True

    async def create_flag(
        self, flag_data: Union[Dict[str, Any], FeatureFlagCreate]
    ) -> Optional[FeatureFlagResponse]:
        """
        Create a new feature flag.

        Args:
            flag_data: Feature flag data

        Returns:
            The created feature flag as a response object, or None if creation failed

        Note:
            This method persists the flag to the database and registers it in the in-memory registry.
            It returns a FeatureFlagResponse with proper UTC timezone conversion, per ADR-011.
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
                metadata=flag.flag_metadata,
                is_system=flag.is_system,
            )

            # Convert to response model to ensure proper UTC conversion
            response = FeatureFlagResponse(
                name=flag.name,
                description=flag.description,
                flag_type=flag.flag_type,
                value=flag.value,
                flag_metadata=flag.flag_metadata,
                is_system=flag.is_system,
                created_at=ensure_utc(flag.created_at),
                updated_at=ensure_utc(flag.updated_at),
            )

            logger.info(f"Feature flag created: {flag.name}")

            # Return the response object with proper timezone conversion
            return response

        except Exception as e:
            logger.error(f"Error creating feature flag: {e}")
            return None

    async def update_flag(
        self, flag_name: str, flag_data: Union[Dict[str, Any], FeatureFlagUpdate]
    ) -> Optional[FeatureFlagResponse]:
        """
        Update an existing feature flag.

        Args:
            flag_name: Name of the flag to update
            flag_data: Updated flag data

        Returns:
            The updated feature flag as a response object, or None if update failed

        Note:
            This method updates both the database and the in-memory registry.
            It returns a FeatureFlagResponse with proper UTC timezone conversion, per ADR-011.
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

            # Convert to response model to ensure proper UTC conversion
            response = FeatureFlagResponse(
                name=updated_flag.name,
                description=updated_flag.description,
                flag_type=updated_flag.flag_type,
                value=updated_flag.value,
                flag_metadata=updated_flag.flag_metadata,
                is_system=updated_flag.is_system,
                created_at=ensure_utc(updated_flag.created_at),
                updated_at=ensure_utc(updated_flag.updated_at),
            )

            logger.info(f"Feature flag updated: {flag_name}")
            return response

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

    async def get_all_flags(
        self,
        include_details: bool = True,
        prefix: Optional[str] = None,
        enabled_only: bool = False,
    ) -> List[FeatureFlagResponse]:
        """
        Get all feature flags with optional filtering.

        Args:
            include_details: Whether to include full details (metadata, etc.)
            prefix: Filter flags by name prefix
            enabled_only: Only return enabled flags

        Returns:
            List of feature flag responses
        """
        # Get flags from database to ensure we have the full details
        db_flags = await self.repository.get_all()

        # Apply filters
        filtered_flags = []
        for flag in db_flags:
            # Apply prefix filter if specified
            if prefix and not flag.name.startswith(prefix):
                continue

            # Apply enabled_only filter if specified
            if enabled_only:
                # For boolean flags, check value directly
                if flag.flag_type == FeatureFlagType.BOOLEAN and not flag.value:
                    continue

                # For other flag types, we would need context to evaluate
                # Since we don't have context here, we include them

            filtered_flags.append(flag)

        # Convert to response schema
        return [
            FeatureFlagResponse(
                name=flag.name,
                description=flag.description,
                flag_type=flag.flag_type,
                value=flag.value,
                flag_metadata=flag.flag_metadata,
                is_system=flag.is_system,
                created_at=ensure_utc(flag.created_at),
                updated_at=ensure_utc(flag.updated_at),
            )
            for flag in filtered_flags
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
            flag_metadata=db_flag.flag_metadata,  # Changed field name
            is_system=db_flag.is_system,
            created_at=ensure_utc(db_flag.created_at),
            updated_at=ensure_utc(db_flag.updated_at),
        )

    async def bulk_update_flags(
        self, updates: Dict[str, Union[Dict[str, Any], FeatureFlagUpdate]]
    ) -> Dict[str, FeatureFlagResponse]:
        """
        Update multiple feature flags in a single operation.

        Args:
            updates: Dictionary mapping flag names to update data

        Returns:
            Dictionary mapping flag names to updated flag responses
        """
        result = {}

        for flag_name, update_data in updates.items():
            # update_flag now returns a FeatureFlagResponse with proper UTC conversion
            response = await self.update_flag(flag_name, update_data)
            if response:
                result[flag_name] = response

        return result

    async def reset(self) -> None:
        """
        Reset the service state for testing.
        
        This method:
        1. Resets the internal initialization flag
        2. Clears the registry state
        3. Removes all observers
        
        This is primarily intended for testing scenarios where
        service state needs to be reset between tests.
        """
        self._initialized = False
        self.registry.reset()
        logger.info("Feature flag service reset to initial state")
        
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
        logger.info(
            f"Feature flag '{flag_name}' changed: {old_value} -> {new_value}",
            extra={
                "flag_name": flag_name,
                "old_value": old_value,
                "new_value": new_value,
                "source": "registry_notification",
            },
        )
