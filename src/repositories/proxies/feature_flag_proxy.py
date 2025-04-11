"""
Feature Flag Repository Proxy implementation.

This module provides a proxy implementation that intercepts repository method calls
and enforces feature flag requirements. It's a key component of the centralized
feature flag system defined in ADR-024.

The proxy wraps repository instances and uses the feature flag service and config
provider to determine if a method should be allowed based on current feature flag
settings.
"""

import inspect
import logging
import re
from functools import wraps
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Type, Union, cast

from src.config.providers.feature_flags import ConfigProvider
from src.errors.feature_flags import FeatureConfigurationError, FeatureDisabledError

# Configure logger
logger = logging.getLogger(__name__)


class FeatureFlagRepositoryProxy:
    """
    Repository proxy that enforces feature flag requirements.
    
    This proxy wraps repository instances and intercepts method calls to check
    if they're allowed based on feature flag settings. It extracts account types
    from method arguments and compares them against the requirements defined for
    each feature flag.
    """
    
    def __init__(
        self,
        repository: Any,
        feature_flag_service: Any,
        config_provider: ConfigProvider,
    ):
        """
        Initialize the repository proxy.
        
        Args:
            repository: Repository instance to wrap
            feature_flag_service: Service for checking feature flag values
            config_provider: Provider for loading feature requirements
        """
        self._repository = repository
        self._feature_flag_service = feature_flag_service
        self._config_provider = config_provider
        self._method_cache: Dict[str, Callable] = {}
        
        # Store repository class name for logging
        self._repository_class_name = repository.__class__.__name__
        
        # Set up memoization for faster repeated lookups
        self._feature_check_cache: Dict[str, Dict[str, bool]] = {}
    
    def __getattr__(self, name: str) -> Any:
        """
        Intercept attribute access to wrap method calls.
        
        Args:
            name: Name of the attribute being accessed
            
        Returns:
            Wrapped method if it's a callable, or original attribute
            
        Raises:
            AttributeError: If the attribute doesn't exist
        """
        # Get the original attribute
        attr = getattr(self._repository, name)
        
        # If it's not a method, return it directly
        if not callable(attr):
            return attr
        
        # Check if we've already wrapped this method
        if name in self._method_cache:
            return self._method_cache[name]
        
        # Wrap the method with feature flag checking
        @wraps(attr)
        async def wrapped(*args: Any, **kwargs: Any) -> Any:
            # Check if this method is restricted by any feature flags
            await self._check_feature_requirements(name, args, kwargs)
            
            # Call the original method
            return await attr(*args, **kwargs)
        
        # Cache the wrapped method
        self._method_cache[name] = wrapped
        
        return wrapped
    
    async def _check_feature_requirements(
        self, method_name: str, args: Tuple[Any, ...], kwargs: Dict[str, Any]
    ) -> None:
        """
        Check if the method call is allowed based on feature requirements.
        
        Args:
            method_name: Name of the method being called
            args: Positional arguments to the method
            kwargs: Keyword arguments to the method
            
        Raises:
            FeatureDisabledError: If the method is not allowed
        """
        # Get all feature requirements
        all_requirements = await self._config_provider.get_all_requirements()
        
        # Extract account type from arguments
        account_type = self._extract_account_type(method_name, args, kwargs)
        
        # If no account type found and not a general method, allow it
        if not account_type and not method_name.startswith("get_all"):
            logger.debug(
                f"No account type found for {self._repository_class_name}.{method_name}, "
                "allowing method call"
            )
            return
        
        # Check each feature flag's requirements
        for feature_name, requirements in all_requirements.items():
            # Skip if this feature doesn't have repository requirements
            if "repository" not in requirements:
                continue
            
            repository_requirements = requirements["repository"]
            
            # Skip if this method isn't in the requirements
            if method_name not in repository_requirements:
                continue
            
            # Get the account types required for this method
            required_account_types = repository_requirements[method_name]
            
            # Special case: wildcard matches all account types
            is_wildcard = any(t == "*" for t in required_account_types)
            
            # Skip if account type doesn't match requirements
            if not is_wildcard and account_type and account_type not in required_account_types:
                continue
            
            # Check if the feature is enabled, using cache if available
            cache_key = f"{feature_name}:{account_type}"
            if cache_key in self._feature_check_cache:
                feature_cache = self._feature_check_cache[cache_key]
                # Use cached result if not expired
                if method_name in feature_cache:
                    is_enabled = feature_cache[method_name]
                    if not is_enabled:
                        raise FeatureDisabledError(
                            feature_name=feature_name,
                            entity_type="account",
                            operation=method_name,
                            entity_id=self._extract_entity_id(args, kwargs),
                        )
                    # Feature is enabled, continue to next feature check
                    continue
            
            # Check if feature is enabled
            is_enabled = await self._is_feature_enabled(feature_name, account_type)
            
            # Cache the result
            if cache_key not in self._feature_check_cache:
                self._feature_check_cache[cache_key] = {}
            self._feature_check_cache[cache_key][method_name] = is_enabled
            
            # If feature is disabled and this method requires it, raise an error
            if not is_enabled:
                logger.info(
                    f"Blocking {self._repository_class_name}.{method_name} due to "
                    f"disabled feature {feature_name}"
                )
                raise FeatureDisabledError(
                    feature_name=feature_name,
                    entity_type="account" if account_type else None,
                    entity_id=self._extract_entity_id(args, kwargs),
                    operation=method_name,
                )
    
    def _extract_account_type(
        self, method_name: str, args: Tuple[Any, ...], kwargs: Dict[str, Any]
    ) -> Optional[str]:
        """
        Extract account type from method arguments.
        
        This method inspects both positional and keyword arguments to find
        account type information. It checks common parameter names and patterns
        used in repository methods.
        
        Args:
            method_name: Name of the method being called
            args: Positional arguments to the method
            kwargs: Keyword arguments to the method
            
        Returns:
            Account type string or None if not found
        """
        # Check for account_type in kwargs
        if "account_type" in kwargs:
            return str(kwargs["account_type"])
        
        # Check for type in kwargs
        if "type" in kwargs:
            return str(kwargs["type"])
        
        # Check for entity with account_type attribute in args or kwargs
        for arg in list(args) + list(kwargs.values()):
            if hasattr(arg, "account_type"):
                return str(getattr(arg, "account_type"))
        
        # Extract from method name for specific patterns
        if method_name.startswith(("create_", "update_", "get_", "validate_")):
            # Check if method is specific to an account type (e.g., create_bnpl_account)
            for account_type in ["bnpl", "ewa", "payment_app", "checking", "savings", "credit"]:
                if account_type in method_name:
                    return account_type
        
        # Get method signature to look for parameters
        try:
            sig = inspect.signature(getattr(self._repository.__class__, method_name))
            param_names = list(sig.parameters.keys())
            
            # Check if there's a parameter that might contain the account type
            for i, param_name in enumerate(param_names):
                if param_name in ["account_type", "type"] and i < len(args):
                    return str(args[i])
        except (ValueError, AttributeError):
            # Method might be dynamically added or signature inspection failed
            pass
        
        # If repository class name contains account type, use that
        repository_name = self._repository_class_name.lower()
        for account_type in ["bnpl", "ewa", "payment_app", "checking", "savings", "credit"]:
            if account_type in repository_name:
                return account_type
        
        # No account type found
        return None
    
    def _extract_entity_id(
        self, args: Tuple[Any, ...], kwargs: Dict[str, Any]
    ) -> Optional[Union[str, int]]:
        """
        Extract entity ID from method arguments.
        
        Args:
            args: Positional arguments to the method
            kwargs: Keyword arguments to the method
            
        Returns:
            Entity ID or None if not found
        """
        # Common ID parameter names
        id_param_names = ["id", "account_id", "entity_id", "record_id"]
        
        # Check kwargs first
        for name in id_param_names:
            if name in kwargs:
                return kwargs[name]
        
        # Check first argument if it's likely an ID (string or integer)
        if args and isinstance(args[0], (str, int)):
            return args[0]
        
        # Check for entity with id attribute
        for arg in list(args) + list(kwargs.values()):
            if hasattr(arg, "id"):
                return getattr(arg, "id")
        
        return None
    
    async def _is_feature_enabled(
        self, feature_name: str, account_type: Optional[str] = None
    ) -> bool:
        """
        Check if a feature is enabled, optionally for a specific account type.
        
        Args:
            feature_name: Name of the feature flag to check
            account_type: Optional account type to check against whitelist
            
        Returns:
            True if the feature is enabled, False otherwise
        """
        # Special case for testing - if feature flag service is None, allow everything
        if self._feature_flag_service is None:
            return True
        
        # Use the feature flag service to check if the feature is enabled
        try:
            is_enabled = await self._feature_flag_service.is_enabled(feature_name)
            
            # Feature is disabled - no need to check account type
            if not is_enabled:
                return False
            
            # Feature is enabled - check account type whitelist if applicable
            if account_type:
                if hasattr(self._feature_flag_service, 'get_account_types_whitelist'):
                    whitelist = await self._feature_flag_service.get_account_types_whitelist(feature_name)
                
                    # If whitelist is empty, all account types are allowed
                    if not whitelist:
                        return True
                    
                    # Check if account type is in whitelist
                    return account_type in whitelist
                else:
                    # Whitelist functionality not implemented, allow all types
                    return True
            
            # No account type - feature is enabled
            return True
            
        except Exception as e:
            # Log error and allow the operation to proceed (fail open)
            logger.error(
                f"Error checking feature {feature_name}: {e}. Allowing operation to proceed."
            )
            return True
