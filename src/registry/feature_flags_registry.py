"""
Feature Flag Registry for in-memory storage and evaluation of feature flags.

This module provides the FeatureFlagRegistry class which maintains the in-memory state
of all feature flags in the system. It supports different flag types (boolean, percentage,
user segment, time-based) and provides methods for flag evaluation based on context.

The registry is a core component of the Feature Flag System defined in ADR-024.
"""

import hashlib
import logging
import threading
from datetime import datetime
from typing import Any, Dict, List, Optional, Protocol, Union

from src.schemas.feature_flags import FeatureFlagType
from src.utils.datetime_utils import ensure_utc, utc_datetime_from_str, utc_now

logger = logging.getLogger(__name__)


class FeatureFlagObserver(Protocol):
    """Protocol for objects that observe feature flag changes."""

    def flag_changed(self, flag_name: str, old_value: Any, new_value: Any) -> None:
        """Called when a feature flag's value changes."""


class FeatureFlagRegistry:
    """
    Central registry for feature flags and their current state.

    This class provides in-memory storage and evaluation logic for all feature flags.
    It supports different flag types (boolean, percentage, user segment, time-based)
    and provides methods for registering, retrieving, and updating flags.

    The registry uses the observer pattern to notify interested components
    when flag values change. This allows dependent components to react to
    feature flag changes without polling.

    Thread safety is ensured through a lock mechanism for all operations that
    modify the registry state.
    """

    def __init__(self):
        """Initialize an empty registry."""
        self._flags: Dict[str, Dict[str, Any]] = {}
        self._observers: List[FeatureFlagObserver] = []
        self._lock = threading.RLock()  # Reentrant lock for thread safety
        logger.info("Feature flag registry initialized")

    def register(
        self,
        flag_name: str,
        flag_type: Union[str, FeatureFlagType],
        default_value: Any,
        description: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None,
        is_system: bool = False,
    ) -> None:
        """
        Register a new feature flag.

        Args:
            flag_name: Unique identifier for the feature flag
            flag_type: Type of the feature flag (boolean, percentage, user_segment, time_based)
            default_value: Initial value for the feature flag
            description: Optional human-readable description
            metadata: Optional additional configuration data
            is_system: Whether this is a system-defined flag (protected)

        Raises:
            ValueError: If a flag with the given name already exists
        """
        with self._lock:
            if flag_name in self._flags:
                raise ValueError(f"Feature flag {flag_name} already registered")

            # Convert string flag_type to enum if necessary
            if isinstance(flag_type, str):
                flag_type = FeatureFlagType(flag_type.lower())

            self._flags[flag_name] = {
                "type": (
                    flag_type.value
                    if isinstance(flag_type, FeatureFlagType)
                    else flag_type
                ),
                "value": default_value,
                "description": description or f"Feature flag: {flag_name}",
                "metadata": metadata or {},
                "is_system": is_system,
                "registered_at": utc_now(),
            }

            logger.info("Feature flag registered: %s (%s)", flag_name, flag_type)

    def get_flag(self, flag_name: str) -> Optional[Dict[str, Any]]:
        """
        Get the configuration for a specific feature flag.

        Args:
            flag_name: Name of the feature flag

        Returns:
            Dict containing flag configuration, or None if not found
        """
        with self._lock:
            return self._flags.get(flag_name)

    def get_value(
        self, flag_name: str, context: Optional[Dict[str, Any]] = None
    ) -> Any:
        """
        Get the current value of a feature flag, evaluated in the given context.

        For boolean flags, this returns the raw value.
        For percentage rollout flags, this evaluates based on the user_id in the context.
        For user segment flags, this checks if the user is in any of the specified segments.
        For time-based flags, this checks if the current time is within the specified range.

        Args:
            flag_name: Name of the feature flag
            context: Optional context data for flag evaluation

        Returns:
            The evaluated flag value

        Raises:
            ValueError: If the flag does not exist
        """
        with self._lock:
            flag = self._flags.get(flag_name)
            if not flag:
                raise ValueError(f"Unknown feature flag: {flag_name}")

            # Default context if not provided
            context = context or {}

            # Boolean flags: just return the value
            if flag["type"] == FeatureFlagType.BOOLEAN:
                return flag["value"]

            # Percentage rollout: check if user_id falls within percentage
            if flag["type"] == FeatureFlagType.PERCENTAGE:
                user_id = context.get("user_id")
                if user_id:
                    percentage = flag["value"]
                    return self._is_user_in_percentage(user_id, flag_name, percentage)
                # If no user_id in context, treat as globally disabled
                return False

            # User segment: check if user is in any specified segment
            if flag["type"] == FeatureFlagType.USER_SEGMENT:
                segments = flag["value"]

                # Check admin segment
                if "admin" in segments and context.get("is_admin"):
                    return True

                # Check beta tester segment
                if "beta" in segments and context.get("is_beta_tester"):
                    return True

                # Check user groups
                user_groups = context.get("user_groups", [])
                if any(group in segments for group in user_groups):
                    return True

                # No segment match
                return False

            # Time-based: check if current time is within the specified range
            if flag["type"] == FeatureFlagType.TIME_BASED:
                now = utc_now()
                start_time = flag["value"].get("start_time")
                end_time = flag["value"].get("end_time")

                # Convert string timestamps to datetime if needed
                if isinstance(start_time, str):
                    start_time = utc_datetime_from_str(
                        start_time.replace("Z", "+00:00"), "%Y-%m-%dT%H:%M:%S.%f%z"
                    )
                if isinstance(end_time, str):
                    end_time = utc_datetime_from_str(
                        end_time.replace("Z", "+00:00"), "%Y-%m-%dT%H:%M:%S.%f%z"
                    )

                # Ensure datetimes are UTC-compliant per ADR-011
                if isinstance(start_time, datetime):
                    start_time = ensure_utc(start_time)
                if isinstance(end_time, datetime):
                    end_time = ensure_utc(end_time)

                # Check time range
                if start_time and now < start_time:
                    return False
                if end_time and now > end_time:
                    return False
                return True

            # Default fallback for unknown types
            return flag["value"]

    def set_value(self, flag_name: str, value: Any) -> None:
        """
        Set the value of a feature flag.

        This method notifies all registered observers if the flag value changes.

        Args:
            flag_name: Name of the feature flag
            value: New value for the flag

        Raises:
            ValueError: If the flag does not exist
        """
        with self._lock:
            flag = self._flags.get(flag_name)
            if not flag:
                raise ValueError(f"Unknown feature flag: {flag_name}")

            old_value = flag["value"]

            # Update the value
            flag["value"] = value
            flag["updated_at"] = utc_now()

            # Notify observers if value changed
            if old_value != value:
                logger.info("Feature flag value changed: %s = %s", flag_name, value)
                observers = (
                    self._observers.copy()
                )  # Copy to avoid issues if observers modify the list

                for observer in observers:
                    try:
                        observer.flag_changed(flag_name, old_value, value)
                    except (TypeError, ValueError, AttributeError, RuntimeError) as e:
                        logger.error(
                            "Error notifying observer about flag change: %s",
                            e,
                            exc_info=True,  # Include stack trace for better debugging
                            extra={
                                "flag_name": flag_name,
                                "old_value": old_value,
                                "new_value": value,
                                "observer": observer.__class__.__name__,
                            },
                        )

    def get_all_flags(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all registered feature flags and their current values.

        Returns:
            Dict mapping flag names to their configurations
        """
        with self._lock:
            return {name: flag.copy() for name, flag in self._flags.items()}

    def add_observer(self, observer: FeatureFlagObserver) -> None:
        """
        Add an observer to be notified when flag values change.

        Args:
            observer: Object implementing the FeatureFlagObserver protocol
        """
        with self._lock:
            if observer not in self._observers:
                self._observers.append(observer)
                logger.debug("Added feature flag observer: %s", observer)

    def remove_observer(self, observer: FeatureFlagObserver) -> None:
        """
        Remove an observer.

        Args:
            observer: Previously registered observer
        """
        with self._lock:
            if observer in self._observers:
                self._observers.remove(observer)
                logger.debug("Removed feature flag observer: %s", observer)

    def reset(self) -> None:
        """
        Reset the registry to its initial state.

        This method is primarily intended for testing scenarios where
        registry state needs to be cleaned between tests.
        """
        with self._lock:
            self._flags = {}
            self._observers = []
            logger.info("Feature flag registry reset to initial state")

    def get_all_flag_names(self) -> List[str]:
        """
        Get a list of all registered feature flag names.

        Returns:
            List of flag names
        """
        with self._lock:
            return list(self._flags.keys())

    def _is_user_in_percentage(
        self, user_id: str, flag_name: str, percentage: float
    ) -> bool:
        """
        Determine if a user falls within the percentage rollout.

        This uses a hash of the user_id and flag_name to ensure consistent behavior
        for the same user across different sessions.

        Args:
            user_id: User identifier
            flag_name: Feature flag name
            percentage: Percentage value (0-100)

        Returns:
            True if the user is within the percentage, False otherwise
        """
        # Create a hash from user_id and flag_name to ensure consistent behavior
        hash_input = f"{user_id}:{flag_name}"
        hash_value = int(hashlib.md5(hash_input.encode()).hexdigest(), 16)

        # Normalize to 0-100 range
        bucket = hash_value % 100

        # User is included if their bucket is below the percentage
        return bucket < percentage

# Global instance for convenience - follows singleton pattern
feature_flag_registry = FeatureFlagRegistry()
