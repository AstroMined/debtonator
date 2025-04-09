"""
Unit tests for payment app account error classes.

Tests ensure that payment app account error classes properly handle error details,
message formatting, and inheritance relationships.
"""

from decimal import Decimal

from src.errors.account_types.banking.payment_app import (
    PaymentAppAccountError,
    PaymentAppCardInformationError,
    PaymentAppLinkedAccountError,
    PaymentAppPlatformFeatureError,
    PaymentAppTransferError,
    PaymentAppUnsupportedPlatformError,
)
from src.errors.accounts import AccountError


def test_payment_app_account_error_with_message_only():
    """Test initializing PaymentAppAccountError with just a message."""
    error = PaymentAppAccountError("Test error message")
    assert error.message == "Test error message"
    assert error.details == {}
    assert str(error) == "Test error message"
    assert isinstance(error, AccountError)


def test_payment_app_account_error_with_details():
    """Test initializing PaymentAppAccountError with details."""
    details = {"key1": "value1", "key2": 42}
    error = PaymentAppAccountError("Test error message", details)
    assert error.message == "Test error message"
    assert error.details == details


def test_payment_app_unsupported_platform_error_with_platform_only():
    """Test initializing PaymentAppUnsupportedPlatformError with platform only."""
    error = PaymentAppUnsupportedPlatformError("Unknown")
    assert error.message == "Unsupported payment platform: Unknown"
    assert error.details == {"platform": "Unknown"}
    assert isinstance(error, PaymentAppAccountError)


def test_payment_app_unsupported_platform_error_with_custom_message():
    """Test initializing PaymentAppUnsupportedPlatformError with custom message."""
    error = PaymentAppUnsupportedPlatformError(
        "Unknown", message="Custom platform error message"
    )
    assert error.message == "Custom platform error message"
    assert error.details == {"platform": "Unknown"}


def test_payment_app_unsupported_platform_error_with_all_parameters():
    """Test initializing PaymentAppUnsupportedPlatformError with all parameters."""
    error = PaymentAppUnsupportedPlatformError(
        "Unknown",
        message="Custom platform error message",
        supported_platforms=["PayPal", "Venmo", "Cash App"],
        details={"account_id": 123, "integration_status": "failed"},
    )
    assert error.message == "Custom platform error message"
    assert error.details["platform"] == "Unknown"
    assert error.details["supported_platforms"] == ["PayPal", "Venmo", "Cash App"]
    assert error.details["account_id"] == 123
    assert error.details["integration_status"] == "failed"


def test_payment_app_linked_account_error_with_message_only():
    """Test initializing PaymentAppLinkedAccountError with just a message."""
    error = PaymentAppLinkedAccountError("Linked account error")
    assert error.message == "Linked account error"
    assert error.details == {}
    assert isinstance(error, PaymentAppAccountError)


def test_payment_app_linked_account_error_with_account_id():
    """Test initializing PaymentAppLinkedAccountError with account ID."""
    error = PaymentAppLinkedAccountError("Linked account error", account_id=123)
    assert error.message == "Linked account error"
    assert error.details == {"account_id": 123}


def test_payment_app_linked_account_error_with_all_parameters():
    """Test initializing PaymentAppLinkedAccountError with all parameters."""
    error = PaymentAppLinkedAccountError(
        "Linked account error",
        linked_account_ids=[456, 789],
        account_id=123,
        details={"platform": "PayPal", "link_status": "failed"},
    )
    assert error.message == "Linked account error"
    assert error.details["linked_account_ids"] == [456, 789]
    assert error.details["account_id"] == 123
    assert error.details["platform"] == "PayPal"
    assert error.details["link_status"] == "failed"


def test_payment_app_card_information_error_with_message_only():
    """Test initializing PaymentAppCardInformationError with just a message."""
    error = PaymentAppCardInformationError("Card information error")
    assert error.message == "Card information error"
    assert error.details == {}
    assert isinstance(error, PaymentAppAccountError)


def test_payment_app_card_information_error_with_has_debit_card():
    """Test initializing PaymentAppCardInformationError with has_debit_card."""
    error = PaymentAppCardInformationError(
        "Card information error", has_debit_card=False
    )
    assert error.message == "Card information error"
    assert error.details == {"has_debit_card": False}


def test_payment_app_card_information_error_with_all_parameters():
    """Test initializing PaymentAppCardInformationError with all parameters."""
    error = PaymentAppCardInformationError(
        "Card information error",
        has_debit_card=True,
        card_last_four="1234",
        details={"account_id": 123, "platform": "Venmo"},
    )
    assert error.message == "Card information error"
    assert error.details["has_debit_card"] is True
    assert error.details["card_last_four"] == "1234"
    assert error.details["account_id"] == 123
    assert error.details["platform"] == "Venmo"


def test_payment_app_platform_feature_error_with_feature_only():
    """Test initializing PaymentAppPlatformFeatureError with feature only."""
    error = PaymentAppPlatformFeatureError("instant_transfer")
    assert error.message == "Feature 'instant_transfer' not supported"
    assert error.details == {"feature": "instant_transfer"}
    assert isinstance(error, PaymentAppAccountError)


def test_payment_app_platform_feature_error_with_platform():
    """Test initializing PaymentAppPlatformFeatureError with platform."""
    error = PaymentAppPlatformFeatureError("instant_transfer", platform="Cash App")
    assert (
        error.message
        == "Feature 'instant_transfer' not supported for platform 'Cash App'"
    )
    assert error.details == {"feature": "instant_transfer", "platform": "Cash App"}


def test_payment_app_platform_feature_error_with_all_parameters():
    """Test initializing PaymentAppPlatformFeatureError with all parameters."""
    error = PaymentAppPlatformFeatureError(
        "instant_transfer",
        platform="Cash App",
        message="Custom feature error message",
        details={"account_id": 123, "alternative_feature": "standard_transfer"},
    )
    assert error.message == "Custom feature error message for platform 'Cash App'"
    assert error.details["feature"] == "instant_transfer"
    assert error.details["platform"] == "Cash App"
    assert error.details["account_id"] == 123
    assert error.details["alternative_feature"] == "standard_transfer"


def test_payment_app_transfer_error_with_message_only():
    """Test initializing PaymentAppTransferError with just a message."""
    error = PaymentAppTransferError("Transfer error")
    assert error.message == "Transfer error"
    assert error.details == {}
    assert isinstance(error, PaymentAppAccountError)


def test_payment_app_transfer_error_with_transfer_type():
    """Test initializing PaymentAppTransferError with transfer_type."""
    error = PaymentAppTransferError("Transfer error", transfer_type="withdrawal")
    assert error.message == "Transfer error"
    assert error.details == {"transfer_type": "withdrawal"}


def test_payment_app_transfer_error_with_all_parameters():
    """Test initializing PaymentAppTransferError with all parameters."""
    error = PaymentAppTransferError(
        "Transfer error",
        transfer_type="withdrawal",
        source_id=123,
        destination_id=456,
        amount=Decimal("100.00"),
        details={
            "platform": "PayPal",
            "status": "failed",
            "reason": "insufficient_funds",
        },
    )
    assert error.message == "Transfer error"
    assert error.details["transfer_type"] == "withdrawal"
    assert error.details["source_id"] == 123
    assert error.details["destination_id"] == 456
    assert error.details["amount"] == Decimal("100.00")
    assert error.details["platform"] == "PayPal"
    assert error.details["status"] == "failed"
    assert error.details["reason"] == "insufficient_funds"
