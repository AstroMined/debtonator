"""
Feature flag related errors.

This module provides a comprehensive hierarchy of errors related to the feature flag system,
as specified in ADR-024. These errors are used across all layers of the application to
provide consistent error handling for feature flag violations.
"""

from typing import Any, Dict, Optional, Union
from src.errors.accounts import AccountError  # Import base account error


class FeatureFlagError(Exception):
    """Base class for all feature flag related errors."""

    def __init__(
        self,
        message: str,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.message = message
        self.details = details or {}
        super().__init__(message)


class FeatureDisabledError(FeatureFlagError):
    """
    Error raised when a disabled feature is accessed.
    
    This error is raised by the feature flag system when an attempt is made to use
    functionality that is controlled by a disabled feature flag.
    """

    def __init__(
        self,
        feature_name: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[Union[str, int]] = None,
        operation: Optional[str] = None,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.feature_name = feature_name
        self.entity_type = entity_type
        self.entity_id = entity_id
        self.operation = operation
        
        # Construct detailed error message
        if not message:
            message = f"Operation not available: feature '{feature_name}' is disabled"
            
            if entity_type:
                message += f" for {entity_type}"
                if entity_id:
                    message += f" (id: {entity_id})"
            
            if operation:
                message += f" during {operation}"
        
        # Add context to details
        combined_details = details or {}
        combined_details.update({
            "feature_name": feature_name,
            "error_type": "feature_disabled",
        })
        
        if entity_type:
            combined_details["entity_type"] = entity_type
        if entity_id:
            combined_details["entity_id"] = entity_id
        if operation:
            combined_details["operation"] = operation
            
        super().__init__(message, combined_details)


class FeatureConfigurationError(FeatureFlagError):
    """
    Error raised when there's an issue with feature flag configuration.
    
    This error indicates problems with the feature flag system itself, such as
    missing configurations, invalid requirements, or conflicting settings.
    """

    def __init__(
        self,
        feature_name: Optional[str] = None,
        config_issue: str = "Invalid configuration",
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        self.feature_name = feature_name
        self.config_issue = config_issue
        
        # Construct detailed error message
        if not message:
            message = f"Feature flag configuration error: {config_issue}"
            if feature_name:
                message += f" for feature '{feature_name}'"
        
        # Add context to details
        combined_details = details or {}
        combined_details.update({
            "error_type": "feature_configuration",
            "config_issue": config_issue,
        })
        
        if feature_name:
            combined_details["feature_name"] = feature_name
            
        super().__init__(message, combined_details)


# Account-specific feature flag errors with multiple inheritance
class FeatureFlagAccountError(FeatureDisabledError, AccountError):
    """
    Error raised when a feature flag prevents an account operation.
    
    This class maintains backward compatibility with existing code while
    providing the enhanced functionality of FeatureDisabledError.
    Multiple inheritance ensures it works with both error handling systems.
    """

    def __init__(
        self,
        flag_name: str,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        # Initialize FeatureDisabledError
        FeatureDisabledError.__init__(
            self,
            feature_name=flag_name,
            entity_type="account",
            message=message,
            details=details,
        )
        
        # Also initialize AccountError to ensure proper MRO
        AccountError.__init__(
            self,
            message=self.message,
            details=self.details
        )
