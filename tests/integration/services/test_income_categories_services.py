from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.schemas.income_categories import (IncomeCategoryCreate,
                                           IncomeCategoryUpdate)
from src.services.income_categories import IncomeCategoryService


@pytest.fixture
async def income_category_service(db_session: AsyncSession):
    return IncomeCategoryService(db_session)


@pytest.fixture
async def sample_category(
    income_category_service: IncomeCategoryService, db_session: AsyncSession
):
    category = IncomeCategoryCreate(
        name="Salary", description="Regular employment income"
    )
    return await income_category_service.create_category(category)


async def test_create_category(income_category_service: IncomeCategoryService):
    """Test creating a new income category"""
    category = IncomeCategoryCreate(
        name="Freelance", description="Income from freelance work"
    )
    db_category = await income_category_service.create_category(category)
    assert db_category.name == "Freelance"
    assert db_category.description == "Income from freelance work"


async def test_get_category(
    income_category_service: IncomeCategoryService, sample_category
):
    """Test retrieving a category by ID"""
    category = await income_category_service.get_category(sample_category.id)
    assert category is not None
    assert category.name == sample_category.name
    assert category.description == sample_category.description


async def test_get_categories(
    income_category_service: IncomeCategoryService, sample_category
):
    """Test retrieving all categories"""
    # Create another category
    await income_category_service.create_category(
        IncomeCategoryCreate(name="Investments", description="Investment returns")
    )

    categories = await income_category_service.get_categories()
    assert len(categories) == 2
    assert any(c.name == "Salary" for c in categories)
    assert any(c.name == "Investments" for c in categories)


async def test_update_category(
    income_category_service: IncomeCategoryService, sample_category
):
    """Test updating a category"""
    update_data = IncomeCategoryUpdate(
        name="Updated Salary", description="Updated description"
    )
    updated = await income_category_service.update_category(
        sample_category.id, update_data
    )
    assert updated is not None
    assert updated.name == "Updated Salary"
    assert updated.description == "Updated description"


async def test_delete_category(
    income_category_service: IncomeCategoryService, sample_category
):
    """Test deleting a category"""
    result = await income_category_service.delete_category(sample_category.id)
    assert result is True

    # Verify category is deleted
    category = await income_category_service.get_category(sample_category.id)
    assert category is None


async def test_get_nonexistent_category(income_category_service: IncomeCategoryService):
    """Test retrieving a non-existent category"""
    category = await income_category_service.get_category(999)
    assert category is None


async def test_update_nonexistent_category(
    income_category_service: IncomeCategoryService,
):
    """Test updating a non-existent category"""
    update_data = IncomeCategoryUpdate(name="Test")
    updated = await income_category_service.update_category(999, update_data)
    assert updated is None


async def test_delete_nonexistent_category(
    income_category_service: IncomeCategoryService,
):
    """Test deleting a non-existent category"""
    result = await income_category_service.delete_category(999)
    assert result is False
