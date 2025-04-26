"""
Categories service implementation.

This module provides services for category management, hierarchical organization,
and category-liability relationships with proper system category protection.
"""

from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from src.constants import DEFAULT_CATEGORY_ID
from src.models.categories import Category
from src.repositories.categories import CategoryRepository
from src.schemas.categories import (
    CategoryCreate,
    CategoryTree,
    CategoryUpdate,
    CategoryWithBillsResponse,
)
from src.services.base import BaseService


class CategoryError(Exception):
    """Base exception for category-related errors."""

    def __init__(self, message: str, category_id: Optional[int] = None, name: Optional[str] = None):
        self.category_id = category_id
        self.name = name
        self.message = message
        super().__init__(self.message)


class CategoryService(BaseService):
    """
    Service for category management.
    
    This service provides comprehensive support for hierarchical category management,
    including category-bill relationships, system category protection, and
    hierarchical tree operations.
    """

    def __init__(
        self,
        session: AsyncSession,
        feature_flag_service: Optional[Any] = None,
        config_provider: Optional[Any] = None,
    ):
        """
        Initialize the category service.
        
        Args:
            session: Database session for operations
            feature_flag_service: Optional feature flag service
            config_provider: Optional configuration provider
        """
        super().__init__(session, feature_flag_service, config_provider)

    async def validate_parent_category(
        self, parent_id: int, category_id: Optional[int] = None
    ) -> Category:
        """
        Validate parent category exists and prevent circular references.
        
        Args:
            parent_id: ID of the parent category
            category_id: Optional ID of the category being validated
            
        Returns:
            The parent category if valid
            
        Raises:
            CategoryError: If parent doesn't exist or would create a circular reference
        """
        if parent_id is None:
            return None

        # Get the repository
        category_repo = await self._get_repository(CategoryRepository)
            
        # Get the parent category
        parent = await category_repo.get(parent_id)
        if not parent:
            raise CategoryError(
                f"Parent category with ID {parent_id} does not exist", 
                category_id=parent_id
            )

        # For existing categories, prevent circular references
        if category_id:
            if parent_id == category_id:
                raise CategoryError(
                    "Category cannot be its own parent",
                    category_id=category_id
                )
                
            category = await category_repo.get(category_id)
            if category:
                # Check if the parent is actually a descendant of the category
                if await category_repo.is_ancestor_of(category_id, parent_id):
                    raise CategoryError(
                        "Circular reference detected in category hierarchy",
                        category_id=category_id
                    )

        return parent

    async def create_category(self, category: CategoryCreate) -> Category:
        """
        Create a new category.
        
        Args:
            category: Data for the new category
            
        Returns:
            The newly created category
            
        Raises:
            CategoryError: If validation fails or name is duplicate
        """
        # Get the repository
        category_repo = await self._get_repository(CategoryRepository)
            
        # Validate parent if specified
        if category.parent_id:
            await self.validate_parent_category(category.parent_id)

        # Check for duplicate name
        existing = await category_repo.get_by_name(category.name)
        if existing:
            raise CategoryError(
                f"Category with name '{category.name}' already exists",
                name=category.name
            )
            
        # Create category using repository
        try:
            return await category_repo.create(category.model_dump())
        except IntegrityError:
            raise CategoryError(
                f"Category with name '{category.name}' already exists",
                name=category.name
            )

    async def get_category(self, category_id: int) -> Optional[Category]:
        """
        Get a category by ID.
        
        Args:
            category_id: ID of the category
            
        Returns:
            Category or None if not found
        """
        category_repo = await self._get_repository(CategoryRepository)
        return await category_repo.get(category_id)

    async def get_category_by_name(self, name: str) -> Optional[Category]:
        """
        Get a category by name.
        
        Args:
            name: Name of the category
            
        Returns:
            Category or None if not found
        """
        category_repo = await self._get_repository(CategoryRepository)
        return await category_repo.get_by_name(name)

    async def get_categories(self, skip: int = 0, limit: int = 100) -> List[Category]:
        """
        Get a list of categories with pagination.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            
        Returns:
            List of categories
        """
        category_repo = await self._get_repository(CategoryRepository)
        all_categories = await category_repo.get_multi()
        
        # Apply manual pagination
        start = min(skip, len(all_categories))
        end = min(start + limit, len(all_categories))
        return all_categories[start:end]

    async def update_category(
        self, category_id: int, category_update: CategoryUpdate
    ) -> Optional[Category]:
        """
        Update a category.
        
        Args:
            category_id: ID of the category to update
            category_update: Data to update
            
        Returns:
            Updated category or None if not found
            
        Raises:
            CategoryError: If validation fails, name is duplicate, or attempting to update system category
        """
        category_repo = await self._get_repository(CategoryRepository)
        
        # Get current category
        db_category = await category_repo.get(category_id)
        if not db_category:
            return None
            
        # Extract update fields
        update_data = category_update.model_dump(exclude_unset=True)

        # Validate parent_id if being updated
        if "parent_id" in update_data:
            await self.validate_parent_category(update_data["parent_id"], category_id)

        try:
            # Update through repository, which handles system category protection
            return await category_repo.update(category_id, update_data)
        except ValueError as e:
            # Repository throws ValueError for system categories
            raise CategoryError(str(e), category_id=category_id)
        except IntegrityError:
            # Handle duplicate name
            await self._session.rollback()
            raise CategoryError(
                f"Category name '{category_update.name}' already exists",
                category_id=category_id,
                name=category_update.name
            )

    async def delete_category(self, category_id: int) -> bool:
        """
        Delete a category.
        
        Args:
            category_id: ID of the category to delete
            
        Returns:
            True if successfully deleted, False if not found
            
        Raises:
            CategoryError: If category has bills, children, or is a system category
        """
        category_repo = await self._get_repository(CategoryRepository)
        
        # Load category with relationships
        category = await category_repo.get_with_relationships(
            category_id, 
            include_bills=True,
            include_children=True
        )
        
        if not category:
            return False

        # Check system category
        if category.system or category_id == DEFAULT_CATEGORY_ID:
            raise CategoryError(
                f"Cannot delete system category: {category.name}",
                category_id=category_id,
                name=category.name
            )

        # Check for bills
        if category.bills and len(category.bills) > 0:
            raise CategoryError(
                "Cannot delete category that has bills assigned to it",
                category_id=category_id
            )

        # Check for children
        if category.children and len(category.children) > 0:
            raise CategoryError(
                "Cannot delete category that has child categories",
                category_id=category_id
            )

        # Delete using repository
        try:
            return await category_repo.delete(category_id)
        except ValueError as e:
            # Repository throws ValueError for system categories
            raise CategoryError(str(e), category_id=category_id)

    async def get_category_with_children(self, category_id: int) -> Optional[Category]:
        """
        Get a category with its child categories.
        
        Args:
            category_id: ID of the category
            
        Returns:
            Category with loaded children or None if not found
        """
        category_repo = await self._get_repository(CategoryRepository)
        return await category_repo.get_with_children(category_id)

    async def get_category_with_parent(self, category_id: int) -> Optional[Category]:
        """
        Get a category with its parent category.
        
        Args:
            category_id: ID of the category
            
        Returns:
            Category with loaded parent or None if not found
        """
        category_repo = await self._get_repository(CategoryRepository)
        return await category_repo.get_with_parent(category_id)

    async def get_root_categories(self) -> List[Category]:
        """
        Get all top-level categories (categories without parents).
        
        Returns:
            List of root categories
        """
        category_repo = await self._get_repository(CategoryRepository)
        return await category_repo.get_root_categories()

    async def get_category_with_bills(self, category_id: int) -> Optional[Category]:
        """
        Get a category with its associated bills.
        
        Args:
            category_id: ID of the category
            
        Returns:
            Category with loaded bills or None if not found
        """
        category_repo = await self._get_repository(CategoryRepository)
        return await category_repo.get_with_bills(category_id)

    async def get_full_path(self, category: Category) -> str:
        """
        Get the full hierarchical path of the category.
        
        Args:
            category: The category to get the full path for
            
        Returns:
            A string representing the full hierarchical path of the category
        """
        if not category:
            return ""

        category_repo = await self._get_repository(CategoryRepository)
        
        # Use repository to get category path
        return await category_repo.get_category_path(category.id)

    async def is_ancestor_of(self, ancestor: Category, descendant: Category) -> bool:
        """
        Check if one category is an ancestor of another category.
        
        Args:
            ancestor: The potential ancestor category
            descendant: The potential descendant category
            
        Returns:
            True if ancestor is an ancestor of descendant, False otherwise
        """
        if not ancestor or not descendant:
            return False
            
        category_repo = await self._get_repository(CategoryRepository)
        
        # Use repository to check ancestry
        return await category_repo.is_ancestor_of(ancestor.id, descendant.id)

    async def move_category(
        self, category_id: int, new_parent_id: Optional[int]
    ) -> Optional[Category]:
        """
        Move a category to a new parent.
        
        Args:
            category_id: ID of the category to move
            new_parent_id: ID of the new parent category or None for root
            
        Returns:
            Updated category or None if not found or invalid move
            
        Raises:
            CategoryError: If validation fails or category is a system category
        """
        category_repo = await self._get_repository(CategoryRepository)
        
        try:
            # Use repository to move the category
            return await category_repo.move_category(category_id, new_parent_id)
        except ValueError as e:
            # Repository throws ValueError for system categories
            raise CategoryError(str(e), category_id=category_id)

    # Rich composition methods for building response objects without circular references

    async def compose_category_tree(
        self, category_id: int, depth: int = -1
    ) -> Optional[CategoryTree]:
        """
        Build a rich category tree response without circular references.
        
        Args:
            category_id: ID of the root category
            depth: Maximum depth to recurse (-1 for unlimited)
            
        Returns:
            CategoryTree object with child categories nested to specified depth
        """
        category_repo = await self._get_repository(CategoryRepository)
        
        # Get category with children loaded
        category = await category_repo.get_with_children(category_id)
        if not category:
            return None

        # Create the base tree node
        result = CategoryTree(
            id=category.id,
            name=category.name,
            description=category.description,
            parent_id=category.parent_id,
            created_at=category.created_at,
            updated_at=category.updated_at,
        )

        # Add full path
        result.full_path = await category_repo.get_category_path(category.id)

        # Only recurse if depth limit not reached
        if depth != 0 and category.children:
            result.children = []
            for child in category.children:
                child_tree = await self.compose_category_tree(
                    child.id, depth - 1 if depth > 0 else -1
                )
                if child_tree:
                    result.children.append(child_tree)

        return result

    async def compose_category_with_bills(
        self, category_id: int
    ) -> Optional[CategoryWithBillsResponse]:
        """
        Build a rich category response with bills without circular references.
        
        Args:
            category_id: ID of the category
            
        Returns:
            CategoryWithBillsResponse object with bills and child categories
        """
        category_repo = await self._get_repository(CategoryRepository)
        
        # Get category with bills and children loaded
        category = await category_repo.get_with_relationships(
            category_id,
            include_bills=True,
            include_children=True
        )
        
        if not category:
            return None

        # Create the base response object
        result = CategoryWithBillsResponse(
            id=category.id,
            name=category.name,
            description=category.description,
            parent_id=category.parent_id,
            created_at=category.created_at,
            updated_at=category.updated_at,
        )

        # Add full path
        result.full_path = await category_repo.get_category_path(category.id)

        # Transform bills to simplified dict representation
        result.bills = [
            {
                "id": bill.id,
                "name": bill.name,
                "amount": bill.amount,
                "due_date": bill.due_date,
                "status": bill.status.value if hasattr(bill, "status") else None,
                "paid": bill.paid,
            }
            for bill in category.bills
        ]

        # Add children recursively
        result.children = []
        for child in category.children:
            child_with_bills = await self.compose_category_with_bills(child.id)
            if child_with_bills:
                result.children.append(child_with_bills)

        return result
        
    async def get_category_with_bill_count(
        self, category_id: int
    ) -> Tuple[Optional[Category], int]:
        """
        Get a category with the count of bills assigned to it.
        
        Args:
            category_id: ID of the category
            
        Returns:
            Tuple of (category, bill_count)
        """
        category_repo = await self._get_repository(CategoryRepository)
        return await category_repo.get_category_with_bill_count(category_id)
        
    async def get_categories_with_bill_counts(self) -> List[Tuple[Category, int]]:
        """
        Get all categories with bill counts.
        
        Returns:
            List of (category, bill_count) tuples
        """
        category_repo = await self._get_repository(CategoryRepository)
        return await category_repo.get_categories_with_bill_counts()
        
    async def get_ancestors(self, category_id: int) -> List[Category]:
        """
        Get all ancestors of a category.
        
        Args:
            category_id: ID of the category
            
        Returns:
            List of ancestor categories
        """
        category_repo = await self._get_repository(CategoryRepository)
        return await category_repo.get_ancestors(category_id)
        
    async def get_descendants(self, category_id: int) -> List[Category]:
        """
        Get all descendants of a category.
        
        Args:
            category_id: ID of the category
            
        Returns:
            List of descendant categories
        """
        category_repo = await self._get_repository(CategoryRepository)
        return await category_repo.get_descendants(category_id)
        
    async def find_categories_by_prefix(self, prefix: str) -> List[Category]:
        """
        Find categories whose names start with the given prefix.
        
        Args:
            prefix: Prefix to search for
            
        Returns:
            List of matching categories
        """
        category_repo = await self._get_repository(CategoryRepository)
        return await category_repo.find_categories_by_prefix(prefix)
        
    async def delete_if_unused(self, category_id: int) -> bool:
        """
        Delete a category only if it has no children and no bills.
        
        Args:
            category_id: ID of the category
            
        Returns:
            True if deleted, False if not deleted (has children or bills)
        """
        category_repo = await self._get_repository(CategoryRepository)
        return await category_repo.delete_if_unused(category_id)
        
    async def get_default_category_id(self) -> int:
        """
        Get the default category ID, creating it if needed.
        
        Returns:
            ID of the default category
        """
        category_repo = await self._get_repository(CategoryRepository)
        return await category_repo.get_default_category_id()
