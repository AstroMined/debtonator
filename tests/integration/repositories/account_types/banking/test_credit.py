"""
Integration tests for credit account repository operations.

This module tests both the base repository's polymorphic handling of credit accounts
and the specialized operations in the credit account repository module.
Following the "Real Objects Testing Philosophy" with no mocks.
"""

from datetime import timedelta
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.credit import CreditAccount
from src.repositories.accounts import AccountRepository
from src.repositories.factory import RepositoryFactory
from src.services.feature_flags import FeatureFlagService
from src.utils.datetime_utils import utc_now

pytestmark = pytest.mark.asyncio


class TestCreditAccountRepository:
    """Test credit account repository operations with real objects."""

    @pytest.fixture
    async def repository(self, db_session: AsyncSession) -> AccountRepository:
        """Create a base account repository for testing."""
        return AccountRepository(db_session)

    @pytest.fixture
    async def credit_repository(
        self, db_session: AsyncSession, feature_flag_service: FeatureFlagService
    ) -> AccountRepository:
        """Create a credit-specific repository for testing."""
        factory = RepositoryFactory(db_session, feature_flag_service)
        return factory.create_account_repository(account_type="credit")

    @pytest.fixture
    async def test_credit_with_due_date(
        self, db_session: AsyncSession
    ) -> CreditAccount:
        """Create a credit account with due date for testing."""
        now = utc_now()
        due_date = now + timedelta(days=15)

        account = CreditAccount(
            name="Test Credit With Due Date",
            current_balance=Decimal("-1000.00"),  # Negative for amount owed
            available_balance=Decimal("-1000.00"),
            credit_limit=Decimal("5000.00"),
            available_credit=Decimal("4000.00"),  # credit_limit - abs(current_balance)
            statement_balance=Decimal("1000.00"),
            statement_due_date=due_date,
            minimum_payment=Decimal("35.00"),
            apr=Decimal("18.99"),
            created_at=now,
            updated_at=now,
        )
        db_session.add(account)
        await db_session.flush()
        await db_session.refresh(account)
        return account

    @pytest.fixture
    async def test_credit_with_rewards(self, db_session: AsyncSession) -> CreditAccount:
        """Create a credit account with rewards program for testing."""
        account = CreditAccount(
            name="Rewards Credit Card",
            current_balance=Decimal("-2500.00"),
            available_balance=Decimal("-2500.00"),
            credit_limit=Decimal("10000.00"),
            available_credit=Decimal("7500.00"),
            apr=Decimal("21.99"),
            annual_fee=Decimal("95.00"),
            rewards_program="Cash Back",
            autopay_status="full_balance",
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        db_session.add(account)
        await db_session.flush()
        await db_session.refresh(account)
        return account

    async def test_get_with_type_returns_credit_account(
        self, repository: AccountRepository, test_credit_account: CreditAccount
    ):
        """Test that get_with_type returns a CreditAccount instance."""
        # ACT
        result = await repository.get_with_type(test_credit_account.id)

        # ASSERT
        assert result is not None
        assert isinstance(result, CreditAccount)
        assert result.id == test_credit_account.id
        assert result.name == test_credit_account.name
        assert result.account_type == "credit"

        # Verify credit-specific fields are loaded
        assert hasattr(result, "credit_limit")
        if hasattr(test_credit_account, "apr"):
            assert result.apr == test_credit_account.apr

    async def test_get_by_type_returns_only_credit_accounts(
        self,
        repository: AccountRepository,
        test_credit_account: CreditAccount,
        test_checking_account,
        test_savings_account,
    ):
        """Test that get_by_type returns only credit accounts."""
        # ACT
        credit_accounts = await repository.get_by_type("credit")

        # ASSERT
        assert len(credit_accounts) >= 1
        assert all(isinstance(a, CreditAccount) for a in credit_accounts)
        assert all(a.account_type == "credit" for a in credit_accounts)

        # Verify the test account is in the results
        account_ids = [a.id for a in credit_accounts]
        assert test_credit_account.id in account_ids

        # Verify other account types are not in the results
        assert test_checking_account.id not in account_ids
        assert test_savings_account.id not in account_ids

    async def test_create_typed_account_with_credit_type(
        self, repository: AccountRepository, db_session: AsyncSession
    ):
        """Test creating a typed credit account."""
        # ARRANGE
        account_data = {
            "name": "New Credit Account",
            "account_type": "credit",
            "current_balance": Decimal("-500.00"),
            "available_balance": Decimal("-500.00"),
            "credit_limit": Decimal("3000.00"),
            "available_credit": Decimal("2500.00"),
            "apr": Decimal("15.99"),
            "created_at": utc_now(),
            "updated_at": utc_now(),
        }

        # ACT
        result = await repository.create_typed_account("credit", account_data)

        # ASSERT
        assert result is not None
        assert isinstance(result, CreditAccount)
        assert result.id is not None
        assert result.name == "New Credit Account"
        assert result.account_type == "credit"
        assert result.current_balance == Decimal("-500.00")
        assert result.available_balance == Decimal("-500.00")
        assert result.credit_limit == Decimal("3000.00")
        assert result.available_credit == Decimal("2500.00")
        assert result.apr == Decimal("15.99")

        # Verify it was actually persisted
        persisted = await repository.get(result.id)
        assert persisted is not None
        assert persisted.id == result.id

    async def test_update_typed_account_with_credit_type(
        self, repository: AccountRepository, test_credit_account: CreditAccount
    ):
        """Test updating a typed credit account."""
        # ARRANGE
        update_data = {
            "name": "Updated Credit Account",
            "apr": Decimal("14.99"),
            "rewards_program": "Travel Points",
            "autopay_status": "minimum_payment",
        }

        # ACT
        result = await repository.update_typed_account(
            test_credit_account.id, "credit", update_data
        )

        # ASSERT
        assert result is not None
        assert isinstance(result, CreditAccount)
        assert result.id == test_credit_account.id
        assert result.name == "Updated Credit Account"
        assert result.apr == Decimal("14.99")
        assert result.rewards_program == "Travel Points"
        assert result.autopay_status == "minimum_payment"

    # Tests for specialized repository module functions

    async def test_get_credit_accounts_with_upcoming_payments(
        self,
        credit_repository: AccountRepository,
        test_credit_with_due_date: CreditAccount,
        test_credit_account: CreditAccount,
        db_session: AsyncSession,
    ):
        """Test getting credit accounts with payments due in the next X days."""
        # ARRANGE
        # Ensure test_credit_account has a due date in the distant future
        far_future = utc_now() + timedelta(days=45)
        test_credit_account.statement_due_date = far_future
        await db_session.flush()

        # ACT - Get accounts with payments due in next 20 days
        upcoming_payments = (
            await credit_repository.get_credit_accounts_with_upcoming_payments(days=20)
        )

        # ASSERT
        assert len(upcoming_payments) >= 1

        # Verify account with upcoming due date is included
        account_ids = [a.id for a in upcoming_payments]
        assert test_credit_with_due_date.id in account_ids

        # Verify account with far future due date is excluded
        assert test_credit_account.id not in account_ids

        # All accounts should have due dates within the next 20 days
        now = utc_now()
        for account in upcoming_payments:
            assert account.statement_due_date is not None
            days_until_due = (account.statement_due_date - now).days
            assert 0 <= days_until_due <= 20

    async def test_get_credit_accounts_by_utilization(
        self, credit_repository: AccountRepository, db_session: AsyncSession
    ):
        """Test getting credit accounts by utilization range."""
        # ARRANGE
        # Create accounts with different utilization rates
        low_util = CreditAccount(
            name="Low Utilization",
            current_balance=Decimal("-500.00"),  # 10% utilization
            available_balance=Decimal("-500.00"),
            credit_limit=Decimal("5000.00"),
            available_credit=Decimal("4500.00"),
            created_at=utc_now(),
            updated_at=utc_now(),
        )

        mid_util = CreditAccount(
            name="Mid Utilization",
            current_balance=Decimal("-3000.00"),  # 30% utilization
            available_balance=Decimal("-3000.00"),
            credit_limit=Decimal("10000.00"),
            available_credit=Decimal("7000.00"),
            created_at=utc_now(),
            updated_at=utc_now(),
        )

        high_util = CreditAccount(
            name="High Utilization",
            current_balance=Decimal("-8000.00"),  # 80% utilization
            available_balance=Decimal("-8000.00"),
            credit_limit=Decimal("10000.00"),
            available_credit=Decimal("2000.00"),
            created_at=utc_now(),
            updated_at=utc_now(),
        )

        db_session.add_all([low_util, mid_util, high_util])
        await db_session.flush()

        # ACT - Get accounts with 25-60% utilization
        mid_range_accounts = await credit_repository.get_credit_accounts_by_utilization(
            min_percent=25, max_percent=60
        )

        # ASSERT
        assert len(mid_range_accounts) >= 1

        # Verify correct accounts are included/excluded
        account_ids = [a.id for a in mid_range_accounts]
        assert mid_util.id in account_ids
        assert low_util.id not in account_ids
        assert high_util.id not in account_ids

        # All accounts should have utilization within the specified range
        for account in mid_range_accounts:
            utilization = abs(account.current_balance) / account.credit_limit * 100
            assert 25 <= utilization <= 60

    async def test_get_credit_accounts_by_statement_status(
        self,
        credit_repository: AccountRepository,
        test_credit_with_due_date: CreditAccount,
        db_session: AsyncSession,
    ):
        """Test getting credit accounts with or without open statements."""
        # ARRANGE
        # Create an account with no statement
        no_statement = CreditAccount(
            name="No Statement",
            current_balance=Decimal("-1500.00"),
            available_balance=Decimal("-1500.00"),
            credit_limit=Decimal("5000.00"),
            available_credit=Decimal("3500.00"),
            statement_balance=None,
            statement_due_date=None,
            created_at=utc_now(),
            updated_at=utc_now(),
        )

        db_session.add(no_statement)
        await db_session.flush()

        # ACT
        with_statement = (
            await credit_repository.get_credit_accounts_with_open_statements()
        )
        without_statement = (
            await credit_repository.get_credit_accounts_without_statements()
        )

        # ASSERT - With statements
        assert len(with_statement) >= 1
        with_ids = [a.id for a in with_statement]
        assert test_credit_with_due_date.id in with_ids
        assert no_statement.id not in with_ids

        # All accounts should have statement balance and due date
        for account in with_statement:
            assert account.statement_balance is not None
            assert account.statement_due_date is not None

        # ASSERT - Without statements
        assert len(without_statement) >= 1
        without_ids = [a.id for a in without_statement]
        assert no_statement.id in without_ids
        assert test_credit_with_due_date.id not in without_ids

        # All accounts should have no statement balance or due date
        for account in without_statement:
            assert (
                account.statement_balance is None or account.statement_due_date is None
            )

    async def test_get_credit_accounts_with_autopay(
        self,
        credit_repository: AccountRepository,
        test_credit_with_rewards: CreditAccount,
        db_session: AsyncSession,
    ):
        """Test getting credit accounts with autopay enabled."""
        # ARRANGE
        # Create an account without autopay
        no_autopay = CreditAccount(
            name="No Autopay",
            current_balance=Decimal("-1000.00"),
            available_balance=Decimal("-1000.00"),
            credit_limit=Decimal("5000.00"),
            available_credit=Decimal("4000.00"),
            autopay_status="none",  # No autopay
            created_at=utc_now(),
            updated_at=utc_now(),
        )

        db_session.add(no_autopay)
        await db_session.flush()

        # ACT
        with_autopay = await credit_repository.get_credit_accounts_with_autopay()

        # ASSERT
        assert len(with_autopay) >= 1

        # Verify account with autopay is included
        account_ids = [a.id for a in with_autopay]
        assert test_credit_with_rewards.id in account_ids

        # Verify account without autopay is excluded
        assert no_autopay.id not in account_ids

        # All accounts should have autopay enabled (not 'none')
        for account in with_autopay:
            assert account.autopay_status is not None
            assert account.autopay_status != "none"
