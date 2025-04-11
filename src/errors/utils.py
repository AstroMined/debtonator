"""
Utility functions for error handling.

This module provides utility functions for converting between error types
and other error-related operations.
"""

from fastapi import status

from src.errors.accounts import (
    AccountError,
    AccountNotFoundError,
    AccountOperationError,
    AccountTypeError,
    AccountValidationError,
)
from src.errors.feature_flags import (
    FeatureFlagError,
    FeatureDisabledError,
    FeatureConfigurationError,
    FeatureFlagAccountError
)
from src.errors.http_exceptions import (
    AccountHTTPException,
    AccountNotFoundHTTPException,
    AccountOperationHTTPException,
    AccountTypeHTTPException,
    AccountValidationHTTPException,
    FeatureFlagHTTPException,
    FeatureDisabledHTTPException,
    FeatureConfigurationHTTPException,
    FeatureFlagAccountHTTPException,
)


def feature_flag_error_to_http_exception(error: FeatureFlagError) -> FeatureFlagHTTPException:
    """Convert a FeatureFlagError to an appropriate HTTP exception."""
    if isinstance(error, FeatureFlagAccountError):
        return FeatureFlagAccountHTTPException(
            flag_name=error.feature_name,
            message=error.message,
            details=error.details,
        )
    elif isinstance(error, FeatureDisabledError):
        return FeatureDisabledHTTPException(
            feature_name=error.feature_name,
            entity_type=error.entity_type,
            entity_id=error.entity_id,
            message=error.message,
            details=error.details,
        )
    elif isinstance(error, FeatureConfigurationError):
        return FeatureConfigurationHTTPException(
            feature_name=error.feature_name,
            config_issue=error.config_issue,
            message=error.message,
            details=error.details,
        )
    else:
        # Generic fallback
        return FeatureFlagHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
            feature_name=getattr(error, "feature_name", "unknown"),
            details=getattr(error, "details", None),
        )


def account_error_to_http_exception(error: AccountError) -> AccountHTTPException:
    """Convert an AccountError to an appropriate HTTP exception."""
    # If it's also a FeatureFlagError, use that handler
    if isinstance(error, FeatureFlagError):
        return feature_flag_error_to_http_exception(error)
        
    if isinstance(error, AccountNotFoundError):
        return AccountNotFoundHTTPException(
            account_id=error.details.get("account_id"), message=error.message
        )
    elif isinstance(error, AccountTypeError):
        return AccountTypeHTTPException(
            account_type=error.details.get("account_type"), message=error.message
        )
    elif isinstance(error, AccountValidationError):
        return AccountValidationHTTPException(
            message=error.message,
            field_errors=error.details.get("field_errors"),
            details=error.details,
        )
    elif isinstance(error, AccountOperationError):
        return AccountOperationHTTPException(
            operation=error.details.get("operation"),
            message=error.message,
            details=error.details,
        )
    else:
        # Generic fallback
        return AccountHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
            details=getattr(error, "details", None),
        )
