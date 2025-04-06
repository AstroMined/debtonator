"""
Payment app account specific errors.

This module provides error classes specific to payment app accounts
(e.g., PayPal, Venmo, Cash App, etc.).
"""

from typing import Any, Dict, List, Optional

from src.errors.accounts import AccountError


class PaymentAppAccountError(AccountError):
    """Base class for payment app account errors."""

    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, details)


class PaymentAppUnsupportedPlatformError(PaymentAppAccountError):
    """Error raised when the payment platform is not supported."""

    def __init__(
        self,
        platform: str,
        message: Optional[str] = None,
        supported_platforms: Optional[List[str]] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        message = message or f"Unsupported payment platform: {platform}"
        combined_details = details or {}
        combined_details["platform"] = platform
        if supported_platforms:
            combined_details["supported_platforms"] = supported_platforms
        super().__init__(message, combined_details)


class PaymentAppLinkedAccountError(PaymentAppAccountError):
    """Error raised for linked account issues."""

    def __init__(
        self,
        message: str,
        linked_account_ids: Optional[List[int]] = None,
        account_id: Optional[int] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        combined_details = details or {}
        if linked_account_ids:
            combined_details["linked_account_ids"] = linked_account_ids
        if account_id:
            combined_details["account_id"] = account_id
        super().__init__(message, combined_details)


class PaymentAppCardInformationError(PaymentAppAccountError):
    """Error raised for card information issues."""

    def __init__(
        self,
        message: str,
        has_debit_card: Optional[bool] = None,
        card_last_four: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        combined_details = details or {}
        if has_debit_card is not None:
            combined_details["has_debit_card"] = has_debit_card
        if card_last_four:
            combined_details["card_last_four"] = card_last_four
        super().__init__(message, combined_details)


class PaymentAppPlatformFeatureError(PaymentAppAccountError):
    """Error raised when a platform feature is not supported."""

    def __init__(
        self,
        feature: str,
        platform: Optional[str] = None,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        message = message or f"Feature '{feature}' not supported"
        if platform:
            message += f" for platform '{platform}'"

        combined_details = details or {}
        combined_details["feature"] = feature
        if platform:
            combined_details["platform"] = platform
        super().__init__(message, combined_details)


class PaymentAppTransferError(PaymentAppAccountError):
    """Error raised for transfer issues between payment app and linked accounts."""

    def __init__(
        self,
        message: str,
        transfer_type: Optional[str] = None,
        source_id: Optional[int] = None,
        destination_id: Optional[int] = None,
        amount: Optional[float] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        combined_details = details or {}
        if transfer_type:
            combined_details["transfer_type"] = transfer_type
        if source_id:
            combined_details["source_id"] = source_id
        if destination_id:
            combined_details["destination_id"] = destination_id
        if amount is not None:
            combined_details["amount"] = amount
        super().__init__(message, combined_details)
