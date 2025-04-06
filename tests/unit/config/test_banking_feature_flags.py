"""
Unit tests for banking feature flags configuration.

Tests the banking feature flags registration and validation functions.
"""

import pytest
from unittest.mock import MagicMock, patch

from src.config.banking_feature_flags import (
    register_banking_feature_flags,
    initialize_banking_feature_flags,
    is_account_type_enabled,
)
from src.services.feature_flags import FeatureFlagService
from src.registry.feature_flags_registry import FeatureFlagRegistry


class TestBankingFeatureFlagsRegistration:
    """Tests for banking feature flags registration."""

    def test_register_banking_feature_flags(self):
        """Test registering all banking feature flags."""
        # Setup mock service
        mock_service = MagicMock(spec=FeatureFlagService)
        
        # Call the register function
        register_banking_feature_flags(mock_service)
        
        # Verify all expected flags were registered
        expected_flags = [
            "BANKING_ACCOUNT_TYPES_ENABLED",
            "CHECKING_ACCOUNTS_ENABLED",
            "SAVINGS_ACCOUNTS_ENABLED",
            "CREDIT_ACCOUNTS_ENABLED",
            "PAYMENT_APP_ACCOUNTS_ENABLED",
            "BNPL_ACCOUNTS_ENABLED",
            "EWA_ACCOUNTS_ENABLED",
            "MULTI_CURRENCY_SUPPORT_ENABLED",
            "INTERNATIONAL_ACCOUNT_SUPPORT_ENABLED",
        ]
        
        # Count calls and check each expected flag was registered
        assert mock_service.register_flag.call_count == len(expected_flags)
        for flag_name in expected_flags:
            mock_service.register_flag.assert_any_call(
                name=flag_name,
                default_value=mock_service.register_flag.call_args_list[
                    expected_flags.index(flag_name)
                ].kwargs["default_value"],
                description=mock_service.register_flag.call_args_list[
                    expected_flags.index(flag_name)
                ].kwargs["description"],
                category=mock_service.register_flag.call_args_list[
                    expected_flags.index(flag_name)
                ].kwargs["category"],
                **{k: v for k, v in mock_service.register_flag.call_args_list[
                    expected_flags.index(flag_name)
                ].kwargs.items() if k not in ("name", "default_value", "description", "category")}
            )

    @patch("src.config.banking_feature_flags.register_banking_feature_flags")
    def test_initialize_with_app(self, mock_register):
        """Test initializing feature flags with app."""
        # Setup mock app
        mock_app = MagicMock()
        mock_app.state.feature_flag_service = MagicMock(spec=FeatureFlagService)
        
        # Call initialize function
        initialize_banking_feature_flags(mock_app)
        
        # Verify it used the app's feature flag service
        mock_register.assert_called_once_with(mock_app.state.feature_flag_service)

    @patch("src.config.banking_feature_flags.FeatureFlagRegistry")
    @patch("src.config.banking_feature_flags.FeatureFlagRepository")
    @patch("src.config.banking_feature_flags.get_db_session")
    @patch("src.config.banking_feature_flags.register_banking_feature_flags")
    def test_initialize_without_app(
        self, mock_register, mock_get_db, mock_repo_class, mock_registry_class
    ):
        """Test initializing feature flags without app (standalone mode)."""
        # Setup mocks
        mock_registry = MagicMock()
        mock_registry_class.return_value = mock_registry
        
        mock_db = MagicMock()
        mock_get_db.return_value = iter([mock_db])
        
        mock_repo = MagicMock()
        mock_repo_class.return_value = mock_repo
        
        # Call initialize function
        initialize_banking_feature_flags()
        
        # Verify correct setup
        mock_registry_class.assert_called_once()
        mock_get_db.assert_called_once()
        mock_repo_class.assert_called_once_with(mock_db)
        mock_register.assert_called_once()


class TestAccountTypeFeatureFlags:
    """Tests for account type feature flag validation."""
    
    def test_is_account_type_enabled_with_master_disabled(self):
        """Test that all account types are disabled when master switch is off."""
        # Setup mock service with master switch disabled
        mock_service = MagicMock(spec=FeatureFlagService)
        mock_service.is_enabled.return_value = False
        
        # Test all account types
        account_types = ["checking", "savings", "credit", "payment_app", "bnpl", "ewa"]
        for account_type in account_types:
            assert is_account_type_enabled(account_type, mock_service) is False
            
        # Verify master switch was checked each time
        assert mock_service.is_enabled.call_count == len(account_types)
        mock_service.is_enabled.assert_called_with("BANKING_ACCOUNT_TYPES_ENABLED")
    
    def test_is_account_type_enabled_with_specific_flags(self):
        """Test that each account type respects its specific flag."""
        # Setup mock service with master switch enabled
        mock_service = MagicMock(spec=FeatureFlagService)
        
        # Configure mock to return True for master switch and custom values for specific types
        def is_enabled_side_effect(flag_name):
            if flag_name == "BANKING_ACCOUNT_TYPES_ENABLED":
                return True
            elif flag_name == "CHECKING_ACCOUNTS_ENABLED":
                return True
            elif flag_name == "SAVINGS_ACCOUNTS_ENABLED":
                return False
            elif flag_name == "CREDIT_ACCOUNTS_ENABLED":
                return True
            elif flag_name == "PAYMENT_APP_ACCOUNTS_ENABLED":
                return False
            elif flag_name == "BNPL_ACCOUNTS_ENABLED":
                return True
            elif flag_name == "EWA_ACCOUNTS_ENABLED":
                return False
            return False
            
        mock_service.is_enabled.side_effect = is_enabled_side_effect
        
        # Test each account type
        assert is_account_type_enabled("checking", mock_service) is True
        assert is_account_type_enabled("savings", mock_service) is False
        assert is_account_type_enabled("credit", mock_service) is True
        assert is_account_type_enabled("payment_app", mock_service) is False
        assert is_account_type_enabled("bnpl", mock_service) is True
        assert is_account_type_enabled("ewa", mock_service) is False
        
    def test_is_account_type_enabled_with_unknown_type(self):
        """Test that unknown account types are disabled by default."""
        # Setup mock service with master switch enabled
        mock_service = MagicMock(spec=FeatureFlagService)
        mock_service.is_enabled.return_value = True
        
        # Test an unknown account type
        assert is_account_type_enabled("invalid_type", mock_service) is False
        
        # Verify only the master switch was checked
        mock_service.is_enabled.assert_called_once_with("BANKING_ACCOUNT_TYPES_ENABLED")
