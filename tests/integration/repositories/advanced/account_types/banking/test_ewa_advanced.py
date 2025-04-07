# pylint: disable=no-member,no-value-for-argument
"""
Integration tests for EWA account repository advanced operations.

Tests specialized methods from the ewa repository module.
"""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.ewa import EWAAccount
from src.repositories.accounts import AccountRepository
from src.repositories.factory import RepositoryFactory
from src.repositories.account_types.banking.ewa import (
    get_ewa_accounts_approaching_payday,
    get_ewa_accounts_by_provider,
    get_ewa_accounts_by_advance_percentage,
    get_ewa_accounts_with_no_transaction_fee
)
from src.services.feature_flags import FeatureFlagService
from tests.helpers.schema_factories.account_types.banking.ewa import create_ewa_account_schema

pytestmark = pytest.mark.asyncio


class TestEWAAccountAdvanced:
    """Test advanced operations for EWA accounts."""
    
    @pytest.fixture
    async def repository(self, db_session: AsyncSession, feature_flag_service: FeatureFlagService) -> AccountRepository:
        """Create a repository for testing."""
        return RepositoryFactory.create_account_repository(
            session=db_session, 
            account_type="ewa",
            feature_flag_service=feature_flag_service
        )
    
    async def test_get_ewa_accounts_approaching_payday(
        self, 
        db_session: AsyncSession,
        test_ewa_account: EWAAccount,  # Payday in 7 days
        test_ewa_account_approaching_payday: EWAAccount  # Payday in 2 days
    ):
        """Test getting EWA accounts with approaching paydays."""
        # 1. ARRANGE: Accounts are set up via fixtures
        
        # 2. ACT: Call the specialized repository method with 3-day window
        accounts_with_approaching_payday = await get_ewa_accounts_approaching_payday(db_session, 3)
        
        # 3. ASSERT: Verify the results
        assert len(accounts_with_approaching_payday) >= 1
        
        # Check if the account with an imminent payday is included
        account_ids = [account.id for account in accounts_with_approaching_payday]
        assert test_ewa_account_approaching_payday.id in account_ids
        
        # Check if the account with a later payday is excluded when window is 3 days
        assert test_ewa_account.id not in account_ids
        
        # Now check with a larger window (10 days) - should include both accounts
        accounts_with_paydays_10_days = await get_ewa_accounts_approaching_payday(db_session, 10)
        account_ids_10_days = [account.id for account in accounts_with_paydays_10_days]
        assert test_ewa_account.id in account_ids_10_days
        assert test_ewa_account_approaching_payday.id in account_ids_10_days
    
    async def test_get_ewa_accounts_by_provider(
        self, 
        db_session: AsyncSession,
        test_ewa_account: EWAAccount,  # PayActiv
        test_ewa_account_approaching_payday: EWAAccount,  # DailyPay
        test_ewa_account_no_transaction_fee: EWAAccount  # Employer Direct
    ):
        """Test getting EWA accounts by provider."""
        # 1. ARRANGE: Accounts are set up via fixtures
        
        # 2. ACT: Call the specialized repository method for each provider
        payactiv_accounts = await get_ewa_accounts_by_provider(db_session, "PayActiv")
        dailypay_accounts = await get_ewa_accounts_by_provider(db_session, "DailyPay")
        employer_direct_accounts = await get_ewa_accounts_by_provider(db_session, "Employer Direct")
        
        # 3. ASSERT: Verify the results
        assert len(payactiv_accounts) >= 1
        assert all(account.provider == "PayActiv" for account in payactiv_accounts)
        assert test_ewa_account.id in [account.id for account in payactiv_accounts]
        
        assert len(dailypay_accounts) >= 1
        assert all(account.provider == "DailyPay" for account in dailypay_accounts)
        assert test_ewa_account_approaching_payday.id in [account.id for account in dailypay_accounts]
        
        assert len(employer_direct_accounts) >= 1
        assert all(account.provider == "Employer Direct" for account in employer_direct_accounts)
        assert test_ewa_account_no_transaction_fee.id in [account.id for account in employer_direct_accounts]
    
    async def test_get_ewa_accounts_by_advance_percentage(
        self, 
        db_session: AsyncSession,
        test_ewa_account: EWAAccount,  # 50%
        test_ewa_account_approaching_payday: EWAAccount,  # 50%
        test_ewa_account_no_transaction_fee: EWAAccount  # 75%
    ):
        """Test getting EWA accounts with a specific advance percentage range."""
        # 1. ARRANGE: Create an additional account with a 25% max advance
        low_percentage_schema = create_ewa_account_schema(
            name="Limited Advance EWA",
            provider="Even",
            max_advance_percentage=Decimal("25.00")
        )
        low_percentage_account = EWAAccount(**low_percentage_schema.model_dump())
        db_session.add(low_percentage_account)
        await db_session.flush()
        
        # 2. ACT: Call the specialized repository method with different ranges
        # Range: 20-30%
        low_range_accounts = await get_ewa_accounts_by_advance_percentage(
            db_session, Decimal("20.00"), Decimal("30.00")
        )
        
        # Range: 45-55%
        mid_range_accounts = await get_ewa_accounts_by_advance_percentage(
            db_session, Decimal("45.00"), Decimal("55.00")
        )
        
        # Range: 70-80%
        high_range_accounts = await get_ewa_accounts_by_advance_percentage(
            db_session, Decimal("70.00"), Decimal("80.00")
        )
        
        # 3. ASSERT: Verify the results
        # Low range should include the 25% account
        assert len(low_range_accounts) >= 1
        low_range_ids = [account.id for account in low_range_accounts]
        assert low_percentage_account.id in low_range_ids
        
        # Mid range should include the 50% accounts
        assert len(mid_range_accounts) >= 2
        mid_range_ids = [account.id for account in mid_range_accounts]
        assert test_ewa_account.id in mid_range_ids
        assert test_ewa_account_approaching_payday.id in mid_range_ids
        
        # High range should include the 75% account
        assert len(high_range_accounts) >= 1
        high_range_ids = [account.id for account in high_range_accounts]
        assert test_ewa_account_no_transaction_fee.id in high_range_ids
    
    async def test_get_ewa_accounts_with_no_transaction_fee(
        self, 
        db_session: AsyncSession,
        test_ewa_account: EWAAccount,  # Has $5.00 fee
        test_ewa_account_approaching_payday: EWAAccount,  # Has $2.99 fee
        test_ewa_account_no_transaction_fee: EWAAccount  # Has $0.00 fee
    ):
        """Test getting EWA accounts with no transaction fee."""
        # 1. ARRANGE: Accounts are set up via fixtures
        
        # 2. ACT: Call the specialized repository method
        no_fee_accounts = await get_ewa_accounts_with_no_transaction_fee(db_session)
        
        # 3. ASSERT: Verify the results
        assert len(no_fee_accounts) >= 1
        no_fee_ids = [account.id for account in no_fee_accounts]
        
        # Check that only the no-fee account is included
        assert test_ewa_account_no_transaction_fee.id in no_fee_ids
        
        # Check that fee-charging accounts are excluded
        assert test_ewa_account.id not in no_fee_ids
        assert test_ewa_account_approaching_payday.id not in no_fee_ids
    
    async def test_repository_has_specialized_methods(self, repository: AccountRepository):
        """Test that the repository has the specialized EWA methods."""
        # 1. ARRANGE: Repository is provided by fixture
        
        # 2. ACT & ASSERT: Verify the repository has specialized EWA methods
        assert hasattr(repository, "get_ewa_accounts_approaching_payday")
        assert callable(getattr(repository, "get_ewa_accounts_approaching_payday"))
        
        assert hasattr(repository, "get_ewa_accounts_by_provider")
        assert callable(getattr(repository, "get_ewa_accounts_by_provider"))
        
        assert hasattr(repository, "get_ewa_accounts_by_advance_percentage")
        assert callable(getattr(repository, "get_ewa_accounts_by_advance_percentage"))
        
        assert hasattr(repository, "get_ewa_accounts_with_no_transaction_fee")
        assert callable(getattr(repository, "get_ewa_accounts_with_no_transaction_fee"))
