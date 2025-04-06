"""
Checking account specific errors.

This module provides error classes specific to checking accounts.
"""

from typing import Any, Dict, Optional

from src.errors.accounts import AccountError


class CheckingAccountError(AccountError):
    """Base class for checking account errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class CheckingOverdraftError(CheckingAccountError):
    """Error raised when there's an issue with overdraft protection."""

    def __init__(
        self,
        message: str,
        account_id: Optional[int] = None,
        current_balance: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        combined_details = details or {}
        if account_id:
            combined_details["account_id"] = account_id
        if current_balance is not None:
            combined_details["current_balance"] = current_balance
        super().__init__(message, combined_details)


class CheckingInsufficientFundsError(CheckingAccountError):
    """Error raised when there are insufficient funds for an operation."""

    def __init__(
        self,
        message: str,
        account_id: Optional[int] = None,
        current_balance: Optional[float] = None,
        required_amount: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        combined_details = details or {}
        if account_id:
            combined_details["account_id"] = account_id
        if current_balance is not None:
            combined_details["current_balance"] = current_balance
        if required_amount is not None:
            combined_details["required_amount"] = required_amount
        super().__init__(message, combined_details)


class CheckingInvalidRoutingNumberError(CheckingAccountError):
    """Error raised when the routing number is invalid."""

    def __init__(
        self,
        routing_number: str,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        message = message or f"Invalid routing number: {routing_number}"
        combined_details = details or {}
        combined_details["routing_number"] = routing_number
        super().__init__(message, combined_details)


class CheckingInternationalBankingError(CheckingAccountError):
    """Error raised for international banking field issues."""

    def __init__(
        self,
        field_name: str,
        value: str,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        message = message or f"Invalid {field_name}: {value}"
        combined_details = details or {}
        combined_details["field_name"] = field_name
        combined_details["value"] = value
        super().__init__(message, combined_details)
