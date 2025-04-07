"""
Unit tests for feature flag error classes.

Tests ensure that feature flag error classes properly handle error details,
message formatting, and inheritance relationships.
"""

import pytest

from src.errors.accounts import AccountError
from src.errors.feature_flags import FeatureFlagAccountError


def test_feature_flag_account_error_with_flag_name_only():
    """Test initializing FeatureFlagAccountError with flag name only."""
    error = FeatureFlagAccountError("TEST_FLAG")
    assert error.message == "Operation not available: feature 'TEST_FLAG' is disabled"
    assert error.details == {"feature_flag": "TEST_FLAG"}
    assert isinstance(error, AccountError)


def test_feature_flag_account_error_with_custom_message():
    """Test initializing FeatureFlagAccountError with custom message."""
    error = FeatureFlagAccountError("TEST_FLAG", message="Custom feature flag message")
    assert error.message == "Custom feature flag message"
    assert error.details == {"feature_flag": "TEST_FLAG"}


def test_feature_flag_account_error_with_details():
    """Test initializing FeatureFlagAccountError with details."""
    details = {"account_id": 123, "account_type": "checking"}
    error = FeatureFlagAccountError("TEST_FLAG", details=details)
    assert error.message == "Operation not available: feature 'TEST_FLAG' is disabled"
    assert error.details["feature_flag"] == "TEST_FLAG"
    assert error.details["account_id"] == 123
    assert error.details["account_type"] == "checking"


def test_feature_flag_account_error_with_all_parameters():
    """Test initializing FeatureFlagAccountError with all parameters."""
    details = {"operation": "create", "reason": "maintenance"}
    error = FeatureFlagAccountError(
        "TEST_FLAG",
        message="Custom feature flag message",
        details=details
    )
    assert error.message == "Custom feature flag message"
    assert error.details["feature_flag"] == "TEST_FLAG"
    assert error.details["operation"] == "create"
    assert error.details["reason"] == "maintenance"


def test_feature_flag_account_error_to_dict():
    """Test converting FeatureFlagAccountError to dictionary."""
    error = FeatureFlagAccountError("TEST_FLAG")
    error_dict = error.to_dict()
    
    assert error_dict["error"] == "FeatureFlagAccountError"
    assert error_dict["message"] == "Operation not available: feature 'TEST_FLAG' is disabled"
    assert error_dict["details"]["feature_flag"] == "TEST_FLAG"


def test_feature_flag_account_error_str():
    """Test string representation of FeatureFlagAccountError."""
    error = FeatureFlagAccountError("TEST_FLAG")
    assert str(error) == "Operation not available: feature 'TEST_FLAG' is disabled"
