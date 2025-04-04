"""
Integration tests for registry initialization.

These tests verify that both account type and feature flag registries
are properly initialized through the application startup process.
"""

import pytest
from fastapi.testclient import TestClient

from src.registry.account_types import account_type_registry
from src.utils.feature_flags.feature_flags import get_registry


async def test_account_type_registry_initialized(client):
    """Test that the account type registry is initialized through the app startup."""
    # The client fixture initializes the app
    
    # Verify registry contains expected types
    types = account_type_registry.get_all_types()
    type_ids = [t["id"] for t in types]
    
    # Check for essential banking types
    assert "checking" in type_ids
    assert "savings" in type_ids
    assert "credit" in type_ids
    assert "bnpl" in type_ids
    assert "ewa" in type_ids
    assert "payment_app" in type_ids
    
    # Verify we can validate account types
    assert account_type_registry.is_valid_account_type("checking")
    assert account_type_registry.is_valid_account_type("savings")
    assert account_type_registry.is_valid_account_type("credit")
    
    # Verify invalid types are rejected
    assert not account_type_registry.is_valid_account_type("invalid_type")


async def test_feature_flag_registry_initialized(client):
    """Test that the feature flag registry is initialized through the app startup."""
    # Get the singleton registry instance
    registry = get_registry()
    
    # Verify basic registry operations work
    # Since we can't predict exact flags in the test DB, we just verify the registry exists
    # and basic methods are operational
    assert registry is not None
    
    # Verify we can get all flags (even if empty in test environment)
    flags = registry.get_all_flags()
    assert isinstance(flags, dict)
    
    # Test we can register a flag (this would only work if registry is initialized)
    test_flag_name = "TEST_INTEGRATION_FLAG"
    if test_flag_name not in flags:
        registry.register(
            flag_name=test_flag_name,
            flag_type="boolean",
            default_value=True,
            description="Test flag for integration testing"
        )
        
    # Verify we can get the flag value
    assert registry.get_value(test_flag_name) is True
