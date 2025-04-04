"""
Integration tests for bill split repository with polymorphic account types.

This module tests how bill splits work with various account types, ensuring
proper transaction boundaries and validation across account types.
Following the "Real Objects Testing Philosophy" with no mocks.
"""

import pytest
from decimal import Decimal
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.bill_splits import BillSplit
from src.models.accounts import Account
from src.models.account_types.banking.checking import CheckingAccount
from src.models.account_types.banking.credit import CreditAccount
from src.models.account_types.banking.savings import SavingsAccount
from src.repositories.bill_splits import BillSplitRepository
from src.repositories.accounts import AccountRepository
from src.utils.datetime_utils import utc_now

pytestmark = pytest.mark.asyncio


class TestBillSplitsWithAccountTypes:
    """Test bill split repository integration with account types."""
    
    @pytest.fixture
    async def bill_split_repository(self, db_session: AsyncSession, feature_flag_service=None) -> BillSplitRepository:
        """Create a bill split repository for testing."""
        return BillSplitRepository(db_session, feature_flag_service)
    
    @pytest.fixture
    async def bill_with_checking_primary(self, db_session: AsyncSession, test_checking_account: CheckingAccount) -> dict:
        """Create a bill with checking account as primary for testing."""
        # Create a bill using direct SQL or the repository to avoid circular dependencies
        from src.models.liabilities import Liability  # Bill model
        
        bill = Liability(
            name="Test Bill with Checking Primary",
            amount=Decimal("100.00"),
            due_date=utc_now().replace(day=15),  # Due on the 15th
            user_id=1,
            primary_account_id=test_checking_account.id,
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        
        db_session.add(bill)
        await db_session.flush()
        await db_session.refresh(bill)
        
        return {
            "id": bill.id,
            "name": bill.name,
            "amount": bill.amount,
            "primary_account_id": bill.primary_account_id
        }
    
    @pytest.fixture
    async def test_accounts_for_splits(self, db_session: AsyncSession) -> dict:
        """Create a set of test accounts for bill split testing."""
        # Create one of each account type
        checking = CheckingAccount(
            name="Split Test Checking",
            current_balance=Decimal("1000.00"),
            available_balance=Decimal("1000.00"),
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        
        savings = SavingsAccount(
            name="Split Test Savings",
            current_balance=Decimal("5000.00"),
            available_balance=Decimal("5000.00"),
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        
        credit = CreditAccount(
            name="Split Test Credit",
            current_balance=Decimal("-500.00"),
            available_balance=Decimal("-500.00"),
            credit_limit=Decimal("2000.00"),
            available_credit=Decimal("1500.00"),
            created_at=utc_now(),
            updated_at=utc_now(),
        )
        
        db_session.add_all([checking, savings, credit])
        await db_session.flush()
        
        # Refresh to get IDs
        for account in [checking, savings, credit]:
            await db_session.refresh(account)
            
        return {
            "checking": checking,
            "savings": savings,
            "credit": credit
        }
    
    async def test_create_bill_split_with_different_account_types(
        self, db_session: AsyncSession,
        bill_split_repository: BillSplitRepository,
        bill_with_checking_primary: dict,
        test_accounts_for_splits: dict
    ):
        """Test creating bill splits with different account types."""
        # ARRANGE
        bill_id = bill_with_checking_primary["id"]
        primary_account_id = bill_with_checking_primary["primary_account_id"]
        bill_amount = bill_with_checking_primary["amount"]
        
        # Create splits between checking (primary) and credit accounts
        splits = [
            {
                "bill_id": bill_id,
                "account_id": test_accounts_for_splits["credit"].id,
                "amount": Decimal("40.00")
            },
            {
                "bill_id": bill_id,
                "account_id": test_accounts_for_splits["savings"].id,
                "amount": Decimal("30.00")
            }
        ]
        
        # ACT
        created_splits = await bill_split_repository.create_bill_splits(bill_id, splits)
        
        # ASSERT
        assert len(created_splits) == 3  # 2 explicit + 1 primary account split
        
        # Get all splits to check
        all_splits = await bill_split_repository.get_splits_by_bill(bill_id)
        assert len(all_splits) == 3
        
        # Find each split by account type
        primary_split = next(s for s in all_splits if s.account_id == primary_account_id)
        credit_split = next(s for s in all_splits if s.account_id == test_accounts_for_splits["credit"].id)
        savings_split = next(s for s in all_splits if s.account_id == test_accounts_for_splits["savings"].id)
        
        # Verify split amounts
        assert credit_split.amount == Decimal("40.00")
        assert savings_split.amount == Decimal("30.00")
        assert primary_split.amount == Decimal("30.00")  # 100 - 40 - 30 = 30
        
        # Verify total equals bill amount
        split_total = sum(s.amount for s in all_splits)
        assert split_total == bill_amount
    
    async def test_bill_split_validation_with_account_types(
        self, db_session: AsyncSession,
        bill_split_repository: BillSplitRepository,
        bill_with_checking_primary: dict,
        test_accounts_for_splits: dict
    ):
        """Test bill split validation with different account types."""
        # ARRANGE
        bill_id = bill_with_checking_primary["id"]
        
        # Split amounts exceed bill total - should validate and fail
        invalid_splits = [
            {
                "bill_id": bill_id,
                "account_id": test_accounts_for_splits["credit"].id,
                "amount": Decimal("60.00")
            },
            {
                "bill_id": bill_id,
                "account_id": test_accounts_for_splits["savings"].id,
                "amount": Decimal("50.00")
            }
        ]
        
        # ACT & ASSERT - Should fail validation (total > bill amount)
        with pytest.raises(ValueError, match="Total of splits .* exceeds bill amount"):
            await bill_split_repository.create_bill_splits(bill_id, invalid_splits)
        
        # Verify no splits were created
        all_splits = await bill_split_repository.get_splits_by_bill(bill_id)
        assert len(all_splits) == 0
    
    async def test_transaction_rollback_on_validation_failure(
        self, db_session: AsyncSession,
        bill_split_repository: BillSplitRepository,
        bill_with_checking_primary: dict,
        test_accounts_for_splits: dict
    ):
        """Test that failed validation causes transaction rollback."""
        # ARRANGE
        bill_id = bill_with_checking_primary["id"]
        
        # Create a bill split with invalid account ID
        invalid_account_splits = [
            {
                "bill_id": bill_id,
                "account_id": 9999,  # Non-existent account ID
                "amount": Decimal("40.00")
            }
        ]
        
        # ACT & ASSERT - Should fail due to foreign key constraint
        with pytest.raises(Exception):  # Could be IntegrityError or similar
            await bill_split_repository.create_bill_splits(bill_id, invalid_account_splits)
        
        # Verify no splits were created (transaction rollback worked)
        all_splits = await bill_split_repository.get_splits_by_bill(bill_id)
        assert len(all_splits) == 0
    
    async def test_updating_bill_splits_with_account_types(
        self, db_session: AsyncSession,
        bill_split_repository: BillSplitRepository,
        bill_with_checking_primary: dict,
        test_accounts_for_splits: dict
    ):
        """Test updating bill splits with different account types."""
        # ARRANGE - Create initial splits
        bill_id = bill_with_checking_primary["id"]
        primary_account_id = bill_with_checking_primary["primary_account_id"]
        
        initial_splits = [
            {
                "bill_id": bill_id,
                "account_id": test_accounts_for_splits["credit"].id,
                "amount": Decimal("30.00")
            }
        ]
        
        created_splits = await bill_split_repository.create_bill_splits(bill_id, initial_splits)
        assert len(created_splits) == 2  # 1 explicit + 1 primary account split
        
        # ACT - Update the splits
        updated_splits = [
            {
                "bill_id": bill_id,
                "account_id": test_accounts_for_splits["credit"].id,
                "amount": Decimal("40.00")
            },
            {
                "bill_id": bill_id,
                "account_id": test_accounts_for_splits["savings"].id,
                "amount": Decimal("35.00")
            }
        ]
        
        updated_result = await bill_split_repository.update_bill_splits(bill_id, updated_splits)
        
        # ASSERT
        # Should have 3 splits now
        all_splits = await bill_split_repository.get_splits_by_bill(bill_id)
        assert len(all_splits) == 3
        
        # Find each split by account type
        primary_split = next(s for s in all_splits if s.account_id == primary_account_id)
        credit_split = next(s for s in all_splits if s.account_id == test_accounts_for_splits["credit"].id)
        savings_split = next(s for s in all_splits if s.account_id == test_accounts_for_splits["savings"].id)
        
        # Verify updated split amounts
        assert credit_split.amount == Decimal("40.00")
        assert savings_split.amount == Decimal("35.00")
        assert primary_split.amount == Decimal("25.00")  # 100 - 40 - 35 = 25
        
        # Verify total equals bill amount
        split_total = sum(s.amount for s in all_splits)
        assert split_total == bill_with_checking_primary["amount"]
    
    async def test_creating_primary_account_split_automatically(
        self, db_session: AsyncSession,
        bill_split_repository: BillSplitRepository,
        bill_with_checking_primary: dict,
        test_accounts_for_splits: dict
    ):
        """Test that primary account split is created automatically with correct amount."""
        # ARRANGE
        bill_id = bill_with_checking_primary["id"]
        primary_account_id = bill_with_checking_primary["primary_account_id"]
        bill_amount = bill_with_checking_primary["amount"]
        
        # Create just one non-primary split
        splits = [
            {
                "bill_id": bill_id,
                "account_id": test_accounts_for_splits["credit"].id,
                "amount": Decimal("75.00")
            }
        ]
        
        # ACT
        created_splits = await bill_split_repository.create_bill_splits(bill_id, splits)
        
        # ASSERT
        # Should have 2 splits: explicit + primary
        assert len(created_splits) == 2
        
        # The primary account split should have been created automatically
        primary_splits = [s for s in created_splits if s.account_id == primary_account_id]
        assert len(primary_splits) == 1
        
        # The primary account split amount should be the remainder
        assert primary_splits[0].amount == Decimal("25.00")  # 100 - 75 = 25
        
        # Verify total equals bill amount
        split_total = sum(s.amount for s in created_splits)
        assert split_total == bill_amount
