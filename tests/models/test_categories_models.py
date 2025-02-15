import pytest
from datetime import datetime
from zoneinfo import ZoneInfo
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.categories import Category

pytestmark = pytest.mark.asyncio

class TestCategory:
    async def test_create_basic_category(self, db_session: AsyncSession):
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

    async def test_create_hierarchical_categories(self, db_session: AsyncSession):
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

    async def test_category_full_path(self, db_session: AsyncSession):
        """Test the full_path property for nested categories"""
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

        assert child.full_path == "Grandparent > Parent > Child"
        assert child.parent.full_path == "Grandparent > Parent"
        assert child.parent.parent.full_path == "Grandparent"

    async def test_is_ancestor_of(self, db_session: AsyncSession):
        """Test the is_ancestor_of method"""
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
        stmt = select(Category).where(Category.id == grandparent.id).options(
            selectinload(Category.children)
        )
        result = await db_session.execute(stmt)
        grandparent = result.unique().scalar_one()

        stmt = select(Category).where(Category.id == parent.id).options(
            selectinload(Category.parent),
            selectinload(Category.children)
        )
        result = await db_session.execute(stmt)
        parent = result.unique().scalar_one()

        stmt = select(Category).where(Category.id == child.id).options(
            selectinload(Category.parent.of_type(Category))
        )
        result = await db_session.execute(stmt)
        child = result.unique().scalar_one()

        # Test ancestor relationships
        assert await grandparent.is_ancestor_of(parent)
        assert await grandparent.is_ancestor_of(child)
        assert await parent.is_ancestor_of(child)
        
        # Test non-ancestor relationships
        assert not await child.is_ancestor_of(parent)
        assert not await child.is_ancestor_of(grandparent)
        assert not await parent.is_ancestor_of(grandparent)

    async def test_category_str_representation(self, db_session: AsyncSession):
        """Test the string representation of Category"""
        category = Category(
            name="Test Category",
            description="Test Description"
        )
        db_session.add(category)
        await db_session.commit()

        expected = f"<Category(id={category.id}, name='Test Category', parent_id=None)>"
        assert str(category) == expected

    async def test_category_relationships_cascade(self, db_session: AsyncSession):
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
        stmt = select(func.count(Category.id)).select_from(Category).where(Category.parent_id == parent.id)
        result = await db_session.execute(stmt)
        count = result.scalar()
        assert count == 0

    async def test_get_parent_helper(self, db_session: AsyncSession):
        """Test the _get_parent helper method"""
        parent = Category(name="Parent")
        db_session.add(parent)
        await db_session.commit()

        child = Category(name="Child", parent_id=parent.id)
        db_session.add(child)
        await db_session.commit()

        # Fetch fresh instances
        stmt = select(Category).where(Category.id == child.id).options(
            selectinload(Category.parent)
        )
        result = await db_session.execute(stmt)
        child = result.unique().scalar_one()

        # Test getting parent
        retrieved_parent = await Category._get_parent(child)
        assert retrieved_parent is not None
        assert retrieved_parent.id == parent.id
        assert retrieved_parent.name == "Parent"

        # Test with category having no parent
        stmt = select(Category).where(Category.id == parent.id).options(
            selectinload(Category.parent)
        )
        result = await db_session.execute(stmt)
        parent = result.unique().scalar_one()
        
        no_parent = await Category._get_parent(parent)
        assert no_parent is None
