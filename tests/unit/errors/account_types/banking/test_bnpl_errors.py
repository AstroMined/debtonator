"""
Unit tests for BNPL account error classes.

Tests ensure that BNPL account error classes properly handle error details,
message formatting, and inheritance relationships.
"""

import pytest
from decimal import Decimal

from src.errors.accounts import AccountError
from src.utils.datetime_utils import utc_datetime
from src.errors.account_types.banking.bnpl import (
    BNPLAccountError,
    BNPLInstallmentError,
    BNPLInstallmentCountError,
    BNPLPaymentFrequencyError,
    BNPLNextPaymentDateError,
    BNPLProviderError,
    BNPLLifecycleError,
)


def test_bnpl_account_error_with_message_only():
    """Test initializing BNPLAccountError with just a message."""
    error = BNPLAccountError("Test error message")
    assert error.message == "Test error message"
    assert error.details == {}
    assert str(error) == "Test error message"
    assert isinstance(error, AccountError)


def test_bnpl_account_error_with_account_id():
    """Test initializing BNPLAccountError with account ID."""
    error = BNPLAccountError("Test error message", account_id=123)
    assert error.message == "Test error message"
    assert error.details == {"account_id": 123}


def test_bnpl_account_error_with_details():
    """Test initializing BNPLAccountError with details."""
    details = {"key1": "value1", "key2": 42}
    error = BNPLAccountError("Test error message", details=details)
    assert error.message == "Test error message"
    assert error.details == details


def test_bnpl_account_error_with_account_id_and_details():
    """Test initializing BNPLAccountError with account ID and details."""
    details = {"key1": "value1", "key2": 42}
    error = BNPLAccountError("Test error message", account_id=123, details=details)
    assert error.message == "Test error message"
    assert error.details["account_id"] == 123
    assert error.details["key1"] == "value1"
    assert error.details["key2"] == 42


def test_bnpl_installment_error_with_message_only():
    """Test initializing BNPLInstallmentError with just a message."""
    error = BNPLInstallmentError("Installment error")
    assert error.message == "Installment error"
    assert error.details == {}
    assert isinstance(error, BNPLAccountError)


def test_bnpl_installment_error_with_account_id():
    """Test initializing BNPLInstallmentError with account ID."""
    error = BNPLInstallmentError("Installment error", account_id=123)
    assert error.message == "Installment error"
    assert error.details == {"account_id": 123}


def test_bnpl_installment_error_with_all_parameters():
    """Test initializing BNPLInstallmentError with all parameters."""
    error = BNPLInstallmentError(
        "Installment error",
        account_id=123,
        installment_number=2,
        installment_amount=Decimal("50.00"),
        details={"due_date": "2025-04-15"}
    )
    assert error.message == "Installment error"
    assert error.details["account_id"] == 123
    assert error.details["installment_number"] == 2
    assert error.details["installment_amount"] == Decimal("50.00")
    assert error.details["due_date"] == "2025-04-15"


def test_bnpl_installment_count_error_with_message_only():
    """Test initializing BNPLInstallmentCountError with just a message."""
    error = BNPLInstallmentCountError("Installment count error")
    assert error.message == "Installment count error"
    assert error.details == {}
    assert isinstance(error, BNPLAccountError)


def test_bnpl_installment_count_error_with_account_id():
    """Test initializing BNPLInstallmentCountError with account ID."""
    error = BNPLInstallmentCountError("Installment count error", account_id=123)
    assert error.message == "Installment count error"
    assert error.details == {"account_id": 123}


def test_bnpl_installment_count_error_with_all_parameters():
    """Test initializing BNPLInstallmentCountError with all parameters."""
    error = BNPLInstallmentCountError(
        "Installment count error",
        account_id=123,
        installment_count=4,
        installments_paid=2,
        details={"remaining_amount": Decimal("100.00")}
    )
    assert error.message == "Installment count error"
    assert error.details["account_id"] == 123
    assert error.details["installment_count"] == 4
    assert error.details["installments_paid"] == 2
    assert error.details["remaining_amount"] == Decimal("100.00")


def test_bnpl_payment_frequency_error_with_message_only():
    """Test initializing BNPLPaymentFrequencyError with just a message."""
    error = BNPLPaymentFrequencyError("Payment frequency error")
    assert error.message == "Payment frequency error"
    assert error.details == {}
    assert isinstance(error, BNPLAccountError)


