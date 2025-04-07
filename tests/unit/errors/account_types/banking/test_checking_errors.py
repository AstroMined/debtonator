"""
Unit tests for checking account error classes.

Tests ensure that checking account error classes properly handle error details,
message formatting, and inheritance relationships.
"""

import pytest
from decimal import Decimal

from src.errors.accounts import AccountError
from src.errors.account_types.banking.checking import (
    CheckingAccountError,
    CheckingOverdraftError,
    CheckingInsufficientFundsError,
    CheckingInvalidRoutingNumberError,
    CheckingInternationalBankingError,
)


def test_checking_account_error_with_message_only():
    """Test initializing CheckingAccountError with just a message."""
    error = CheckingAccountError("Test error message")
    assert error.message == "Test error message"
    assert error.details == {}
    assert str(error) == "Test error message"
    assert isinstance(error, AccountError)


def test_checking_account_error_with_details():
    """Test initializing CheckingAccountError with details."""
    details = {"key1": "value1", "key2": 42}
    error = CheckingAccountError("Test error message", details)
    assert error.message == "Test error message"
    assert error.details == details


def test_checking_overdraft_error_with_message_only():
    """Test initializing CheckingOverdraftError with just a message."""
    error = CheckingOverdraftError("Overdraft error")
    assert error.message == "Overdraft error"
    assert error.details == {}
    assert isinstance(error, CheckingAccountError)


def test_checking_overdraft_error_with_account_id():
    """Test initializing CheckingOverdraftError with account ID."""
    error = CheckingOverdraftError("Overdraft error", account_id=123)
    assert error.message == "Overdraft error"
    assert error.details == {"account_id": 123}


def test_checking_overdraft_error_with_all_parameters():
    """Test initializing CheckingOverdraftError with all parameters."""
    error = CheckingOverdraftError(
        "Overdraft error",
        account_id=123,
        current_balance=Decimal("100.00"),
        details={"additional": "info"}
    )
    assert error.message == "Overdraft error"
    assert error.details["account_id"] == 123
    assert error.details["current_balance"] == Decimal("100.00")
    assert error.details["additional"] == "info"


def test_checking_insufficient_funds_error_with_message_only():
    """Test initializing CheckingInsufficientFundsError with just a message."""
    error = CheckingInsufficientFundsError("Insufficient funds")
    assert error.message == "Insufficient funds"
    assert error.details == {}
    assert isinstance(error, CheckingAccountError)


def test_checking_insufficient_funds_error_with_account_id():
    """Test initializing CheckingInsufficientFundsError with account ID."""
    error = CheckingInsufficientFundsError("Insufficient funds", account_id=123)
    assert error.message == "Insufficient funds"
    assert error.details == {"account_id": 123}


def test_checking_insufficient_funds_error_with_all_parameters():
    """Test initializing CheckingInsufficientFundsError with all parameters."""
    error = CheckingInsufficientFundsError(
        "Insufficient funds",
        account_id=123,
        current_balance=Decimal("50.00"),
        required_amount=Decimal("100.00"),
        details={"transaction_id": 456}
    )
    assert error.message == "Insufficient funds"
    assert error.details["account_id"] == 123
    assert error.details["current_balance"] == Decimal("50.00")
    assert error.details["required_amount"] == Decimal("100.00")
    assert error.details["transaction_id"] == 456


def test_checking_invalid_routing_number_error_with_routing_number():
    """Test initializing CheckingInvalidRoutingNumberError with routing number."""
    error = CheckingInvalidRoutingNumberError("123456789")
    assert error.message == "Invalid routing number: 123456789"
    assert error.details == {"routing_number": "123456789"}
    assert isinstance(error, CheckingAccountError)


def test_checking_invalid_routing_number_error_with_custom_message():
    """Test initializing CheckingInvalidRoutingNumberError with custom message."""
    error = CheckingInvalidRoutingNumberError(
        "123456789", 
        message="Custom routing number error"
    )
    assert error.message == "Custom routing number error"
    assert error.details == {"routing_number": "123456789"}


def test_checking_invalid_routing_number_error_with_details():
    """Test initializing CheckingInvalidRoutingNumberError with details."""
    error = CheckingInvalidRoutingNumberError(
        "123456789",
        details={"bank_name": "Test Bank"}
    )
    assert error.message == "Invalid routing number: 123456789"
    assert error.details["routing_number"] == "123456789"
    assert error.details["bank_name"] == "Test Bank"


def test_checking_international_banking_error_with_required_parameters():
    """Test initializing CheckingInternationalBankingError with required parameters."""
    error = CheckingInternationalBankingError("swift_code", "INVALID123")
    assert error.message == "Invalid swift_code: INVALID123"
    assert error.details == {"field_name": "swift_code", "value": "INVALID123"}
    assert isinstance(error, CheckingAccountError)


def test_checking_international_banking_error_with_custom_message():
    """Test initializing CheckingInternationalBankingError with custom message."""
    error = CheckingInternationalBankingError(
        "swift_code", 
        "INVALID123", 
        message="Invalid SWIFT code format"
    )
    assert error.message == "Invalid SWIFT code format"
    assert error.details == {"field_name": "swift_code", "value": "INVALID123"}


def test_checking_international_banking_error_with_details():
    """Test initializing CheckingInternationalBankingError with details."""
    error = CheckingInternationalBankingError(
        "swift_code",
        "INVALID123",
        details={"country": "US", "bank_name": "Test Bank"}
    )
    assert error.message == "Invalid swift_code: INVALID123"
    assert error.details["field_name"] == "swift_code"
    assert error.details["value"] == "INVALID123"
    assert error.details["country"] == "US"
    assert error.details["bank_name"] == "Test Bank"
