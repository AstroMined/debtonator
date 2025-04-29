"""
Categories repository implementation.

This module provides a repository for Category model CRUD operations and specialized
category-related queries.
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.constants import (
    DEFAULT_CATEGORY_DESCRIPTION,
    DEFAULT_CATEGORY_ID,
    DEFAULT_CATEGORY_NAME,
)
from src.models.categories import Category
from src.models.liabilities import Liability
from src.repositories.base_repository import BaseRepository


class CategoryRepository(BaseRepository[Category, int]):
    """
    Repository for Category model operations.

    This repository handles CRUD operations for categories and provides specialized
    queries for category-related functionality.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session (AsyncSession): SQLAlchemy async session
        """
        super().__init__(session, Category)

    async def get_by_name(self, name: str) -> Optional[Category]:
        """
        Get category by name.

        Args:
            name (str): Category name to search for

        Returns:
            Optional[Category]: Category with matching name or None
        """
        result = await self.session.execute(
            select(Category).where(Category.name == name)
        )
        return result.scalars().first()

    async def get_default_category_id(self) -> int:
        """
        Get the default category ID, creating it if needed.

        Returns:
            int: Default category ID
        """
        # Try to get the default category
        default_category = await self.get(DEFAULT_CATEGORY_ID)

        # If it doesn't exist, create it
        if not default_category:
            default_category = await self.create(
                {
                    "id": DEFAULT_CATEGORY_ID,
                    "name": DEFAULT_CATEGORY_NAME,
                    "description": DEFAULT_CATEGORY_DESCRIPTION,
                    "system": True,
                }
            )
        elif not default_category.system:
            # Ensure the default category is marked as a system category
            await self.update(DEFAULT_CATEGORY_ID, {"system": True})

        return default_category.id

    async def update(self, id: int, values: Dict[str, Any]) -> Optional[Category]:
        """
        Update a category with protection for system categories.

        Args:
            id (int): Category ID
            values (Dict[str, Any]): Values to update

        Returns:
            Optional[Category]: Updated category or None if not found

        Raises:
            ValueError: If attempting to modify a system category
        """
        # Get the category to check if it's a system category
        category = await self.get(id)
        if category and (category.system or id == DEFAULT_CATEGORY_ID):
            raise ValueError(f"Cannot modify system category: {category.name}")

        # Proceed with normal update for non-system categories
        return await super().update(id, values)

    async def delete(self, id: int) -> bool:
        """
        Delete a category with protection for system categories.

        Args:
            id (int): Category ID

        Returns:
            bool: True if successfully deleted, False otherwise

        Raises:
            ValueError: If attempting to delete a system category
        """
        # Get the category to check if it's a system category
        category = await self.get(id)
        if category and (category.system or id == DEFAULT_CATEGORY_ID):
            raise ValueError(f"Cannot delete system category: {category.name}")

        # Proceed with normal delete for non-system categories
        return await super().delete(id)

    async def get_root_categories(self) -> List[Category]:
        """
        Get all root categories (categories without parents).

        Returns:
            List[Category]: List of root categories
        """
        result = await self.session.execute(
            select(Category).where(Category.parent_id.is_(None)).order_by(Category.name)
        )
        return result.scalars().unique().all()

    async def get_with_children(self, category_id: int) -> Optional[Category]:
        """
        Get category with its immediate children.

        Args:
            category_id (int): Category ID

        Returns:
            Optional[Category]: Category with loaded children or None
        """
        result = await self.session.execute(
            select(Category)
            .options(selectinload(Category.children))
            .where(Category.id == category_id)
        )
        return result.scalars().unique().first()

    async def get_with_parent(self, category_id: int) -> Optional[Category]:
        """
        Get category with its parent.

        Args:
            category_id (int): Category ID

        Returns:
            Optional[Category]: Category with loaded parent or None
        """
        result = await self.session.execute(
            select(Category)
            .options(joinedload(Category.parent))
            .where(Category.id == category_id)
        )
        return result.scalars().first()

    async def get_with_bills(self, category_id: int) -> Optional[Category]:
        """
        Get category with its bills.

        Args:
            category_id (int): Category ID

        Returns:
            Optional[Category]: Category with loaded bills or None
        """
        result = await self.session.execute(
            select(Category)
            .options(selectinload(Category.bills))
            .where(Category.id == category_id)
        )
        return result.scalars().unique().first()

    async def get_with_relationships(
        self,
        category_id: int,
        include_parent: bool = False,
        include_children: bool = False,
        include_bills: bool = False,
    ) -> Optional[Category]:
        """
        Get category with specified relationships loaded.

        Args:
            category_id (int): Category ID
            include_parent (bool): Load parent relationship
            include_children (bool): Load children relationship
            include_bills (bool): Load bills relationship

        Returns:
            Optional[Category]: Category with loaded relationships or None
        """
        # Create a query with conditional relationship loading
        query = select(Category).where(Category.id == category_id)

        # Add relationship loading options based on parameters
        if include_parent:
            query = query.options(joinedload(Category.parent))

        if include_children:
            query = query.options(selectinload(Category.children))

        if include_bills:
            query = query.options(selectinload(Category.bills))

        # Execute the query and return the result
        result = await self.session.execute(query)
        return result.scalars().unique().first()

    async def get_children(self, parent_id: int) -> List[Category]:
        """
        Get immediate children of a category.

        Args:
            parent_id (int): Parent category ID

        Returns:
            List[Category]: List of child categories
        """
        result = await self.session.execute(
            select(Category)
            .where(Category.parent_id == parent_id)
            .order_by(Category.name)
        )
        return result.scalars().unique().all()

    async def get_ancestors(self, category_id: int) -> List[Category]:
        """
        Get all ancestors of a category (parent, grandparent, etc.).

        Args:
            category_id (int): Category ID

        Returns:
            List[Category]: List of ancestor categories from direct parent to root
        """
        ancestors = []
        current_id = category_id

        while current_id is not None:
            # Get the parent of the current category
            category = await self.get_with_parent(current_id)
            if not category or not category.parent:
                break

            ancestors.append(category.parent)
            current_id = category.parent.id

        return ancestors

    async def get_descendants(self, category_id: int) -> List[Category]:
        """
        Get all descendants of a category (children, grandchildren, etc.).

        Args:
            category_id (int): Category ID

        Returns:
            List[Category]: List of all descendant categories
        """
        # Start with immediate children
        children = await self.get_children(category_id)
        if not children:
            return []

        descendants = list(children)

        # Recursively get descendants of each child
        for child in children:
            child_descendants = await self.get_descendants(child.id)
            descendants.extend(child_descendants)

        return descendants

    async def is_ancestor_of(self, ancestor_id: int, descendant_id: int) -> bool:
        """
        Check if a category is an ancestor of another category.

        Args:
            ancestor_id (int): Potential ancestor category ID
            descendant_id (int): Potential descendant category ID

        Returns:
            bool: True if ancestor_id is an ancestor of descendant_id
        """
        if ancestor_id == descendant_id:
            return False

        descendants = await self.get_descendants(ancestor_id)
        return any(d.id == descendant_id for d in descendants)

    async def move_category(
        self, category_id: int, new_parent_id: Optional[int]
    ) -> Optional[Category]:
        """
        Move a category to a new parent.

        Args:
            category_id (int): Category ID to move
            new_parent_id (Optional[int]): New parent category ID or None for root

        Returns:
            Optional[Category]: Updated category or None if not found or invalid move
        """
        # Don't allow moving a category to itself
        if category_id == new_parent_id:
            return None

        # Check if the new parent exists (if not None)
        if new_parent_id is not None:
            new_parent = await self.get(new_parent_id)
            if not new_parent:
                return None

            # Don't allow moving a category to its descendant
            if await self.is_ancestor_of(category_id, new_parent_id):
                return None

        # Prevent moving system categories
        category = await self.get(category_id)
        if category and category.system:
            raise ValueError(f"Cannot move system category: {category.name}")

        # Update the category's parent_id
        return await self.update(category_id, {"parent_id": new_parent_id})

    async def get_category_path(self, category_id: int) -> str:
        """
        Get the full path of a category (Parent > Child > Grandchild).

        Args:
            category_id (int): Category ID

        Returns:
            str: Full path of the category
        """
        category = await self.get(category_id)
        if not category:
            return ""

        ancestors = await self.get_ancestors(category_id)

        # Reverse ancestors to get path from root to category
        path_parts = [a.name for a in reversed(ancestors)]
        path_parts.append(category.name)

        return " > ".join(path_parts)

    async def find_categories_by_prefix(self, prefix: str) -> List[Category]:
        """
        Find categories whose names start with the given prefix.

        Args:
            prefix (str): Prefix to search for

        Returns:
            List[Category]: List of matching categories
        """
        result = await self.session.execute(
            select(Category)
            .where(Category.name.ilike(f"{prefix}%"))
            .order_by(Category.name)
        )
        return result.scalars().unique().all()

    async def get_category_with_bill_count(
        self, category_id: int
    ) -> Tuple[Category, int]:
        """
        Get a category with the count of bills assigned to it.

        Args:
            category_id (int): Category ID

        Returns:
            Tuple[Category, int]: (category, bill_count) tuple
        """
        result = await self.session.execute(
            select(Category, func.count(Liability.id).label("bill_count"))
            .select_from(Category)
            .outerjoin(Liability, Liability.category_id == Category.id)
            .where(Category.id == category_id)
            .group_by(Category.id)
        )
        row = result.first()

        if not row:
            return None, 0

        return row.Category, row.bill_count

    async def get_categories_with_bill_counts(self) -> List[Tuple[Category, int]]:
        """
        Get all categories with bill counts.

        Returns:
            List[Tuple[Category, int]]: List of (category, bill_count) tuples
        """
        result = await self.session.execute(
            select(Category, func.count(Liability.id).label("bill_count"))
            .select_from(Category)
            .outerjoin(Liability, Liability.category_id == Category.id)
            .group_by(Category.id)
            .order_by(Category.name)
        )
        # Use unique() to ensure we don't get duplicates due to the join
        return [(row.Category, row.bill_count) for row in result.unique().all()]

    async def get_total_by_category(self) -> List[Tuple[Category, Decimal]]:
        """
        Get total amount of bills by category.

        Returns:
            List[Tuple[Category, Decimal]]: List of (category, total_amount) tuples
        """
        result = await self.session.execute(
            select(Category, func.sum(Liability.amount).label("total_amount"))
            .join(Liability, Liability.category_id == Category.id)
            .group_by(Category.id)
            .order_by(desc("total_amount"))
        )
        return [(row.Category, row.total_amount) for row in result.all()]

    async def is_category_or_child(
        self, transaction_category: str, filter_category: str
    ) -> bool:
        """
        Check if transaction category matches filter category or is a child category.

        This method is used for hierarchical category matching, supporting the
        Transaction Reference System from ADR-029.

        Args:
            transaction_category (str): Category name from the transaction
            filter_category (str): Category name to filter by

        Returns:
            bool: True if transaction_category matches or is a child of filter_category
        """
        # Exact match case
        if transaction_category == filter_category:
            return True

        # Get category objects by name
        transaction_cat_obj = await self.get_by_name(transaction_category)
        filter_cat_obj = await self.get_by_name(filter_category)

        # If either category doesn't exist, no match
        if not transaction_cat_obj or not filter_cat_obj:
            return False

        # Check if filter category is an ancestor of transaction category
        ancestors = await self.get_ancestors(transaction_cat_obj.id)

        # Check if filter category is among the ancestors
        return any(ancestor.id == filter_cat_obj.id for ancestor in ancestors)

    async def delete_if_unused(self, category_id: int) -> bool:
        """
        Delete a category only if it has no children and no bills.

        Args:
            category_id (int): Category ID

        Returns:
            bool: True if deleted, False if not deleted (has children or bills)
        """
        # Check if it's a system category
        category = await self.get(category_id)
        if category and category.system:
            return False

        category, bill_count = await self.get_category_with_bill_count(category_id)

        if not category:
            return False

        # Check if it has children
        children = await self.get_children(category_id)

        # Only delete if no children and no bills
        if not children and bill_count == 0:
            return await self.delete(category_id)

        return False