def test_bnpl_payment_frequency_error_with_account_id():
    """Test initializing BNPLPaymentFrequencyError with account ID."""
    error = BNPLPaymentFrequencyError("Payment frequency error", account_id=123)
    assert error.message == "Payment frequency error"
    assert error.details == {"account_id": 123}


def test_bnpl_payment_frequency_error_with_all_parameters():
    """Test initializing BNPLPaymentFrequencyError with all parameters."""
    error = BNPLPaymentFrequencyError(
        "Payment frequency error",
        account_id=123,
        payment_frequency="invalid",
        valid_frequencies=["weekly", "biweekly", "monthly"],
        details={"provider": "Affirm"}
    )
    assert error.message == "Payment frequency error"
    assert error.details["account_id"] == 123
    assert error.details["payment_frequency"] == "invalid"
    assert error.details["valid_frequencies"] == ["weekly", "biweekly", "monthly"]
    assert error.details["provider"] == "Affirm"


def test_bnpl_next_payment_date_error_with_message_only():
    """Test initializing BNPLNextPaymentDateError with just a message."""
    error = BNPLNextPaymentDateError("Next payment date error")
    assert error.message == "Next payment date error"
    assert error.details == {}
    assert isinstance(error, BNPLAccountError)


def test_bnpl_next_payment_date_error_with_account_id():
    """Test initializing BNPLNextPaymentDateError with account ID."""
    error = BNPLNextPaymentDateError("Next payment date error", account_id=123)
    assert error.message == "Next payment date error"
    assert error.details == {"account_id": 123}


def test_bnpl_next_payment_date_error_with_all_parameters():
    """Test initializing BNPLNextPaymentDateError with all parameters."""
    next_payment_date = utc_datetime(2025, 4, 15)
    error = BNPLNextPaymentDateError(
        "Next payment date error",
        account_id=123,
        next_payment_date=next_payment_date,
        details={"amount_due": Decimal("50.00")}
    )
    assert error.message == "Next payment date error"
    assert error.details["account_id"] == 123
    assert error.details["next_payment_date"] == next_payment_date.isoformat()
    assert error.details["amount_due"] == Decimal("50.00")


def test_bnpl_provider_error_with_message_only():
    """Test initializing BNPLProviderError with just a message."""
    error = BNPLProviderError("Provider error")
    assert error.message == "Provider error"
    assert error.details == {}
    assert isinstance(error, BNPLAccountError)


def test_bnpl_provider_error_with_account_id():
    """Test initializing BNPLProviderError with account ID."""
    error = BNPLProviderError("Provider error", account_id=123)
    assert error.message == "Provider error"
    assert error.details == {"account_id": 123}


def test_bnpl_provider_error_with_all_parameters():
    """Test initializing BNPLProviderError with all parameters."""
    error = BNPLProviderError(
        "Provider error",
        account_id=123,
        provider="Unknown",
        valid_providers=["Affirm", "Klarna", "Afterpay"],
        details={"integration_status": "failed"}
    )
    assert error.message == "Provider error"
    assert error.details["account_id"] == 123
    assert error.details["provider"] == "Unknown"
    assert error.details["valid_providers"] == ["Affirm", "Klarna", "Afterpay"]
    assert error.details["integration_status"] == "failed"


def test_bnpl_lifecycle_error_with_message_only():
    """Test initializing BNPLLifecycleError with just a message."""
    error = BNPLLifecycleError("Lifecycle error")
    assert error.message == "Lifecycle error"
    assert error.details == {}
    assert isinstance(error, BNPLAccountError)


def test_bnpl_lifecycle_error_with_account_id():
    """Test initializing BNPLLifecycleError with account ID."""
    error = BNPLLifecycleError("Lifecycle error", account_id=123)
    assert error.message == "Lifecycle error"
    assert error.details == {"account_id": 123}


def test_bnpl_lifecycle_error_with_all_parameters():
    """Test initializing BNPLLifecycleError with all parameters."""
    error = BNPLLifecycleError(
        "Lifecycle error",
        account_id=123,
        current_state="active",
        target_state="completed",
        details={"reason": "payments_incomplete"}
    )
    assert error.message == "Lifecycle error"
    assert error.details["account_id"] == 123
    assert error.details["current_state"] == "active"
    assert error.details["target_state"] == "completed"
    assert error.details["reason"] == "payments_incomplete"
