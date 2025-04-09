# pylint: disable=no-member,no-value-for-argument
"""
Integration tests for PaymentApp account repository advanced operations.

Tests specialized methods from the payment_app repository module.
"""


import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.payment_app import PaymentAppAccount
from src.repositories.account_types.banking.payment_app import (
    get_payment_app_accounts_by_platform,
    get_payment_app_accounts_with_debit_cards,
    get_payment_app_accounts_with_direct_deposit,
    get_payment_app_accounts_with_linked_accounts,
)
from src.repositories.accounts import AccountRepository
from src.repositories.factory import RepositoryFactory
from src.services.feature_flags import FeatureFlagService
from tests.helpers.schema_factories.account_types.banking.payment_app_schema_factories import (
    create_payment_app_account_schema,
)

pytestmark = pytest.mark.asyncio


class TestPaymentAppAccountAdvanced:
    """Test advanced operations for payment app accounts."""

    @pytest.fixture
    async def repository(
        self, db_session: AsyncSession, feature_flag_service: FeatureFlagService
    ) -> AccountRepository:
        """Create a repository for testing."""
        return RepositoryFactory.create_account_repository(
            session=db_session,
            account_type="payment_app",
            feature_flag_service=feature_flag_service,
        )

    async def test_get_payment_app_accounts_by_platform(
        self,
        db_session: AsyncSession,
        test_payment_app_account: PaymentAppAccount,  # PayPal
    ):
        """Test getting payment app accounts by platform."""
        # 1. ARRANGE: Create additional accounts with different platforms
        # First account comes from fixture (PayPal platform)

        # Create Venmo account
        venmo_schema = create_payment_app_account_schema(
            name="Test Venmo Account", platform="Venmo"
        )
        venmo_account = PaymentAppAccount(**venmo_schema.model_dump())
        db_session.add(venmo_account)

        # Create another PayPal account
        paypal_schema = create_payment_app_account_schema(
            name="Another PayPal Account", platform="PayPal"
        )
        paypal_account = PaymentAppAccount(**paypal_schema.model_dump())
        db_session.add(paypal_account)

        await db_session.flush()

        # 2. ACT: Call the specialized repository method
        paypal_accounts = await get_payment_app_accounts_by_platform(
            db_session, "PayPal"
        )
        venmo_accounts = await get_payment_app_accounts_by_platform(db_session, "Venmo")

        # 3. ASSERT: Verify the results
        assert len(paypal_accounts) == 2
        assert all(account.platform == "PayPal" for account in paypal_accounts)

        assert len(venmo_accounts) == 1
        assert venmo_accounts[0].platform == "Venmo"

    async def test_get_payment_app_accounts_with_debit_cards(
        self,
        db_session: AsyncSession,
        test_payment_app_account: PaymentAppAccount,  # Has debit card
        test_payment_app_account_with_linked_accounts: PaymentAppAccount,  # No debit card
    ):
        """Test getting payment app accounts with debit cards."""
        # 1. ARRANGE: Accounts are set up via fixtures

        # 2. ACT: Call the specialized repository method
        accounts_with_debit_cards = await get_payment_app_accounts_with_debit_cards(
            db_session
        )

        # 3. ASSERT: Verify the results
        assert len(accounts_with_debit_cards) >= 1
        assert all(account.has_debit_card for account in accounts_with_debit_cards)

        # Verify that the test_payment_app_account is included (has debit card)
        account_ids = [account.id for account in accounts_with_debit_cards]
        assert test_payment_app_account.id in account_ids

        # Verify that the test_payment_app_account_with_linked_accounts is not included (no debit card)
        assert test_payment_app_account_with_linked_accounts.id not in account_ids

    async def test_get_payment_app_accounts_with_linked_accounts(
        self,
        db_session: AsyncSession,
        test_payment_app_account: PaymentAppAccount,  # No linked accounts
        test_payment_app_account_with_linked_accounts: PaymentAppAccount,  # Has linked accounts
    ):
        """Test getting payment app accounts with linked accounts."""
        # 1. ARRANGE: Accounts are set up via fixtures

        # 2. ACT: Call the specialized repository method
        accounts_with_linked = await get_payment_app_accounts_with_linked_accounts(
            db_session
        )

        # 3. ASSERT: Verify the results
        assert len(accounts_with_linked) >= 1
        assert all(account.linked_account_ids for account in accounts_with_linked)

        # Verify that the test_payment_app_account_with_linked_accounts is included
        account_ids = [account.id for account in accounts_with_linked]
        assert test_payment_app_account_with_linked_accounts.id in account_ids

        # Verify that the test_payment_app_account is not included (no linked accounts)
        assert test_payment_app_account.id not in account_ids

    async def test_get_payment_app_accounts_with_direct_deposit(
        self,
        db_session: AsyncSession,
        test_payment_app_account: PaymentAppAccount,  # No direct deposit
        test_payment_app_account_with_linked_accounts: PaymentAppAccount,  # Has direct deposit
    ):
        """Test getting payment app accounts with direct deposit enabled."""
        # 1. ARRANGE: Accounts are set up via fixtures

        # 2. ACT: Call the specialized repository method
        accounts_with_direct_deposit = (
            await get_payment_app_accounts_with_direct_deposit(db_session)
        )

        # 3. ASSERT: Verify the results
        assert len(accounts_with_direct_deposit) >= 1
        assert all(
            account.supports_direct_deposit for account in accounts_with_direct_deposit
        )

        # Verify that the test_payment_app_account_with_linked_accounts is included
        account_ids = [account.id for account in accounts_with_direct_deposit]
        assert test_payment_app_account_with_linked_accounts.id in account_ids

        # Verify that the test_payment_app_account is not included (no direct deposit)
        assert test_payment_app_account.id not in account_ids

    async def test_repository_has_specialized_methods(
        self, repository: AccountRepository
    ):
        """Test that the repository has the specialized payment app methods."""
        # 1. ARRANGE: Repository is provided by fixture

        # 2. ACT & ASSERT: Verify the repository has specialized payment app methods
        assert hasattr(repository, "get_payment_app_accounts_by_platform")
        assert callable(getattr(repository, "get_payment_app_accounts_by_platform"))

        assert hasattr(repository, "get_payment_app_accounts_with_debit_cards")
        assert callable(
            getattr(repository, "get_payment_app_accounts_with_debit_cards")
        )

        assert hasattr(repository, "get_payment_app_accounts_with_linked_accounts")
        assert callable(
            getattr(repository, "get_payment_app_accounts_with_linked_accounts")
        )

        assert hasattr(repository, "get_payment_app_accounts_with_direct_deposit")
        assert callable(
            getattr(repository, "get_payment_app_accounts_with_direct_deposit")
        )
