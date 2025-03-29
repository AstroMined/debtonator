from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import Field, field_validator

from src.schemas.base_schema import BaseSchemaValidator, MoneyDecimal


class RecurringIncomeBase(BaseSchemaValidator):
    """
    Base schema for recurring income.

    Contains common fields and validation shared by all recurring income schemas.
    """

    source: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Source of the recurring income",
        examples=["Monthly Salary", "Rental Income"],
    )
    amount: MoneyDecimal = Field(
        ...,
        ge=Decimal("0.01"),
        description="Income amount (must be positive)",
        examples=["5000.00", "1200.50"],
    )
    day_of_month: int = Field(
        ...,
        ge=1,
        le=31,
        description="Day of the month when income occurs",
        examples=[1, 15, 30],
    )
    account_id: int = Field(
        ..., gt=0, description="ID of the account this income belongs to"
    )
    category_id: Optional[int] = Field(
        None, gt=0, description="ID of the income category (optional)"
    )
    auto_deposit: bool = Field(
        default=False, description="Whether to automatically mark as deposited"
    )

    @field_validator("day_of_month", mode="before")
    @classmethod
    def validate_day_of_month(cls, v: int) -> int:
        """
        Additional validation for day of month.

        Args:
            v: The day of month value to validate

        Returns:
            The validated day of month

        Raises:
            ValueError: If day 31 is provided
        """
        if v == 31:
            raise ValueError(
                "Day 31 is not supported as it doesn't exist in all months"
            )
        if v == 30:
            # Add a warning in the documentation about months with less than 30 days
            pass
        return v


class RecurringIncomeCreate(RecurringIncomeBase):
    """
    Schema for creating a recurring income.

    Inherits all fields and validation from RecurringIncomeBase.
    """


class RecurringIncomeUpdate(BaseSchemaValidator):
    """
    Schema for updating a recurring income.

    All fields are optional to allow partial updates.
    """

    source: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Updated source of the recurring income",
    )
    amount: Optional[MoneyDecimal] = Field(
        default=None, gt=0, description="Updated income amount"
    )
    day_of_month: Optional[int] = Field(
        None, ge=1, le=31, description="Updated day of the month"
    )
    account_id: Optional[int] = Field(None, gt=0, description="Updated account ID")
    category_id: Optional[int] = Field(None, gt=0, description="Updated category ID")
    auto_deposit: Optional[bool] = Field(
        None, description="Updated auto-deposit setting"
    )
    active: Optional[bool] = Field(None, description="Updated active status")


class RecurringIncomeInDB(RecurringIncomeBase):
    """
    Schema for recurring income in database.

    Extends RecurringIncomeBase with database fields.
    All datetime fields are validated to ensure they have UTC timezone.
    """

    id: int = Field(..., description="Unique identifier for the recurring income")
    active: bool = Field(True, description="Whether this recurring income is active")
    created_at: datetime = Field(
        ..., description="Timestamp when the record was created (UTC timezone)"
    )
    updated_at: datetime = Field(
        ..., description="Timestamp when the record was last updated (UTC timezone)"
    )


class RecurringIncomeResponse(RecurringIncomeBase):
    """
    Schema for recurring income responses.

    Extends RecurringIncomeBase with database fields.
    All datetime fields are validated to ensure they have UTC timezone.
    """

    id: int = Field(..., description="Unique identifier for the recurring income")
    active: bool = Field(True, description="Whether this recurring income is active")
    created_at: datetime = Field(
        ..., description="Timestamp when the record was created (UTC timezone)"
    )
    updated_at: datetime = Field(
        ..., description="Timestamp when the record was last updated (UTC timezone)"
    )


class GenerateIncomeRequest(BaseSchemaValidator):
    """
    Schema for generating income entries from a recurring pattern.

    Used to create actual income entries from recurring income patterns for a specific month.
    """

    month: int = Field(
        ..., ge=1, le=12, description="Month to generate income for (1-12)"
    )
    year: int = Field(..., ge=2000, le=3000, description="Year to generate income for")
