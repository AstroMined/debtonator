"""
Earned Wage Access (EWA) account specific errors.

This module provides error classes specific to EWA accounts
(e.g., Payactiv, DailyPay, etc.).
"""

from datetime import datetime
from typing import Any, Dict, Optional

from src.errors.accounts import AccountError


class EWAAccountError(AccountError):
    """Base class for EWA account errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class EWAProviderError(EWAAccountError):
    """Error raised for EWA provider issues."""

    def __init__(
        self,
        message: str,
        provider: Optional[str] = None,
        valid_providers: Optional[list] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        combined_details = details or {}
        if provider:
            combined_details["provider"] = provider
        if valid_providers:
            combined_details["valid_providers"] = valid_providers
        super().__init__(message, combined_details)


class EWAAdvancePercentageError(EWAAccountError):
    """Error raised for advance percentage issues."""

    def __init__(
        self,
        message: str,
        account_id: Optional[int] = None,
        max_advance_percentage: Optional[float] = None,
        requested_percentage: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        combined_details = details or {}
        if account_id:
            combined_details["account_id"] = account_id
        if max_advance_percentage is not None:
            combined_details["max_advance_percentage"] = max_advance_percentage
        if requested_percentage is not None:
            combined_details["requested_percentage"] = requested_percentage
        super().__init__(message, combined_details)


class EWAPayPeriodError(EWAAccountError):
    """Error raised for pay period issues."""

    def __init__(
        self,
        message: str,
        account_id: Optional[int] = None,
        pay_period_start: Optional[datetime] = None,
        pay_period_end: Optional[datetime] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        combined_details = details or {}
        if account_id:
            combined_details["account_id"] = account_id
        if pay_period_start:
            combined_details["pay_period_start"] = (
                pay_period_start.isoformat() if pay_period_start else None
            )
        if pay_period_end:
            combined_details["pay_period_end"] = (
                pay_period_end.isoformat() if pay_period_end else None
            )
        super().__init__(message, combined_details)


class EWANextPaydayError(EWAAccountError):
    """Error raised for next payday issues."""

    def __init__(
        self,
        message: str,
        account_id: Optional[int] = None,
        next_payday: Optional[datetime] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        combined_details = details or {}
        if account_id:
            combined_details["account_id"] = account_id
        if next_payday:
            combined_details["next_payday"] = (
                next_payday.isoformat() if next_payday else None
            )
        super().__init__(message, combined_details)


class EWATransactionFeeError(EWAAccountError):
    """Error raised for transaction fee issues."""

    def __init__(
        self,
        message: str,
        account_id: Optional[int] = None,
        per_transaction_fee: Optional[float] = None,
        transaction_amount: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        combined_details = details or {}
        if account_id:
            combined_details["account_id"] = account_id
        if per_transaction_fee is not None:
            combined_details["per_transaction_fee"] = per_transaction_fee
        if transaction_amount is not None:
            combined_details["transaction_amount"] = transaction_amount
        super().__init__(message, combined_details)


class EWAEarningsValidationError(EWAAccountError):
    """Error raised for earnings validation issues."""

    def __init__(
        self,
        message: str,
        account_id: Optional[int] = None,
        earned_amount: Optional[float] = None,
        advance_amount: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        combined_details = details or {}
        if account_id:
            combined_details["account_id"] = account_id
        if earned_amount is not None:
            combined_details["earned_amount"] = earned_amount
        if advance_amount is not None:
            combined_details["advance_amount"] = advance_amount
        super().__init__(message, combined_details)
