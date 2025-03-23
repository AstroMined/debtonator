"""
Income category repository implementation.

This module provides a repository for IncomeCategory model CRUD operations and specialized
income category-related queries.
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.models.income import Income
from src.models.income_categories import IncomeCategory
from src.repositories.base import BaseRepository


class IncomeCategoryRepository(BaseRepository[IncomeCategory, int]):
    """
    Repository for IncomeCategory model operations.

    This repository handles CRUD operations for income categories and provides specialized
    queries for income category-related functionality.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session (AsyncSession): SQLAlchemy async session
        """
        super().__init__(session, IncomeCategory)

    async def get_by_name(self, name: str) -> Optional[IncomeCategory]:
        """
        Get income category by name.

        Args:
            name (str): Category name to search for

        Returns:
            Optional[IncomeCategory]: Category with matching name or None
        """
        result = await self.session.execute(
            select(IncomeCategory).where(IncomeCategory.name == name)
        )
        return result.scalars().first()

    async def get_with_income(self, category_id: int) -> Optional[IncomeCategory]:
        """
        Get income category with its related income entries.

        Args:
            category_id (int): Category ID

        Returns:
            Optional[IncomeCategory]: Category with loaded income entries or None
        """
        result = await self.session.execute(
            select(IncomeCategory)
            .options(selectinload(IncomeCategory.income_entries))
            .where(IncomeCategory.id == category_id)
        )
        return result.scalars().unique().first()

    async def get_total_by_category(self) -> List[Tuple[IncomeCategory, Decimal]]:
        """
        Get total amount of income by category.

        Returns:
            List[Tuple[IncomeCategory, Decimal]]: List of (category, total_amount) tuples
        """
        result = await self.session.execute(
            select(IncomeCategory, func.sum(Income.amount).label("total_amount"))
            .join(Income, Income.category_id == IncomeCategory.id)
            .group_by(IncomeCategory.id)
            .order_by(func.sum(Income.amount).desc())
        )
        return [(row.IncomeCategory, row.total_amount) for row in result.all()]

    async def get_categories_with_income_counts(
        self,
    ) -> List[Tuple[IncomeCategory, int]]:
        """
        Get all income categories with income entry counts.

        Returns:
            List[Tuple[IncomeCategory, int]]: List of (category, income_count) tuples
        """
        result = await self.session.execute(
            select(IncomeCategory, func.count().label("income_count"))
            .outerjoin(Income, Income.category_id == IncomeCategory.id)
            .group_by(IncomeCategory.id)
            .order_by(IncomeCategory.name)
        )
        return [(row.IncomeCategory, row.income_count) for row in result.all()]

    async def find_categories_by_prefix(self, prefix: str) -> List[IncomeCategory]:
        """
        Find income categories whose names start with the given prefix.

        Args:
            prefix (str): Prefix to search for

        Returns:
            List[IncomeCategory]: List of matching categories
        """
        result = await self.session.execute(
            select(IncomeCategory)
            .where(IncomeCategory.name.ilike(f"{prefix}%"))
            .order_by(IncomeCategory.name)
        )
        return result.scalars().unique().all()

    async def delete_if_unused(self, category_id: int) -> bool:
        """
        Delete an income category only if it has no associated income entries.

        Args:
            category_id (int): Category ID

        Returns:
            bool: True if deleted, False if not deleted (has income entries)
        """
        # Check if this category has any income entries
        result = await self.session.execute(
            select(func.count())
            .select_from(Income)
            .where(Income.category_id == category_id)
        )
        count = result.scalar_one()

        # Only delete if no income entries are associated
        if count == 0:
            return await self.delete(category_id)

        return False

    async def get_active_categories(self) -> List[IncomeCategory]:
        """
        Get all income categories that have active associated income.

        Categories are considered active if they are associated with at least one
        non-deposited income entry.

        Returns:
            List[IncomeCategory]: List of active categories
        """
        result = await self.session.execute(
            select(IncomeCategory)
            .join(Income, Income.category_id == IncomeCategory.id)
            .where(Income.is_deposited == False)
            .group_by(IncomeCategory.id)
            .order_by(IncomeCategory.name)
        )
        return result.scalars().unique().all()

    async def get_categories_with_stats(
        self,
    ) -> List[Dict[str, Any]]:
        """
        Get income categories with detailed statistics.

        Returns:
            List[Dict[str, Any]]: List of dictionaries containing:
                - category: IncomeCategory object
                - total_amount: Total income amount
                - entry_count: Number of income entries
                - avg_amount: Average income amount
                - pending_count: Number of non-deposited entries
                - pending_amount: Total non-deposited amount
        """
        # This query gets multiple aggregations for each category
        result = await self.session.execute(
            select(
                IncomeCategory,
                func.sum(Income.amount).label("total_amount"),
                func.count().label("entry_count"),
                func.avg(Income.amount).label("avg_amount"),
                func.sum(func.case((Income.is_deposited == False, 1), else_=0)).label(
                    "pending_count"
                ),
                func.sum(
                    func.case((Income.is_deposited == False, Income.amount), else_=0)
                ).label("pending_amount"),
            )
            .outerjoin(Income, Income.category_id == IncomeCategory.id)
            .group_by(IncomeCategory.id)
            .order_by(func.sum(Income.amount).desc())
        )

        stats = []
        for row in result.all():
            stats.append(
                {
                    "category": row.IncomeCategory,
                    "total_amount": row.total_amount or Decimal("0.00"),
                    "entry_count": row.entry_count or 0,
                    "avg_amount": row.avg_amount or Decimal("0.00"),
                    "pending_count": row.pending_count or 0,
                    "pending_amount": row.pending_amount or Decimal("0.00"),
                }
            )

        return stats
