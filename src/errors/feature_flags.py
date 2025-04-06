"""
Feature flag related errors for account operations.

This module provides errors that occur due to feature flag restrictions.
"""

from typing import Any, Dict, Optional

from src.errors.accounts import AccountError


class FeatureFlagAccountError(AccountError):
    """Error raised when a feature flag prevents an account operation."""

    def __init__(
        self,
        flag_name: str,
        message: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ):
        message = (
            message or f"Operation not available: feature '{flag_name}' is disabled"
        )
        combined_details = details or {}
        combined_details["feature_flag"] = flag_name
        super().__init__(message, combined_details)
