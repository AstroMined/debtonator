"""
Integration tests for bill split repository with polymorphic account types.

This module tests how bill splits work with various account types, ensuring
proper transaction boundaries and validation across account types.
Following the "Real Objects Testing Philosophy" with no mocks.
"""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.checking import CheckingAccount
from src.models.account_types.banking.credit import CreditAccount
from src.models.account_types.banking.savings import SavingsAccount
from src.models.liabilities import Liability
from src.repositories.bill_splits import BillSplitRepository
from src.utils.datetime_utils import utc_now
from tests.helpers.schema_factories.bill_splits_schema_factories import (
    create_bill_split_schema,
)
from tests.helpers.schema_factories.liabilities_schema_factories import (
    create_liability_schema,
)

pytestmark = pytest.mark.asyncio


@pytest.mark.asyncio
async def test_create_bill_split_with_different_account_types(
    bill_split_repository: BillSplitRepository,
    db_session: AsyncSession,
    test_checking_account: CheckingAccount,
):
    """
    Test creating bill splits with different account types.

    This test verifies that bill splits can be created with different account types
    and that the primary account split is calculated correctly.

    Args:
        bill_split_repository: Bill split repository
        db_session: Database session
        test_checking_account: Checking account fixture
    """
    # 1. ARRANGE: Create a bill and test accounts for splits
    # Create a bill with checking account as primary
    bill_schema = create_liability_schema(
        name="Test Bill with Checking Primary",
        amount=Decimal("100.00"),
        due_date=utc_now().replace(day=15),  # Due on the 15th
        primary_account_id=test_checking_account.id,
    )

    bill = Liability(**bill_schema.model_dump())
    db_session.add(bill)
    await db_session.flush()
    await db_session.refresh(bill)

    # Create one of each account type for splits
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

    # 2. SCHEMA: Create bill split schemas
    credit_split_schema = create_bill_split_schema(
        bill_id=bill.id,
        account_id=credit.id,
        amount=Decimal("40.00"),
    )

    savings_split_schema = create_bill_split_schema(
        bill_id=bill.id,
        account_id=savings.id,
        amount=Decimal("30.00"),
    )

    splits = [
        credit_split_schema.model_dump(),
        savings_split_schema.model_dump(),
    ]

    # 3. ACT: Create the bill splits
    created_splits = await bill_split_repository.create_bill_splits(bill.id, splits)

    # 4. ASSERT: Verify the results
    assert len(created_splits) == 3  # 2 explicit + 1 primary account split

    # Get all splits to check
    all_splits = await bill_split_repository.get_splits_by_bill(bill.id)
    assert len(all_splits) == 3

    # Find each split by account type
    primary_split = next(
        s for s in all_splits if s.account_id == test_checking_account.id
    )
    credit_split = next(s for s in all_splits if s.account_id == credit.id)
    savings_split = next(s for s in all_splits if s.account_id == savings.id)

    # Verify split amounts
    assert credit_split.amount == Decimal("40.00")
    assert savings_split.amount == Decimal("30.00")
    assert primary_split.amount == Decimal("30.00")  # 100 - 40 - 30 = 30

    # Verify total equals bill amount
    split_total = sum(s.amount for s in all_splits)
    assert split_total == bill.amount


