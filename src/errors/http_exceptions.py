"""
HTTP-specific exceptions for account operations.

This module provides HTTP exceptions that can be used directly in API endpoints
or converted from regular account errors.
"""

from typing import Any, Dict, Optional, Union

from fastapi import HTTPException, status


class AccountHTTPException(HTTPException):
    """Base class for account HTTP exceptions."""

    def __init__(
        self,
        status_code: int,
        detail: str,
        headers: Optional[Dict[str, str]] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        error_detail = {"message": detail}
        if details:
            error_detail.update(details)
        super().__init__(status_code=status_code, detail=error_detail, headers=headers)


class AccountNotFoundHTTPException(AccountHTTPException):
    """HTTP exception for account not found."""

    def __init__(self, account_id: int, message: Optional[str] = None):
        message = message or f"Account with ID {account_id} not found"
        super().__init__(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=message,
            details={"account_id": account_id},
        )


class AccountTypeHTTPException(AccountHTTPException):
    """HTTP exception for account type issues."""

    def __init__(self, account_type: str, message: Optional[str] = None):
        message = message or f"Invalid or unsupported account type: {account_type}"
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
            details={"account_type": account_type},
        )


class AccountValidationHTTPException(AccountHTTPException):
    """HTTP exception for account validation failures."""

    def __init__(
        self,
        message: str,
        field_errors: Optional[Dict[str, str]] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        combined_details = details or {}
        if field_errors:
            combined_details["field_errors"] = field_errors
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=message,
            details=combined_details,
        )


class AccountOperationHTTPException(AccountHTTPException):
    """HTTP exception for account operation failures."""

    def __init__(
        self,
        operation: str,
        message: str,
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None,
    ):
        combined_details = details or {}
        combined_details["operation"] = operation
        super().__init__(
            status_code=status_code, detail=message, details=combined_details
        )


# Feature Flag HTTP Exceptions

class FeatureFlagHTTPException(HTTPException):
    """Base HTTP exception for feature flag errors."""
    
    def __init__(
        self,
        status_code: int,
        detail: str,
        feature_name: str,
        headers: Optional[Dict[str, str]] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        combined_details = {"message": detail}
        if details:
            combined_details.update(details)
        combined_details["feature_flag"] = feature_name
        super().__init__(status_code=status_code, detail=combined_details, headers=headers)


class FeatureDisabledHTTPException(FeatureFlagHTTPException):
    """HTTP exception for disabled features."""
    
    def __init__(
        self,
        feature_name: str,
        entity_type: Optional[str] = None,
        entity_id: Optional[Union[str, int]] = None,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        if not message:
            message = f"Operation not available: feature '{feature_name}' is disabled"
            if entity_type:
                message += f" for {entity_type}"
                if entity_id:
                    message += f" (id: {entity_id})"
                    
        combined_details = details or {}
        if entity_type:
            combined_details["entity_type"] = entity_type
        if entity_id:
            combined_details["entity_id"] = entity_id
            
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message,
            feature_name=feature_name,
            details=combined_details,
        )


class FeatureConfigurationHTTPException(FeatureFlagHTTPException):
    """HTTP exception for feature configuration issues."""
    
    def __init__(
        self,
        feature_name: Optional[str] = None,
        config_issue: str = "Invalid configuration",
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        if not message:
            message = f"Feature flag configuration error: {config_issue}"
            if feature_name:
                message += f" for feature '{feature_name}'"
                
        combined_details = details or {}
        combined_details["config_issue"] = config_issue
        
        super().__init__(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=message,
            feature_name=feature_name or "unknown",
            details=combined_details,
        )


# Update existing FeatureFlagAccountHTTPException to use multiple inheritance
class FeatureFlagAccountHTTPException(FeatureDisabledHTTPException, AccountHTTPException):
    """HTTP exception for feature flag restrictions on accounts."""

    def __init__(
        self,
        flag_name: str,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        message = message or f"Operation not available: feature '{flag_name}' is disabled for account"
        combined_details = details or {}
        
        # Initialize FeatureDisabledHTTPException
        FeatureDisabledHTTPException.__init__(
            self,
            feature_name=flag_name,
            entity_type="account",
            message=message,
            details=combined_details,
        )
