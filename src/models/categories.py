from datetime import datetime
from typing import Optional, List
from sqlalchemy import String, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from zoneinfo import ZoneInfo

from .base_model import BaseDBModel

class Category(BaseDBModel):
    """Category model for organizing bills and expenses"""
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    parent_id: Mapped[Optional[int]] = mapped_column(ForeignKey('categories.id', ondelete='CASCADE'), nullable=True)

    # Relationship with liabilities (bills)
    bills: Mapped[List["Liability"]] = relationship("Liability", back_populates="category")

    # Hierarchical relationships
    parent: Mapped[Optional["Category"]] = relationship(
        "Category",
        remote_side=[id],
        back_populates="children",
        lazy="joined"
    )
    children: Mapped[List["Category"]] = relationship(
        "Category",
        back_populates="parent",
        cascade="all, delete-orphan",
        lazy="joined"
    )

    def __repr__(self) -> str:
        return f"<Category(id={self.id}, name='{self.name}', parent_id={self.parent_id})>"

    @property
    def full_path(self) -> str:
        """Returns the full hierarchical path of the category."""
        if self.parent:
            return f"{self.parent.full_path} > {self.name}"
        return self.name

    async def is_ancestor_of(self, category: 'Category') -> bool:
        """Check if this category is an ancestor of the given category."""
        if not category or not category.parent_id:
            return False
        if category.parent_id == self.id:
            return True
        parent = await self._get_parent(category)
        if not parent:
            return False
        return await self.is_ancestor_of(parent)

    @staticmethod
    async def _get_parent(category: 'Category') -> Optional['Category']:
        """Helper method to get parent category"""
        if not category.parent_id:
            return None
        return category.parent
