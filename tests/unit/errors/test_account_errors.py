"""
Unit tests for account error classes.

Tests ensure that account error classes properly handle error details, 
message formatting, and conversion to HTTP exceptions.
"""

import pytest
from fastapi import status

from src.errors.accounts import (
    AccountError,
    AccountNotFoundError,
    AccountTypeError,
    AccountValidationError,
    AccountOperationError,
    CheckingAccountError,
    SavingsAccountError,
    CreditAccountError,
    PaymentAppAccountError,
    BNPLAccountError,
    BNPLInstallmentError,
    EWAAccountError,
    FeatureFlagAccountError,
    AccountHTTPException,
    AccountNotFoundHTTPException,
    AccountTypeHTTPException,
    AccountValidationHTTPException,
    AccountOperationHTTPException,
    FeatureFlagAccountHTTPException,
    account_error_to_http_exception,
)


class TestBaseAccountError:
    """Tests for the base AccountError class."""

    def test_init_with_message_only(self):
        """Test initializing with just a message."""
        error = AccountError("Test error message")
        assert error.message == "Test error message"
        assert error.details == {}
        assert str(error) == "Test error message"

    def test_init_with_details(self):
        """Test initializing with details."""
        details = {"key1": "value1", "key2": 42}
        error = AccountError("Test error message", details)
        assert error.message == "Test error message"
        assert error.details == details

    def test_to_dict(self):
        """Test converting error to dictionary."""
        details = {"key1": "value1", "key2": 42}
        error = AccountError("Test error message", details)
        error_dict = error.to_dict()
        
        assert error_dict["error"] == "AccountError"
        assert error_dict["message"] == "Test error message"
        assert error_dict["details"] == details


class TestAccountNotFoundError:
    """Tests for AccountNotFoundError."""

    def test_init_with_account_id(self):
        """Test initializing with account ID."""
        error = AccountNotFoundError(123)
        assert error.message == "Account with ID 123 not found"
        assert error.details == {"account_id": 123}

    def test_init_with_custom_message(self):
        """Test initializing with custom message."""
        error = AccountNotFoundError(123, "Custom not found message")
        assert error.message == "Custom not found message"
        assert error.details == {"account_id": 123}


class TestAccountTypeError:
    """Tests for AccountTypeError."""

    def test_init_with_account_type(self):
        """Test initializing with account type."""
        error = AccountTypeError("invalid_type")
        assert error.message == "Invalid or unsupported account type: invalid_type"
        assert error.details == {"account_type": "invalid_type"}

    def test_init_with_custom_message(self):
        """Test initializing with custom message."""
        error = AccountTypeError("invalid_type", "Custom type error message")
        assert error.message == "Custom type error message"
        assert error.details == {"account_type": "invalid_type"}


class TestAccountValidationError:
    """Tests for AccountValidationError."""

    def test_init_with_message_only(self):
        """Test initializing with message only."""
        error = AccountValidationError("Validation error")
        assert error.message == "Validation error"
        assert error.details == {}

    def test_init_with_field_errors(self):
        """Test initializing with field errors."""
        field_errors = {"field1": "Error in field1", "field2": "Error in field2"}
        error = AccountValidationError("Validation error", field_errors)
        assert error.message == "Validation error"
        assert error.details == {"field_errors": field_errors}

    def test_init_with_field_errors_and_details(self):
        """Test initializing with field errors and additional details."""
        field_errors = {"field1": "Error in field1"}
        details = {"additional": "info"}
        error = AccountValidationError("Validation error", field_errors, details)
        assert error.message == "Validation error"
        assert error.details["field_errors"] == field_errors
        assert error.details["additional"] == "info"


class TestAccountOperationError:
    """Tests for AccountOperationError."""

    def test_init_with_operation_and_message(self):
        """Test initializing with operation and message."""
        error = AccountOperationError("create", "Operation failed")
        assert error.message == "Operation failed"
        assert error.details == {"operation": "create"}

    def test_init_with_additional_details(self):
        """Test initializing with additional details."""
        details = {"cause": "database_error"}
        error = AccountOperationError("update", "Operation failed", details)
        assert error.message == "Operation failed"
        assert error.details["operation"] == "update"
        assert error.details["cause"] == "database_error"


