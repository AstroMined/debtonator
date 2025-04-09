"""
Integration tests for checking account repository operations.

This module tests both the base repository's polymorphic handling of checking accounts
and the specialized operations in the checking account repository module.
Following the "Real Objects Testing Philosophy" with no mocks.
"""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.checking import CheckingAccount
from src.repositories.accounts import AccountRepository
from src.repositories.factory import RepositoryFactory
from src.services.feature_flags import FeatureFlagService
from src.utils.datetime_utils import utc_now

pytestmark = pytest.mark.asyncio


class TestCheckingAccountRepository:
    """Test checking account repository operations with real objects."""

    @pytest.fixture
    async def repository(self, db_session: AsyncSession) -> AccountRepository:
        """Create a base account repository for testing."""
        return AccountRepository(db_session)

    @pytest.fixture
    async def checking_repository(
        self, db_session: AsyncSession, feature_flag_service: FeatureFlagService
    ) -> AccountRepository:
        """Create a checking-specific repository for testing."""
        factory = RepositoryFactory(db_session, feature_flag_service)
        return factory.create_account_repository(account_type="checking")

    async def test_get_with_type_returns_checking_account(
        self, repository: AccountRepository, test_checking_account: CheckingAccount
    ):
        """Test that get_with_type returns a CheckingAccount instance."""
        # ACT
        result = await repository.get_with_type(test_checking_account.id)

        # ASSERT
        assert result is not None
        assert isinstance(result, CheckingAccount)
        assert result.id == test_checking_account.id
        assert result.name == test_checking_account.name
        assert result.account_type == "checking"

        # Verify checking-specific fields are loaded
        assert hasattr(result, "has_overdraft_protection")
        if hasattr(test_checking_account, "routing_number"):
            assert result.routing_number == test_checking_account.routing_number

    async def test_get_by_type_returns_only_checking_accounts(
        self,
        repository: AccountRepository,
        test_checking_account: CheckingAccount,
        test_savings_account,
        test_credit_account,
    ):
        """Test that get_by_type returns only checking accounts."""
        # ACT
        checking_accounts = await repository.get_by_type("checking")

        # ASSERT
        assert len(checking_accounts) >= 1
        assert all(isinstance(a, CheckingAccount) for a in checking_accounts)
        assert all(a.account_type == "checking" for a in checking_accounts)

        # Verify the test account is in the results
        account_ids = [a.id for a in checking_accounts]
        assert test_checking_account.id in account_ids

        # Verify other account types are not in the results
        assert test_savings_account.id not in account_ids
        assert test_credit_account.id not in account_ids

    async def test_create_typed_account_with_checking_type(
        self, repository: AccountRepository, db_session: AsyncSession
    ):
        """Test creating a typed checking account."""
        # ARRANGE
        account_data = {
            "name": "New Checking Account",
            "account_type": "checking",
            "current_balance": Decimal("1000.00"),
            "available_balance": Decimal("1000.00"),
            "has_overdraft_protection": True,
            "overdraft_limit": Decimal("500.00"),
            "created_at": utc_now(),
            "updated_at": utc_now(),
        }

        # ACT
        result = await repository.create_typed_account("checking", account_data)

        # ASSERT
        assert result is not None
        assert isinstance(result, CheckingAccount)
        assert result.id is not None
        assert result.name == "New Checking Account"
        assert result.account_type == "checking"
        assert result.current_balance == Decimal("1000.00")
        assert result.available_balance == Decimal("1000.00")
        assert result.has_overdraft_protection is True
        assert result.overdraft_limit == Decimal("500.00")

        # Verify it was actually persisted
        persisted = await repository.get(result.id)
        assert persisted is not None
        assert persisted.id == result.id

    async def test_update_typed_account_with_checking_type(
        self, repository: AccountRepository, test_checking_account: CheckingAccount
    ):
        """Test updating a typed checking account."""
        # ARRANGE
        update_data = {
            "name": "Updated Checking Account",
            "has_overdraft_protection": True,
            "overdraft_limit": Decimal("250.00"),
            "monthly_fee": Decimal("5.99"),
        }

        # ACT
        result = await repository.update_typed_account(
            test_checking_account.id, "checking", update_data
        )

        # ASSERT
        assert result is not None
        assert isinstance(result, CheckingAccount)
        assert result.id == test_checking_account.id
        assert result.name == "Updated Checking Account"
        assert result.has_overdraft_protection is True
        assert result.overdraft_limit == Decimal("250.00")
        assert result.monthly_fee == Decimal("5.99")

    # Tests for specialized repository module functions

    async def test_get_checking_accounts_with_overdraft(
        self,
        checking_repository: AccountRepository,
        test_checking_account: CheckingAccount,
        db_session: AsyncSession,
    ):
        """Test getting checking accounts with overdraft protection."""
        # ARRANGE
        # Create an account with overdraft protection
        overdraft_account = CheckingAccount(
            name="With Overdraft",
            current_balance=Decimal("1000.00"),
            available_balance=Decimal("1000.00"),
            has_overdraft_protection=True,
            overdraft_limit=Decimal("500.00"),
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        db_session.add(overdraft_account)
        await db_session.flush()

        # Ensure the test_checking_account has overdraft protection disabled
        if test_checking_account.has_overdraft_protection:
            test_checking_account.has_overdraft_protection = False
            await db_session.flush()

        # ACT
        with_overdraft = (
            await checking_repository.get_checking_accounts_with_overdraft()
        )

        # ASSERT
        assert (
            len(with_overdraft) >= 1
        )  # Should at least have the account we just created
        assert all(a.has_overdraft_protection for a in with_overdraft)

        # Verify the overdraft account is in the results
        account_ids = [a.id for a in with_overdraft]
        assert overdraft_account.id in account_ids

        # Verify the test account without overdraft is not in the results
        assert test_checking_account.id not in account_ids

    async def test_get_checking_accounts_by_balance_range(
        self, checking_repository: AccountRepository, db_session: AsyncSession
    ):
        """Test getting checking accounts within a balance range."""
        # ARRANGE
        # Create accounts with different balances
        low_balance = CheckingAccount(
            name="Low Balance",
            current_balance=Decimal("100.00"),
            available_balance=Decimal("100.00"),
            created_at=utc_now(),
            updated_at=utc_now(),
        )

        mid_balance = CheckingAccount(
            name="Mid Balance",
            current_balance=Decimal("500.00"),
            available_balance=Decimal("500.00"),
            created_at=utc_now(),
            updated_at=utc_now(),
        )

        high_balance = CheckingAccount(
            name="High Balance",
            current_balance=Decimal("1500.00"),
            available_balance=Decimal("1500.00"),
            created_at=utc_now(),
            updated_at=utc_now(),
        )

        db_session.add_all([low_balance, mid_balance, high_balance])
        await db_session.flush()

        # ACT
        between_400_and_1000 = (
            await checking_repository.get_checking_accounts_by_balance_range(
                Decimal("400.00"), Decimal("1000.00")
            )
        )

        # ASSERT
        assert len(between_400_and_1000) >= 1  # Should at least have mid_balance

        # Verify correct accounts are in the results
        account_ids = [a.id for a in between_400_and_1000]
        assert mid_balance.id in account_ids
        assert low_balance.id not in account_ids
        assert high_balance.id not in account_ids

        # All accounts should have balances within the range
        assert all(
            Decimal("400.00") <= a.available_balance <= Decimal("1000.00")
            for a in between_400_and_1000
        )

    async def test_get_checking_accounts_with_international_features(
        self,
        checking_repository: AccountRepository,
        test_international_checking: CheckingAccount,
        test_checking_account: CheckingAccount,
    ):
        """Test getting checking accounts with international features."""
        # ACT
        international_accounts = (
            await checking_repository.get_checking_accounts_with_international_features()
        )

        # ASSERT
        assert len(international_accounts) >= 1

        # Verify the international account is in the results
        account_ids = [a.id for a in international_accounts]
        assert test_international_checking.id in account_ids

        # Verify regular checking account is not in the results (assuming it doesn't have international features)
        assert test_checking_account.id not in account_ids

        # All accounts should have at least one international feature
        for account in international_accounts:
            has_international_feature = (
                account.iban is not None
                or account.swift_bic is not None
                or account.sort_code is not None
                or account.branch_code is not None
                or account.account_format != "local"
            )
            assert has_international_feature

    async def test_get_checking_accounts_without_fees(
        self, checking_repository: AccountRepository, db_session: AsyncSession
    ):
        """Test getting checking accounts without monthly fees."""
        # ARRANGE
        # Create accounts with and without fees
        with_fee = CheckingAccount(
            name="With Fee",
            current_balance=Decimal("1000.00"),
            available_balance=Decimal("1000.00"),
            monthly_fee=Decimal("10.00"),
            created_at=utc_now(),
            updated_at=utc_now(),
        )

        no_fee = CheckingAccount(
            name="No Fee",
            current_balance=Decimal("1000.00"),
            available_balance=Decimal("1000.00"),
            monthly_fee=Decimal("0.00"),
            created_at=utc_now(),
            updated_at=utc_now(),
        )

        null_fee = CheckingAccount(
            name="Null Fee",
            current_balance=Decimal("1000.00"),
            available_balance=Decimal("1000.00"),
            monthly_fee=None,
            created_at=utc_now(),
            updated_at=utc_now(),
        )

        db_session.add_all([with_fee, no_fee, null_fee])
        await db_session.flush()

        # ACT
        fee_free_accounts = (
            await checking_repository.get_checking_accounts_without_fees()
        )

        # ASSERT
        assert len(fee_free_accounts) >= 2  # Should have no_fee and null_fee

        # Verify correct accounts are in the results
        account_ids = [a.id for a in fee_free_accounts]
        assert no_fee.id in account_ids
        assert null_fee.id in account_ids
        assert with_fee.id not in account_ids

        # All accounts should have no fees or null fees
        for account in fee_free_accounts:
            assert account.monthly_fee is None or account.monthly_fee == 0
