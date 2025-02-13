from datetime import datetime
from typing import Optional
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship

from src.database.base import Base

class Category(Base):
    __tablename__ = "categories"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    description = Column(String, nullable=True)
    parent_id = Column(Integer, ForeignKey('categories.id', ondelete='CASCADE'), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationship with liabilities (bills)
    bills = relationship("Liability", back_populates="category")

    # Hierarchical relationships
    parent = relationship("Category", remote_side=[id], back_populates="children")
    children = relationship("Category", back_populates="parent", cascade="all, delete-orphan")

    def __repr__(self):
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
