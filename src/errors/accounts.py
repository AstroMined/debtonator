"""
Base error classes for account operations.

This module provides the core error classes used throughout the account system.
More specific error types can be found in the account_types subdirectory.
"""

from typing import Any, Dict, Optional


class AccountError(Exception):
    """Base class for all account-related errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(message)

    def to_dict(self) -> Dict[str, Any]:
        """Convert the error to a dictionary."""
        result = {
            "error": self.__class__.__name__,
            "message": self.message,
        }
        if self.details:
            result["details"] = self.details
        return result


class AccountNotFoundError(AccountError):
    """Error raised when an account is not found."""

    def __init__(self, account_id: int, message: Optional[str] = None):
        message = message or f"Account with ID {account_id} not found"
        super().__init__(message, {"account_id": account_id})


class AccountTypeError(AccountError):
    """Error raised for account type issues."""

    def __init__(self, account_type: str, message: Optional[str] = None):
        message = message or f"Invalid or unsupported account type: {account_type}"
        super().__init__(message, {"account_type": account_type})


class AccountValidationError(AccountError):
    """Error raised for account validation failures."""

    def __init__(
        self,
        message: str,
        field_errors: Optional[Dict[str, str]] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        combined_details = details or {}
        if field_errors:
            combined_details["field_errors"] = field_errors
        super().__init__(message, combined_details)


class AccountOperationError(AccountError):
    """Error raised when an account operation fails."""

    def __init__(
        self, operation: str, message: str, details: Optional[Dict[str, Any]] = None
    ):
        combined_details = details or {}
        combined_details["operation"] = operation
        super().__init__(message, combined_details)
