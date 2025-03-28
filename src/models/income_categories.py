from typing import List, Optional

from sqlalchemy import String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .base_model import BaseDBModel


class IncomeCategory(BaseDBModel):
    """
    Model for categorizing income sources.
    Inherits created_at and updated_at from BaseDBModel (naive UTC).
    """

    __tablename__ = "income_categories"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    name: Mapped[str] = mapped_column(
        String(100), unique=True, nullable=False, index=True
    )
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    # Relationship to Income model
    incomes: Mapped[List["Income"]] = relationship(
        "Income",
        back_populates="category",
        cascade="all, delete-orphan",
        doc="Income entries in this category",
    )

    def __repr__(self) -> str:
        return f"<IncomeCategory {self.name}>"
