from datetime import datetime
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.categories import Category
from src.models.liabilities import Liability
from src.utils.datetime_utils import naive_utc_from_date, naive_utc_now

pytestmark = pytest.mark.asyncio


async def test_create_basic_liability(
    db_session: AsyncSession, test_checking_account: Account
):
    """Test creating a basic liability (bill)"""
    # Create category first
    utilities_category = Category(name="Utilities")
    db_session.add(utilities_category)
    await db_session.commit()

    liability = Liability(
        name="Internet Bill",
        amount=Decimal("89.99"),
        due_date=naive_utc_from_date(2025, 3, 15),
        category_id=utilities_category.id,
        recurring=False,
        primary_account_id=test_checking_account.id,
        created_at=naive_utc_now(),
        updated_at=naive_utc_now(),
    )
    db_session.add(liability)
    await db_session.commit()
    await db_session.refresh(liability)

    assert liability.id is not None
    assert liability.name == "Internet Bill"
    assert liability.amount == Decimal("89.99")
    assert liability.due_date == naive_utc_from_date(2025, 3, 15)
    assert liability.category.name == "Utilities"
    assert liability.recurring is False
    assert liability.primary_account_id == test_checking_account.id
    assert liability.paid is False
    assert liability.auto_pay is False


async def test_create_recurring_liability(
    db_session: AsyncSession, test_checking_account: Account
):
    """Test creating a recurring liability"""
    # Create category first
    entertainment_category = Category(name="Entertainment")
    db_session.add(entertainment_category)
    await db_session.commit()

    liability = Liability(
        name="Netflix Subscription",
        amount=Decimal("19.99"),
        due_date=naive_utc_from_date(2025, 3, 1),
        category_id=entertainment_category.id,
        recurring=True,
        recurrence_pattern={"frequency": "monthly", "day": 1},
        primary_account_id=test_checking_account.id,
        auto_pay=True,
        created_at=naive_utc_now(),
        updated_at=naive_utc_now(),
    )
    db_session.add(liability)
    await db_session.commit()
    await db_session.refresh(liability)

    assert liability.id is not None
    assert liability.name == "Netflix Subscription"
    assert liability.amount == Decimal("19.99")
    assert liability.recurring is True
    assert liability.recurrence_pattern == {"frequency": "monthly", "day": 1}
    assert liability.auto_pay is True


async def test_update_liability_amount(
    db_session: AsyncSession, test_liability: Liability
):
    """Test updating a liability's amount"""
    # Update the amount
    test_liability.amount = Decimal("150.00")
    await db_session.commit()
    await db_session.refresh(test_liability)

    assert test_liability.amount == Decimal("150.00")


async def test_liability_with_description(
    db_session: AsyncSession, test_checking_account: Account
):
    """Test creating a liability with an optional description"""
    # Create category first
    insurance_category = Category(name="Insurance")
    db_session.add(insurance_category)
    await db_session.commit()

    liability = Liability(
        name="Car Insurance",
        amount=Decimal("200.00"),
        due_date=naive_utc_from_date(2025, 3, 1),
        category_id=insurance_category.id,
        description="Semi-annual premium payment",
        recurring=False,
        primary_account_id=test_checking_account.id,
        created_at=naive_utc_now(),
        updated_at=naive_utc_now(),
    )
    db_session.add(liability)
    await db_session.commit()
    await db_session.refresh(liability)

    assert liability.description == "Semi-annual premium payment"


async def test_mark_liability_as_paid(
    db_session: AsyncSession, test_liability: Liability
):
    """Test marking a liability as paid"""
    test_liability.paid = True
    await db_session.commit()
    await db_session.refresh(test_liability)

    assert test_liability.paid is True


async def test_liability_account_relationship(
    db_session: AsyncSession, test_liability: Liability
):
    """Test the relationship between liability and account"""
    assert test_liability.primary_account is not None
    assert "Primary Test Checking" in test_liability.primary_account.name


async def test_liability_defaults(
    db_session: AsyncSession, test_checking_account: Account
):
    """Test liability creation with minimal required fields"""
    # Create category first
    other_category = Category(name="Other")
    db_session.add(other_category)
    await db_session.commit()

    liability = Liability(
        name="Simple Bill",
        amount=Decimal("50.00"),
        due_date=naive_utc_from_date(2025, 3, 1),
        category_id=other_category.id,
        primary_account_id=test_checking_account.id,
    )
    db_session.add(liability)
    await db_session.commit()
    await db_session.refresh(liability)

    assert liability.id is not None
    assert liability.recurring is False
    assert liability.description is None
    assert liability.recurrence_pattern is None
    assert liability.auto_pay is False
    assert liability.paid is False
    assert isinstance(liability.created_at, datetime)
    assert isinstance(liability.updated_at, datetime)


async def test_repr_method(db_session: AsyncSession, test_checking_account: Account):
    """Test the string representation of Liability"""
    # Create category first
    category = Category(name="Test Category")
    db_session.add(category)
    await db_session.commit()

    # Create liability with specific due date for consistent repr
    due_date = naive_utc_from_date(2025, 3, 15)
    liability = Liability(
        name="Test Bill",
        amount=Decimal("100.00"),
        due_date=due_date,
        category_id=category.id,
        primary_account_id=test_checking_account.id,
    )
    db_session.add(liability)
    await db_session.commit()
    await db_session.refresh(liability)

    expected = f"<Liability Test Bill due {due_date}>"
    assert str(liability) == expected


async def test_datetime_handling(
    db_session: AsyncSession, test_checking_account: Account
):
    """Test proper datetime handling in liabilities"""
    # Create category first
    category = Category(name="Test Category")
    db_session.add(category)
    await db_session.commit()

    # Create liability with explicit datetime values
    liability = Liability(
        name="Test Bill",
        amount=Decimal("100.00"),
        due_date=naive_utc_from_date(2025, 3, 15),
        category_id=category.id,
        primary_account_id=test_checking_account.id,
        created_at=naive_utc_now(),
        updated_at=naive_utc_now(),
    )
    db_session.add(liability)
    await db_session.commit()
    await db_session.refresh(liability)

    # Verify all datetime fields are naive (no tzinfo)
    assert liability.due_date.tzinfo is None
    assert liability.created_at.tzinfo is None
    assert liability.updated_at.tzinfo is None

    # Verify due_date components
    assert liability.due_date.year == 2025
    assert liability.due_date.month == 3
    assert liability.due_date.day == 15
    assert liability.due_date.hour == 0
    assert liability.due_date.minute == 0
    assert liability.due_date.second == 0
