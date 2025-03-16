import pytest
from datetime import datetime
from sqlalchemy import select, func
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.categories import Category
from src.models.liabilities import Liability
from src.models.base_model import naive_utc_from_date, naive_utc_now

pytestmark = pytest.mark.asyncio

async def test_bills_relationship(
    db_session: AsyncSession,
    test_category: Category
):
    """Test the relationship between Category and Liability"""
    # Create a bill in the category
    bill = Liability(
        name="Test Bill",
        amount=100.00,
        due_date=naive_utc_from_date(2025, 2, 15),
        category_id=test_category.id,
        primary_account_id=1
    )
    db_session.add(bill)
    await db_session.commit()
    
    # Refresh category to load bills relationship
    await db_session.refresh(test_category, ['bills'])
    
    assert len(test_category.bills) == 1
    assert test_category.bills[0].name == "Test Bill"

async def test_unique_name_constraint(db_session: AsyncSession):
    """Test that category names must be unique"""
    # Create first category
    category1 = Category(name="Unique Name")
    db_session.add(category1)
    await db_session.commit()
    
    # Try to create second category with same name
    category2 = Category(name="Unique Name")
    db_session.add(category2)
    
    with pytest.raises(IntegrityError):
        await db_session.commit()
    await db_session.rollback()

# Note: is_ancestor_of_none test has been removed as the method is now in CategoryService

async def test_lazy_loading_config(
    db_session: AsyncSession,
    test_category: Category
):
    """Test lazy loading configuration of relationships"""
    # Create child category
    child = Category(
        name="Child Category",
        parent_id=test_category.id
    )
    db_session.add(child)
    await db_session.commit()
    
    # Get fresh instances with specific relationship loading
    await db_session.refresh(test_category, ['children'])
    await db_session.refresh(child, ['parent'])
    
    # Verify relationships are loaded
    assert test_category.children[0].name == "Child Category"
    assert child.parent.name == test_category.name


async def test_datetime_handling(db_session: AsyncSession):
    """Test proper datetime handling in Category model"""
    # Create category with explicit datetime values
    category = Category(
        name="Test Category",
        description="Test Description",
        created_at=naive_utc_from_date(2025, 3, 15),
        updated_at=naive_utc_from_date(2025, 3, 15)
    )

    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    # Verify all datetime fields are naive (no tzinfo)
    assert category.created_at.tzinfo is None
    assert category.updated_at.tzinfo is None

    # Verify created_at components
    assert category.created_at.year == 2025
    assert category.created_at.month == 3
    assert category.created_at.day == 15
    assert category.created_at.hour == 0
    assert category.created_at.minute == 0
    assert category.created_at.second == 0

    # Verify updated_at components
    assert category.updated_at.year == 2025
    assert category.updated_at.month == 3
    assert category.updated_at.day == 15
    assert category.updated_at.hour == 0
    assert category.updated_at.minute == 0
    assert category.updated_at.second == 0

async def test_default_datetime_handling(db_session: AsyncSession):
    """Test default datetime values are properly set"""
    category = Category(
        name="Test Category",
        description="Test Description"
    )

    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    # Verify created_at and updated_at are set and naive
    assert category.created_at is not None
    assert category.updated_at is not None
    assert category.created_at.tzinfo is None
    assert category.updated_at.tzinfo is None

async def test_create_basic_category(db_session: AsyncSession):
    """Test creating a basic category"""
    category = Category(
        name="Test Category",
        description="Test Description"
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)

    assert category.id is not None
    assert category.name == "Test Category"
    assert category.description == "Test Description"
    assert category.parent_id is None
    assert isinstance(category.created_at, datetime)
    assert isinstance(category.updated_at, datetime)
    assert category.created_at.tzinfo is None
    assert category.updated_at.tzinfo is None

async def test_create_hierarchical_categories(db_session: AsyncSession):
    """Test creating categories with parent-child relationships"""
    parent = Category(
        name="Parent Category",
        description="Parent Description"
    )
    db_session.add(parent)
    await db_session.commit()

    child = Category(
        name="Child Category",
        description="Child Description",
        parent_id=parent.id
    )
    db_session.add(child)
    await db_session.commit()

    # Fetch fresh instances to ensure relationships are loaded
    stmt = select(Category).where(Category.id == parent.id).options(
        selectinload(Category.children)
    )
    result = await db_session.execute(stmt)
    parent = result.unique().scalar_one()

    stmt = select(Category).where(Category.id == child.id).options(
        selectinload(Category.parent)
    )
    result = await db_session.execute(stmt)
    child = result.unique().scalar_one()

    assert child.parent_id == parent.id
    assert child.parent.name == "Parent Category"
    assert len(parent.children) == 1
    assert parent.children[0].name == "Child Category"
    assert child.created_at.tzinfo is None
    assert child.updated_at.tzinfo is None
    assert parent.created_at.tzinfo is None
    assert parent.updated_at.tzinfo is None

async def test_category_hierarchical_relationships(db_session: AsyncSession):
    """Test the hierarchical relationships between categories"""
    # Create the category hierarchy
    grandparent = Category(name="Grandparent")
    db_session.add(grandparent)
    await db_session.commit()

    parent = Category(
        name="Parent",
        parent_id=grandparent.id
    )
    db_session.add(parent)
    await db_session.commit()

    child = Category(
        name="Child",
        parent_id=parent.id
    )
    db_session.add(child)
    await db_session.commit()

    # Fetch fresh instances
    stmt = select(Category).where(Category.id == child.id).options(
        selectinload(Category.parent.of_type(Category))
    )
    result = await db_session.execute(stmt)
    child = result.unique().scalar_one()

    # Test relationship navigation
    assert child.parent_id == parent.id
    assert child.parent.parent_id == grandparent.id
    assert child.parent.parent.parent_id is None
    
    # Verify datetime fields remain naive
    assert child.created_at.tzinfo is None
    assert child.updated_at.tzinfo is None
    assert child.parent.created_at.tzinfo is None
    assert child.parent.updated_at.tzinfo is None

async def test_category_without_parent(db_session: AsyncSession):
    """Test a category without a parent"""
    category = Category(name="Solo Category")
    db_session.add(category)
    await db_session.commit()
    
    assert category.parent_id is None
    assert category.parent is None

# Note: is_ancestor_of test has been removed as the method is now in CategoryService

async def test_category_str_representation(db_session: AsyncSession):
    """Test the string representation of Category"""
    category = Category(
        name="Test Category",
        description="Test Description"
    )
    db_session.add(category)
    await db_session.commit()

    expected = f"<Category(id={category.id}, name='Test Category', parent_id=None)>"
    assert str(category) == expected
    assert category.created_at.tzinfo is None
    assert category.updated_at.tzinfo is None

async def test_category_relationships_cascade(db_session: AsyncSession):
    """Test that deleting a parent category cascades to children"""
    parent = Category(name="Parent")
    db_session.add(parent)
    await db_session.commit()

    child1 = Category(name="Child 1", parent_id=parent.id)
    child2 = Category(name="Child 2", parent_id=parent.id)
    db_session.add_all([child1, child2])
    await db_session.commit()

    # Delete parent and verify children are also deleted
    await db_session.delete(parent)
    await db_session.commit()

    # Verify children no longer exist
    stmt = select(Category).where(Category.parent_id == parent.id)
    result = await db_session.execute(stmt)
    children = result.scalars().all()
    assert len(children) == 0
