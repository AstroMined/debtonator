"""
Unit tests for the account type registry.

These tests verify that the account type registry properly stores, retrieves,
and validates account types.
"""

from src.registry.account_types import account_type_registry


def test_account_type_registry():
    """Test account type registry lookup and validation."""
    # Verify registry contains expected types
    # Note: Only banking types are currently registered
    valid_types = [
        "checking",
        "savings",
        "credit",
        "payment_app",
        "bnpl",
        "ewa",
    ]

    for account_type in valid_types:
        assert account_type_registry.is_valid_account_type(account_type)

    # Test with invalid account type
    assert not account_type_registry.is_valid_account_type("invalid_type")

    # Future account types that are planned but not yet implemented should not be valid
    assert not account_type_registry.is_valid_account_type("investment")
    assert not account_type_registry.is_valid_account_type("loan")
    assert not account_type_registry.is_valid_account_type("mortgage")
    assert not account_type_registry.is_valid_account_type("bill")
    assert not account_type_registry.is_valid_account_type("prepaid")

    # Test getting all types
    all_types = account_type_registry.get_all_types()
    assert len(all_types) >= len(valid_types)

    # Check structure of returned type info
    for type_info in all_types:
        assert "id" in type_info
        assert "name" in type_info
        assert "description" in type_info
