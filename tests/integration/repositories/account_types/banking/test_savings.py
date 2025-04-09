"""
Integration tests for savings account repository operations.

This module tests both the base repository's polymorphic handling of savings accounts
and the specialized operations in the savings account repository module.
Following the "Real Objects Testing Philosophy" with no mocks.
"""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.savings import SavingsAccount
from src.repositories.accounts import AccountRepository
from src.repositories.factory import RepositoryFactory
from src.services.feature_flags import FeatureFlagService
from src.utils.datetime_utils import utc_now

pytestmark = pytest.mark.asyncio


class TestSavingsAccountRepository:
    """Test savings account repository operations with real objects."""

    @pytest.fixture
    async def repository(self, db_session: AsyncSession) -> AccountRepository:
        """Create a base account repository for testing."""
        return AccountRepository(db_session)

    @pytest.fixture
    async def savings_repository(
        self, db_session: AsyncSession, feature_flag_service: FeatureFlagService
    ) -> AccountRepository:
        """Create a savings-specific repository for testing."""
        factory = RepositoryFactory(db_session, feature_flag_service)
        return factory.create_account_repository(account_type="savings")

    @pytest.fixture
    async def test_savings_with_interest(
        self, db_session: AsyncSession
    ) -> SavingsAccount:
        """Create a savings account with interest rate for testing."""
        account = SavingsAccount(
            name="High-Yield Savings",
            current_balance=Decimal("5000.00"),
            available_balance=Decimal("5000.00"),
            interest_rate=Decimal("2.50"),  # 2.50%
            interest_earned_ytd=Decimal("75.50"),
            compound_frequency="monthly",
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        db_session.add(account)
        await db_session.flush()
        await db_session.refresh(account)
        return account

    @pytest.fixture
    async def test_savings_with_min_balance(
        self, db_session: AsyncSession
    ) -> SavingsAccount:
        """Create a savings account with minimum balance requirement."""
        account = SavingsAccount(
            name="Premium Savings",
            current_balance=Decimal("10000.00"),
            available_balance=Decimal("10000.00"),
            interest_rate=Decimal("3.00"),  # 3.00%
            minimum_balance=Decimal("5000.00"),
            withdrawal_limit=12,  # Standard Reg D limit
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        db_session.add(account)
        await db_session.flush()
        await db_session.refresh(account)
        return account

    async def test_get_with_type_returns_savings_account(
        self, repository: AccountRepository, test_savings_account: SavingsAccount
    ):
        """Test that get_with_type returns a SavingsAccount instance."""
        # ACT
        result = await repository.get_with_type(test_savings_account.id)

        # ASSERT
        assert result is not None
        assert isinstance(result, SavingsAccount)
        assert result.id == test_savings_account.id
        assert result.name == test_savings_account.name
        assert result.account_type == "savings"

        # Verify savings-specific fields are loaded
        assert hasattr(result, "interest_rate")
        if hasattr(test_savings_account, "compound_frequency"):
            assert result.compound_frequency == test_savings_account.compound_frequency

    async def test_get_by_type_returns_only_savings_accounts(
        self,
        repository: AccountRepository,
        test_savings_account: SavingsAccount,
        test_checking_account,
        test_credit_account,
    ):
        """Test that get_by_type returns only savings accounts."""
        # ACT
        savings_accounts = await repository.get_by_type("savings")

        # ASSERT
        assert len(savings_accounts) >= 1
        assert all(isinstance(a, SavingsAccount) for a in savings_accounts)
        assert all(a.account_type == "savings" for a in savings_accounts)

        # Verify the test account is in the results
        account_ids = [a.id for a in savings_accounts]
        assert test_savings_account.id in account_ids

        # Verify other account types are not in the results
        assert test_checking_account.id not in account_ids
        assert test_credit_account.id not in account_ids

    async def test_create_typed_account_with_savings_type(
        self, repository: AccountRepository, db_session: AsyncSession
    ):
        """Test creating a typed savings account."""
        # ARRANGE
        account_data = {
            "name": "New Savings Account",
            "account_type": "savings",
            "current_balance": Decimal("5000.00"),
            "available_balance": Decimal("5000.00"),
            "interest_rate": Decimal("1.75"),
            "compound_frequency": "daily",
            "created_at": utc_now(),
            "updated_at": utc_now(),
        }

        # ACT
        result = await repository.create_typed_account("savings", account_data)

        # ASSERT
        assert result is not None
        assert isinstance(result, SavingsAccount)
        assert result.id is not None
        assert result.name == "New Savings Account"
        assert result.account_type == "savings"
        assert result.current_balance == Decimal("5000.00")
        assert result.available_balance == Decimal("5000.00")
        assert result.interest_rate == Decimal("1.75")
        assert result.compound_frequency == "daily"

        # Verify it was actually persisted
        persisted = await repository.get(result.id)
        assert persisted is not None
        assert persisted.id == result.id

    async def test_update_typed_account_with_savings_type(
        self, repository: AccountRepository, test_savings_account: SavingsAccount
    ):
        """Test updating a typed savings account."""
        # ARRANGE
        update_data = {
            "name": "Updated Savings Account",
            "interest_rate": Decimal("2.25"),
            "compound_frequency": "quarterly",
            "minimum_balance": Decimal("1000.00"),
        }

        # ACT
        result = await repository.update_typed_account(
            test_savings_account.id, "savings", update_data
        )

        # ASSERT
        assert result is not None
        assert isinstance(result, SavingsAccount)
        assert result.id == test_savings_account.id
        assert result.name == "Updated Savings Account"
        assert result.interest_rate == Decimal("2.25")
        assert result.compound_frequency == "quarterly"
        assert result.minimum_balance == Decimal("1000.00")

    # Tests for specialized repository module functions

    async def test_get_accounts_by_interest_rate_threshold(
        self,
        savings_repository: AccountRepository,
        test_savings_with_interest: SavingsAccount,
        test_savings_with_min_balance: SavingsAccount,
        test_savings_account: SavingsAccount,
        db_session: AsyncSession,
    ):
        """Test getting savings accounts with interest rate above threshold."""
        # ARRANGE
        # Ensure basic test_savings_account has a low interest rate
        if hasattr(test_savings_account, "interest_rate") and (
            test_savings_account.interest_rate is None
            or test_savings_account.interest_rate > Decimal("1.0")
        ):
            test_savings_account.interest_rate = Decimal("0.50")
            await db_session.flush()

        # ACT
        high_interest = (
            await savings_repository.get_accounts_by_interest_rate_threshold(
                Decimal("2.0")
            )
        )

        # ASSERT
        assert (
            len(high_interest) >= 2
        )  # Should have our test accounts with 2.5% and 3.0%

        # Verify the right accounts are included
        account_ids = [a.id for a in high_interest]
        assert test_savings_with_interest.id in account_ids
        assert test_savings_with_min_balance.id in account_ids

        # Verify low interest account is excluded
        if hasattr(
            test_savings_account, "interest_rate"
        ) and test_savings_account.interest_rate < Decimal("2.0"):
            assert test_savings_account.id not in account_ids

        # All accounts should have interest rates above threshold
        assert all(
            a.interest_rate is not None and a.interest_rate >= Decimal("2.0")
            for a in high_interest
        )

    async def test_get_accounts_with_minimum_balance(
        self,
        savings_repository: AccountRepository,
        test_savings_with_min_balance: SavingsAccount,
        test_savings_with_interest: SavingsAccount,
    ):
        """Test getting savings accounts with minimum balance requirements."""
        # ACT
        min_balance_accounts = (
            await savings_repository.get_accounts_with_minimum_balance()
        )

        # ASSERT
        assert len(min_balance_accounts) >= 1

        # Verify account with minimum balance is included
        account_ids = [a.id for a in min_balance_accounts]
        assert test_savings_with_min_balance.id in account_ids

        # Verify account without minimum balance is excluded (if it doesn't have one)
        if (
            not hasattr(test_savings_with_interest, "minimum_balance")
            or test_savings_with_interest.minimum_balance is None
        ):
            assert test_savings_with_interest.id not in account_ids

        # All accounts should have a minimum balance
        assert all(
            a.minimum_balance is not None and a.minimum_balance > 0
            for a in min_balance_accounts
        )

    async def test_get_accounts_below_minimum_balance(
        self, savings_repository: AccountRepository, db_session: AsyncSession
    ):
        """Test getting savings accounts with balance below their minimum requirement."""
        # ARRANGE
        # Create an account below its minimum balance
        below_min = SavingsAccount(
            name="Below Minimum",
            current_balance=Decimal("800.00"),
            available_balance=Decimal("800.00"),
            minimum_balance=Decimal("1000.00"),
            created_at=utc_now(),
            updated_at=utc_now(),
        )

        # Create an account above its minimum balance
        above_min = SavingsAccount(
            name="Above Minimum",
            current_balance=Decimal("2000.00"),
            available_balance=Decimal("2000.00"),
            minimum_balance=Decimal("1000.00"),
            created_at=utc_now(),
            updated_at=utc_now(),
        )

        db_session.add_all([below_min, above_min])
        await db_session.flush()

        # ACT
        below_min_accounts = (
            await savings_repository.get_accounts_below_minimum_balance()
        )

        # ASSERT
        assert len(below_min_accounts) >= 1

        # Verify correct accounts are included/excluded
        account_ids = [a.id for a in below_min_accounts]
        assert below_min.id in account_ids
        assert above_min.id not in account_ids

        # All accounts should be below their minimum balance
        for account in below_min_accounts:
            assert account.minimum_balance is not None
            assert account.available_balance < account.minimum_balance

    async def test_get_highest_yield_accounts(
        self,
        savings_repository: AccountRepository,
        test_savings_with_interest: SavingsAccount,
        test_savings_with_min_balance: SavingsAccount,
        test_savings_account: SavingsAccount,
        db_session: AsyncSession,
    ):
        """Test getting highest yield savings accounts with limit."""
        # ACT
        top_accounts = await savings_repository.get_highest_yield_accounts(limit=2)

        # ASSERT
        assert len(top_accounts) <= 2  # Should respect the limit

        # Verify top accounts are returned in descending order of interest rate
        if len(top_accounts) >= 2:
            assert top_accounts[0].interest_rate >= top_accounts[1].interest_rate

        # Verify the highest interest rate account is included
        # (test_savings_with_min_balance has 3.00%)
        if len(top_accounts) > 0:
            assert top_accounts[0].id == test_savings_with_min_balance.id
