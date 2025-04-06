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
from src.errors.feature_flags import FeatureFlagAccountError
from src.errors.http_exceptions import (
    AccountHTTPException,
    AccountNotFoundHTTPException,
    AccountOperationHTTPException,
    AccountTypeHTTPException,
    AccountValidationHTTPException,
    FeatureFlagAccountHTTPException,
)


def account_error_to_http_exception(error: AccountError) -> AccountHTTPException:
    """Convert an AccountError to an appropriate HTTP exception."""
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
    elif isinstance(error, FeatureFlagAccountError):
        return FeatureFlagAccountHTTPException(
            flag_name=error.details.get("feature_flag"),
            message=error.message,
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
