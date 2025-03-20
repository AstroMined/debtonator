from datetime import datetime
from enum import Enum
from typing import ForwardRef, List, Optional

from pydantic import Field, field_validator

from src.schemas import BaseSchemaValidator

# Forward reference for circular references
LiabilityBaseRef = ForwardRef("LiabilityBase")


class CategoryBase(BaseSchemaValidator):
    """
    Base schema for category data.

    Contains common fields and validation shared by all category schemas.
    """

    name: str = Field(..., description="Name of the category", max_length=100)
    description: Optional[str] = Field(
        None, description="Optional description of the category", max_length=500
    )
    parent_id: Optional[int] = Field(
        None, description="ID of the parent category, if this is a subcategory"
    )


# Common validator function to avoid duplication
def validate_parent_id_common(v: Optional[int], values) -> Optional[int]:
    """
    Validates that a category cannot be its own parent.

    Args:
        v: The parent_id value
        values: ValidationInfo object or dictionary containing validation data

    Returns:
        The original parent_id if validation passes

    Raises:
        ValueError: If category would be its own parent
    """
    # Handle both Pydantic v2 ValidationInfo objects and dictionaries for testing
    if hasattr(values, "data"):
        # Pydantic v2 ValidationInfo object
        current_id = values.data.get("id")
    else:
        # Dictionary for testing compatibility
        current_id = values.get("id")

    if v is not None and v == current_id:
        raise ValueError("Category cannot be its own parent")
    return v


class CategoryCreate(CategoryBase):
    """
    Schema for creating a new category.

    Inherits all fields and validation from CategoryBase and adds specific
    validation for creation operations.
    """

    @field_validator("parent_id")
    @classmethod
    def validate_parent_id(cls, v: Optional[int], values: dict) -> Optional[int]:
        """Ensure a category cannot be its own parent"""
        return validate_parent_id_common(v, values)


class CategoryUpdate(BaseSchemaValidator):
    """
    Schema for updating an existing category.

    All fields are optional to allow partial updates.
    Includes validation to ensure a category cannot be its own parent.
    """

    name: Optional[str] = Field(
        None, description="Name of the category", max_length=100
    )
    description: Optional[str] = Field(
        None, description="Optional description of the category", max_length=500
    )
    parent_id: Optional[int] = Field(
        None, description="ID of the parent category, if this is a subcategory"
    )

    @field_validator("parent_id")
    @classmethod
    def validate_parent_id(cls, v: Optional[int], values: dict) -> Optional[int]:
        """Ensure a category cannot be its own parent"""
        return validate_parent_id_common(v, values)


class Category(CategoryBase):
    """
    Schema for category data returned from the database.

    Extends the base schema with database-specific fields.
    All datetime fields are validated to ensure they have UTC timezone.
    """

    id: int = Field(..., description="Unique category identifier")
    created_at: datetime = Field(
        ..., description="Timestamp when the record was created (UTC timezone)"
    )
    updated_at: datetime = Field(
        ..., description="Timestamp when the record was last updated (UTC timezone)"
    )
    # Note: full_path is now computed by CategoryService.get_full_path() method
    # This field will be populated in the API layer before returning to clients
    full_path: str = Field(
        default="", description="Full hierarchical path of the category"
    )


class CategoryWithChildren(Category):
    """
    Extended category schema that includes child categories.

    Used for returning hierarchical category structures.
    """

    children: List["CategoryWithChildren"] = Field(
        default_factory=list, description="List of child categories"
    )


class CategoryWithParent(Category):
    """
    Extended category schema that includes the parent category.

    Used for returning categories with their parent information.
    """

    parent: Optional[CategoryWithChildren] = Field(
        None, description="Parent category, if this is a subcategory"
    )


class CategoryWithBills(CategoryWithChildren):
    """
    Extended category schema that includes both children and associated bills.

    Used for category-based financial reporting.
    """

    bills: List[LiabilityBaseRef] = Field(
        default_factory=list,
        description="List of liabilities associated with this category",
    )


# Update forward references after class definitions
from src.schemas.liabilities import LiabilityBase

CategoryWithBills.model_rebuild()
CategoryWithChildren.model_rebuild()
