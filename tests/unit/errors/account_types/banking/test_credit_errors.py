"""
Unit tests for credit account error classes.

Tests ensure that credit account error classes properly handle error details,
message formatting, and inheritance relationships.
"""

from decimal import Decimal

from src.errors.account_types.banking.credit import (
    CreditAccountError,
    CreditAPRError,
    CreditAutopayError,
    CreditCreditLimitExceededError,
    CreditPaymentDueError,
    CreditStatementError,
)
from src.errors.accounts import AccountError
from src.utils.datetime_utils import utc_datetime


def test_credit_account_error_with_message_only():
    """Test initializing CreditAccountError with just a message."""
    error = CreditAccountError("Test error message")
    assert error.message == "Test error message"
    assert error.details == {}
    assert str(error) == "Test error message"
    assert isinstance(error, AccountError)


def test_credit_account_error_with_details():
    """Test initializing CreditAccountError with details."""
    details = {"key1": "value1", "key2": 42}
    error = CreditAccountError("Test error message", details)
    assert error.message == "Test error message"
    assert error.details == details


def test_credit_credit_limit_exceeded_error_with_message_only():
    """Test initializing CreditCreditLimitExceededError with just a message."""
    error = CreditCreditLimitExceededError("Credit limit exceeded")
    assert error.message == "Credit limit exceeded"
    assert error.details == {}
    assert isinstance(error, CreditAccountError)


def test_credit_credit_limit_exceeded_error_with_account_id():
    """Test initializing CreditCreditLimitExceededError with account ID."""
    error = CreditCreditLimitExceededError("Credit limit exceeded", account_id=123)
    assert error.message == "Credit limit exceeded"
    assert error.details == {"account_id": 123}


def test_credit_credit_limit_exceeded_error_with_all_parameters():
    """Test initializing CreditCreditLimitExceededError with all parameters."""
    error = CreditCreditLimitExceededError(
        "Credit limit exceeded",
        account_id=123,
        current_balance=Decimal("1500.00"),
        credit_limit=Decimal("1000.00"),
        transaction_amount=Decimal("600.00"),
        details={"transaction_id": 456},
    )
    assert error.message == "Credit limit exceeded"
    assert error.details["account_id"] == 123
    assert error.details["current_balance"] == Decimal("1500.00")
    assert error.details["credit_limit"] == Decimal("1000.00")
    assert error.details["transaction_amount"] == Decimal("600.00")
    assert error.details["transaction_id"] == 456


def test_credit_payment_due_error_with_message_only():
    """Test initializing CreditPaymentDueError with just a message."""
    error = CreditPaymentDueError("Payment past due")
    assert error.message == "Payment past due"
    assert error.details == {}
    assert isinstance(error, CreditAccountError)


def test_credit_payment_due_error_with_account_id():
    """Test initializing CreditPaymentDueError with account ID."""
    error = CreditPaymentDueError("Payment past due", account_id=123)
    assert error.message == "Payment past due"
    assert error.details == {"account_id": 123}


def test_credit_payment_due_error_with_all_parameters():
    """Test initializing CreditPaymentDueError with all parameters."""
    due_date = utc_datetime(2025, 4, 1)
    error = CreditPaymentDueError(
        "Payment past due",
        account_id=123,
        due_date=due_date,
        minimum_payment=Decimal("35.00"),
        details={"days_past_due": 5},
    )
    assert error.message == "Payment past due"
    assert error.details["account_id"] == 123
    assert error.details["due_date"] == due_date.isoformat()
    assert error.details["minimum_payment"] == Decimal("35.00")
    assert error.details["days_past_due"] == 5


def test_credit_apr_error_with_message_only():
    """Test initializing CreditAPRError with just a message."""
    error = CreditAPRError("Invalid APR")
    assert error.message == "Invalid APR"
    assert error.details == {}
    assert isinstance(error, CreditAccountError)


def test_credit_apr_error_with_apr():
    """Test initializing CreditAPRError with APR."""
    error = CreditAPRError("Invalid APR", apr=Decimal("30.0"))
    assert error.message == "Invalid APR"
    assert error.details == {"apr": Decimal("30.0")}


def test_credit_apr_error_with_all_parameters():
    """Test initializing CreditAPRError with all parameters."""
    error = CreditAPRError(
        "Invalid APR",
        apr=Decimal("30.0"),
        details={"card_type": "rewards", "max_apr": Decimal("29.99")},
    )
    assert error.message == "Invalid APR"
    assert error.details["apr"] == Decimal("30.0")
    assert error.details["card_type"] == "rewards"
    assert error.details["max_apr"] == Decimal("29.99")


def test_credit_autopay_error_with_message_only():
    """Test initializing CreditAutopayError with just a message."""
    error = CreditAutopayError("Autopay setup failed")
    assert error.message == "Autopay setup failed"
    assert error.details == {}
    assert isinstance(error, CreditAccountError)


def test_credit_autopay_error_with_autopay_status():
    """Test initializing CreditAutopayError with autopay status."""
    error = CreditAutopayError("Autopay setup failed", autopay_status="disabled")
    assert error.message == "Autopay setup failed"
    assert error.details == {"autopay_status": "disabled"}


def test_credit_autopay_error_with_all_parameters():
    """Test initializing CreditAutopayError with all parameters."""
    error = CreditAutopayError(
        "Autopay setup failed",
        autopay_status="failed",
        details={
            "account_id": 123,
            "payment_source_id": 456,
            "autopay_type": "minimum_payment",
            "reason": "invalid_payment_source",
        },
    )
    assert error.message == "Autopay setup failed"
    assert error.details["autopay_status"] == "failed"
    assert error.details["account_id"] == 123
    assert error.details["payment_source_id"] == 456
    assert error.details["autopay_type"] == "minimum_payment"
    assert error.details["reason"] == "invalid_payment_source"


def test_credit_statement_error_with_message_only():
    """Test initializing CreditStatementError with just a message."""
    error = CreditStatementError("Statement generation failed")
    assert error.message == "Statement generation failed"
    assert error.details == {}
    assert isinstance(error, CreditAccountError)


def test_credit_statement_error_with_statement_date():
    """Test initializing CreditStatementError with statement date."""
    statement_date = utc_datetime(2025, 3, 31)
    error = CreditStatementError(
        "Statement generation failed", statement_date=statement_date
    )
    assert error.message == "Statement generation failed"
    assert error.details == {"statement_date": statement_date.isoformat()}


def test_credit_statement_error_with_none_statement_date():
    """Test initializing CreditStatementError with None statement date."""
    error = CreditStatementError("Statement generation failed", statement_date=None)
    assert error.message == "Statement generation failed"
    assert error.details == {}


def test_credit_statement_error_with_all_parameters():
    """Test initializing CreditStatementError with all parameters."""
    statement_date = utc_datetime(2025, 3, 31)
    error = CreditStatementError(
        "Statement generation failed",
        statement_date=statement_date,
        details={"account_id": 123, "reason": "missing_transactions"},
    )
    assert error.message == "Statement generation failed"
    assert error.details["statement_date"] == statement_date.isoformat()
    assert error.details["account_id"] == 123
    assert error.details["reason"] == "missing_transactions"
