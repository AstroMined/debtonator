"""
Unit tests for error utility functions.

Tests ensure that error utility functions properly convert between error types
and perform other error-related operations.
"""

import pytest
from fastapi import status

from src.errors.accounts import (
    AccountError,
    AccountNotFoundError,
    AccountTypeError,
    AccountValidationError,
    AccountOperationError,
)
from src.errors.feature_flags import FeatureFlagAccountError
from src.errors.http_exceptions import (
    AccountHTTPException,
    AccountNotFoundHTTPException,
    AccountTypeHTTPException,
    AccountValidationHTTPException,
    AccountOperationHTTPException,
    FeatureFlagAccountHTTPException,
)
from src.errors.utils import account_error_to_http_exception


def test_account_not_found_error_conversion():
    """Test converting AccountNotFoundError to HTTP exception."""
    error = AccountNotFoundError(123)
    exception = account_error_to_http_exception(error)
    
    assert isinstance(exception, AccountNotFoundHTTPException)
    assert exception.status_code == status.HTTP_404_NOT_FOUND
    assert exception.detail["message"] == "Account with ID 123 not found"
    assert exception.detail["account_id"] == 123


def test_account_type_error_conversion():
    """Test converting AccountTypeError to HTTP exception."""
    error = AccountTypeError("invalid_type")
    exception = account_error_to_http_exception(error)
    
    assert isinstance(exception, AccountTypeHTTPException)
    assert exception.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.detail["message"] == "Invalid or unsupported account type: invalid_type"
    assert exception.detail["account_type"] == "invalid_type"


def test_account_validation_error_conversion():
    """Test converting AccountValidationError to HTTP exception."""
    field_errors = {"field1": "Error in field1", "field2": "Error in field2"}
    error = AccountValidationError("Validation error", field_errors)
    exception = account_error_to_http_exception(error)
    
    assert isinstance(exception, AccountValidationHTTPException)
    assert exception.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert exception.detail["message"] == "Validation error"
    assert exception.detail["field_errors"] == field_errors


def test_account_operation_error_conversion():
    """Test converting AccountOperationError to HTTP exception."""
    error = AccountOperationError("create", "Operation failed")
    exception = account_error_to_http_exception(error)
    
    assert isinstance(exception, AccountOperationHTTPException)
    assert exception.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.detail["message"] == "Operation failed"
    assert exception.detail["operation"] == "create"


def test_feature_flag_account_error_conversion():
    """Test converting FeatureFlagAccountError to HTTP exception."""
    error = FeatureFlagAccountError("TEST_FLAG")
    exception = account_error_to_http_exception(error)
    
    assert isinstance(exception, FeatureFlagAccountHTTPException)
    assert exception.status_code == status.HTTP_403_FORBIDDEN
    assert exception.detail["message"] == "Operation not available: feature 'TEST_FLAG' is disabled"
    assert exception.detail["feature_flag"] == "TEST_FLAG"


def test_unknown_account_error_conversion():
    """Test converting unknown AccountError to HTTP exception."""
    class CustomAccountError(AccountError):
        """Custom account error for testing."""
        pass
    
    error = CustomAccountError("Custom error message")
    exception = account_error_to_http_exception(error)
    
    assert isinstance(exception, AccountHTTPException)
    assert exception.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exception.detail["message"] == "Custom error message"


def test_account_error_with_details_conversion():
    """Test converting AccountError with details to HTTP exception."""
    details = {"key1": "value1", "key2": 42}
    error = AccountError("Error with details", details)
    exception = account_error_to_http_exception(error)
    
    assert isinstance(exception, AccountHTTPException)
    assert exception.status_code == status.HTTP_500_INTERNAL_SERVER_ERROR
    assert exception.detail["message"] == "Error with details"
    assert exception.detail["key1"] == "value1"
    assert exception.detail["key2"] == 42


def test_account_validation_error_with_details_conversion():
    """Test converting AccountValidationError with details to HTTP exception."""
    field_errors = {"field1": "Error in field1"}
    details = {"account_id": 123, "additional": "info"}
    error = AccountValidationError("Validation error", field_errors, details)
    exception = account_error_to_http_exception(error)
    
    assert isinstance(exception, AccountValidationHTTPException)
    assert exception.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert exception.detail["message"] == "Validation error"
    assert exception.detail["field_errors"] == field_errors
    assert exception.detail["account_id"] == 123
    assert exception.detail["additional"] == "info"
