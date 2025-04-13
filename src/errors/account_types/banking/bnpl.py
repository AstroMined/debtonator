"""
Buy Now Pay Later (BNPL) account specific errors.

This module provides error classes specific to BNPL accounts
(e.g., Affirm, Klarna, Afterpay, etc.).

All datetime handling follows ADR-011 requirements for UTC datetime standardization.
"""

from typing import Any, Dict, Optional

from src.errors.accounts import AccountError
from src.utils.datetime_utils import ensure_utc


class BNPLAccountError(AccountError):
    """Base class for BNPL account errors."""

    def __init__(
        self,
        message: str,
        account_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
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
        installment_amount: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        combined_details = details or {}
        if installment_number is not None:
            combined_details["installment_number"] = installment_number
        if installment_amount is not None:
            combined_details["installment_amount"] = installment_amount
        super().__init__(message, account_id, combined_details)


class BNPLInstallmentCountError(BNPLAccountError):
    """Error raised when there are issues with installment count."""

    def __init__(
        self,
        message: str,
        account_id: Optional[int] = None,
        installment_count: Optional[int] = None,
        installments_paid: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        combined_details = details or {}
        if installment_count is not None:
            combined_details["installment_count"] = installment_count
        if installments_paid is not None:
            combined_details["installments_paid"] = installments_paid
        super().__init__(message, account_id, combined_details)


class BNPLPaymentFrequencyError(BNPLAccountError):
    """Error raised for payment frequency issues."""

    def __init__(
        self,
        message: str,
        account_id: Optional[int] = None,
        payment_frequency: Optional[str] = None,
        valid_frequencies: Optional[list] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        combined_details = details or {}
        if payment_frequency:
            combined_details["payment_frequency"] = payment_frequency
        if valid_frequencies:
            combined_details["valid_frequencies"] = valid_frequencies
        super().__init__(message, account_id, combined_details)


class BNPLNextPaymentDateError(BNPLAccountError):
    """
    Error raised for next payment date issues.
    
    Per ADR-011, ensures all datetime values are converted to UTC before processing.
    """

    def __init__(
        self,
        message: str,
        account_id: Optional[int] = None,
        next_payment_date: Optional[Any] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        combined_details = details or {}
        if next_payment_date:
            # Ensure datetime is UTC-aware before conversion to string per ADR-011
            utc_date = ensure_utc(next_payment_date) if next_payment_date else None
            combined_details["next_payment_date"] = (
                utc_date.isoformat() if utc_date else None
            )
        super().__init__(message, account_id, combined_details)


class BNPLProviderError(BNPLAccountError):
    """Error raised for BNPL provider issues."""

    def __init__(
        self,
        message: str,
        account_id: Optional[int] = None,
        provider: Optional[str] = None,
        valid_providers: Optional[list] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        combined_details = details or {}
        if provider:
            combined_details["provider"] = provider
        if valid_providers:
            combined_details["valid_providers"] = valid_providers
        super().__init__(message, account_id, combined_details)


class BNPLLifecycleError(BNPLAccountError):
    """Error raised for lifecycle management issues."""

    def __init__(
        self,
        message: str,
        account_id: Optional[int] = None,
        current_state: Optional[str] = None,
        target_state: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        combined_details = details or {}
        if current_state:
            combined_details["current_state"] = current_state
        if target_state:
            combined_details["target_state"] = target_state
        super().__init__(message, account_id, combined_details)
