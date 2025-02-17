from datetime import datetime
from decimal import Decimal
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.recurring_income import RecurringIncome
from src.models.income import Income
from src.models.accounts import Account
from src.models.income_categories import IncomeCategory
from src.models.base_model import naive_utc_now, naive_utc_from_date

pytestmark = pytest.mark.asyncio


async def test_create_recurring_income(
    db_session: AsyncSession,
    test_checking_account: Account,
    test_income_category: IncomeCategory
):
    """Test creating a recurring income model."""
    recurring_income = RecurringIncome(
        source="Test Income",
        amount=Decimal("1000.00"),
        day_of_month=15,
        account_id=test_checking_account.id,
        category_id=test_income_category.id,
        auto_deposit=False,
        active=True
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

async def test_create_income_entry(
    test_recurring_income: RecurringIncome
):
    """Test creating an income entry from recurring income."""
    # Test creating entry for current month
    now = naive_utc_now()
    income_entry = test_recurring_income.create_income_entry(now.month, now.year)

    assert isinstance(income_entry, Income)
    assert income_entry.source == test_recurring_income.source
    assert income_entry.amount == test_recurring_income.amount
    assert income_entry.account_id == test_recurring_income.account_id
    assert income_entry.category_id == test_recurring_income.category_id
    assert income_entry.deposited == test_recurring_income.auto_deposit
    assert income_entry.recurring is True
    assert income_entry.recurring_income_id == test_recurring_income.id
    assert income_entry.date.month == now.month
    assert income_entry.date.year == now.year
    assert income_entry.date.day == test_recurring_income.day_of_month

async def test_create_income_entry_future_date(
    test_recurring_income: RecurringIncome
):
    """Test creating an income entry for a future date."""
    now = naive_utc_now()
    future_month = (now.month % 12) + 1
    future_year = now.year + (1 if future_month < now.month else 0)

    income_entry = test_recurring_income.create_income_entry(future_month, future_year)

    assert isinstance(income_entry, Income)
    assert income_entry.date.month == future_month
    assert income_entry.date.year == future_year
    assert income_entry.date.day == test_recurring_income.day_of_month

async def test_create_income_entry_with_category(
    test_recurring_income: RecurringIncome,
    test_income_category: IncomeCategory
):
    """Test creating an income entry with category relationship."""
    now = naive_utc_now()
    income_entry = test_recurring_income.create_income_entry(now.month, now.year)

    assert income_entry.category_id == test_income_category.id
    assert income_entry.category == test_income_category

async def test_create_income_entry_with_auto_deposit(
    db_session: AsyncSession,
    test_checking_account: Account,
    test_income_category: IncomeCategory
):
    """Test creating an income entry with auto deposit enabled."""
    recurring_income = RecurringIncome(
        source="Auto Deposit Income",
        amount=Decimal("1000.00"),
        day_of_month=15,
        account_id=test_checking_account.id,
        category_id=test_income_category.id,
        auto_deposit=True,
        active=True
    )
    db_session.add(recurring_income)
    await db_session.commit()

    now = naive_utc_now()
    income_entry = recurring_income.create_income_entry(now.month, now.year)

    assert income_entry.deposited is True

async def test_datetime_handling(
    db_session: AsyncSession,
    test_checking_account: Account,
    test_income_category: IncomeCategory
):
    """Test proper datetime handling in recurring income and generated entries"""
    recurring_income = RecurringIncome(
        source="Test Income",
        amount=Decimal("1000.00"),
        day_of_month=15,
        account_id=test_checking_account.id,
        category_id=test_income_category.id,
        auto_deposit=False,
        active=True,
        created_at=naive_utc_now(),
        updated_at=naive_utc_now()
    )
    db_session.add(recurring_income)
    await db_session.commit()
    await db_session.refresh(recurring_income)

    # Verify recurring income datetime fields are naive
    assert recurring_income.created_at.tzinfo is None
    assert recurring_income.updated_at.tzinfo is None

    # Create and verify income entry datetime handling
    income_entry = recurring_income.create_income_entry(3, 2025)

    # Verify income entry date is naive and correct
    assert income_entry.date.tzinfo is None
    assert income_entry.date.year == 2025
    assert income_entry.date.month == 3
    assert income_entry.date.day == 15
    assert income_entry.date.hour == 0
    assert income_entry.date.minute == 0
    assert income_entry.date.second == 0
