import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.income_categories import IncomeCategory


@pytest_asyncio.fixture
async def test_income_category(db_session: AsyncSession) -> IncomeCategory:
    """
    Create a test income category.

    Args:
        db_session: The database session to use for creating the income category.

    Returns:
        IncomeCategory: A test income category instance.
    """
    income_category = IncomeCategory(name="Test Category")
    db_session.add(income_category)
    await db_session.flush()
    await db_session.refresh(income_category)
    return income_category
