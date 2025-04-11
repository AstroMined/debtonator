"""
Feature Flag Service Interceptor.

This module provides the ServiceInterceptor class that enforces feature flag requirements
at the service layer. The interceptor checks method calls against feature flag requirements
and blocks operations that are protected by disabled features.

This is part of the implementation of ADR-024: Feature Flag System.
"""

import fnmatch
import functools
import logging
import time
from typing import Any, Callable, Dict, List, Optional, Set, Tuple, Union

from src.config.providers.feature_flags import ConfigProvider
from src.errors.feature_flags import FeatureDisabledError
from src.services.feature_flags import FeatureFlagService

# Configure logger
logger = logging.getLogger(__name__)

# Type aliases for better readability
MethodName = str
AccountType = str
PatternRequirements = Dict[str, Dict[MethodName, Union[bool, Dict[AccountType, bool]]]]
CacheEntry = Tuple[float, PatternRequirements]  # (timestamp, data)


class ServiceInterceptor:
    """
    Intercepts service method calls to enforce feature flag requirements.
    
    This class provides a centralized mechanism for enforcing feature flag requirements
    at the service layer, keeping feature gate logic separate from business logic.
    """
    
    def __init__(
        self,
        feature_flag_service: FeatureFlagService,
        config_provider: ConfigProvider,
        cache_ttl: int = 60,  # 1 minute by default
    ):
        """
        Initialize the service interceptor.
        
        Args:
            feature_flag_service: Service for checking feature flag status
            config_provider: Provider for loading feature requirements
            cache_ttl: Cache time-to-live in seconds
        """
        self.feature_flag_service = feature_flag_service
        self.config_provider = config_provider
        self.cache_ttl = cache_ttl
        self._cache: Dict[str, CacheEntry] = {}
        
        logger.debug("Service interceptor initialized")
    
    async def intercept(
        self,
        service_class: str,
        method_name: str,
        args: Tuple[Any, ...],
        kwargs: Dict[str, Any],
    ) -> bool:
        """
        Intercept a service method call to check feature flags.
        
        Args:
            service_class: Name of the service class
            method_name: Name of the method being called
            args: Positional arguments to the method
            kwargs: Keyword arguments to the method
            
        Returns:
            True if the method call is allowed, otherwise raises an exception
            
        Raises:
            FeatureDisabledError: If a required feature is disabled
        """
        # Get account_type from args or kwargs
        account_type = self._extract_account_type(args, kwargs)
        
        # Get service requirements for all feature flags
        all_requirements = await self._get_all_requirements()
        
        # Check each feature flag's requirements
        for flag_name, requirements in all_requirements.items():
            # Check if this method is covered by any pattern
            for pattern, methods in requirements.items():
                if self._matches_pattern(method_name, pattern):
                    # If the method is in the methods list
                    if method_name in methods:
                        # Check requirement details
                        requirement = methods[method_name]
                        
                        # If requirement is a boolean, apply it regardless of account_type
                        if isinstance(requirement, bool) and requirement:
                            if not await self.feature_flag_service.is_enabled(flag_name):
                                raise FeatureDisabledError(
                                    feature_name=flag_name,
                                    entity_type="service_method",
                                    entity_id=method_name,
                                    operation=f"{service_class}.{method_name}"
                                )
                        
                        # If requirement is a dict, check for the specific account_type
                        elif isinstance(requirement, dict) and account_type:
                            # If this account_type is specifically regulated
                            if account_type in requirement and requirement[account_type]:
                                if not await self.feature_flag_service.is_enabled(flag_name):
                                    raise FeatureDisabledError(
                                        feature_name=flag_name,
                                        entity_type="account_type",
                                        entity_id=account_type,
                                        operation=f"{service_class}.{method_name}"
                                    )
                            # Check if there's a wildcard entry
                            elif "*" in requirement and requirement["*"]:
                                if not await self.feature_flag_service.is_enabled(flag_name):
                                    raise FeatureDisabledError(
                                        feature_name=flag_name,
                                        entity_type="service_method",
                                        entity_id=method_name,
                                        operation=f"{service_class}.{method_name}"
                                    )
        
        # If we get here, all checks passed
        logger.debug(
            f"Feature flag check passed for {service_class}.{method_name}",
            extra={
                "service": service_class,
                "method": method_name,
                "account_type": account_type
            }
        )
        return True
    
    def _matches_pattern(self, method_name: str, pattern: str) -> bool:
        """
        Check if a method name matches a pattern.
        
        Supports glob-style pattern matching (*, ?) and exact matches.
        
        Args:
            method_name: Name of the method
            pattern: Pattern to match against
            
        Returns:
            True if the method name matches the pattern, False otherwise
        """
        # Exact match
        if pattern == method_name:
            return True
        
        # Glob pattern matching
        if any(c in pattern for c in "*?[]"):
            return fnmatch.fnmatch(method_name, pattern)
        
        # No match
        return False
    
    def _extract_account_type(
        self, args: Tuple[Any, ...], kwargs: Dict[str, Any]
    ) -> Optional[str]:
        """
        Extract account_type from method arguments.
        
        This method attempts to find the account_type in several common patterns:
        1. Direct 'account_type' keyword argument
        2. 'data' or 'account_data' dictionary with 'account_type' key
        3. First positional argument if it's a string (assuming it's account_type)
        
        Args:
            args: Positional arguments
            kwargs: Keyword arguments
            
        Returns:
            Extracted account_type or None if not found
        """
        # Check for direct account_type keyword argument
        if "account_type" in kwargs:
            return kwargs["account_type"]
        
        # Check for account_type in data dictionary
        for data_param in ["data", "account_data", "account"]:
            if data_param in kwargs and isinstance(kwargs[data_param], dict):
                if "account_type" in kwargs[data_param]:
                    return kwargs[data_param]["account_type"]
        
        # Check for schema objects with account_type
        for param_name, param_value in kwargs.items():
            # Check for pydantic models with account_type attribute
            if hasattr(param_value, "account_type"):
                return getattr(param_value, "account_type")
            
            # Check for pydantic models with dict-like access
            if hasattr(param_value, "model_dump"):
                try:
                    data_dict = param_value.model_dump()
                    if "account_type" in data_dict:
                        return data_dict["account_type"]
                except Exception:
                    pass
        
        # Check first positional argument if it looks like an account_type
        if args and len(args) > 0 and isinstance(args[0], str):
            # Heuristic: account types are typically short, lowercase strings
            if args[0].lower() in {
                "checking", "savings", "credit", "investment", 
                "loan", "mortgage", "retirement", "ewa", "bnpl", 
                "payment_app", "paymentapp"  # Handle variations
            }:
                return args[0].lower()
        
        # No account_type found
        return None
    
    async def _get_all_requirements(self) -> PatternRequirements:
        """
        Get all service requirements with caching.
        
        Returns a dictionary mapping feature names to their service method requirements.
        
        Returns:
            Dictionary of feature flag requirements
        """
        # Get current time for cache check
        current_time = time.time()
        
        # Check if cache is valid
        if "service_requirements" in self._cache:
            cache_time, cached_data = self._cache["service_requirements"]
            if current_time - cache_time < self.cache_ttl:
                logger.debug("Using cached service requirements")
                return cached_data
        
        # Cache expired or not found, get fresh data
        try:
            # Get all requirements from config provider
            all_reqs = await self.config_provider.get_all_requirements()
            
            # Extract service requirements
            result = {}
            for feature_name, feature_reqs in all_reqs.items():
                if "service" in feature_reqs:
                    result[feature_name] = feature_reqs["service"]
            
            # Cache the result
            self._cache["service_requirements"] = (current_time, result)
            
            return result
        except Exception as e:
            logger.error(f"Error getting service requirements: {e}")
            
            # Return empty dict if no cache, or use expired cache in emergency
            if "service_requirements" in self._cache:
                logger.warning("Using expired cache due to error")
                return self._cache["service_requirements"][1]
            
            return {}
    
    async def invalidate_cache(self) -> None:
        """
        Invalidate the requirements cache.
        
        This method should be called when feature flag requirements are updated.
        """
        if "service_requirements" in self._cache:
            del self._cache["service_requirements"]
        logger.debug("Service requirements cache invalidated")