class TestTypeSpecificErrors:
    """Tests for type-specific error classes."""

    def test_checking_account_error(self):
        """Test CheckingAccountError."""
        error = CheckingAccountError("Checking account error")
        assert error.message == "Checking account error"
        assert isinstance(error, AccountError)

    def test_savings_account_error(self):
        """Test SavingsAccountError."""
        error = SavingsAccountError("Savings account error")
        assert error.message == "Savings account error"
        assert isinstance(error, AccountError)

    def test_credit_account_error(self):
        """Test CreditAccountError."""
        error = CreditAccountError("Credit account error")
        assert error.message == "Credit account error"
        assert isinstance(error, AccountError)

    def test_payment_app_account_error(self):
        """Test PaymentAppAccountError."""
        error = PaymentAppAccountError("Payment app error")
        assert error.message == "Payment app error"
        assert isinstance(error, AccountError)

    def test_ewa_account_error(self):
        """Test EWAAccountError."""
        error = EWAAccountError("EWA account error")
        assert error.message == "EWA account error"
        assert isinstance(error, AccountError)


class TestBNPLErrors:
    """Tests for BNPL-specific error classes."""

    def test_bnpl_account_error(self):
        """Test BNPLAccountError."""
        error = BNPLAccountError("BNPL error")
        assert error.message == "BNPL error"
        assert error.details == {}
        assert isinstance(error, AccountError)

    def test_bnpl_account_error_with_account_id(self):
        """Test BNPLAccountError with account ID."""
        error = BNPLAccountError("BNPL error", 123)
        assert error.message == "BNPL error"
        assert error.details == {"account_id": 123}

    def test_bnpl_account_error_with_details(self):
        """Test BNPLAccountError with details."""
        details = {"provider": "Affirm"}
        error = BNPLAccountError("BNPL error", 123, details)
        assert error.message == "BNPL error"
        assert error.details["account_id"] == 123
        assert error.details["provider"] == "Affirm"

    def test_bnpl_installment_error(self):
        """Test BNPLInstallmentError."""
        error = BNPLInstallmentError("Installment error")
        assert error.message == "Installment error"
        assert error.details == {}
        assert isinstance(error, BNPLAccountError)

    def test_bnpl_installment_error_with_all_fields(self):
        """Test BNPLInstallmentError with all fields."""
        details = {"amount": 100.0}
        error = BNPLInstallmentError("Installment error", 123, 2, details)
        assert error.message == "Installment error"
        assert error.details["account_id"] == 123
        assert error.details["installment_number"] == 2
        assert error.details["amount"] == 100.0


class TestFeatureFlagAccountError:
    """Tests for FeatureFlagAccountError."""

    def test_init_with_flag_name(self):
        """Test initializing with flag name."""
        error = FeatureFlagAccountError("TEST_FLAG")
        assert error.message == "Operation not available: feature 'TEST_FLAG' is disabled"
        assert error.details == {"feature_flag": "TEST_FLAG"}

    def test_init_with_custom_message(self):
        """Test initializing with custom message."""
        error = FeatureFlagAccountError("TEST_FLAG", "Custom message")
        assert error.message == "Custom message"
        assert error.details == {"feature_flag": "TEST_FLAG"}

    def test_init_with_details(self):
        """Test initializing with details."""
        details = {"account_type": "checking"}
        error = FeatureFlagAccountError("TEST_FLAG", "Custom message", details)
        assert error.message == "Custom message"
        assert error.details["feature_flag"] == "TEST_FLAG"
        assert error.details["account_type"] == "checking"


