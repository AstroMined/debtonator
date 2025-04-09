"""
Unit tests for base account error classes.

Tests ensure that base account error classes properly handle error details,
message formatting, and inheritance relationships.
"""

from src.errors.accounts import (
    AccountError,
    AccountNotFoundError,
    AccountOperationError,
    AccountTypeError,
    AccountValidationError,
)


def test_account_error_with_message_only():
    """Test initializing AccountError with just a message."""
    error = AccountError("Test error message")
    assert error.message == "Test error message"
    assert error.details == {}
    assert str(error) == "Test error message"


def test_account_error_with_details():
    """Test initializing AccountError with details."""
    details = {"key1": "value1", "key2": 42}
    error = AccountError("Test error message", details)
    assert error.message == "Test error message"
    assert error.details == details


def test_account_error_to_dict_with_details():
    """Test converting AccountError with details to dictionary."""
    details = {"key1": "value1", "key2": 42}
    error = AccountError("Test error message", details)
    error_dict = error.to_dict()

    assert error_dict["error"] == "AccountError"
    assert error_dict["message"] == "Test error message"
    assert error_dict["details"] == details


def test_account_error_to_dict_without_details():
    """Test converting AccountError without details to dictionary."""
    error = AccountError("Test error message")
    error_dict = error.to_dict()

    assert error_dict["error"] == "AccountError"
    assert error_dict["message"] == "Test error message"
    assert "details" not in error_dict


def test_account_not_found_error_with_account_id():
    """Test initializing AccountNotFoundError with account ID."""
    error = AccountNotFoundError(123)
    assert error.message == "Account with ID 123 not found"
    assert error.details == {"account_id": 123}
    assert isinstance(error, AccountError)


def test_account_not_found_error_with_custom_message():
    """Test initializing AccountNotFoundError with custom message."""
    error = AccountNotFoundError(123, "Custom not found message")
    assert error.message == "Custom not found message"
    assert error.details == {"account_id": 123}


def test_account_type_error_with_account_type():
    """Test initializing AccountTypeError with account type."""
    error = AccountTypeError("invalid_type")
    assert error.message == "Invalid or unsupported account type: invalid_type"
    assert error.details == {"account_type": "invalid_type"}
    assert isinstance(error, AccountError)


def test_account_type_error_with_custom_message():
    """Test initializing AccountTypeError with custom message."""
    error = AccountTypeError("invalid_type", "Custom type error message")
    assert error.message == "Custom type error message"
    assert error.details == {"account_type": "invalid_type"}


def test_account_validation_error_with_message_only():
    """Test initializing AccountValidationError with message only."""
    error = AccountValidationError("Validation error")
    assert error.message == "Validation error"
    assert error.details == {}
    assert isinstance(error, AccountError)


def test_account_validation_error_with_field_errors():
    """Test initializing AccountValidationError with field errors."""
    field_errors = {"field1": "Error in field1", "field2": "Error in field2"}
    error = AccountValidationError("Validation error", field_errors)
    assert error.message == "Validation error"
    assert error.details == {"field_errors": field_errors}


def test_account_validation_error_with_none_field_errors():
    """Test initializing AccountValidationError with None field errors."""
    error = AccountValidationError("Validation error", None)
    assert error.message == "Validation error"
    assert error.details == {}


def test_account_validation_error_with_field_errors_and_details():
    """Test initializing AccountValidationError with field errors and additional details."""
    field_errors = {"field1": "Error in field1"}
    details = {"additional": "info"}
    error = AccountValidationError("Validation error", field_errors, details)
    assert error.message == "Validation error"
    assert error.details["field_errors"] == field_errors
    assert error.details["additional"] == "info"


def test_account_operation_error_with_operation_and_message():
    """Test initializing AccountOperationError with operation and message."""
    error = AccountOperationError("create", "Operation failed")
    assert error.message == "Operation failed"
    assert error.details == {"operation": "create"}
    assert isinstance(error, AccountError)


def test_account_operation_error_with_additional_details():
    """Test initializing AccountOperationError with additional details."""
    details = {"cause": "database_error"}
    error = AccountOperationError("update", "Operation failed", details)
    assert error.message == "Operation failed"
    assert error.details["operation"] == "update"
    assert error.details["cause"] == "database_error"
