from datetime import datetime, timezone
from decimal import Decimal
from typing import Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator, model_validator

from . import BaseSchemaValidator, MoneyDecimal
from .income_categories import IncomeCategory


class IncomeBase(BaseSchemaValidator):
    """
    Base schema for income data.

    Contains common fields and validation shared by all income schemas.
    All datetime fields are validated to ensure they have UTC timezone.
    """

    date: datetime = Field(
        ...,
        description="Date of the income (UTC timezone)",
        examples=["2025-03-15T00:00:00Z"],
    )
    source: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Source of the income",
        examples=["Salary", "Freelance Work", "Investment"],
    )
    amount: MoneyDecimal = Field(
        ...,
        ge=Decimal("0.01"),
        description="Income amount (must be positive)",
        examples=["1000.00", "5250.50"],
    )
    deposited: bool = Field(
        default=False,
        description="Whether the income has been deposited into the account",
    )
    account_id: int = Field(
        ..., gt=0, description="ID of the account this income belongs to"
    )
    category_id: Optional[int] = Field(
        None, gt=0, description="ID of the income category (optional)"
    )


class IncomeCreate(IncomeBase):
    """
    Schema for creating a new income record.

    Inherits all fields and validation from IncomeBase.
    """

    pass


class IncomeUpdate(BaseSchemaValidator):
    """
    Schema for updating an income record.

    All fields are optional to allow partial updates.
    All datetime fields are validated to ensure they have UTC timezone.
    """

    date: Optional[datetime] = Field(
        None, description="Updated date of the income (UTC timezone)"
    )
    source: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Updated source of the income"
    )
    amount: Optional[MoneyDecimal] = Field(
        default=None, ge=0, description="Updated income amount"
    )
    deposited: Optional[bool] = Field(None, description="Updated deposit status")
    category_id: Optional[int] = Field(None, gt=0, description="Updated category ID")


class IncomeInDB(IncomeBase):
    """
    Schema for income record in database.

    Extends IncomeBase with database fields.
    All datetime fields are validated to ensure they have UTC timezone.
    """

    id: int = Field(..., description="Unique identifier for the income record")
    created_at: datetime = Field(
        ..., description="Timestamp when the record was created (UTC timezone)"
    )
    updated_at: datetime = Field(
        ..., description="Timestamp when the record was last updated (UTC timezone)"
    )


class IncomeResponse(IncomeInDB):
    """
    Schema for income response.

    Extends IncomeInDB with additional fields for API responses.
    """

    category: Optional[IncomeCategory] = Field(
        None, description="Category information if available"
    )


class IncomeList(BaseSchemaValidator):
    """
    Schema for list of income records.

    Used for paginated responses of income records.
    """

    items: List[IncomeResponse] = Field(..., description="List of income records")
    total: int = Field(..., description="Total number of records matching the query")


class IncomeFilters(BaseSchemaValidator):
    """
    Schema for income filtering parameters.

    Used for filtering income records in queries.
    All datetime fields are validated to ensure they have UTC timezone.
    """

    start_date: Optional[datetime] = Field(
        None,
        description="Start date for filtering (UTC timezone)",
        examples=["2025-01-01T00:00:00Z"],
    )
    end_date: Optional[datetime] = Field(
        None,
        description="End date for filtering (UTC timezone)",
        examples=["2025-12-31T23:59:59Z"],
    )
    source: Optional[str] = Field(
        None, min_length=1, max_length=255, description="Filter by income source"
    )
    deposited: Optional[bool] = Field(None, description="Filter by deposit status")
    min_amount: Optional[MoneyDecimal] = Field(
        default=None, ge=Decimal("0.01"), description="Minimum amount filter"
    )
    max_amount: Optional[MoneyDecimal] = Field(
        default=None, ge=Decimal("0.01"), description="Maximum amount filter"
    )
    account_id: Optional[int] = Field(None, gt=0, description="Filter by account ID")
    category_id: Optional[int] = Field(None, gt=0, description="Filter by category ID")

    @model_validator(mode="after")
    def validate_date_range(self) -> "IncomeFilters":
        """
        Ensure end_date is after start_date if both are provided.

        Returns:
            The validated object

        Raises:
            ValueError: If end_date is not after start_date
        """
        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                raise ValueError("end_date must be after start_date")
        return self

    @model_validator(mode="after")
    def validate_amount_range(self) -> "IncomeFilters":
        """
        Ensure max_amount is greater than min_amount if both are provided.

        Returns:
            The validated object

        Raises:
            ValueError: If max_amount is not greater than min_amount
        """
        if self.min_amount and self.max_amount:
            if self.max_amount <= self.min_amount:
                raise ValueError("max_amount must be greater than min_amount")
        return self