@pytest.mark.asyncio
async def test_bill_split_validation_with_account_types(
    bill_split_repository: BillSplitRepository,
    db_session: AsyncSession,
    test_checking_account: CheckingAccount,
):
    """
    Test bill split validation with different account types.

    This test verifies that bill splits are validated correctly and that
    validation errors are raised when appropriate.

    Args:
        bill_split_repository: Bill split repository
        db_session: Database session
        test_checking_account: Checking account fixture
    """
    # 1. ARRANGE: Create a bill and test accounts for splits
    # Create a bill with checking account as primary
    bill_schema = create_liability_schema(
        name="Test Bill with Checking Primary",
        amount=Decimal("100.00"),
        due_date=utc_now().replace(day=15),  # Due on the 15th
        primary_account_id=test_checking_account.id,
    )

    bill = Liability(**bill_schema.model_dump())
    db_session.add(bill)
    await db_session.flush()
    await db_session.refresh(bill)

    # Create accounts for splits
    credit = CreditAccount(
        name="Split Test Credit",
        current_balance=Decimal("-500.00"),
        available_balance=Decimal("-500.00"),
        credit_limit=Decimal("2000.00"),
        available_credit=Decimal("1500.00"),
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

    db_session.add_all([credit, savings])
    await db_session.flush()
    for account in [credit, savings]:
        await db_session.refresh(account)

    # 2. SCHEMA: Create invalid bill split schemas (total > bill amount)
    credit_split_schema = create_bill_split_schema(
        bill_id=bill.id,
        account_id=credit.id,
        amount=Decimal("60.00"),
    )

    savings_split_schema = create_bill_split_schema(
        bill_id=bill.id,
        account_id=savings.id,
        amount=Decimal("50.00"),
    )

    invalid_splits = [
        credit_split_schema.model_dump(),
        savings_split_schema.model_dump(),
    ]

    # 3. ACT & ASSERT: Verify validation fails
    with pytest.raises(ValueError, match="Total of splits .* exceeds bill amount"):
        await bill_split_repository.create_bill_splits(bill.id, invalid_splits)

    # Verify no splits were created
    all_splits = await bill_split_repository.get_splits_by_bill(bill.id)
    assert len(all_splits) == 0


@pytest.mark.asyncio
async def test_transaction_rollback_on_validation_failure(
    bill_split_repository: BillSplitRepository,
    db_session: AsyncSession,
    test_checking_account: CheckingAccount,
):
    """
    Test that failed validation causes transaction rollback.

    This test verifies that when a validation error occurs during bill split creation,
    the transaction is rolled back and no splits are created.

    Args:
        bill_split_repository: Bill split repository
        db_session: Database session
        test_checking_account: Checking account fixture
    """
    # 1. ARRANGE: Create a bill
    bill_schema = create_liability_schema(
        name="Test Bill with Checking Primary",
        amount=Decimal("100.00"),
        due_date=utc_now().replace(day=15),  # Due on the 15th
        primary_account_id=test_checking_account.id,
    )

    bill = Liability(**bill_schema.model_dump())
    db_session.add(bill)
    await db_session.flush()
    await db_session.refresh(bill)

    # 2. SCHEMA: Create a bill split with invalid account ID
    invalid_split_schema = create_bill_split_schema(
        bill_id=bill.id,
        account_id=9999,  # Non-existent account ID
        amount=Decimal("40.00"),
    )

    invalid_account_splits = [invalid_split_schema.model_dump()]

    # 3. ACT & ASSERT: Verify validation fails
    with pytest.raises(Exception):  # Could be IntegrityError or similar
        await bill_split_repository.create_bill_splits(bill.id, invalid_account_splits)

    # Verify no splits were created (transaction rollback worked)
    all_splits = await bill_split_repository.get_splits_by_bill(bill.id)
    assert len(all_splits) == 0


@pytest.mark.asyncio
async def test_updating_bill_splits_with_account_types(
    bill_split_repository: BillSplitRepository,
    db_session: AsyncSession,
    test_checking_account: CheckingAccount,
):
    """
    Test updating bill splits with different account types.

    This test verifies that bill splits can be updated with different account types
    and that the primary account split is recalculated correctly.

    Args:
        bill_split_repository: Bill split repository
        db_session: Database session
        test_checking_account: Checking account fixture
    """
    # 1. ARRANGE: Create a bill and test accounts for splits
    # Create a bill with checking account as primary
    bill_schema = create_liability_schema(
        name="Test Bill with Checking Primary",
        amount=Decimal("100.00"),
        due_date=utc_now().replace(day=15),  # Due on the 15th
        primary_account_id=test_checking_account.id,
    )

    bill = Liability(**bill_schema.model_dump())
    db_session.add(bill)
    await db_session.flush()
    await db_session.refresh(bill)

    # Create accounts for splits
    credit = CreditAccount(
        name="Split Test Credit",
        current_balance=Decimal("-500.00"),
        available_balance=Decimal("-500.00"),
        credit_limit=Decimal("2000.00"),
        available_credit=Decimal("1500.00"),
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

    db_session.add_all([credit, savings])
    await db_session.flush()
    for account in [credit, savings]:
        await db_session.refresh(account)

    # Create initial splits
    initial_split_schema = create_bill_split_schema(
        bill_id=bill.id,
        account_id=credit.id,
        amount=Decimal("30.00"),
    )

    initial_splits = [initial_split_schema.model_dump()]

    created_splits = await bill_split_repository.create_bill_splits(
        bill.id, initial_splits
    )
    assert len(created_splits) == 2  # 1 explicit + 1 primary account split

    # 2. SCHEMA: Create updated bill split schemas
    credit_split_schema = create_bill_split_schema(
        bill_id=bill.id,
        account_id=credit.id,
        amount=Decimal("40.00"),
    )

    savings_split_schema = create_bill_split_schema(
        bill_id=bill.id,
        account_id=savings.id,
        amount=Decimal("35.00"),
    )

    updated_splits = [
        credit_split_schema.model_dump(),
        savings_split_schema.model_dump(),
    ]

    # 3. ACT: Update the bill splits
    updated_result = await bill_split_repository.update_bill_splits(
        bill.id, updated_splits
    )

    # 4. ASSERT: Verify the results
    # Should have 3 splits now
    all_splits = await bill_split_repository.get_splits_by_bill(bill.id)
    assert len(all_splits) == 3

    # Find each split by account type
    primary_split = next(
        s for s in all_splits if s.account_id == test_checking_account.id
    )
    credit_split = next(s for s in all_splits if s.account_id == credit.id)
    savings_split = next(s for s in all_splits if s.account_id == savings.id)

    # Verify updated split amounts
    assert credit_split.amount == Decimal("40.00")
    assert savings_split.amount == Decimal("35.00")
    assert primary_split.amount == Decimal("25.00")  # 100 - 40 - 35 = 25

    # Verify total equals bill amount
    split_total = sum(s.amount for s in all_splits)
    assert split_total == bill.amount


@pytest.mark.asyncio
async def test_creating_primary_account_split_automatically(
    bill_split_repository: BillSplitRepository,
    db_session: AsyncSession,
    test_checking_account: CheckingAccount,
):
    """
    Test that primary account split is created automatically with correct amount.

    This test verifies that when bill splits are created, a split for the primary account
    is automatically created with the correct amount (bill amount - sum of other splits).

    Args:
        bill_split_repository: Bill split repository
        db_session: Database session
        test_checking_account: Checking account fixture
    """
    # 1. ARRANGE: Create a bill and test accounts for splits
    # Create a bill with checking account as primary
    bill_schema = create_liability_schema(
        name="Test Bill with Checking Primary",
        amount=Decimal("100.00"),
        due_date=utc_now().replace(day=15),  # Due on the 15th
        primary_account_id=test_checking_account.id,
    )

    bill = Liability(**bill_schema.model_dump())
    db_session.add(bill)
    await db_session.flush()
    await db_session.refresh(bill)

    # Create account for split
    credit = CreditAccount(
        name="Split Test Credit",
        current_balance=Decimal("-500.00"),
        available_balance=Decimal("-500.00"),
        credit_limit=Decimal("2000.00"),
        available_credit=Decimal("1500.00"),
        created_at=utc_now(),
        updated_at=utc_now(),
    )

    db_session.add(credit)
    await db_session.flush()
    await db_session.refresh(credit)

    # 2. SCHEMA: Create bill split schema
    credit_split_schema = create_bill_split_schema(
        bill_id=bill.id,
        account_id=credit.id,
        amount=Decimal("75.00"),
    )

    splits = [credit_split_schema.model_dump()]

    # 3. ACT: Create the bill splits
    created_splits = await bill_split_repository.create_bill_splits(bill.id, splits)

    # 4. ASSERT: Verify the results
    # Should have 2 splits: explicit + primary
    assert len(created_splits) == 2

    # The primary account split should have been created automatically
    primary_splits = [
        s for s in created_splits if s.account_id == test_checking_account.id
    ]
    assert len(primary_splits) == 1

    # The primary account split amount should be the remainder
    assert primary_splits[0].amount == Decimal("25.00")  # 100 - 75 = 25

    # Verify total equals bill amount
    split_total = sum(s.amount for s in created_splits)
    assert split_total == bill.amount
