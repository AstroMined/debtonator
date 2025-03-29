from datetime import datetime
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.income import Income
from src.models.income_categories import IncomeCategory
from src.models.recurring_income import RecurringIncome
from src.schemas.income import (
    GenerateIncomeRequest,
    RecurringIncomeCreate,
    RecurringIncomeUpdate,
)
from src.services.recurring_income import RecurringIncomeService
from src.utils.datetime_utils import naive_utc_from_date, naive_utc_now

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="function")
async def test_recurring_income(
    db_session: AsyncSession, test_checking_account: Account
) -> RecurringIncome:
    """Create a basic recurring income for testing."""
    recurring_income = RecurringIncome(
        source="Test Income",
        amount=Decimal("1000.00"),
        day_of_month=15,
        account_id=test_checking_account.id,
        auto_deposit=False,
        active=True,
        created_at=naive_utc_now(),
        updated_at=naive_utc_now(),
    )
    db_session.add(recurring_income)
    await db_session.commit()
    await db_session.refresh(recurring_income)
    return recurring_income


@pytest.fixture(scope="function")
async def test_recurring_income_with_category(
    db_session: AsyncSession,
    test_checking_account: Account,
    test_income_category: IncomeCategory,
) -> RecurringIncome:
    """Create a test recurring income with a category."""
    recurring_income = RecurringIncome(
        source="Salary",
        amount=Decimal("2000.00"),
        day_of_month=15,
        account_id=test_checking_account.id,
        category_id=test_income_category.id,
        auto_deposit=True,
        active=True,
        created_at=naive_utc_now(),
        updated_at=naive_utc_now(),
    )
    db_session.add(recurring_income)
    await db_session.commit()
    await db_session.refresh(recurring_income, ["account", "category"])
    return recurring_income


async def test_create_recurring_income(
    db_session: AsyncSession, test_checking_account: Account
):
    """Test creating a recurring income template."""
    service = RecurringIncomeService(db_session)
    income_data = RecurringIncomeCreate(
        source="Test Income",
        amount=Decimal("1000.00"),
        day_of_month=15,
        account_id=test_checking_account.id,
        auto_deposit=False,
    )

    result = await service.create(income_data)
    assert result.source == "Test Income"
    assert result.amount == Decimal("1000.00")
    assert result.day_of_month == 15
    assert result.account_id == test_checking_account.id
    assert result.auto_deposit is False
    assert result.active is True


async def test_get_recurring_income(
    db_session: AsyncSession, test_recurring_income: RecurringIncome
):
    """Test retrieving a recurring income template."""
    service = RecurringIncomeService(db_session)
    result = await service.get(test_recurring_income.id)
    assert result is not None
    assert result.id == test_recurring_income.id
    assert result.source == test_recurring_income.source
    assert result.amount == test_recurring_income.amount


async def test_update_recurring_income(
    db_session: AsyncSession, test_recurring_income: RecurringIncome
):
    """Test updating a recurring income template."""
    service = RecurringIncomeService(db_session)
    update_data = RecurringIncomeUpdate(
        source="Updated Income", amount=Decimal("1500.00")
    )

    result = await service.update(test_recurring_income.id, update_data)
    assert result is not None
    assert result.source == "Updated Income"
    assert result.amount == Decimal("1500.00")
    assert result.day_of_month == test_recurring_income.day_of_month


async def test_delete_recurring_income(
    db_session: AsyncSession, test_recurring_income: RecurringIncome
):
    """Test deleting a recurring income template."""
    service = RecurringIncomeService(db_session)
    success = await service.delete(test_recurring_income.id)
    assert success is True

    # Verify it's deleted
    result = await service.get(test_recurring_income.id)
    assert result is None


async def test_list_recurring_income(
    db_session: AsyncSession, test_recurring_income: RecurringIncome
):
    """Test listing recurring income templates."""
    service = RecurringIncomeService(db_session)
    items, total = await service.list()
    assert total >= 1
    assert any(item.id == test_recurring_income.id for item in items)


async def test_generate_income(
    db_session: AsyncSession, test_recurring_income: RecurringIncome
):
    """Test generating income entries from recurring templates."""
    service = RecurringIncomeService(db_session)
    now = naive_utc_now()
    request = GenerateIncomeRequest(month=now.month, year=now.year)

    results = await service.generate_income(request)
    assert len(results) > 0

    generated = results[0]
    assert isinstance(generated, Income)
    assert generated.source == test_recurring_income.source
    assert generated.amount == test_recurring_income.amount
    assert generated.account_id == test_recurring_income.account_id
    assert generated.recurring is True
    assert generated.recurring_income_id == test_recurring_income.id

    # Test that duplicate entries are not created
    new_results = await service.generate_income(request)
    assert len(new_results) == 0


