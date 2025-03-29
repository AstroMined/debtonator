import pytest
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.income import Income
from src.models.income_categories import IncomeCategory
from src.utils.datetime_utils import naive_utc_from_date

pytestmark = pytest.mark.asyncio


async def test_income_category_crud(db_session: AsyncSession):
    """Test basic CRUD operations for IncomeCategory model"""
    # Create
    income_category = IncomeCategory(name="Salary", description="Monthly salary income")
    db_session.add(income_category)
    await db_session.commit()

    # Read
    await db_session.refresh(income_category)
    assert income_category.id is not None
    assert income_category.name == "Salary"
    assert income_category.description == "Monthly salary income"

    # Update
    income_category.name = "Updated Salary"
    await db_session.commit()
    await db_session.refresh(income_category)
    assert income_category.name == "Updated Salary"

    # Test __repr__
    expected_repr = "<IncomeCategory Updated Salary>"
    assert repr(income_category) == expected_repr


async def test_unique_name_constraint(db_session: AsyncSession):
    """Test unique constraint on name field"""
    # Create first category
    first_category = IncomeCategory(name="Unique Name")
    db_session.add(first_category)
    await db_session.commit()

    # Try to create second category with same name
    second_category = IncomeCategory(name="Unique Name")
    db_session.add(second_category)

    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()


async def test_nullable_description(db_session: AsyncSession):
    """Test that description field is optional"""
    income_category = IncomeCategory(name="No Description")
    db_session.add(income_category)
    await db_session.commit()

    await db_session.refresh(income_category)
    assert income_category.description is None


async def test_datetime_handling(db_session: AsyncSession):
    """Test proper datetime handling in IncomeCategory model"""
    # Create income_category with explicit datetime values
    income_category = IncomeCategory(
        name="Salary",
        description="Monthly salary income",
        created_at=naive_utc_from_date(2025, 3, 15),
        updated_at=naive_utc_from_date(2025, 3, 15),
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
    income_category = IncomeCategory(name="Salary", description="Monthly salary income")

    db_session.add(income_category)
    await db_session.commit()
    await db_session.refresh(income_category)

    # Verify created_at and updated_at are set and naive
    assert income_category.created_at is not None
    assert income_category.updated_at is not None
    assert income_category.created_at.tzinfo is None
    assert income_category.updated_at.tzinfo is None


async def test_relationship_datetime_handling(
    db_session: AsyncSession, test_income_record: Income
):
    """Test datetime handling with relationships"""
    income_category = IncomeCategory(name="Salary", description="Monthly salary income")
    db_session.add(income_category)
    await db_session.commit()
    await db_session.refresh(income_category)

    test_income_record.income_category = income_category
    await db_session.commit()
    await db_session.refresh(test_income_record)

    # Verify datetime fields remain naive after refresh
    assert income_category.created_at.tzinfo is None
    assert income_category.updated_at.tzinfo is None
