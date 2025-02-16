from datetime import datetime
from decimal import Decimal
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.recurring_income import RecurringIncome
from src.models.income import Income
from src.models.accounts import Account
from src.models.income_categories import IncomeCategory

pytestmark = pytest.mark.asyncio

@pytest.fixture(scope="function")
async def test_account(db_session: AsyncSession) -> Account:
    account = Account(
        name="Test Account",
        type="checking",
        available_balance=Decimal("1000.00"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account

@pytest.fixture
async def test_category(db_session: AsyncSession) -> IncomeCategory:
    category = IncomeCategory(name="Test Category")
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category

@pytest.fixture
async def test_recurring_income(
    db_session: AsyncSession,
    test_account: Account,
    test_category: IncomeCategory
) -> RecurringIncome:
    recurring_income = RecurringIncome(
        source="Test Income",
        amount=Decimal("1000.00"),
        day_of_month=15,
        account_id=test_account.id,
        category_id=test_category.id,
        auto_deposit=False,
        active=True,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(recurring_income)
    await db_session.commit()
    await db_session.refresh(recurring_income)
    return recurring_income

async def test_create_recurring_income(
    db_session: AsyncSession,
    test_account: Account,
    test_category: IncomeCategory
):
    """Test creating a recurring income model."""
    recurring_income = RecurringIncome(
        source="Test Income",
        amount=Decimal("1000.00"),
        day_of_month=15,
        account_id=test_account.id,
        category_id=test_category.id,
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
    assert recurring_income.account_id == test_account.id
    assert recurring_income.category_id == test_category.id
    assert recurring_income.auto_deposit is False
    assert recurring_income.active is True

async def test_create_income_entry(
    test_recurring_income: RecurringIncome
):
    """Test creating an income entry from recurring income."""
    # Test creating entry for current month
    now = datetime.utcnow()
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
    now = datetime.utcnow()
    future_month = (now.month % 12) + 1
    future_year = now.year + (1 if future_month < now.month else 0)

    income_entry = test_recurring_income.create_income_entry(future_month, future_year)

    assert isinstance(income_entry, Income)
    assert income_entry.date.month == future_month
    assert income_entry.date.year == future_year
    assert income_entry.date.day == test_recurring_income.day_of_month

async def test_create_income_entry_with_category(
    test_recurring_income: RecurringIncome,
    test_category: IncomeCategory
):
    """Test creating an income entry with category relationship."""
    now = datetime.utcnow()
    income_entry = test_recurring_income.create_income_entry(now.month, now.year)

    assert income_entry.category_id == test_category.id
    assert income_entry.category == test_category

async def test_create_income_entry_with_auto_deposit(
    db_session: AsyncSession,
    test_account: Account,
    test_category: IncomeCategory
):
    """Test creating an income entry with auto deposit enabled."""
    recurring_income = RecurringIncome(
        source="Auto Deposit Income",
        amount=Decimal("1000.00"),
        day_of_month=15,
        account_id=test_account.id,
        category_id=test_category.id,
        auto_deposit=True,
        active=True
    )
    db_session.add(recurring_income)
    await db_session.commit()

    now = datetime.utcnow()
    income_entry = recurring_income.create_income_entry(now.month, now.year)

    assert income_entry.deposited is True
