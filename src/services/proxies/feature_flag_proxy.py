"""
Feature Flag Service Proxy.

This module provides the ServiceProxy class that wraps service objects to enforce
feature flag requirements. The proxy intercepts method calls and uses the
ServiceInterceptor to check if the method call should be allowed based on feature flags.

This is part of the implementation of ADR-024: Feature Flag System.
"""

import asyncio
import functools
import inspect
import logging
from typing import Any, Callable, Dict, Optional, Type, Union

from src.config.providers.feature_flags import ConfigProvider
from src.errors.feature_flags import FeatureDisabledError
from src.services.feature_flags import FeatureFlagService
from src.services.interceptors.feature_flag_interceptor import ServiceInterceptor

# Configure logger
logger = logging.getLogger(__name__)


class ServiceProxy:
    """
    Proxy that wraps service objects to enforce feature flag requirements.
    
    This class provides a clean separation between service business logic and
    feature flag enforcement by intercepting method calls and checking them
    against feature flag requirements.
    """
    
    def __init__(
        self,
        service: Any,
        feature_flag_service: FeatureFlagService,
        config_provider: ConfigProvider,
        interceptor: Optional[ServiceInterceptor] = None,
    ):
        """
        Initialize the service proxy.
        
        Args:
            service: The service object to wrap
            feature_flag_service: Service for checking feature flag status
            config_provider: Provider for loading feature requirements
            interceptor: Optional pre-configured interceptor to use
        """
        self._service = service
        self._service_class = service.__class__.__name__
        self._feature_flag_service = feature_flag_service
        self._config_provider = config_provider
        self._interceptor = interceptor or ServiceInterceptor(
            feature_flag_service=feature_flag_service,
            config_provider=config_provider,
        )
        
        logger.debug(
            f"ServiceProxy initialized for {self._service_class}",
            extra={"service": self._service_class}
        )
    
    def __getattr__(self, name: str) -> Any:
        """
        Intercept attribute access to wrap methods with feature checking.
        
        Args:
            name: Name of the attribute being accessed
            
        Returns:
            The wrapped method if it's a callable, otherwise the original attribute
            
        Raises:
            AttributeError: If the attribute doesn't exist
        """
        # Get the original attribute
        original_attr = getattr(self._service, name)
        
        # If not a method, return as-is
        if not callable(original_attr):
            return original_attr
        
        # Create a wrapper for the method
        @functools.wraps(original_attr)
        async def wrapper(*args: Any, **kwargs: Any) -> Any:
            # Check if it's an async method
            is_async = asyncio.iscoroutinefunction(original_attr)
            
            # Intercept the method call to check feature flags
            try:
                await self._interceptor.intercept(
                    service_class=self._service_class,
                    method_name=name,
                    args=args,
                    kwargs=kwargs,
                )
                
                # Method call is allowed, execute it
                if is_async:
                    return await original_attr(*args, **kwargs)
                else:
                    return original_attr(*args, **kwargs)
                    
            except FeatureDisabledError as e:
                # Log the feature flag violation
                logger.warning(
                    f"Feature flag check failed: {e}",
                    extra={
                        "service": self._service_class,
                        "method": name,
                        "feature": e.feature_name,
                    }
                )
                # Re-raise the exception
                raise
        
        # If the original method is a normal function, we need a non-async wrapper
        if not asyncio.iscoroutinefunction(original_attr):
            @functools.wraps(original_attr)
            def sync_wrapper(*args: Any, **kwargs: Any) -> Any:
                # For synchronous methods, we need to run the async check in a new event loop
                try:
                    # Create a new event loop for the async check
                    loop = asyncio.new_event_loop()
                    try:
                        # Run the interceptor in the event loop
                        loop.run_until_complete(
                            self._interceptor.intercept(
                                service_class=self._service_class,
                                method_name=name,
                                args=args,
                                kwargs=kwargs,
                            )
                        )
                    finally:
                        loop.close()
                        
                    # Method call is allowed, execute it
                    return original_attr(*args, **kwargs)
                    
                except FeatureDisabledError as e:
                    # Log the feature flag violation
                    logger.warning(
                        f"Feature flag check failed: {e}",
                        extra={
                            "service": self._service_class,
                            "method": name,
                            "feature": e.feature_name,
                        }
                    )
                    # Re-raise the exception
                    raise
            
            return sync_wrapper
        
        return wrapper
    
    def invalidate_cache(self) -> None:
        """
        Invalidate the interceptor's cache.
        
        This method should be called when feature flag requirements are updated.
        """
        # Create a new event loop for the async operation
        loop = asyncio.new_event_loop()
        try:
            loop.run_until_complete(self._interceptor.invalidate_cache())
        finally:
            loop.close()
        
        logger.debug(
            f"Cache invalidated for {self._service_class}",
            extra={"service": self._service_class}
        )
