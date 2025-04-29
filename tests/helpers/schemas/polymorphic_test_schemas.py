"""
Schemas for polymorphic model testing.

This module provides Pydantic schemas for testing polymorphic repository functionality.
These schemas follow the same patterns as business schemas but are simplified for
focused repository testing.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import Field

from src.schemas.base_schema import BaseSchemaValidator


class TestBaseModelSchema(BaseSchemaValidator):
    """
    Base schema for polymorphic model testing.

    Contains common fields for all polymorphic test entities.
    """

    name: str = Field(..., min_length=1, max_length=100, description="Entity name")
    model_type: str = Field(..., description="Polymorphic type discriminator")


class TestTypeASchema(TestBaseModelSchema):
    """
    Schema for Type A test entities.

    Extends base schema with an optional a_field.
    """

    model_type: Literal["type_a"] = "type_a"
    a_field: Optional[str] = Field(
        default=None, max_length=100, description="Type A specific field"
    )


class TestTypeBSchema(TestBaseModelSchema):
    """
    Schema for Type B test entities.

    Extends base schema with a required b_field to test required field handling.
    """

    model_type: Literal["type_b"] = "type_b"
    b_field: str = Field(
        ..., min_length=1, max_length=100, description="Type B required field"
    )


class TestBaseModelCreate(TestBaseModelSchema):
    """Base schema for creating polymorphic entities."""


class TestTypeACreate(TestTypeASchema, TestBaseModelCreate):
    """Schema for creating Type A entities."""


class TestTypeBCreate(TestTypeBSchema, TestBaseModelCreate):
    """Schema for creating Type B entities."""


class TestBaseModelUpdate(BaseSchemaValidator):
    """
    Base schema for updating polymorphic entities.

    All fields are optional to allow partial updates.
    """

    name: Optional[str] = Field(
        default=None, min_length=1, max_length=100, description="Entity name"
    )


class TestTypeAUpdate(TestBaseModelUpdate):
    """Schema for updating Type A entities."""

    a_field: Optional[str] = Field(
        default=None, max_length=100, description="Type A specific field"
    )


class TestTypeBUpdate(TestBaseModelUpdate):
    """Schema for updating Type B entities."""

    b_field: Optional[str] = Field(
        default=None, min_length=1, max_length=100, description="Type B required field"
    )


class TestBaseModelInDB(TestBaseModelSchema):
    """
    Schema for polymorphic entity data as stored in the database.

    Extends the base schema with database-specific fields.
    """

    id: int = Field(..., gt=0, description="Entity ID (unique identifier)")
    created_at: datetime = Field(
        ..., description="Timestamp when the entity was created (UTC timezone)"
    )
    updated_at: datetime = Field(
        ..., description="Timestamp when the entity was last updated (UTC timezone)"
    )


class TestTypeAInDB(TestTypeASchema, TestBaseModelInDB):
    """Schema for Type A entity data as stored in the database."""


class TestTypeBInDB(TestTypeBSchema, TestBaseModelInDB):
    """Schema for Type B entity data as stored in the database."""
