"""
Integration tests for Account Service with Feature Flag integration.

These tests verify that the AccountService properly integrates with the feature flag
system to control the availability of different account types and features. This is a
critical component of ADR-024 Feature Flags implementation.
"""

import pytest
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.feature_flags import FeatureFlag
from src.models.account_types.banking import CheckingAccount, BNPLAccount
from src.registry.account_types import account_type_registry
from src.registry.feature_flags import feature_flag_registry
from src.repositories.feature_flags import FeatureFlagRepository
from src.services.accounts import AccountService
from src.services.factory import ServiceFactory
from src.services.feature_flags import FeatureFlagService
from src.utils.feature_flags.context import EnvironmentContext


@pytest.fixture
async def feature_flag_repo(async_session: AsyncSession) -> FeatureFlagRepository:
    """Create a feature flag repository for testing."""
    return FeatureFlagRepository(async_session)


@pytest.fixture
async def feature_flag_service(
    async_session: AsyncSession, feature_flag_repo: FeatureFlagRepository
) -> FeatureFlagService:
    """Create a feature flag service for testing."""
    context = EnvironmentContext()
    service = FeatureFlagService(
        registry=feature_flag_registry,
        repository=feature_flag_repo,
        context=context
    )
    await service.initialize()
    return service


@pytest.fixture
async def banking_feature_flag(async_session: AsyncSession) -> FeatureFlag:
    """Create the banking account types feature flag."""
    flag = FeatureFlag(
        name="BANKING_ACCOUNT_TYPES_ENABLED",
        description="Enables banking account types",
        flag_type="boolean",
        value=True,  # Enabled by default
        is_system=True
    )
    async_session.add(flag)
    await async_session.commit()
    await async_session.refresh(flag)
    return flag


@pytest.fixture
async def account_service(
    async_session: AsyncSession, 
    feature_flag_service: FeatureFlagService,
    banking_feature_flag: FeatureFlag
) -> AccountService:
    """Create an account service with feature flag integration."""
    return ServiceFactory.create_account_service(
        session=async_session,
        feature_flag_service=feature_flag_service
    )


@pytest.mark.asyncio
async def test_account_service_get_available_account_types(
    async_session: AsyncSession, 
    account_service: AccountService,
    feature_flag_service: FeatureFlagService
):
    """Test that the account service returns available account types based on feature flags."""
    # Act - with banking feature enabled
    available_types = account_service.get_available_account_types()
    
    # Assert
    assert any(t["id"] == "checking" for t in available_types)
    assert any(t["id"] == "bnpl" for t in available_types)
    
    # Disable the banking account types feature
    await feature_flag_service.set_enabled("BANKING_ACCOUNT_TYPES_ENABLED", False)
    
    # Act - with banking feature disabled
    available_types = account_service.get_available_account_types()
    
    # Assert - only basic types are available
    checking_type = next((t for t in available_types if t["id"] == "checking"), None)
    bnpl_type = next((t for t in available_types if t["id"] == "bnpl"), None)
    
    # Checking accounts are considered basic and should still be available
    assert checking_type is not None
    
    # BNPL is a modern financial type and should be hidden when the feature flag is off
    assert bnpl_type is None


@pytest.mark.asyncio
async def test_account_create_with_feature_flag(
    async_session: AsyncSession, 
    account_service: AccountService,
    feature_flag_service: FeatureFlagService
):
    """Test account creation with feature flags controlling available types."""
    # Arrange - checking data
    checking_data = {
        "name": "Test Checking",
        "account_type": "checking",
        "current_balance": Decimal("1000.00"),
        "available_balance": Decimal("1000.00"),
        "routing_number": "123456789"
    }
    
    # Arrange - BNPL data
    bnpl_data = {
        "name": "Test BNPL",
        "account_type": "bnpl",
        "current_balance": Decimal("400.00"),
        "installment_count": 4,
        "installment_amount": Decimal("100.00"),
        "payment_frequency": "monthly"
    }
    
    # Act & Assert - with banking feature enabled
    # Should be able to create both account types
    checking_account = await account_service.create_account(checking_data)
    assert checking_account is not None
    assert checking_account.account_type == "checking"
    
    bnpl_account = await account_service.create_account(bnpl_data)
    assert bnpl_account is not None
    assert bnpl_account.account_type == "bnpl"
    
    # Disable the banking account types feature
    await feature_flag_service.set_enabled("BANKING_ACCOUNT_TYPES_ENABLED", False)
    
    # Act & Assert - with banking feature disabled
    # Should still create checking but fail on BNPL
    checking_account2 = await account_service.create_account(checking_data)
    assert checking_account2 is not None
    assert checking_account2.account_type == "checking"
    
    # BNPL should fail due to disabled feature
    with pytest.raises(ValueError, match="Account type bnpl is not available"):
        await account_service.create_account(bnpl_data)


@pytest.mark.asyncio
async def test_get_banking_overview_feature_flags(
    async_session: AsyncSession, 
    account_service: AccountService
):
    """Test that banking overview includes only enabled account types."""
    # Arrange - create accounts of different types
    checking = CheckingAccount(
        name="Test Checking",
        account_type="checking",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00")
    )
    
    bnpl = BNPLAccount(
        name="Test BNPL",
        account_type="bnpl",
        current_balance=Decimal("400.00"),
        available_balance=Decimal("400.00"),
        installment_count=4,
        installments_paid=0,
        installment_amount=Decimal("100.00")
    )
    
    async_session.add_all([checking, bnpl])
    await async_session.commit()
    
    # Act
    overview = await account_service.get_banking_overview(user_id=1)
    
    # Assert - both account types should contribute to the overview
    assert overview["checking_balance"] == Decimal("1000.00")
    assert overview["bnpl_balance"] == Decimal("400.00")
    assert overview["total_cash"] == Decimal("1000.00")
    assert overview["total_debt"] == Decimal("400.00")
