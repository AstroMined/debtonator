"""
Unit tests for HTTP exception classes.

Tests ensure that HTTP exception classes properly handle error details,
status codes, and message formatting.
"""

import pytest
from fastapi import status

from src.errors.http_exceptions import (
    AccountHTTPException,
    AccountNotFoundHTTPException,
    AccountTypeHTTPException,
    AccountValidationHTTPException,
    AccountOperationHTTPException,
    FeatureFlagAccountHTTPException,
)


def test_account_http_exception_with_message_only():
    """Test initializing AccountHTTPException with message only."""
    exception = AccountHTTPException(status.HTTP_400_BAD_REQUEST, "Bad request")
    assert exception.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.detail == {"message": "Bad request"}


def test_account_http_exception_with_details():
    """Test initializing AccountHTTPException with details."""
    details = {"field": "value", "error_code": "INVALID_INPUT"}
    exception = AccountHTTPException(
        status.HTTP_400_BAD_REQUEST, "Bad request", details=details
    )
    assert exception.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.detail["message"] == "Bad request"
    assert exception.detail["field"] == "value"
    assert exception.detail["error_code"] == "INVALID_INPUT"


def test_account_http_exception_with_headers():
    """Test initializing AccountHTTPException with headers."""
    headers = {"X-Error-Code": "INVALID_INPUT"}
    exception = AccountHTTPException(
        status.HTTP_400_BAD_REQUEST, "Bad request", headers=headers
    )
    assert exception.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.detail == {"message": "Bad request"}
    assert exception.headers == headers


def test_account_http_exception_with_all_parameters():
    """Test initializing AccountHTTPException with all parameters."""
    details = {"field": "value", "error_code": "INVALID_INPUT"}
    headers = {"X-Error-Code": "INVALID_INPUT"}
    exception = AccountHTTPException(
        status.HTTP_400_BAD_REQUEST, "Bad request", headers=headers, details=details
    )
    assert exception.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.detail["message"] == "Bad request"
    assert exception.detail["field"] == "value"
    assert exception.detail["error_code"] == "INVALID_INPUT"
    assert exception.headers == headers


def test_account_not_found_http_exception_with_account_id():
    """Test initializing AccountNotFoundHTTPException with account ID."""
    exception = AccountNotFoundHTTPException(123)
    assert exception.status_code == status.HTTP_404_NOT_FOUND
    assert exception.detail["message"] == "Account with ID 123 not found"
    assert exception.detail["account_id"] == 123


def test_account_not_found_http_exception_with_custom_message():
    """Test initializing AccountNotFoundHTTPException with custom message."""
    exception = AccountNotFoundHTTPException(123, "Custom not found message")
    assert exception.status_code == status.HTTP_404_NOT_FOUND
    assert exception.detail["message"] == "Custom not found message"
    assert exception.detail["account_id"] == 123


def test_account_type_http_exception_with_account_type():
    """Test initializing AccountTypeHTTPException with account type."""
    exception = AccountTypeHTTPException("invalid_type")
    assert exception.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.detail["message"] == "Invalid or unsupported account type: invalid_type"
    assert exception.detail["account_type"] == "invalid_type"


def test_account_type_http_exception_with_custom_message():
    """Test initializing AccountTypeHTTPException with custom message."""
    exception = AccountTypeHTTPException("invalid_type", "Custom type error message")
    assert exception.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.detail["message"] == "Custom type error message"
    assert exception.detail["account_type"] == "invalid_type"


def test_account_validation_http_exception_with_message_only():
    """Test initializing AccountValidationHTTPException with message only."""
    exception = AccountValidationHTTPException("Validation error")
    assert exception.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert exception.detail["message"] == "Validation error"


def test_account_validation_http_exception_with_field_errors():
    """Test initializing AccountValidationHTTPException with field errors."""
    field_errors = {"field1": "Error in field1", "field2": "Error in field2"}
    exception = AccountValidationHTTPException("Validation error", field_errors)
    assert exception.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert exception.detail["message"] == "Validation error"
    assert exception.detail["field_errors"] == field_errors


def test_account_validation_http_exception_with_all_parameters():
    """Test initializing AccountValidationHTTPException with all parameters."""
    field_errors = {"field1": "Error in field1"}
    details = {"account_id": 123, "additional": "info"}
    exception = AccountValidationHTTPException("Validation error", field_errors, details)
    assert exception.status_code == status.HTTP_422_UNPROCESSABLE_ENTITY
    assert exception.detail["message"] == "Validation error"
    assert exception.detail["field_errors"] == field_errors
    assert exception.detail["account_id"] == 123
    assert exception.detail["additional"] == "info"


def test_account_operation_http_exception_with_operation_and_message():
    """Test initializing AccountOperationHTTPException with operation and message."""
    exception = AccountOperationHTTPException("create", "Operation failed")
    assert exception.status_code == status.HTTP_400_BAD_REQUEST
    assert exception.detail["message"] == "Operation failed"
    assert exception.detail["operation"] == "create"


def test_account_operation_http_exception_with_custom_status():
    """Test initializing AccountOperationHTTPException with custom status code."""
    exception = AccountOperationHTTPException(
        "delete", "Operation failed", status.HTTP_409_CONFLICT
    )
    assert exception.status_code == status.HTTP_409_CONFLICT
    assert exception.detail["message"] == "Operation failed"
    assert exception.detail["operation"] == "delete"


def test_account_operation_http_exception_with_all_parameters():
    """Test initializing AccountOperationHTTPException with all parameters."""
    details = {"account_id": 123, "reason": "database_error"}
    exception = AccountOperationHTTPException(
        "update", "Operation failed", status.HTTP_409_CONFLICT, details
    )
    assert exception.status_code == status.HTTP_409_CONFLICT
    assert exception.detail["message"] == "Operation failed"
    assert exception.detail["operation"] == "update"
    assert exception.detail["account_id"] == 123
    assert exception.detail["reason"] == "database_error"


def test_feature_flag_account_http_exception_with_flag_name():
    """Test initializing FeatureFlagAccountHTTPException with flag name."""
    exception = FeatureFlagAccountHTTPException("TEST_FLAG")
    assert exception.status_code == status.HTTP_403_FORBIDDEN
    assert exception.detail["message"] == "Operation not available: feature 'TEST_FLAG' is disabled"
    assert exception.detail["feature_flag"] == "TEST_FLAG"


def test_feature_flag_account_http_exception_with_custom_message():
    """Test initializing FeatureFlagAccountHTTPException with custom message."""
    exception = FeatureFlagAccountHTTPException("TEST_FLAG", "Custom feature flag message")
    assert exception.status_code == status.HTTP_403_FORBIDDEN
    assert exception.detail["message"] == "Custom feature flag message"
    assert exception.detail["feature_flag"] == "TEST_FLAG"


def test_feature_flag_account_http_exception_with_all_parameters():
    """Test initializing FeatureFlagAccountHTTPException with all parameters."""
    details = {"account_id": 123, "account_type": "checking"}
    exception = FeatureFlagAccountHTTPException(
        "TEST_FLAG", "Custom feature flag message", details
    )
    assert exception.status_code == status.HTTP_403_FORBIDDEN
    assert exception.detail["message"] == "Custom feature flag message"
    assert exception.detail["feature_flag"] == "TEST_FLAG"
    assert exception.detail["account_id"] == 123
    assert exception.detail["account_type"] == "checking"
