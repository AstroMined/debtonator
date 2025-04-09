"""
Unit tests for EWA account error classes.

Tests ensure that EWA account error classes properly handle error details,
message formatting, and inheritance relationships.
"""

from decimal import Decimal

from src.errors.account_types.banking.ewa import (
    EWAAccountError,
    EWAAdvancePercentageError,
    EWAEarningsValidationError,
    EWANextPaydayError,
    EWAPayPeriodError,
    EWAProviderError,
    EWATransactionFeeError,
)
from src.errors.accounts import AccountError
from src.utils.datetime_utils import utc_datetime


def test_ewa_account_error_with_message_only():
    """Test initializing EWAAccountError with just a message."""
    error = EWAAccountError("Test error message")
    assert error.message == "Test error message"
    assert error.details == {}
    assert str(error) == "Test error message"
    assert isinstance(error, AccountError)


def test_ewa_account_error_with_details():
    """Test initializing EWAAccountError with details."""
    details = {"key1": "value1", "key2": 42}
    error = EWAAccountError("Test error message", details)
    assert error.message == "Test error message"
    assert error.details == details


def test_ewa_provider_error_with_message_only():
    """Test initializing EWAProviderError with just a message."""
    error = EWAProviderError("Provider error")
    assert error.message == "Provider error"
    assert error.details == {}
    assert isinstance(error, EWAAccountError)


def test_ewa_provider_error_with_provider():
    """Test initializing EWAProviderError with provider."""
    error = EWAProviderError("Provider error", provider="Unknown")
    assert error.message == "Provider error"
    assert error.details == {"provider": "Unknown"}


def test_ewa_provider_error_with_all_parameters():
    """Test initializing EWAProviderError with all parameters."""
    error = EWAProviderError(
        "Provider error",
        provider="Unknown",
        valid_providers=["Payactiv", "DailyPay", "Branch"],
        details={"account_id": 123, "integration_status": "failed"},
    )
    assert error.message == "Provider error"
    assert error.details["provider"] == "Unknown"
    assert error.details["valid_providers"] == ["Payactiv", "DailyPay", "Branch"]
    assert error.details["account_id"] == 123
    assert error.details["integration_status"] == "failed"


def test_ewa_advance_percentage_error_with_message_only():
    """Test initializing EWAAdvancePercentageError with just a message."""
    error = EWAAdvancePercentageError("Advance percentage error")
    assert error.message == "Advance percentage error"
    assert error.details == {}
    assert isinstance(error, EWAAccountError)


def test_ewa_advance_percentage_error_with_account_id():
    """Test initializing EWAAdvancePercentageError with account ID."""
    error = EWAAdvancePercentageError("Advance percentage error", account_id=123)
    assert error.message == "Advance percentage error"
    assert error.details == {"account_id": 123}


def test_ewa_advance_percentage_error_with_all_parameters():
    """Test initializing EWAAdvancePercentageError with all parameters."""
    error = EWAAdvancePercentageError(
        "Advance percentage error",
        account_id=123,
        max_advance_percentage=50.0,
        requested_percentage=75.0,
        details={"provider": "Payactiv", "earned_amount": Decimal("1000.00")},
    )
    assert error.message == "Advance percentage error"
    assert error.details["account_id"] == 123
    assert error.details["max_advance_percentage"] == 50.0
    assert error.details["requested_percentage"] == 75.0
    assert error.details["provider"] == "Payactiv"
    assert error.details["earned_amount"] == Decimal("1000.00")


def test_ewa_pay_period_error_with_message_only():
    """Test initializing EWAPayPeriodError with just a message."""
    error = EWAPayPeriodError("Pay period error")
    assert error.message == "Pay period error"
    assert error.details == {}
    assert isinstance(error, EWAAccountError)


def test_ewa_pay_period_error_with_account_id():
    """Test initializing EWAPayPeriodError with account ID."""
    error = EWAPayPeriodError("Pay period error", account_id=123)
    assert error.message == "Pay period error"
    assert error.details == {"account_id": 123}


