"""
Integration tests for the repository factory with dynamic module loading.

This module tests the RepositoryFactory's ability to dynamically load type-specific
repository modules and create specialized repositories with proper feature flag
integration. Following the "Real Objects Testing Philosophy" with no mocks.
"""

import pytest
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.checking import CheckingAccount
from src.models.account_types.banking.savings import SavingsAccount
from src.models.account_types.banking.credit import CreditAccount
from src.repositories.factory import RepositoryFactory
from src.services.feature_flags import FeatureFlagService
from src.utils.datetime_utils import utc_now

pytestmark = pytest.mark.asyncio


class TestRepositoryFactory:
    """Test repository factory with dynamic module loading."""
    
    @pytest.fixture
    async def factory(self, db_session: AsyncSession, feature_flag_service: FeatureFlagService) -> RepositoryFactory:
        """Create a repository factory for testing."""
        return RepositoryFactory(db_session, feature_flag_service)
    
    @pytest.fixture
    async def test_checking_for_module(self, db_session: AsyncSession) -> CheckingAccount:
        """Create a checking account for testing module-specific methods."""
        account = CheckingAccount(
            name="Module Test Checking",
            current_balance=Decimal("1000.00"),
            available_balance=Decimal("1000.00"),
            has_overdraft_protection=True,
            overdraft_limit=Decimal("500.00"),
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        db_session.add(account)
        await db_session.flush()
        await db_session.refresh(account)
        return account
    
    async def test_create_account_repository_with_type(
        self, factory: RepositoryFactory
    ):
        """Test creating repository for specific account type."""
        # ACT
        checking_repo = await factory.create_account_repository(account_type="checking")
        savings_repo = await factory.create_account_repository(account_type="savings")
        credit_repo = await factory.create_account_repository(account_type="credit")
        
        # ASSERT
        assert checking_repo is not None
        assert savings_repo is not None
        assert credit_repo is not None
        
        # Verify type-specific methods are bound
        assert hasattr(checking_repo, "get_checking_accounts_with_overdraft")
        assert hasattr(savings_repo, "get_accounts_by_interest_rate_threshold")
        assert hasattr(credit_repo, "get_credit_accounts_with_upcoming_payments")
    
    async def test_dynamic_method_binding(
        self, factory: RepositoryFactory, test_checking_for_module: CheckingAccount
    ):
        """Test that dynamically bound methods work correctly."""
        # ACT
        checking_repo = await factory.create_account_repository(account_type="checking")
        
        # Use a dynamically bound method
        accounts_with_overdraft = await checking_repo.get_checking_accounts_with_overdraft()
        
        # ASSERT
        assert len(accounts_with_overdraft) >= 1
        assert test_checking_for_module.id in [a.id for a in accounts_with_overdraft]
        assert all(isinstance(a, CheckingAccount) for a in accounts_with_overdraft)
        assert all(a.has_overdraft_protection for a in accounts_with_overdraft)
    
    async def test_fallback_behavior_for_unknown_type(
        self, factory: RepositoryFactory
    ):
        """Test graceful fallback when module not found."""
        # ACT
        repo = await factory.create_account_repository(account_type="unknown_type")
        
        # ASSERT
        assert repo is not None
        # Should fall back to base repository without specialized methods
        assert not hasattr(repo, "get_checking_accounts_with_overdraft")
        assert not hasattr(repo, "get_accounts_by_interest_rate_threshold")
        assert not hasattr(repo, "get_credit_accounts_with_upcoming_payments")
    
    async def test_feature_flag_integration(
        self, factory: RepositoryFactory, feature_flag_service: FeatureFlagService
    ):
        """Test that factory respects feature flags for banking account types."""
        # ARRANGE
        # Temporarily disable banking account types
        feature_flag_service.set_enabled("BANKING_ACCOUNT_TYPES_ENABLED", False)
        
        # ACT & ASSERT - Standard types should still work
        checking_repo = await factory.create_account_repository(account_type="checking")
        savings_repo = await factory.create_account_repository(account_type="savings")
        credit_repo = await factory.create_account_repository(account_type="credit")
        
        assert checking_repo is not None
        assert savings_repo is not None
        assert credit_repo is not None
        
        # ACT & ASSERT - Modern financial types should be rejected when flag is disabled
        with pytest.raises(ValueError, match="account type .* is not currently enabled"):
            await factory.create_account_repository(account_type="payment_app")
        
        with pytest.raises(ValueError, match="account type .* is not currently enabled"):
            await factory.create_account_repository(account_type="bnpl")
        
        with pytest.raises(ValueError, match="account type .* is not currently enabled"):
            await factory.create_account_repository(account_type="ewa")
        
        # Re-enable feature flag and try again
        feature_flag_service.set_enabled("BANKING_ACCOUNT_TYPES_ENABLED", True)
        
        # Now creating these repositories should succeed
        try:
            # These might still fail if the modules don't exist yet, but not due to feature flags
            payment_app_repo = await factory.create_account_repository(account_type="payment_app")
            assert payment_app_repo is not None
        except (ModuleNotFoundError, ImportError):
            # This is fine - we're just testing the feature flag check, not the module existence
            pass
    
    async def test_session_propagation(
        self, factory: RepositoryFactory, db_session: AsyncSession
    ):
        """Test that session is properly propagated to created repositories."""
        # ACT
        checking_repo = await factory.create_account_repository(account_type="checking")
        
        # ASSERT
        assert checking_repo.session is db_session
        
        # Test that operations using the session work
        account = CheckingAccount(
            name="Session Test",
            current_balance=Decimal("1500.00"),
            available_balance=Decimal("1500.00"),
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        
        db_session.add(account)
        await db_session.flush()
        
        # Use the repository to fetch the account
        fetched = await checking_repo.get(account.id)
        assert fetched is not None
        assert fetched.id == account.id
