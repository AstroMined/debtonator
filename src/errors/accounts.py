"""
Error classes for account operations.

This module provides a hierarchical structure of error classes for account operations,
following the error handling patterns defined in ADR-016 and ADR-019.
"""

from fastapi import HTTPException, status
from typing import Optional, Dict, Any, List


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
        details: Optional[Dict[str, Any]] = None
    ):
        combined_details = details or {}
        if field_errors:
            combined_details["field_errors"] = field_errors
        super().__init__(message, combined_details)


class AccountOperationError(AccountError):
    """Error raised when an account operation fails."""
    
    def __init__(self, operation: str, message: str, details: Optional[Dict[str, Any]] = None):
        combined_details = details or {}
        combined_details["operation"] = operation
        super().__init__(message, combined_details)


# Type-specific errors

class CheckingAccountError(AccountError):
    """Base class for checking account errors."""
    pass


class SavingsAccountError(AccountError):
    """Base class for savings account errors."""
    pass


class CreditAccountError(AccountError):
    """Base class for credit account errors."""
    pass


class PaymentAppAccountError(AccountError):
    """Base class for payment app account errors."""
    pass


class BNPLAccountError(AccountError):
    """Base class for BNPL account errors."""
    
    def __init__(self, message: str, account_id: Optional[int] = None, details: Optional[Dict[str, Any]] = None):
        combined_details = details or {}
        if account_id:
            combined_details["account_id"] = account_id
        super().__init__(message, combined_details)


class BNPLInstallmentError(BNPLAccountError):
    """Error raised for BNPL installment issues."""
    
    def __init__(
        self, 
        message: str, 
        account_id: Optional[int] = None,
        installment_number: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        combined_details = details or {}
        if installment_number:
            combined_details["installment_number"] = installment_number
        super().__init__(message, account_id, combined_details)


class EWAAccountError(AccountError):
    """Base class for EWA account errors."""
    pass


# Feature flag related errors

class FeatureFlagAccountError(AccountError):
    """Error raised when a feature flag prevents an account operation."""
    
    def __init__(
        self, 
        flag_name: str, 
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        message = message or f"Operation not available: feature '{flag_name}' is disabled"
        combined_details = details or {}
        combined_details["feature_flag"] = flag_name
        super().__init__(message, combined_details)


# HTTP API specific errors

class AccountHTTPException(HTTPException):
    """Base class for account HTTP exceptions."""
    
    def __init__(
        self, 
        status_code: int, 
        detail: str,
        headers: Optional[Dict[str, str]] = None,
        details: Optional[Dict[str, Any]] = None
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
            details={"account_id": account_id}
        )


class AccountTypeHTTPException(AccountHTTPException):
    """HTTP exception for account type issues."""
    
    def __init__(self, account_type: str, message: Optional[str] = None):
        message = message or f"Invalid or unsupported account type: {account_type}"
        super().__init__(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message,
            details={"account_type": account_type}
        )


class AccountValidationHTTPException(AccountHTTPException):
    """HTTP exception for account validation failures."""
    
    def __init__(
        self, 
        message: str, 
        field_errors: Optional[Dict[str, str]] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        combined_details = details or {}
        if field_errors:
            combined_details["field_errors"] = field_errors
        super().__init__(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=message,
            details=combined_details
        )


class AccountOperationHTTPException(AccountHTTPException):
    """HTTP exception for account operation failures."""
    
    def __init__(
        self, 
        operation: str, 
        message: str, 
        status_code: int = status.HTTP_400_BAD_REQUEST,
        details: Optional[Dict[str, Any]] = None
    ):
        combined_details = details or {}
        combined_details["operation"] = operation
        super().__init__(
            status_code=status_code,
            detail=message,
            details=combined_details
        )


class FeatureFlagAccountHTTPException(AccountHTTPException):
    """HTTP exception for feature flag restrictions."""
    
    def __init__(
        self, 
        flag_name: str, 
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        message = message or f"Operation not available: feature '{flag_name}' is disabled"
        combined_details = details or {}
        combined_details["feature_flag"] = flag_name
        super().__init__(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=message,
            details=combined_details
        )


# Error conversion utilities

def account_error_to_http_exception(error: AccountError) -> AccountHTTPException:
    """Convert an AccountError to an appropriate HTTP exception."""
    if isinstance(error, AccountNotFoundError):
        return AccountNotFoundHTTPException(
            account_id=error.details.get("account_id"),
            message=error.message
        )
    elif isinstance(error, AccountTypeError):
        return AccountTypeHTTPException(
            account_type=error.details.get("account_type"),
            message=error.message
        )
    elif isinstance(error, AccountValidationError):
        return AccountValidationHTTPException(
            message=error.message,
            field_errors=error.details.get("field_errors"),
            details=error.details
        )
    elif isinstance(error, FeatureFlagAccountError):
        return FeatureFlagAccountHTTPException(
            flag_name=error.details.get("feature_flag"),
            message=error.message,
            details=error.details
        )
    elif isinstance(error, AccountOperationError):
        return AccountOperationHTTPException(
            operation=error.details.get("operation"),
            message=error.message,
            details=error.details
        )
    else:
        # Generic fallback
        return AccountHTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(error),
            details=getattr(error, "details", None)
        )