def test_ewa_pay_period_error_with_all_parameters():
    """Test initializing EWAPayPeriodError with all parameters."""
    pay_period_start = utc_datetime(2025, 4, 1)
    pay_period_end = utc_datetime(2025, 4, 15)
    error = EWAPayPeriodError(
        "Pay period error",
        account_id=123,
        pay_period_start=pay_period_start,
        pay_period_end=pay_period_end,
        details={"provider": "DailyPay"},
    )
    assert error.message == "Pay period error"
    assert error.details["account_id"] == 123
    assert error.details["pay_period_start"] == pay_period_start.isoformat()
    assert error.details["pay_period_end"] == pay_period_end.isoformat()
    assert error.details["provider"] == "DailyPay"


def test_ewa_next_payday_error_with_message_only():
    """Test initializing EWANextPaydayError with just a message."""
    error = EWANextPaydayError("Next payday error")
    assert error.message == "Next payday error"
    assert error.details == {}
    assert isinstance(error, EWAAccountError)


def test_ewa_next_payday_error_with_account_id():
    """Test initializing EWANextPaydayError with account ID."""
    error = EWANextPaydayError("Next payday error", account_id=123)
    assert error.message == "Next payday error"
    assert error.details == {"account_id": 123}


def test_ewa_next_payday_error_with_all_parameters():
    """Test initializing EWANextPaydayError with all parameters."""
    next_payday = utc_datetime(2025, 4, 15)
    error = EWANextPaydayError(
        "Next payday error",
        account_id=123,
        next_payday=next_payday,
        details={"provider": "Branch", "pay_frequency": "biweekly"},
    )
    assert error.message == "Next payday error"
    assert error.details["account_id"] == 123
    assert error.details["next_payday"] == next_payday.isoformat()
    assert error.details["provider"] == "Branch"
    assert error.details["pay_frequency"] == "biweekly"


def test_ewa_transaction_fee_error_with_message_only():
    """Test initializing EWATransactionFeeError with just a message."""
    error = EWATransactionFeeError("Transaction fee error")
    assert error.message == "Transaction fee error"
    assert error.details == {}
    assert isinstance(error, EWAAccountError)


def test_ewa_transaction_fee_error_with_account_id():
    """Test initializing EWATransactionFeeError with account ID."""
    error = EWATransactionFeeError("Transaction fee error", account_id=123)
    assert error.message == "Transaction fee error"
    assert error.details == {"account_id": 123}


def test_ewa_transaction_fee_error_with_all_parameters():
    """Test initializing EWATransactionFeeError with all parameters."""
    error = EWATransactionFeeError(
        "Transaction fee error",
        account_id=123,
        per_transaction_fee=Decimal("5.99"),
        transaction_amount=Decimal("100.00"),
        details={"provider": "Payactiv", "fee_type": "flat"},
    )
    assert error.message == "Transaction fee error"
    assert error.details["account_id"] == 123
    assert error.details["per_transaction_fee"] == Decimal("5.99")
    assert error.details["transaction_amount"] == Decimal("100.00")
    assert error.details["provider"] == "Payactiv"
    assert error.details["fee_type"] == "flat"


def test_ewa_earnings_validation_error_with_message_only():
    """Test initializing EWAEarningsValidationError with just a message."""
    error = EWAEarningsValidationError("Earnings validation error")
    assert error.message == "Earnings validation error"
    assert error.details == {}
    assert isinstance(error, EWAAccountError)


def test_ewa_earnings_validation_error_with_account_id():
    """Test initializing EWAEarningsValidationError with account ID."""
    error = EWAEarningsValidationError("Earnings validation error", account_id=123)
    assert error.message == "Earnings validation error"
    assert error.details == {"account_id": 123}


def test_ewa_earnings_validation_error_with_all_parameters():
    """Test initializing EWAEarningsValidationError with all parameters."""
    error = EWAEarningsValidationError(
        "Earnings validation error",
        account_id=123,
        earned_amount=Decimal("500.00"),
        advance_amount=Decimal("600.00"),
        details={"provider": "DailyPay", "validation_method": "employer_api"},
    )
    assert error.message == "Earnings validation error"
    assert error.details["account_id"] == 123
    assert error.details["earned_amount"] == Decimal("500.00")
    assert error.details["advance_amount"] == Decimal("600.00")
    assert error.details["provider"] == "DailyPay"
    assert error.details["validation_method"] == "employer_api"