class TestHTTPExceptions:
    """Tests for HTTP exception classes."""

    def test_account_http_exception(self):
        """Test AccountHTTPException."""
        exception = AccountHTTPException(status.HTTP_400_BAD_REQUEST, "Bad request")
        assert exception.status_code == status.HTTP_400_BAD_REQUEST
        assert exception.detail == {"message": "Bad request"}

    def test_account_http_exception_with_details(self):
        """Test AccountHTTPException with details."""
        details = {"field": "value"}
        exception = AccountHTTPException(
            status.HTTP_400_BAD_REQUEST, "Bad request", None, details
        )
        assert exception.status_code == status.HTTP_400_BAD_REQUEST
        assert exception.detail["message"] == "Bad request"
        assert exception.detail["field"] == "value"

    def test_account_not_found_http_exception(self):
        """Test AccountNotFoundHTTPException."""
        exception = AccountNotFoundHTTPException(123)
        assert exception.status_code == status.HTTP_404_NOT_FOUND
        assert exception.detail["message"] == "Account with ID 123 not found"
        assert exception.detail["account_id"] == 123

    def test_account_type_http_exception(self):
        """Test AccountTypeHTTPException."""
        exception = AccountTypeHTTPException("invalid_type")
        assert exception.status_code == status.HTTP_400_BAD_REQUEST
        assert exception.detail["message"] == "Invalid or unsupported account type: invalid_type"
        assert exception.detail["account_type"] == "invalid_type"

    def test_account_validation_http_exception(self):
        """Test AccountValidationHTTPException."""
        field_errors = {"field1": "Error in field1"}
        exception = AccountValidationHTTPException("Validation error", field_errors)
        assert exception.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert exception.detail["message"] == "Validation error"
        assert exception.detail["field_errors"] == field_errors

    def test_account_operation_http_exception(self):
        """Test AccountOperationHTTPException."""
        exception = AccountOperationHTTPException("create", "Operation failed")
        assert exception.status_code == status.HTTP_400_BAD_REQUEST
        assert exception.detail["message"] == "Operation failed"
        assert exception.detail["operation"] == "create"

    def test_account_operation_http_exception_with_custom_status(self):
        """Test AccountOperationHTTPException with custom status code."""
        exception = AccountOperationHTTPException(
            "delete", "Operation failed", status.HTTP_409_CONFLICT
        )
        assert exception.status_code == status.HTTP_409_CONFLICT
        assert exception.detail["message"] == "Operation failed"
        assert exception.detail["operation"] == "delete"

    def test_feature_flag_account_http_exception(self):
        """Test FeatureFlagAccountHTTPException."""
        exception = FeatureFlagAccountHTTPException("TEST_FLAG")
        assert exception.status_code == status.HTTP_403_FORBIDDEN
        assert exception.detail["message"] == "Operation not available: feature 'TEST_FLAG' is disabled"
        assert exception.detail["feature_flag"] == "TEST_FLAG"


class TestErrorConversion:
    """Tests for error conversion utilities."""

    def test_account_not_found_error_conversion(self):
        """Test converting AccountNotFoundError to HTTP exception."""
        error = AccountNotFoundError(123)
        exception = account_error_to_http_exception(error)
        assert isinstance(exception, AccountNotFoundHTTPException)
        assert exception.status_code == status.HTTP_404_NOT_FOUND
        assert exception.detail["account_id"] == 123

    def test_account_type_error_conversion(self):
        """Test converting AccountTypeError to HTTP exception."""
        error = AccountTypeError("invalid_type")
        exception = account_error_to_http_exception(error)
        assert isinstance(exception, AccountTypeHTTPException)
        assert exception.status_code == status.HTTP_400_BAD_REQUEST
        assert exception.detail["account_type"] == "invalid_type"

    def test_account_validation_error_conversion(self):
        """Test converting AccountValidationError to HTTP exception."""
        field_errors = {"field1": "Error in field1"}
        error = AccountValidationError("Validation error", field_errors)
        exception = account_error_to_http_exception(error)
        assert isinstance(exception, AccountValidationHTTPException)
        assert exception.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
        assert exception.detail["field_errors"] == field_errors

    def test_feature_flag_account_error_conversion(self):
        """Test converting FeatureFlagAccountError to HTTP exception."""
        error = FeatureFlagAccountError("TEST_FLAG")
        exception = account_error_to_http_exception(error)
        assert isinstance(exception, FeatureFlagAccountHTTPException)
        assert exception.status_code == status.HTTP_403_FORBIDDEN
        assert exception.detail["feature_flag"] == "TEST_FLAG"

    def test_account_operation_error_conversion(self):
        """Test converting AccountOperationError to HTTP exception."""
        error = AccountOperationError("create", "Operation failed")
        exception = account_error_to_http_exception(error)
        assert isinstance(exception, AccountOperationHTTPException)
        assert exception.status_code == status.HTTP_400_BAD_REQUEST
        assert exception.detail["operation"] == "create"

    def test_unknown_error_conversion(self):
        """Test converting unknown error to HTTP exception."""
        class CustomAccountError(AccountError):
            pass

        error = CustomAccountError("Custom error")
        exception = account_error_to_http_exception(error)
        assert isinstance(exception, AccountHTTPException)
        assert exception.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
        assert exception.detail["message"] == "Custom error"
