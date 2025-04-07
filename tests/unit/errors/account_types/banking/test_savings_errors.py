"""
Unit tests for savings account error classes.

Tests ensure that savings account error classes properly handle error details,
message formatting, and inheritance relationships.
"""

import pytest
from decimal import Decimal

from src.errors.accounts import AccountError
from src.errors.account_types.banking.savings import (
    SavingsAccountError,
    SavingsWithdrawalLimitError,
    SavingsMinimumBalanceError,
    SavingsInterestRateError,
    SavingsCompoundFrequencyError,
)


def test_savings_account_error_with_message_only():
    """Test initializing SavingsAccountError with just a message."""
    error = SavingsAccountError("Test error message")
    assert error.message == "Test error message"
    assert error.details == {}
    assert str(error) == "Test error message"
    assert isinstance(error, AccountError)


def test_savings_account_error_with_details():
    """Test initializing SavingsAccountError with details."""
    details = {"key1": "value1", "key2": 42}
    error = SavingsAccountError("Test error message", details)
    assert error.message == "Test error message"
    assert error.details == details


def test_savings_withdrawal_limit_error_with_message_only():
    """Test initializing SavingsWithdrawalLimitError with just a message."""
    error = SavingsWithdrawalLimitError("Withdrawal limit exceeded")
    assert error.message == "Withdrawal limit exceeded"
    assert error.details == {}
    assert isinstance(error, SavingsAccountError)


def test_savings_withdrawal_limit_error_with_account_id():
    """Test initializing SavingsWithdrawalLimitError with account ID."""
    error = SavingsWithdrawalLimitError("Withdrawal limit exceeded", account_id=123)
    assert error.message == "Withdrawal limit exceeded"
    assert error.details == {"account_id": 123}


def test_savings_withdrawal_limit_error_with_all_parameters():
    """Test initializing SavingsWithdrawalLimitError with all parameters."""
    error = SavingsWithdrawalLimitError(
        "Withdrawal limit exceeded",
        account_id=123,
        withdrawal_limit=6,
        withdrawal_count=5,
        details={"period": "monthly"}
    )
    assert error.message == "Withdrawal limit exceeded"
    assert error.details["account_id"] == 123
    assert error.details["withdrawal_count"] == 5
    assert error.details["withdrawal_limit"] == 6
    assert error.details["period"] == "monthly"


def test_savings_minimum_balance_error_with_message_only():
    """Test initializing SavingsMinimumBalanceError with just a message."""
    error = SavingsMinimumBalanceError("Minimum balance not met")
    assert error.message == "Minimum balance not met"
    assert error.details == {}
    assert isinstance(error, SavingsAccountError)


def test_savings_minimum_balance_error_with_account_id():
    """Test initializing SavingsMinimumBalanceError with account ID."""
    error = SavingsMinimumBalanceError("Minimum balance not met", account_id=123)
    assert error.message == "Minimum balance not met"
    assert error.details == {"account_id": 123}


def test_savings_minimum_balance_error_with_all_parameters():
    """Test initializing SavingsMinimumBalanceError with all parameters."""
    error = SavingsMinimumBalanceError(
        "Minimum balance not met",
        account_id=123,
        current_balance=Decimal("50.00"),
        minimum_balance=Decimal("100.00"),
        details={"fee": Decimal("25.00")}
    )
    assert error.message == "Minimum balance not met"
    assert error.details["account_id"] == 123
    assert error.details["current_balance"] == Decimal("50.00")
    assert error.details["minimum_balance"] == Decimal("100.00")
    assert error.details["fee"] == Decimal("25.00")


def test_savings_interest_rate_error_with_message_only():
    """Test initializing SavingsInterestRateError with just a message."""
    error = SavingsInterestRateError("Invalid interest rate")
    assert error.message == "Invalid interest rate"
    assert error.details == {}
    assert isinstance(error, SavingsAccountError)


def test_savings_interest_rate_error_with_interest_rate():
    """Test initializing SavingsInterestRateError with interest rate."""
    error = SavingsInterestRateError("Invalid interest rate", interest_rate=5.0)
    assert error.message == "Invalid interest rate"
    assert error.details == {"interest_rate": 5.0}


def test_savings_interest_rate_error_with_all_parameters():
    """Test initializing SavingsInterestRateError with all parameters."""
    error = SavingsInterestRateError(
        "Invalid interest rate",
        interest_rate=Decimal("5.5"),
        details={"account_id": 123, "max_rate": Decimal("5.0"), "account_type": "high_yield"}
    )
    assert error.message == "Invalid interest rate"
    assert error.details["interest_rate"] == Decimal("5.5")
    assert error.details["account_id"] == 123
    assert error.details["max_rate"] == Decimal("5.0")
    assert error.details["account_type"] == "high_yield"


def test_savings_compound_frequency_error_with_frequency_only():
    """Test initializing SavingsCompoundFrequencyError with just a frequency."""
    error = SavingsCompoundFrequencyError("monthly")
    assert error.message == "Invalid compound frequency: monthly"
    assert error.details == {"frequency": "monthly"}
    assert isinstance(error, SavingsAccountError)


def test_savings_compound_frequency_error_with_custom_message():
    """Test initializing SavingsCompoundFrequencyError with custom message."""
    error = SavingsCompoundFrequencyError("invalid", message="Custom frequency error")
    assert error.message == "Custom frequency error"
    assert error.details == {"frequency": "invalid"}


def test_savings_compound_frequency_error_with_all_parameters():
    """Test initializing SavingsCompoundFrequencyError with all parameters."""
    error = SavingsCompoundFrequencyError(
        "invalid",
        message="Custom frequency error",
        details={"account_id": 123, "valid_frequencies": ["daily", "monthly", "quarterly", "annually"], "account_type": "high_yield"}
    )
    assert error.message == "Custom frequency error"
    assert error.details["frequency"] == "invalid"
    assert error.details["account_id"] == 123
    assert error.details["valid_frequencies"] == ["daily", "monthly", "quarterly", "annually"]
    assert error.details["account_type"] == "high_yield"
