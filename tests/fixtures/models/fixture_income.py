from datetime import datetime, timezone
from decimal import Decimal
from typing import List

import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.income import Income


@pytest_asyncio.fixture
async def test_income(
    db_session: AsyncSession,
    test_checking_account,
) -> Income:
    """Fixture to create a test income entry."""
    # Create a naive datetime for DB storage
    income_date = datetime.now(timezone.utc).replace(tzinfo=None)

    # Create model instance directly
    income = Income(
        source="Monthly Salary",
        amount=Decimal("3000.00"),
        account_id=test_checking_account.id,
        date=income_date,
        deposited=False,
    )

    # Add to session manually
    db_session.add(income)
    await db_session.flush()
    await db_session.refresh(income)

    return income


@pytest_asyncio.fixture
async def test_additional_income(
    db_session: AsyncSession,
    test_second_account,
) -> Income:
    """Fixture to create a second test income entry."""
    # Create a naive datetime for DB storage
    income_date = datetime.now(timezone.utc).replace(tzinfo=None)

    # Create model instance directly
    income = Income(
        source="Freelance Payment",
        amount=Decimal("1500.00"),
        account_id=test_second_account.id,
        date=income_date,
        deposited=False,
    )

    # Add to session manually
    db_session.add(income)
    await db_session.flush()
    await db_session.refresh(income)

    return income


@pytest_asyncio.fixture
async def test_income_entries(
    db_session: AsyncSession,
    test_multiple_categories,
) -> List[Income]:
    """Fixture to create test income entries associated with categories."""
    # Get category IDs for reference
    salary_category_id = test_multiple_categories[0].id
    freelance_category_id = test_multiple_categories[1].id
    investments_category_id = test_multiple_categories[2].id

    # Create income data with various attributes
    income_data = [
        {
            "source": "Monthly Salary",
            "amount": Decimal("3000.00"),
            "account_id": 1,  # Using a default account ID
            "category_id": salary_category_id,
            "deposited": True,
        },
        {
            "source": "Bonus",
            "amount": Decimal("1000.00"),
            "account_id": 1,
            "category_id": salary_category_id,
            "deposited": True,
        },
        {
            "source": "Website Project",
            "amount": Decimal("800.00"),
            "account_id": 1,
            "category_id": freelance_category_id,
            "deposited": False,
        },
        {
            "source": "Logo Design",
            "amount": Decimal("350.00"),
            "account_id": 1,
            "category_id": freelance_category_id,
            "deposited": True,
        },
        {
            "source": "Stock Dividends",
            "amount": Decimal("420.00"),
            "account_id": 1,
            "category_id": investments_category_id,
            "deposited": False,
        },
    ]

    # Create a naive datetime for DB storage
    income_date = datetime.now(timezone.utc).replace(tzinfo=None)

    # Create the income entries using direct model instantiation
    created_incomes = []
    for data in income_data:
        # Create model instance directly
        income = Income(
            source=data["source"],
            amount=data["amount"],
            account_id=data["account_id"],
            category_id=data["category_id"],
            date=income_date,
            deposited=data["deposited"],
        )

        # Add to session manually
        db_session.add(income)
        created_incomes.append(income)

    # Flush to get IDs and establish database rows
    await db_session.flush()

    # Refresh all entries to make sure they reflect what's in the database
    for income in created_incomes:
        await db_session.refresh(income)

    return created_incomes
