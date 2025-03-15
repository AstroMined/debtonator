from typing import List, Optional

from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseDBModel


class Category(BaseDBModel):
    """
    Category model for organizing bills and expenses.

    This is a pure data structure model with no business logic methods.
    All business logic related to category hierarchy and path management
    has been moved to the CategoryService class to comply with ADR-012
    (Validation Layer Standardization).
    """

    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String, unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String, nullable=True)
    parent_id: Mapped[Optional[int]] = mapped_column(
        ForeignKey("categories.id", ondelete="CASCADE"), nullable=True
    )

    # Relationship with liabilities (bills)
    bills: Mapped[List["Liability"]] = relationship(
        "Liability", back_populates="category"
    )

    # Hierarchical relationships
    parent: Mapped[Optional["Category"]] = relationship(
        "Category", remote_side=[id], back_populates="children", lazy="joined"
    )
    children: Mapped[List["Category"]] = relationship(
        "Category", back_populates="parent", cascade="all, delete-orphan", lazy="joined"
    )

    def __repr__(self) -> str:
        return (
            f"<Category(id={self.id}, name='{self.name}', parent_id={self.parent_id})>"
        )

    # The following methods have been removed and moved to CategoryService:
    # - full_path property: Use CategoryService.get_full_path(category) instead
    # - is_ancestor_of method: Use CategoryService.is_ancestor_of(ancestor, descendant) instead
    # - _get_parent helper method: No longer needed as logic is in service layer
