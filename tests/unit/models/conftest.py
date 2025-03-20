from datetime import timedelta
from decimal import Decimal
from uuid import uuid4

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.base_model import naive_utc_from_date, naive_utc_now
from src.models.cashflow import CashflowForecast
from src.models.categories import Category
from src.models.income import Income
from src.models.income_categories import IncomeCategory
from src.models.liabilities import Liability
from src.models.recurring_bills import RecurringBill
from src.models.recurring_income import RecurringIncome

pytestmark = pytest.mark.asyncio


@pytest.fixture(scope="function")
async def test_checking_account(db_session: AsyncSession) -> Account:
    checking_account = Account(
        name="Test Checking Account",
        type="checking",
        available_balance=Decimal("1000.00"),
        created_at=naive_utc_now(),
        updated_at=naive_utc_now(),
    )
    db_session.add(checking_account)
    await db_session.commit()
    await db_session.refresh(checking_account)
    return checking_account


@pytest.fixture(scope="function")
async def test_credit_account(db_session: AsyncSession) -> Account:
    credit_account = Account(
        name="Test Credit Card",
        type="credit",
        available_balance=Decimal("-500.00"),
        total_limit=Decimal("2000.00"),
        created_at=naive_utc_now(),
        updated_at=naive_utc_now(),
    )
    db_session.add(credit_account)
    await db_session.commit()
    await db_session.refresh(credit_account)
    return credit_account


@pytest.fixture(scope="function")
async def test_income_record(
    db_session: AsyncSession, test_checking_account: Account
) -> Income:
    """Create a test income record"""
    income = Income(
        date=naive_utc_now(),
        source="Salary",
        amount=Decimal("2000.00"),
        deposited=False,
        account=test_checking_account,
        # Set undeposited_amount directly since calculate_undeposited() was moved to service
        undeposited_amount=Decimal("2000.00"),  # Same as amount when not deposited
    )
    db_session.add(income)
    await db_session.commit()
    await db_session.refresh(income)
    return income


@pytest.fixture(scope="function")
async def test_cashflow_forecast(db_session: AsyncSession) -> CashflowForecast:
    """Create a test cashflow forecast instance"""
    cashflow_forecast = CashflowForecast(
        forecast_date=naive_utc_now(),
        total_bills=Decimal("1000.00"),
        total_income=Decimal("800.00"),
        balance=Decimal("-200.00"),
        forecast=Decimal("-200.00"),
        min_14_day=Decimal("-300.00"),
        min_30_day=Decimal("-400.00"),
        min_60_day=Decimal("-500.00"),
        min_90_day=Decimal("-600.00"),
        daily_deficit=Decimal("0"),
        yearly_deficit=Decimal("0"),
        required_income=Decimal("0"),
        hourly_rate_40=Decimal("0"),
        hourly_rate_30=Decimal("0"),
        hourly_rate_20=Decimal("0"),
    )

    db_session.add(cashflow_forecast)
    await db_session.commit()
    await db_session.refresh(cashflow_forecast)

    return cashflow_forecast


@pytest.fixture(scope="function")
async def test_category(db_session: AsyncSession) -> Category:
    category = Category(
        name="Utilities",
        description="Monthly utility bills",
        created_at=naive_utc_now(),
        updated_at=naive_utc_now(),
    )

    db_session.add(category)
    await db_session.flush()
    await db_session.refresh(category)

    return category


@pytest.fixture(scope="function")
async def test_recurring_category(db_session: AsyncSession) -> Category:
    """Create a test category for recurring bills"""
    recurring_category = Category(
        name="Recurring",
        description="Recurring monthly bills",
        created_at=naive_utc_now(),
        updated_at=naive_utc_now(),
    )
    db_session.add(recurring_category)
    await db_session.flush()
    await db_session.refresh(recurring_category)
    return recurring_category


@pytest.fixture(scope="function")
async def test_recurring_bill(
    db_session: AsyncSession,
    test_checking_account: Account,
    test_recurring_category: Category,
) -> RecurringBill:
    """Create a test recurring bill instance"""
    bill = RecurringBill(
        bill_name="Netflix",
        amount=Decimal("19.99"),
        day_of_month=15,
        account=test_checking_account,
        category=test_recurring_category,
        auto_pay=True,
        active=True,
        created_at=naive_utc_now(),
        updated_at=naive_utc_now(),
    )
    db_session.add(bill)
    await db_session.flush()
    await db_session.refresh(bill)
    return bill


@pytest.fixture(scope="function")
async def test_income_category(db_session: AsyncSession) -> IncomeCategory:
    category = IncomeCategory(name="Test Category")
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


@pytest.fixture(scope="function")
async def test_recurring_income(
    db_session: AsyncSession,
    test_checking_account: Account,
    test_income_category: IncomeCategory,
) -> RecurringIncome:
    recurring_income = RecurringIncome(
        source="Test Income",
        amount=Decimal("1000.00"),
        day_of_month=15,
        account_id=test_checking_account.id,
        category_id=test_income_category.id,
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
async def test_liability(
    db_session: AsyncSession, test_checking_account: Account, test_category: Category
) -> Liability:
    """Create a basic bill for testing"""
    # Set due_date to 15 days from now for auto-pay testing
    future_date = naive_utc_now() + timedelta(days=15)
    naive_future_date = naive_utc_from_date(
        future_date.year, future_date.month, future_date.day
    )

    liability = Liability(
        name="Test Bill",
        amount=Decimal("100.00"),
        due_date=naive_future_date,
        category_id=test_category.id,
        recurring=False,
        primary_account_id=test_checking_account.id,
        auto_pay=False,
        auto_pay_enabled=False,
        paid=False,
        created_at=naive_utc_now(),
        updated_at=naive_utc_now(),
    )

    db_session.add(liability)
    await db_session.flush()
    await db_session.refresh(liability)  # Ensure we have latest data

    return liability
