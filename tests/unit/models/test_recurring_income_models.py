from datetime import datetime
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.income import Income
from src.models.income_categories import IncomeCategory
from src.models.recurring_income import RecurringIncome
from src.services.recurring_income import RecurringIncomeService
from src.utils.datetime_utils import naive_utc_from_date, naive_utc_now

pytestmark = pytest.mark.asyncio


async def test_recurring_income_repr(
    db_session: AsyncSession,
    test_checking_account: Account,
    test_income_category: IncomeCategory,
):
    """Test string representation of RecurringIncome"""
    recurring_income = RecurringIncome(
        source="Test Income",
        amount=Decimal("1000.00"),
        day_of_month=15,
        account_id=test_checking_account.id,
        category_id=test_income_category.id,
    )
    db_session.add(recurring_income)
    await db_session.commit()

    expected_repr = "<RecurringIncome Test Income $1000.00>"
    assert repr(recurring_income) == expected_repr


async def test_cascade_delete_income_entries(
    db_session: AsyncSession, test_recurring_income: RecurringIncome
):
    """Test cascading delete of income entries when recurring income is deleted"""
    # Create income entries using the service
    service = RecurringIncomeService(db_session)
    now = naive_utc_now()

    # Create two income entries
    income_entry1 = service.create_income_from_recurring(
        test_recurring_income, now.month, now.year
    )
    income_entry2 = service.create_income_from_recurring(
        test_recurring_income, now.month + 1, now.year
    )

    db_session.add_all([income_entry1, income_entry2])
    await db_session.commit()

    # Get income entry IDs
    entry_ids = [income_entry1.id, income_entry2.id]

    # Delete recurring income
    await db_session.delete(test_recurring_income)
    await db_session.commit()

    # Verify income entries were deleted
    for entry_id in entry_ids:
        result = await db_session.get(Income, entry_id)
        assert result is None


async def test_nullable_category(
    db_session: AsyncSession, test_checking_account: Account
):
    """Test that category_id is nullable"""
    recurring_income = RecurringIncome(
        source="No Category Income",
        amount=Decimal("1000.00"),
        day_of_month=15,
        account_id=test_checking_account.id,
        category_id=None,
    )
    db_session.add(recurring_income)
    await db_session.commit()

    await db_session.refresh(recurring_income)
    assert recurring_income.category_id is None
    assert recurring_income.category is None


async def test_relationship_loading(
    db_session: AsyncSession, test_recurring_income: RecurringIncome
):
    """Test loading of relationships"""
    await db_session.refresh(
        test_recurring_income, ["account", "category", "income_entries"]
    )

    assert test_recurring_income.account is not None
    assert test_recurring_income.category is not None
    assert isinstance(test_recurring_income.income_entries, list)


async def test_create_recurring_income(
    db_session: AsyncSession,
    test_checking_account: Account,
    test_income_category: IncomeCategory,
):
    """Test creating a recurring income model."""
    recurring_income = RecurringIncome(
        source="Test Income",
        amount=Decimal("1000.00"),
        day_of_month=15,
        account_id=test_checking_account.id,
        category_id=test_income_category.id,
        auto_deposit=False,
        active=True,
    )
    db_session.add(recurring_income)
    await db_session.commit()
    await db_session.refresh(recurring_income)

    assert recurring_income.id is not None
    assert recurring_income.source == "Test Income"
    assert recurring_income.amount == Decimal("1000.00")
    assert recurring_income.day_of_month == 15
    assert recurring_income.account_id == test_checking_account.id
    assert recurring_income.category_id == test_income_category.id
    assert recurring_income.auto_deposit is False
    assert recurring_income.active is True


async def test_datetime_handling_in_model(
    db_session: AsyncSession,
    test_checking_account: Account,
    test_income_category: IncomeCategory,
):
    """Test proper datetime handling in recurring income model"""
    # Create with explicit datetime values
    current_time = naive_utc_now()
    recurring_income = RecurringIncome(
        source="Test Income",
        amount=Decimal("1000.00"),
        day_of_month=15,
        account_id=test_checking_account.id,
        category_id=test_income_category.id,
        auto_deposit=False,
        active=True,
        created_at=current_time,
        updated_at=current_time,
    )
    db_session.add(recurring_income)
    await db_session.commit()
    await db_session.refresh(recurring_income)

    # Verify datetime fields are stored as naive
    assert recurring_income.created_at.tzinfo is None
    assert recurring_income.updated_at.tzinfo is None

    # Verify correct values are stored
    assert recurring_income.created_at == current_time
    assert recurring_income.updated_at == current_time
