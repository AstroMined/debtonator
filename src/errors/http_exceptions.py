"""
HTTP-specific exceptions for account operations.

This module provides HTTP exceptions that can be used directly in API endpoints
or converted from regular account errors.
"""

from typing import Any, Dict, Optional

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


class FeatureFlagAccountHTTPException(AccountHTTPException):
    """HTTP exception for feature flag restrictions."""

    def __init__(
        self,
        flag_name: str,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        message = (
            message or f"Operation not available: feature '{flag_name}' is disabled"
        )
        combined_details = details or {}
        combined_details["feature_flag"] = flag_name
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message,
            details=combined_details,
        )
