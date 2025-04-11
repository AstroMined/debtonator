"""
Feature Flag Middleware for API layer enforcement.

This middleware enforces feature flag requirements at the API layer by intercepting
HTTP requests and checking if the requested endpoint requires a feature flag.
If the required feature flag is disabled, a FeatureDisabledError is raised.

This is part of the implementation of ADR-024: Feature Flag System.
"""

import logging
import re
import time
from typing import Callable, Dict, Optional, Tuple, Any

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

from src.errors.feature_flags import FeatureDisabledError, FeatureConfigurationError
from src.config.providers.feature_flags import ConfigProvider

# Configure logger
logger = logging.getLogger(__name__)


class FeatureFlagMiddleware(BaseHTTPMiddleware):
    """
    Middleware that enforces feature flag requirements at the API layer.
    
    This middleware intercepts HTTP requests and checks if the requested endpoint
    requires a feature flag. If the required feature flag is disabled, a
    FeatureDisabledError is raised, which will be caught by the FastAPI exception
    handler and converted to an appropriate HTTP response.
    """
    
    def __init__(
        self, 
        app,
        feature_flag_service,
        config_provider: ConfigProvider,
        cache_ttl: int = 30  # Default cache TTL in seconds
    ):
        """
        Initialize the feature flag middleware.
        
        Args:
            app: The FastAPI application
            feature_flag_service: The feature flag service for checking flag status
            config_provider: The config provider for loading requirements
            cache_ttl: Cache time-to-live in seconds
        """
        super().__init__(app)
        self.feature_flag_service = feature_flag_service
        self.config_provider = config_provider
        self._cache: Dict[str, Dict[str, Any]] = {}  # {flag_name: {path_pattern: account_types}}
        self._cache_expiry = 0
        self._cache_ttl = cache_ttl
        
    async def dispatch(self, request: Request, call_next: Callable):
        """
        Process incoming requests to check feature flags.
        
        Args:
            request: The incoming HTTP request
            call_next: The next middleware or route handler
            
        Returns:
            The HTTP response
            
        Raises:
            FeatureDisabledError: If a required feature flag is disabled
        """
        # Check if the request should be blocked based on feature flags
        try:
            # Get all flag_name, path_pattern pairs that match this request path
            matches = await self._get_matching_patterns(request.url.path)
            
            # Check each matching flag to see if it's enabled
            for flag_name, path_pattern, account_types in matches:
                if not await self.feature_flag_service.is_enabled(flag_name):
                    # Convert list of account types to more readable string
                    account_type_str = ", ".join(account_types) if account_types else "all"
                    
                    # Raise domain exception - will be caught by FastAPI's exception handler
                    logger.info(
                        f"Blocking request to {request.url.path} - feature '{flag_name}' is disabled",
                        extra={
                            "path": request.url.path, 
                            "feature": flag_name,
                            "account_types": account_types
                        }
                    )
                    
                    raise FeatureDisabledError(
                        feature_name=flag_name,
                        entity_type="api_endpoint",
                        entity_id=request.url.path,
                        details={
                            "path_pattern": path_pattern,
                            "account_types": account_types
                        }
                    )
                        
            # Log successful check if we had matches
            if matches:
                logger.debug(
                    f"Feature flag check passed for {request.url.path}",
                    extra={"path": request.url.path}
                )
            
            # Proceed with the request
            return await call_next(request)
            
        except FeatureConfigurationError:
            # Configuration errors should propagate to exception handlers
            raise
        except Exception as e:
            # Log unexpected errors and then re-raise
            logger.error(f"Unexpected error in FeatureFlagMiddleware: {e}")
            raise
    
    async def _get_matching_patterns(self, path: str) -> list:
        """
        Get all flag_name, path_pattern pairs that match the given path.
        
        Args:
            path: The request path to check
            
        Returns:
            List of (flag_name, path_pattern, account_types) tuples that match the path
            
        Raises:
            FeatureConfigurationError: If requirements cannot be loaded
        """
        # Refresh cache if needed
        await self._refresh_cache_if_needed()
        
        matches = []
        
        # Check all flag requirements
        for flag_name, path_patterns in self._cache.items():
            for path_pattern, account_types in path_patterns.items():
                # Check if the pattern matches the path
                if self._matches_pattern(path, path_pattern):
                    matches.append((flag_name, path_pattern, account_types))
                    
        return matches
    
    def _matches_pattern(self, path: str, pattern: str) -> bool:
        """
        Check if a path matches a pattern.
        
        Args:
            path: The request path
            pattern: The pattern to match against
            
        Returns:
            True if the path matches the pattern, False otherwise
        """
        # Convert API path pattern to regex
        # Replace {param} with ([^/]+) to match any non-slash characters
        regex_pattern = pattern.replace("{", "(?P<").replace("}", ">[^/]+)")
        
        # Replace asterisks with wildcard pattern, but only if they're at the end
        if regex_pattern.endswith("*"):
            regex_pattern = regex_pattern[:-1] + ".*"
        
        # Check if the path matches the pattern
        return bool(re.match(f"^{regex_pattern}$", path))
        
    async def _refresh_cache_if_needed(self):
        """
        Refresh the cache if it's expired.
        
        Raises:
            FeatureConfigurationError: If requirements cannot be loaded
        """
        current_time = time.time()
        if current_time > self._cache_expiry:
            await self._load_requirements()
            self._cache_expiry = current_time + self._cache_ttl
    
    async def _load_requirements(self):
        """
        Load API requirements from the config provider.
        
        Raises:
            FeatureConfigurationError: If requirements cannot be loaded
        """
        try:
            # Get all requirements
            all_requirements = await self.config_provider.get_all_requirements()
            
            # Transform requirements to our cache format {flag_name: {path_pattern: account_types}}
            transformed_requirements = {}
            for flag_name, requirements in all_requirements.items():
                if "api" in requirements:
                    path_patterns = {}
                    for path_pattern, account_types in requirements["api"].items():
                        path_patterns[path_pattern] = account_types
                    
                    if path_patterns:
                        transformed_requirements[flag_name] = path_patterns
                
            self._cache = transformed_requirements
            
        except Exception as e:
            logger.error(f"Error loading API requirements: {e}")
            # Keep existing cache if available
            if not self._cache:
                self._cache = {}
            raise FeatureConfigurationError(
                config_issue=f"Failed to load API requirements: {str(e)}"
            )