# Tests for the create_income_from_recurring method (ADR-012 implementation)


async def test_create_income_from_recurring(
    db_session: AsyncSession, test_recurring_income_with_category: RecurringIncome
):
    """
    Test the create_income_from_recurring method which replaces the model's
    create_income_entry method as part of ADR-012 implementation.
    """
    service = RecurringIncomeService(db_session)

    # Test for current month
    now = naive_utc_now()
    income_entry = service.create_income_from_recurring(
        test_recurring_income_with_category, now.month, now.year
    )

    # Verify income entry properties
    assert isinstance(income_entry, Income)
    assert income_entry.source == test_recurring_income_with_category.source
    assert income_entry.amount == test_recurring_income_with_category.amount
    assert income_entry.account_id == test_recurring_income_with_category.account_id
    assert income_entry.category_id == test_recurring_income_with_category.category_id
    assert income_entry.category == test_recurring_income_with_category.category
    assert income_entry.deposited == test_recurring_income_with_category.auto_deposit
    assert income_entry.recurring is True
    assert income_entry.recurring_income_id == test_recurring_income_with_category.id

    # Verify date components
    assert income_entry.date.year == now.year
    assert income_entry.date.month == now.month
    assert income_entry.date.day == test_recurring_income_with_category.day_of_month

    # Verify datetime is naive (no timezone)
    assert income_entry.date.tzinfo is None


async def test_create_income_from_recurring_future_date(
    db_session: AsyncSession, test_recurring_income_with_category: RecurringIncome
):
    """Test creating an income entry for a future date."""
    service = RecurringIncomeService(db_session)

    # Test for future month
    now = naive_utc_now()
    future_month = (now.month % 12) + 1
    future_year = now.year + (1 if future_month < now.month else 0)

    income_entry = service.create_income_from_recurring(
        test_recurring_income_with_category, future_month, future_year
    )

    # Verify date components
    assert income_entry.date.year == future_year
    assert income_entry.date.month == future_month
    assert income_entry.date.day == test_recurring_income_with_category.day_of_month


async def test_create_income_from_recurring_without_category(
    db_session: AsyncSession, test_checking_account: Account
):
    """Test creating an income entry without a category."""
    # Create a recurring income without category
    recurring_income = RecurringIncome(
        source="Misc Income",
        amount=Decimal("500.00"),
        day_of_month=1,
        account_id=test_checking_account.id,
        category_id=None,
        auto_deposit=False,
        active=True,
    )
    db_session.add(recurring_income)
    await db_session.commit()
    await db_session.refresh(recurring_income)

    service = RecurringIncomeService(db_session)
    income_entry = service.create_income_from_recurring(
        recurring_income, naive_utc_now().month, naive_utc_now().year
    )

    assert income_entry.category_id is None
    assert income_entry.category is None


async def test_integration_with_generate_income(
    db_session: AsyncSession, test_recurring_income_with_category: RecurringIncome
):
    """
    Test that the generate_income method properly uses
    create_income_from_recurring instead of the model method.
    """
    service = RecurringIncomeService(db_session)

    # Get current date components
    now = naive_utc_now()
    next_month = (now.month % 12) + 1
    next_year = now.year + (1 if next_month < now.month else 0)

    # Create request for next month to avoid conflicts with existing entries
    request = GenerateIncomeRequest(month=next_month, year=next_year)

    # Generate income entries
    results = await service.generate_income(request)

    # Verify results
    assert len(results) == 1

    generated = results[0]
    assert isinstance(generated, Income)
    assert generated.source == test_recurring_income_with_category.source
    assert generated.amount == test_recurring_income_with_category.amount
    assert generated.account_id == test_recurring_income_with_category.account_id
    assert generated.recurring is True
    assert generated.recurring_income_id == test_recurring_income_with_category.id

    # Verify date components
    assert generated.date.year == next_year
    assert generated.date.month == next_month
    assert generated.date.day == test_recurring_income_with_category.day_of_month

    # Test that duplicate entries are not created
    new_results = await service.generate_income(request)
    assert len(new_results) == 0
