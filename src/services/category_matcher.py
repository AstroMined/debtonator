"""
Category Matcher Service for transaction categorization.

This module provides the CategoryMatcher service which handles matching
transactions to categories, including hierarchical relationships between categories.
It eliminates hardcoded string matching and provides more robust category handling.

Implemented as part of ADR-029 Transaction Categorization and Reference System.
"""

import logging
from typing import Any, Dict, List, Optional, Union

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.categories import Category
from src.registry.transaction_reference import transaction_reference_registry
from src.repositories.categories import CategoryRepository
from src.services.base import BaseService
from src.services.feature_flags import FeatureFlagService

logger = logging.getLogger(__name__)


class CategoryMatcher(BaseService):
    """
    Service for matching transactions to categories.

    This service provides methods for determining if a transaction belongs
    to a specific category, including handling hierarchical relationships
    between categories.

    The service uses the registry pattern to access transaction fields and
    leverages the existing CategoryRepository for efficient queries.
    """

    def __init__(
        self,
        session: AsyncSession,
        feature_flag_service: Optional[FeatureFlagService] = None,
        config_provider: Optional[Any] = None,
    ):
        """
        Initialize the category matcher service.

        Args:
            session: SQLAlchemy async session for database operations
            feature_flag_service: Optional feature flag service for repository proxies
            config_provider: Optional config provider for feature flags
        """
        super().__init__(session, feature_flag_service, config_provider)
        self._registry = transaction_reference_registry
        self._category_cache: Dict[str, Category] = {}
        self._relationship_cache: Dict[str, bool] = {}

    async def matches_category(
        self,
        transaction: Dict[str, Any],
        category: Union[str, Category],
        include_child_categories: bool = True,
    ) -> bool:
        """
        Check if transaction matches the given category.

        This method checks if a transaction belongs to the specified category
        or any of its child categories, supporting hierarchical categorization.

        Args:
            transaction: Transaction dictionary
            category: Category name or Category object
            include_child_categories: Whether to include child categories in matching

        Returns:
            True if the transaction matches the category, False otherwise
        """
        # Extract transaction category
        transaction_category = self._registry.extract_category(transaction)
        if not transaction_category:
            return False

        # Get category repository
        category_repo = await self._get_repository(CategoryRepository)

        # Get the category name
        category_name = category.name if isinstance(category, Category) else category

        # Check for exact match first for efficiency
        if transaction_category == category_name:
            return True

        # If not an exact match and we're including child categories, check hierarchy
        if include_child_categories:
            # Use cache to avoid redundant database queries
            cache_key = f"{transaction_category}:{category_name}"
            if cache_key in self._relationship_cache:
                return self._relationship_cache[cache_key]

            # Check if transaction category is a child of target category
            result = await category_repo.is_category_or_child(
                transaction_category, category_name
            )

            # Cache the result
            self._relationship_cache[cache_key] = result
            return result

        return False

    async def get_matching_transactions(
        self,
        transactions: List[Dict[str, Any]],
        category: Union[str, Category],
        include_child_categories: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Filter transactions that match a specific category.

        Args:
            transactions: List of transaction dictionaries
            category: Category name or Category object
            include_child_categories: Whether to include child categories in matching

        Returns:
            List of transactions that match the category
        """
        matching_transactions = []

        for transaction in transactions:
            if await self.matches_category(
                transaction, category, include_child_categories
            ):
                matching_transactions.append(transaction)

        return matching_transactions

    async def get_category_by_name(self, category_name: str) -> Optional[Category]:
        """
        Get a category by name with caching.

        Args:
            category_name: Name of the category to retrieve

        Returns:
            Category object if found, None otherwise
        """
        # Check cache first
        if category_name in self._category_cache:
            return self._category_cache[category_name]

        # Get category repository
        category_repo = await self._get_repository(CategoryRepository)

        # Get category by name
        category = await category_repo.get_by_name(category_name)

        # Cache the result
        if category:
            self._category_cache[category_name] = category

        return category

    async def clear_caches(self) -> None:
        """
        Clear internal caches.

        Call this method if categories have been modified to ensure
        the service uses up-to-date information.
        """
        self._category_cache.clear()
        self._relationship_cache.clear()
        logger.debug("Category matcher caches cleared")

    async def get_category_hierarchy(self, category_name: str) -> List[str]:
        """
        Get the full category hierarchy (ancestors and self).

        Args:
            category_name: Name of the category

        Returns:
            List of category names from root to the specified category
        """
        # Get category
        category = await self.get_category_by_name(category_name)
        if not category:
            return []

        # Get category repository
        category_repo = await self._get_repository(CategoryRepository)

        # Get ancestors
        ancestors = await category_repo.get_ancestors(category.id)

        # Create hierarchy from root to leaf
        hierarchy = [ancestor.name for ancestor in reversed(ancestors)]
        hierarchy.append(category_name)

        return hierarchy

    async def get_category_descendants(self, category_name: str) -> List[str]:
        """
        Get all descendant categories of a category.

        Args:
            category_name: Name of the parent category

        Returns:
            List of descendant category names
        """
        # Get category
        category = await self.get_category_by_name(category_name)
        if not category:
            return []

        # Get category repository
        category_repo = await self._get_repository(CategoryRepository)

        # Get descendants
        descendants = await category_repo.get_descendants(category.id)

        # Return descendant names
        return [descendant.name for descendant in descendants]
