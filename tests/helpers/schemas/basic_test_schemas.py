"""
Test-specific schemas for generic repository testing.

These schemas are intentionally simple and designed specifically for testing
generic repository functionality without dependencies on business schemas.
"""

from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import Field

from src.schemas.base_schema import BaseSchemaValidator, MoneyDecimal


class TestItemBase(BaseSchemaValidator):
    """
    Base schema for test item data.

    Contains common fields and validation logic for test items.
    """

    name: str = Field(..., min_length=1, max_length=50, description="Item name")
    description: Optional[str] = Field(
        default=None, max_length=255, description="Optional description"
    )
    numeric_value: MoneyDecimal = Field(
        default=Decimal("0"), description="Numeric value"
    )
    is_active: bool = Field(default=True, description="Whether the item is active")


class TestItemCreate(TestItemBase):
    """Schema for creating a new test item."""


class TestItemUpdate(TestItemBase):
    """
    Schema for updating an existing test item.

    All fields are optional to allow partial updates.
    """

    name: Optional[str] = Field(
        default=None, min_length=1, max_length=50, description="Item name"
    )
    description: Optional[str] = Field(
        default=None, max_length=255, description="Optional description"
    )
    numeric_value: Optional[MoneyDecimal] = Field(
        default=None, description="Numeric value"
    )
    is_active: Optional[bool] = Field(
        default=None, description="Whether the item is active"
    )


class TestItemInDB(TestItemBase):
    """
    Schema for test item data as stored in the database.

    Extends the base schema with database-specific fields.
    """

    id: int = Field(..., gt=0, description="Item ID (unique identifier)")
    created_at: datetime = Field(
        ..., description="Timestamp when the item was created (UTC timezone)"
    )
    updated_at: datetime = Field(
        ..., description="Timestamp when the item was last updated (UTC timezone)"
    )
