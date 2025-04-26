"""
Credit account specific errors.

This module provides error classes specific to credit accounts.

All datetime handling follows ADR-011 requirements for UTC datetime standardization.
"""

from typing import Any, Dict, Optional

from src.errors.accounts import AccountError
from src.utils.datetime_utils import ensure_utc


class CreditAccountError(AccountError):
    """Base class for credit account errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class CreditCreditLimitExceededError(CreditAccountError):
    """Error raised when a transaction would exceed the credit limit."""

    def __init__(
        self,
        message: str,
        account_id: Optional[int] = None,
        current_balance: Optional[float] = None,
        credit_limit: Optional[float] = None,
        transaction_amount: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        combined_details = details or {}
        if account_id:
            combined_details["account_id"] = account_id
        if current_balance is not None:
            combined_details["current_balance"] = current_balance
        if credit_limit is not None:
            combined_details["credit_limit"] = credit_limit
        if transaction_amount is not None:
            combined_details["transaction_amount"] = transaction_amount
        super().__init__(message, combined_details)


class CreditPaymentDueError(CreditAccountError):
    """
    Error raised for payment due issues.

    Per ADR-011, ensures all datetime values are converted to UTC before processing.
    """

    def __init__(
        self,
        message: str,
        account_id: Optional[int] = None,
        due_date: Optional[Any] = None,
        minimum_payment: Optional[float] = None,
        statement_balance: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        combined_details = details or {}
        if account_id:
            combined_details["account_id"] = account_id
        if due_date:
            # Ensure datetime is UTC-aware before conversion to string per ADR-011
            utc_date = ensure_utc(due_date) if due_date else None
            combined_details["due_date"] = utc_date.isoformat() if utc_date else None
        if minimum_payment is not None:
            combined_details["minimum_payment"] = minimum_payment
        if statement_balance is not None:
            combined_details["statement_balance"] = statement_balance
        super().__init__(message, combined_details)


class CreditAPRError(CreditAccountError):
    """Error raised for APR issues."""

    def __init__(
        self,
        message: str,
        apr: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        combined_details = details or {}
        if apr is not None:
            combined_details["apr"] = apr
        super().__init__(message, combined_details)


class CreditAutopayError(CreditAccountError):
    """Error raised for autopay issues."""

    def __init__(
        self,
        message: str,
        autopay_status: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        combined_details = details or {}
        if autopay_status:
            combined_details["autopay_status"] = autopay_status
        super().__init__(message, combined_details)


class CreditStatementError(CreditAccountError):
    """
    Error raised for statement issues.

    Per ADR-011, ensures all datetime values are converted to UTC before processing.
    """

    def __init__(
        self,
        message: str,
        statement_date: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        combined_details = details or {}
        if statement_date:
            # Ensure datetime is UTC-aware before conversion to string per ADR-011
            utc_date = ensure_utc(statement_date) if statement_date else None
            combined_details["statement_date"] = (
                utc_date.isoformat() if utc_date else None
            )
        super().__init__(message, combined_details)
