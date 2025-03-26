from decimal import Decimal
from typing import List

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.recurring_bills import RecurringBill
from src.models.recurring_income import RecurringIncome


@pytest_asyncio.fixture
async def test_recurring_bill(
    db_session: AsyncSession,
    test_checking_account,
    test_category,
) -> RecurringBill:
    """Create a test recurring bill for use in tests."""
    # Create model instance directly
    bill = RecurringBill(
        bill_name="Test Recurring Bill",
        amount=Decimal("50.00"),
        day_of_month=15,
        account_id=test_checking_account.id,
        category_id=test_category.id,
        auto_pay=True,
        active=True,  # Default to active
    )
    
    # Add to session manually
    db_session.add(bill)
    await db_session.flush()
    await db_session.refresh(bill)
    
    return bill


@pytest_asyncio.fixture
async def test_multiple_recurring_bills(
    db_session: AsyncSession,
    test_checking_account,
    test_category,
) -> List[RecurringBill]:
    """Create multiple recurring bills for testing."""
    # Setup bill configurations
    bills_config = [
        ("Active Bill 1", 1, True, True),
        ("Active Bill 2", 15, True, True),
        ("Inactive Bill", 20, False, True),
        ("Day 10 Bill 1", 10, True, False),
        ("Day 10 Bill 2", 10, True, False),
        ("Day 15 Bill", 15, True, False),
    ]

    bills = []
    for name, day, active, auto_pay in bills_config:
        # Create model instance directly
        bill = RecurringBill(
            bill_name=name,
            amount=Decimal("100.00"),
            day_of_month=day,
            account_id=test_checking_account.id,
            category_id=test_category.id,
            auto_pay=auto_pay,
            active=active,  # Set active status directly
        )
        
        # Add to session manually
        db_session.add(bill)
        bills.append(bill)
    
    # Flush to get IDs and establish database rows
    await db_session.flush()
    
    # Refresh all entries to make sure they reflect what's in the database
    for bill in bills:
        await db_session.refresh(bill)
        
    return bills


@pytest_asyncio.fixture
async def test_recurring_income(
    db_session: AsyncSession,
    test_checking_account,
    test_income_category,
) -> RecurringIncome:
    """Create a test recurring income entry for use in tests."""
    # Create model instance directly
    income = RecurringIncome(
        source="Monthly Salary",
        amount=Decimal("3000.00"),
        account_id=test_checking_account.id,
        category_id=test_income_category.id,
        day_of_month=15,
        active=True,
    )
    
    # Add to session manually
    db_session.add(income)
    await db_session.flush()
    await db_session.refresh(income)
    
    return income


@pytest_asyncio.fixture
async def test_multiple_recurring_incomes(
    db_session: AsyncSession,
    test_checking_account,
    test_second_account,
    test_income_category,
) -> List[RecurringIncome]:
    """Create multiple recurring income entries for testing."""
    # Different recurring income configurations
    income_configs = [
        {
            "source": "Primary Job Salary",
            "amount": Decimal("4000.00"),
            "account_id": test_checking_account.id,
            "category_id": test_income_category.id,
            "day_of_month": 1,
            "active": True,
        },
        {
            "source": "Part-time Job",
            "amount": Decimal("1200.00"),
            "account_id": test_second_account.id,
            "category_id": test_income_category.id,
            "day_of_month": 15,
            "active": True,
        },
        {
            "source": "Rental Income",
            "amount": Decimal("800.00"),
            "account_id": test_checking_account.id,
            "category_id": test_income_category.id,
            "day_of_month": 5,
            "active": True,
        },
        {
            "source": "Previous Freelance Contract",
            "amount": Decimal("1500.00"),
            "account_id": test_second_account.id,
            "category_id": test_income_category.id,
            "day_of_month": 20,
            "active": False,  # Inactive income
        },
    ]

    incomes = []
    for config in income_configs:
        # Create model instance directly
        income = RecurringIncome(
            source=config["source"],
            amount=config["amount"],
            account_id=config["account_id"],
            category_id=config["category_id"],
            day_of_month=config["day_of_month"],
            active=config["active"],
        )
        
        # Add to session manually
        db_session.add(income)
        incomes.append(income)
    
    # Flush to get IDs and establish database rows
    await db_session.flush()
    
    # Refresh all entries to make sure they reflect what's in the database
    for income in incomes:
        await db_session.refresh(income)
        
    return incomes
