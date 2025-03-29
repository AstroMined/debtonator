from pydantic import Field

from src.schemas.base_schema import BaseSchemaValidator


class IncomeCategoryBase(BaseSchemaValidator):
    """
    Base schema for income categories.

    Contains the common fields required for income category operations.
    """

    name: str = Field(
        ..., min_length=1, max_length=100, description="Name of the income category"
    )
    description: str | None = Field(
        None, max_length=500, description="Optional description of the income category"
    )


class IncomeCategoryCreate(IncomeCategoryBase):
    """
    Schema for creating a new income category.

    Extends the base schema without adding additional fields.
    """

    pass


class IncomeCategoryUpdate(IncomeCategoryBase):
    """
    Schema for updating an existing income category.

    Extends the base schema without adding additional fields.
    All fields are optional to allow partial updates.
    """

    name: str | None = Field(
        None,
        min_length=1,
        max_length=100,
        description="Updated name of the income category",
    )
    description: str | None = Field(
        None, max_length=500, description="Updated description of the income category"
    )


class IncomeCategory(IncomeCategoryBase):
    """
    Schema for a complete income category record.

    Includes the ID and all fields from the base schema.
    """

    id: int = Field(..., description="Unique identifier for the income category")
