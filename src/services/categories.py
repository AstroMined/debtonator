from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError

from ..models.categories import Category
from ..schemas.categories import CategoryCreate, CategoryUpdate

class CategoryError(Exception):
    """Base exception for category-related errors"""
    pass

class CategoryService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def validate_parent_category(self, parent_id: int, category_id: Optional[int] = None) -> Category:
        """Validate parent category exists and prevent circular references"""
        if parent_id is None:
            return None
            
        parent = await self.get_category(parent_id)
        if not parent:
            raise CategoryError(f"Parent category with ID {parent_id} does not exist")
            
        # For existing categories, prevent circular references
        if category_id:
            if parent_id == category_id:
                raise CategoryError("Category cannot be its own parent")
            category = await self.get_category(category_id)
            if category:
                # Check if the parent is actually a descendant of the category
                current = parent
                while current and current.parent_id:
                    if current.parent_id == category_id:
                        raise CategoryError("Circular reference detected in category hierarchy")
                    current = await self.get_category(current.parent_id)
                
        return parent

    async def create_category(self, category: CategoryCreate) -> Category:
        """Create a new category"""
        if category.parent_id:
            await self.validate_parent_category(category.parent_id)
            
        db_category = Category(
            name=category.name,
            description=category.description,
            parent_id=category.parent_id
        )
        try:
            self.db.add(db_category)
            await self.db.commit()
            await self.db.refresh(db_category)
            return db_category
        except IntegrityError:
            await self.db.rollback()
            raise CategoryError(f"Category with name '{category.name}' already exists")

    async def get_category(self, category_id: int) -> Optional[Category]:
        """Get a category by ID"""
        query = select(Category).where(Category.id == category_id)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_category_by_name(self, name: str) -> Optional[Category]:
        """Get a category by name"""
        query = select(Category).where(Category.name == name)
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_categories(self, skip: int = 0, limit: int = 100) -> List[Category]:
        """Get a list of categories with pagination"""
        query = select(Category).offset(skip).limit(limit)
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def update_category(self, category_id: int, category_update: CategoryUpdate) -> Optional[Category]:
        """Update a category"""
        db_category = await self.get_category(category_id)
        if not db_category:
            return None

        update_data = category_update.model_dump(exclude_unset=True)
        
        if 'parent_id' in update_data:
            await self.validate_parent_category(update_data['parent_id'], category_id)

        try:
            for field, value in update_data.items():
                setattr(db_category, field, value)
            await self.db.commit()
            await self.db.refresh(db_category)
            return db_category
        except IntegrityError:
            await self.db.rollback()
            raise CategoryError(f"Category name '{category_update.name}' already exists")

    async def delete_category(self, category_id: int) -> bool:
        """Delete a category"""
        # Get category with bills and children loaded
        query = (
            select(Category)
            .where(Category.id == category_id)
            .options(
                selectinload(Category.bills),
                selectinload(Category.children)
            )
        )
        result = await self.db.execute(query)
        db_category = result.scalar_one_or_none()
        
        if not db_category:
            return False

        if db_category.bills:
            raise CategoryError("Cannot delete category that has bills assigned to it")
            
        if db_category.children:
            raise CategoryError("Cannot delete category that has child categories")

        await self.db.delete(db_category)
        await self.db.commit()
        await self.db.flush()
        return True

    async def get_category_with_children(self, category_id: int) -> Optional[Category]:
        """Get a category with its child categories"""
        query = (
            select(Category)
            .where(Category.id == category_id)
            .options(selectinload(Category.children))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_category_with_parent(self, category_id: int) -> Optional[Category]:
        """Get a category with its parent category"""
        query = (
            select(Category)
            .where(Category.id == category_id)
            .options(selectinload(Category.parent))
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()

    async def get_root_categories(self) -> List[Category]:
        """Get all top-level categories (categories without parents)"""
        query = (
            select(Category)
            .where(Category.parent_id.is_(None))
            .options(selectinload(Category.children))
        )
        result = await self.db.execute(query)
        return list(result.scalars().all())

    async def get_category_with_bills(self, category_id: int) -> Optional[Category]:
        """Get a category with its associated bills"""
        query = (
            select(Category)
            .where(Category.id == category_id)
            .options(
                selectinload(Category.bills),
                selectinload(Category.children)
            )
        )
        result = await self.db.execute(query)
        return result.scalar_one_or_none()
