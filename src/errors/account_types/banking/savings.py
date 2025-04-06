"""
Savings account specific errors.

This module provides error classes specific to savings accounts.
"""

from typing import Any, Dict, Optional

from src.errors.accounts import AccountError


class SavingsAccountError(AccountError):
    """Base class for savings account errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class SavingsWithdrawalLimitError(SavingsAccountError):
    """Error raised when withdrawals exceed the account limit."""

    def __init__(
        self,
        message: str,
        account_id: Optional[int] = None,
        withdrawal_limit: Optional[int] = None,
        withdrawal_count: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        combined_details = details or {}
        if account_id:
            combined_details["account_id"] = account_id
        if withdrawal_limit is not None:
            combined_details["withdrawal_limit"] = withdrawal_limit
        if withdrawal_count is not None:
            combined_details["withdrawal_count"] = withdrawal_count
        super().__init__(message, combined_details)


class SavingsMinimumBalanceError(SavingsAccountError):
    """Error raised when the balance falls below the minimum required."""

    def __init__(
        self,
        message: str,
        account_id: Optional[int] = None,
        current_balance: Optional[float] = None,
        minimum_balance: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        combined_details = details or {}
        if account_id:
            combined_details["account_id"] = account_id
        if current_balance is not None:
            combined_details["current_balance"] = current_balance
        if minimum_balance is not None:
            combined_details["minimum_balance"] = minimum_balance
        super().__init__(message, combined_details)


class SavingsInterestRateError(SavingsAccountError):
    """Error raised for interest rate issues."""

    def __init__(
        self,
        message: str,
        interest_rate: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        combined_details = details or {}
        if interest_rate is not None:
            combined_details["interest_rate"] = interest_rate
        super().__init__(message, combined_details)


class SavingsCompoundFrequencyError(SavingsAccountError):
    """Error raised for compound frequency issues."""

    def __init__(
        self,
        frequency: str,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        message = message or f"Invalid compound frequency: {frequency}"
        combined_details = details or {}
        combined_details["frequency"] = frequency
        super().__init__(message, combined_details)
