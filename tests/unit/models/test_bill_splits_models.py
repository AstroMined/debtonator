from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.base_model import naive_utc_from_date, naive_utc_now
from src.models.bill_splits import BillSplit
from src.models.liabilities import Liability

pytestmark = pytest.mark.asyncio


async def test_bill_split_crud(
    db_session: AsyncSession, test_checking_account: Account, test_liability: Liability
):
    """Test basic CRUD operations for BillSplit model"""
    # Create
    bill_split = BillSplit(
        liability_id=test_liability.id,
        account_id=test_checking_account.id,
        amount=Decimal("500.00"),
    )
    db_session.add(bill_split)
    await db_session.commit()

    # Read
    await db_session.refresh(bill_split)
    assert bill_split.id is not None
    assert bill_split.liability_id == test_liability.id
    assert bill_split.account_id == test_checking_account.id
    assert bill_split.amount == Decimal("500.00")

    # Update
    bill_split.amount = Decimal("600.00")
    await db_session.commit()
    await db_session.refresh(bill_split)
    assert bill_split.amount == Decimal("600.00")

    # Test __repr__
    expected_repr = f"<BillSplit liability_id={test_liability.id} account_id={test_checking_account.id} amount={Decimal('600.00')}>"
    assert repr(bill_split) == expected_repr


async def test_bill_split_relationships(
    db_session: AsyncSession, test_checking_account: Account, test_liability: Liability
):
    """Test relationship loading for BillSplit model"""
    bill_split = BillSplit(
        liability_id=test_liability.id,
        account_id=test_checking_account.id,
        amount=Decimal("500.00"),
    )
    db_session.add(bill_split)
    await db_session.commit()

    # Test relationship loading
    await db_session.refresh(bill_split, ["liability", "account"])
    assert bill_split.liability.id == test_liability.id
    assert bill_split.account.id == test_checking_account.id


async def test_datetime_handling(
    db_session: AsyncSession, test_checking_account: Account, test_liability: Liability
):
    """Test proper datetime handling in BillSplit model"""
    # Create bill_split with explicit datetime values
    bill_split = BillSplit(
        liability_id=1,
        account_id=test_checking_account.id,
        amount=500.00,
        created_at=naive_utc_from_date(2025, 3, 15),
        updated_at=naive_utc_from_date(2025, 3, 15),
    )

    db_session.add(bill_split)
    await db_session.commit()
    await db_session.refresh(bill_split)

    # Verify all datetime fields are naive (no tzinfo)
    assert bill_split.created_at.tzinfo is None
    assert bill_split.updated_at.tzinfo is None

    # Verify created_at components
    assert bill_split.created_at.year == 2025
    assert bill_split.created_at.month == 3
    assert bill_split.created_at.day == 15
    assert bill_split.created_at.hour == 0
    assert bill_split.created_at.minute == 0
    assert bill_split.created_at.second == 0

    # Verify updated_at components
    assert bill_split.updated_at.year == 2025
    assert bill_split.updated_at.month == 3
    assert bill_split.updated_at.day == 15
    assert bill_split.updated_at.hour == 0
    assert bill_split.updated_at.minute == 0
    assert bill_split.updated_at.second == 0


async def test_default_datetime_handling(
    db_session: AsyncSession, test_checking_account: Account, test_liability: Liability
):
    """Test default datetime values are properly set"""
    bill_split = BillSplit(
        liability_id=test_liability.id,
        account_id=test_checking_account.id,
        amount=500.00,
    )

    db_session.add(bill_split)
    await db_session.commit()
    await db_session.refresh(bill_split)

    # Verify created_at and updated_at are set and naive
    assert bill_split.created_at is not None
    assert bill_split.updated_at is not None
    assert bill_split.created_at.tzinfo is None
    assert bill_split.updated_at.tzinfo is None


async def test_relationship_datetime_handling(db_session):
    """Test datetime handling with relationships"""
    bill_split = BillSplit(liability_id=1, account_id=1, amount=500.00)
    db_session.add(bill_split)
    await db_session.commit()

    # Refresh to load relationships
    await db_session.refresh(bill_split, ["liability", "account"])

    # Verify datetime fields remain naive after refresh
    assert bill_split.created_at.tzinfo is None
    assert bill_split.updated_at.tzinfo is None


async def test_decimal_precision_storage(
    db_session: AsyncSession, test_checking_account: Account, test_liability: Liability
):
    """Test four decimal place precision storage for bill splits."""
    # Test with 4 decimal precision
    amount_4_decimals = Decimal("500.1234")
    bill_split = BillSplit(
        liability_id=test_liability.id,
        account_id=test_checking_account.id,
        amount=amount_4_decimals,
    )
    db_session.add(bill_split)
    await db_session.commit()

    # Verify storage with 4 decimal places
    await db_session.refresh(bill_split)
    assert bill_split.amount == amount_4_decimals
    assert bill_split.amount.as_tuple().exponent == -4, "Should store 4 decimal places"

    # Test with 2 decimal precision
    amount_2_decimals = Decimal("600.12")
    bill_split.amount = amount_2_decimals
    await db_session.commit()
    await db_session.refresh(bill_split)
    assert bill_split.amount == amount_2_decimals

    # Test with integer
    amount_integer = Decimal("700")
    bill_split.amount = amount_integer
    await db_session.commit()
    await db_session.refresh(bill_split)
    assert bill_split.amount == amount_integer
