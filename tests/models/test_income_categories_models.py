import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.income import Income
from src.models.income_categories import IncomeCategory
from src.models.base_model import naive_utc_from_date

pytestmark = pytest.mark.asyncio


async def test_datetime_handling(db_session: AsyncSession):
    """Test proper datetime handling in IncomeCategory model"""
    # Create income_category with explicit datetime values
    income_category = IncomeCategory(
        name="Salary",
        description="Monthly salary income",
        created_at=naive_utc_from_date(2025, 3, 15),
        updated_at=naive_utc_from_date(2025, 3, 15)
    )

    db_session.add(income_category)
    await db_session.commit()
    await db_session.refresh(income_category)

    # Verify all datetime fields are naive (no tzinfo)
    assert income_category.created_at.tzinfo is None
    assert income_category.updated_at.tzinfo is None

    # Verify created_at components
    assert income_category.created_at.year == 2025
    assert income_category.created_at.month == 3
    assert income_category.created_at.day == 15
    assert income_category.created_at.hour == 0
    assert income_category.created_at.minute == 0
    assert income_category.created_at.second == 0

    # Verify updated_at components
    assert income_category.updated_at.year == 2025
    assert income_category.updated_at.month == 3
    assert income_category.updated_at.day == 15
    assert income_category.updated_at.hour == 0
    assert income_category.updated_at.minute == 0
    assert income_category.updated_at.second == 0

async def test_default_datetime_handling(db_session: AsyncSession):
    """Test default datetime values are properly set"""
    income_category = IncomeCategory(
        name="Salary",
        description="Monthly salary income"
    )

    db_session.add(income_category)
    await db_session.commit()
    await db_session.refresh(income_category)

    # Verify created_at and updated_at are set and naive
    assert income_category.created_at is not None
    assert income_category.updated_at is not None
    assert income_category.created_at.tzinfo is None
    assert income_category.updated_at.tzinfo is None

async def test_relationship_datetime_handling(
    db_session: AsyncSession,
    test_income_record: Income
):
    """Test datetime handling with relationships"""
    income_category = IncomeCategory(
        name="Salary",
        description="Monthly salary income"
    )
    db_session.add(income_category)
    await db_session.commit()
    await db_session.refresh(income_category)

    test_income_record.income_category = income_category
    await db_session.commit()
    await db_session.refresh(test_income_record)

    # Verify datetime fields remain naive after refresh
    assert income_category.created_at.tzinfo is None
    assert income_category.updated_at.tzinfo is None
