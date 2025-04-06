# pylint: disable=no-member,no-value-for-argument
"""
Integration tests for BNPL account repository advanced operations.

Tests specialized methods from the bnpl repository module.
"""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.bnpl import BNPLAccount
from src.repositories.accounts import AccountRepository
from src.repositories.factory import RepositoryFactory
from src.repositories.account_types.banking.bnpl import (
    get_bnpl_accounts_with_upcoming_payments,
    get_bnpl_accounts_by_provider,
    get_bnpl_accounts_with_remaining_installments,
    get_bnpl_accounts_by_payment_frequency
)
from src.services.feature_flags import FeatureFlagService
from tests.helpers.schema_factories.account_types.banking.bnpl import create_bnpl_account_schema

pytestmark = pytest.mark.asyncio


class TestBNPLAccountAdvanced:
    """Test advanced operations for BNPL accounts."""
    
    @pytest.fixture
    async def repository(self, db_session: AsyncSession, feature_flag_service: FeatureFlagService) -> AccountRepository:
        """Create a repository for testing."""
        return RepositoryFactory.create_account_repository(
            session=db_session, 
            account_type="bnpl",
            feature_flag_service=feature_flag_service
        )
    
    async def test_get_bnpl_accounts_with_upcoming_payments(
        self, 
        db_session: AsyncSession,
        test_bnpl_account: BNPLAccount,  # Payment in 14 days
        test_bnpl_account_with_upcoming_payment: BNPLAccount  # Payment in 3 days
    ):
        """Test getting BNPL accounts with upcoming payments."""
        # 1. ARRANGE: Accounts are set up via fixtures
        
        # 2. ACT: Call the specialized repository method with 7-day window
        accounts_with_upcoming_payments = await get_bnpl_accounts_with_upcoming_payments(db_session, 7)
        
        # 3. ASSERT: Verify the results
        assert len(accounts_with_upcoming_payments) >= 1
        
        # Check if the account with a soon payment is included
        account_ids = [account.id for account in accounts_with_upcoming_payments]
        assert test_bnpl_account_with_upcoming_payment.id in account_ids
        
        # Check if the account with a later payment is excluded when window is 7 days
        assert test_bnpl_account.id not in account_ids
        
        # Now check with a larger window (20 days) - should include both accounts
        accounts_with_payments_20_days = await get_bnpl_accounts_with_upcoming_payments(db_session, 20)
        account_ids_20_days = [account.id for account in accounts_with_payments_20_days]
        assert test_bnpl_account.id in account_ids_20_days
        assert test_bnpl_account_with_upcoming_payment.id in account_ids_20_days
    
    async def test_get_bnpl_accounts_by_provider(
        self, 
        db_session: AsyncSession,
        test_bnpl_account: BNPLAccount,  # Affirm
        test_bnpl_account_with_upcoming_payment: BNPLAccount,  # Klarna
        test_bnpl_account_nearly_paid: BNPLAccount  # Afterpay
    ):
        """Test getting BNPL accounts by provider."""
        # 1. ARRANGE: Accounts are set up via fixtures
        
        # 2. ACT: Call the specialized repository method for each provider
        affirm_accounts = await get_bnpl_accounts_by_provider(db_session, "Affirm")
        klarna_accounts = await get_bnpl_accounts_by_provider(db_session, "Klarna")
        afterpay_accounts = await get_bnpl_accounts_by_provider(db_session, "Afterpay")
        
        # 3. ASSERT: Verify the results
        assert len(affirm_accounts) >= 1
        assert all(account.bnpl_provider == "Affirm" for account in affirm_accounts)
        assert test_bnpl_account.id in [account.id for account in affirm_accounts]
        
        assert len(klarna_accounts) >= 1
        assert all(account.bnpl_provider == "Klarna" for account in klarna_accounts)
        assert test_bnpl_account_with_upcoming_payment.id in [account.id for account in klarna_accounts]
        
        assert len(afterpay_accounts) >= 1
        assert all(account.bnpl_provider == "Afterpay" for account in afterpay_accounts)
        assert test_bnpl_account_nearly_paid.id in [account.id for account in afterpay_accounts]
    
    async def test_get_bnpl_accounts_with_remaining_installments(
        self, 
        db_session: AsyncSession,
        test_bnpl_account: BNPLAccount,  # 4 installments, 0 paid
        test_bnpl_account_with_upcoming_payment: BNPLAccount,  # 4 installments, 1 paid
        test_bnpl_account_nearly_paid: BNPLAccount  # 4 installments, 3 paid
    ):
        """Test getting BNPL accounts with specified remaining installments."""
        # 1. ARRANGE: Accounts are set up via fixtures
        
        # 2. ACT: Call the specialized repository method with different thresholds
        accounts_3_or_more_remaining = await get_bnpl_accounts_with_remaining_installments(db_session, 3)
        accounts_2_or_more_remaining = await get_bnpl_accounts_with_remaining_installments(db_session, 2)
        accounts_1_or_more_remaining = await get_bnpl_accounts_with_remaining_installments(db_session, 1)
        
        # 3. ASSERT: Verify the results
        # 3+ remaining installments - only the first account (4 - 0 = 4 remaining)
        assert len(accounts_3_or_more_remaining) >= 1
        account_ids_3_plus = [account.id for account in accounts_3_or_more_remaining]
        assert test_bnpl_account.id in account_ids_3_plus
        assert test_bnpl_account_with_upcoming_payment.id not in account_ids_3_plus  # (4 - 1 = 3 remaining)
        assert test_bnpl_account_nearly_paid.id not in account_ids_3_plus  # (4 - 3 = 1 remaining)
        
        # 2+ remaining installments - first two accounts
        assert len(accounts_2_or_more_remaining) >= 2
        account_ids_2_plus = [account.id for account in accounts_2_or_more_remaining]
        assert test_bnpl_account.id in account_ids_2_plus
        assert test_bnpl_account_with_upcoming_payment.id in account_ids_2_plus
        assert test_bnpl_account_nearly_paid.id not in account_ids_2_plus
        
        # 1+ remaining installments - all accounts
        assert len(accounts_1_or_more_remaining) >= 3
        account_ids_1_plus = [account.id for account in accounts_1_or_more_remaining]
        assert test_bnpl_account.id in account_ids_1_plus
        assert test_bnpl_account_with_upcoming_payment.id in account_ids_1_plus
        assert test_bnpl_account_nearly_paid.id in account_ids_1_plus
    
    async def test_get_bnpl_accounts_by_payment_frequency(
        self, 
        db_session: AsyncSession,
        test_bnpl_account: BNPLAccount,  # biweekly
        test_bnpl_account_with_upcoming_payment: BNPLAccount,  # biweekly
        test_bnpl_account_nearly_paid: BNPLAccount  # biweekly
    ):
        """Test getting BNPL accounts by payment frequency."""
        # 1. ARRANGE: Create an additional account with monthly frequency
        monthly_schema = create_bnpl_account_schema(
            name="Monthly Payment BNPL",
            bnpl_provider="SplitIt",
            payment_frequency="monthly"
        )
        monthly_account = BNPLAccount(**monthly_schema.model_dump())
        db_session.add(monthly_account)
        await db_session.flush()
        
        # 2. ACT: Call the specialized repository method for each frequency
        biweekly_accounts = await get_bnpl_accounts_by_payment_frequency(db_session, "biweekly")
        monthly_accounts = await get_bnpl_accounts_by_payment_frequency(db_session, "monthly")
        
        # 3. ASSERT: Verify the results
        assert len(biweekly_accounts) >= 3
        assert all(account.payment_frequency == "biweekly" for account in biweekly_accounts)
        biweekly_ids = [account.id for account in biweekly_accounts]
        assert test_bnpl_account.id in biweekly_ids
        assert test_bnpl_account_with_upcoming_payment.id in biweekly_ids
        assert test_bnpl_account_nearly_paid.id in biweekly_ids
        
        assert len(monthly_accounts) >= 1
        assert all(account.payment_frequency == "monthly" for account in monthly_accounts)
        assert monthly_account.id in [account.id for account in monthly_accounts]
    
    async def test_repository_has_specialized_methods(self, repository: AccountRepository):
        """Test that the repository has the specialized BNPL methods."""
        # 1. ARRANGE: Repository is provided by fixture
        
        # 2. ACT & ASSERT: Verify the repository has specialized BNPL methods
        assert hasattr(repository, "get_bnpl_accounts_with_upcoming_payments")
        assert callable(getattr(repository, "get_bnpl_accounts_with_upcoming_payments"))
        
        assert hasattr(repository, "get_bnpl_accounts_by_provider")
        assert callable(getattr(repository, "get_bnpl_accounts_by_provider"))
        
        assert hasattr(repository, "get_bnpl_accounts_with_remaining_installments")
        assert callable(getattr(repository, "get_bnpl_accounts_with_remaining_installments"))
        
        assert hasattr(repository, "get_bnpl_accounts_by_payment_frequency")
        assert callable(getattr(repository, "get_bnpl_accounts_by_payment_frequency"))
