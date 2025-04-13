"""
Tests for feature flag context schema.

This module contains tests for the FeatureFlagContext schema, which is used to
provide context information for feature flag evaluation.
"""

import pytest
from pydantic import ValidationError

from src.schemas.feature_flags import FeatureFlagContext


def test_empty_context():
    """Test that an empty context is valid."""
    context = FeatureFlagContext()
    assert context.user_id is None
    assert context.user_groups is None
    assert context.is_admin is None
    assert context.is_beta_tester is None
    assert context.request_path is None
    assert context.client_ip is None


def test_user_context():
    """Test a context with user information."""
    context = FeatureFlagContext(
        user_id="user-123",
        user_groups=["admin", "beta"],
        is_admin=True,
        is_beta_tester=True,
    )
    assert context.user_id == "user-123"
    assert context.user_groups == ["admin", "beta"]
    assert context.is_admin is True
    assert context.is_beta_tester is True


def test_request_context():
    """Test a context with request information."""
    context = FeatureFlagContext(
        request_path="/api/v1/accounts",
        client_ip="192.168.1.1",
    )
    assert context.request_path == "/api/v1/accounts"
    assert context.client_ip == "192.168.1.1"


def test_full_context():
    """Test a context with all information."""
    context = FeatureFlagContext(
        user_id="user-123",
        user_groups=["admin", "beta"],
        is_admin=True,
        is_beta_tester=True,
        request_path="/api/v1/accounts",
        client_ip="192.168.1.1",
    )
    assert context.user_id == "user-123"
    assert context.user_groups == ["admin", "beta"]
    assert context.is_admin is True
    assert context.is_beta_tester is True
    assert context.request_path == "/api/v1/accounts"
    assert context.client_ip == "192.168.1.1"


def test_feature_flag_context_with_all_fields():
    """Test feature flag context with all fields populated."""
    context = FeatureFlagContext(
        user_id="user-123",
        user_groups=["admin", "beta", "premium"],
        is_admin=True,
        is_beta_tester=True,
        request_path="/api/v1/accounts",
        client_ip="192.168.1.1",
    )
    assert context.user_id == "user-123"
    assert context.user_groups == ["admin", "beta", "premium"]
    assert context.is_admin is True
    assert context.is_beta_tester is True
    assert context.request_path == "/api/v1/accounts"
    assert context.client_ip == "192.168.1.1"


def test_context_with_invalid_user_groups():
    """Test that user_groups must be a list."""
    with pytest.raises(ValidationError, match="Input should be a valid list"):
        FeatureFlagContext(
            user_id="user-123",
            user_groups="admin,beta",  # String instead of list
        )


def test_context_with_invalid_user_group_types():
    """Test that user_groups must contain strings."""
    with pytest.raises(ValidationError, match="Input should be a valid string"):
        FeatureFlagContext(
            user_id="user-123",
            user_groups=[123, 456],  # Numbers instead of strings
        )


def test_context_with_invalid_boolean_fields():
    """Test that boolean fields must be booleans."""
    with pytest.raises(ValidationError, match="is_admin must be a boolean value"):
        FeatureFlagContext(
            user_id="user-123",
            is_admin="yes",  # String instead of boolean
        )

    with pytest.raises(ValidationError, match="is_beta_tester must be a boolean value"):
        FeatureFlagContext(
            user_id="user-123",
            is_beta_tester="true",  # String instead of boolean
        )


def test_context_with_invalid_ip_address():
    """Test that client_ip must be a valid IP address format."""
    with pytest.raises(ValidationError, match="client_ip must be a valid IP address"):
        FeatureFlagContext(
            client_ip="not-an-ip-address",  # Invalid IP format
        )

    # Valid IPv4
    context = FeatureFlagContext(client_ip="192.168.1.1")
    assert context.client_ip == "192.168.1.1"

    # Valid IPv6
    context = FeatureFlagContext(client_ip="2001:0db8:85a3:0000:0000:8a2e:0370:7334")
    assert context.client_ip == "2001:0db8:85a3:0000:0000:8a2e:0370:7334"
