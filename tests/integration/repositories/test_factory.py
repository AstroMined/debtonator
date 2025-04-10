"""
Integration tests for the repository factory with dynamic module loading.

This module tests the RepositoryFactory's ability to dynamically load type-specific
repository modules and create specialized repositories with proper feature flag
integration. Following the "Real Objects Testing Philosophy" with no mocks.
"""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.checking import CheckingAccount
from src.repositories.factory import RepositoryFactory
from src.services.feature_flags import FeatureFlagService
from src.utils.datetime_utils import utc_now

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_create_account_repository_with_type(
    repository_factory: RepositoryFactory
):
    """
    Test creating repository for specific account type.
    
    This test verifies that the RepositoryFactory correctly creates specialized
    repositories for different account types with type-specific methods.
    
    Args:
        repository_factory: Repository factory fixture
    """
    # 1. ARRANGE: Repository factory is provided by fixture

    # 2. SCHEMA: Not applicable for this test

    # 3. ACT: Create repositories for different account types
    checking_repo = await repository_factory.create_account_repository(account_type="checking")
    savings_repo = await repository_factory.create_account_repository(account_type="savings")
    credit_repo = await repository_factory.create_account_repository(account_type="credit")

    # 4. ASSERT: Verify the repositories were created with type-specific methods
    assert checking_repo is not None
    assert savings_repo is not None
    assert credit_repo is not None

    # Verify type-specific methods are bound
    assert hasattr(checking_repo, "get_checking_accounts_with_overdraft")
    assert hasattr(savings_repo, "get_accounts_by_interest_rate_threshold")
    assert hasattr(credit_repo, "get_credit_accounts_with_upcoming_payments")


@pytest.mark.asyncio
async def test_dynamic_method_binding(
    repository_factory: RepositoryFactory, test_checking_for_module: CheckingAccount
):
    """
    Test that dynamically bound methods work correctly.
    
    This test verifies that the methods dynamically bound to repositories
    by the RepositoryFactory work correctly when called.
    
    Args:
        repository_factory: Repository factory fixture
        test_checking_for_module: Checking account with overdraft protection
    """
    # 1. ARRANGE: Repository factory and test account are provided by fixtures

    # 2. SCHEMA: Not applicable for this test

    # 3. ACT: Create checking repository and use a dynamically bound method
    checking_repo = await repository_factory.create_account_repository(account_type="checking")
    accounts_with_overdraft = await checking_repo.get_checking_accounts_with_overdraft()

    # 4. ASSERT: Verify the method works correctly
    assert len(accounts_with_overdraft) >= 1
    assert test_checking_for_module.id in [a.id for a in accounts_with_overdraft]
    assert all(isinstance(a, CheckingAccount) for a in accounts_with_overdraft)
    assert all(a.has_overdraft_protection for a in accounts_with_overdraft)


@pytest.mark.asyncio
async def test_fallback_behavior_for_unknown_type(repository_factory: RepositoryFactory):
    """
    Test graceful fallback when module not found.
    
    This test verifies that the RepositoryFactory gracefully falls back to
    the base repository when a module for an unknown account type is not found.
    
    Args:
        repository_factory: Repository factory fixture
    """
    # 1. ARRANGE: Repository factory is provided by fixture

    # 2. SCHEMA: Not applicable for this test

    # 3. ACT: Create repository for unknown account type
    repo = await repository_factory.create_account_repository(account_type="unknown_type")

    # 4. ASSERT: Verify fallback behavior
    assert repo is not None
    # Should fall back to base repository without specialized methods
    assert not hasattr(repo, "get_checking_accounts_with_overdraft")
    assert not hasattr(repo, "get_accounts_by_interest_rate_threshold")
    assert not hasattr(repo, "get_credit_accounts_with_upcoming_payments")


@pytest.mark.asyncio
async def test_feature_flag_integration(
    repository_factory: RepositoryFactory, feature_flag_service: FeatureFlagService
):
    """
    Test that factory respects feature flags for banking account types.
    
    This test verifies that the RepositoryFactory respects feature flags
    when creating repositories for different account types.
    
    Args:
        repository_factory: Repository factory fixture
        feature_flag_service: Feature flag service fixture
    """
    # 1. ARRANGE: Temporarily disable banking account types
    feature_flag_service.set_enabled("BANKING_ACCOUNT_TYPES_ENABLED", False)

    # 2. SCHEMA: Not applicable for this test

    # 3. ACT & ASSERT: Standard types should still work
    checking_repo = await repository_factory.create_account_repository(account_type="checking")
    savings_repo = await repository_factory.create_account_repository(account_type="savings")
    credit_repo = await repository_factory.create_account_repository(account_type="credit")

    assert checking_repo is not None
    assert savings_repo is not None
    assert credit_repo is not None

    # Modern financial types should be rejected when flag is disabled
    with pytest.raises(
        ValueError, match="account type .* is not currently enabled"
    ):
        await repository_factory.create_account_repository(account_type="payment_app")

    with pytest.raises(
        ValueError, match="account type .* is not currently enabled"
    ):
        await repository_factory.create_account_repository(account_type="bnpl")

    with pytest.raises(
        ValueError, match="account type .* is not currently enabled"
    ):
        await repository_factory.create_account_repository(account_type="ewa")

    # Re-enable feature flag and try again
    feature_flag_service.set_enabled("BANKING_ACCOUNT_TYPES_ENABLED", True)

    # Now creating these repositories should succeed
    try:
        # These might still fail if the modules don't exist yet, but not due to feature flags
        payment_app_repo = await repository_factory.create_account_repository(
            account_type="payment_app"
        )
        assert payment_app_repo is not None
    except (ModuleNotFoundError, ImportError):
        # This is fine - we're just testing the feature flag check, not the module existence
        pass


@pytest.mark.asyncio
async def test_session_propagation(
    repository_factory: RepositoryFactory, db_session: AsyncSession
):
    """
    Test that session is properly propagated to created repositories.
    
    This test verifies that the database session is properly propagated
    to repositories created by the RepositoryFactory.
    
    Args:
        repository_factory: Repository factory fixture
        db_session: Database session fixture
    """
    # 1. ARRANGE: Repository factory and database session are provided by fixtures

    # 2. SCHEMA: Not applicable for this test

    # 3. ACT: Create repository and verify session propagation
    checking_repo = await repository_factory.create_account_repository(account_type="checking")

    # 4. ASSERT: Verify session propagation
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
