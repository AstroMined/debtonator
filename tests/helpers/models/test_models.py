"""
Test-specific models for generic repository testing.

These models are intentionally simple and designed specifically for testing
generic repository functionality without dependencies on business models.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, DateTime, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column

from src.models.base_model import BaseDBModel


class TestItem(BaseDBModel):
    """
    Simple model for testing generic repository functionality.
    
    This model has minimal fields but covers different data types to ensure
    the repository can handle various field types correctly.
    """
    
    __tablename__ = "test_items"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    numeric_value: Mapped[Decimal] = mapped_column(Numeric(12, 4), nullable=False, default=0)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    
    def __repr__(self) -> str:
        return f"<TestItem(id={self.id}, name={self.name})>"
