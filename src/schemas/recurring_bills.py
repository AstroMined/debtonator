from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import Field, field_validator

from src.schemas import BaseSchemaValidator, MoneyDecimal


class RecurringBillBase(BaseSchemaValidator):
    """
    Base schema for recurring bills.

    Contains the common fields and validation rules for recurring bill operations.
    All datetime fields are stored in UTC timezone.
    """

    bill_name: str = Field(
        ..., min_length=1, max_length=255, description="Name of the recurring bill"
    )
    amount: MoneyDecimal = Field(
        ..., gt=0, description="Amount of the recurring bill in dollars"
    )
    day_of_month: int = Field(
        ..., ge=1, le=31, description="Day of the month when the bill is due"
    )
    account_id: int = Field(
        ..., description="ID of the account associated with this bill"
    )
    category_id: int = Field(
        ..., description="ID of the category associated with this bill"
    )
    auto_pay: bool = Field(
        False, description="Whether the bill is set up for automatic payment"
    )


class RecurringBillCreate(RecurringBillBase):
    """
    Schema for creating a recurring bill.

    Extends the base schema without adding additional fields.
    """

    pass


class RecurringBillUpdate(BaseSchemaValidator):
    """
    Schema for updating a recurring bill.

    All fields are optional to allow partial updates.
    """

    bill_name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Updated name of the recurring bill",
    )
    amount: Optional[MoneyDecimal] = Field(
        default=None,
        gt=0,
        description="Updated amount of the recurring bill in dollars",
    )
    day_of_month: Optional[int] = Field(
        None, ge=1, le=31, description="Updated day of the month when the bill is due"
    )
    account_id: Optional[int] = Field(
        None, description="Updated ID of the account associated with this bill"
    )
    category_id: Optional[int] = Field(
        None, description="Updated ID of the category associated with this bill"
    )
    auto_pay: Optional[bool] = Field(
        None, description="Updated automatic payment setting"
    )
    active: Optional[bool] = Field(
        None, description="Whether the recurring bill is active"
    )


class RecurringBillResponse(RecurringBillBase):
    """
    Schema for recurring bill responses.

    Contains all base fields plus system-generated fields like ID and timestamps.
    All datetime fields are stored in UTC timezone.
    """

    id: int = Field(..., description="Unique identifier for the recurring bill")
    active: bool = Field(
        ..., description="Whether the recurring bill is currently active"
    )
    created_at: datetime = Field(
        ..., description="Date and time when the record was created in UTC timezone"
    )
    updated_at: datetime = Field(
        ...,
        description="Date and time when the record was last updated in UTC timezone",
    )


class GenerateBillsRequest(BaseSchemaValidator):
    """
    Schema for generating bills from a recurring bill pattern.

    Used to create one-time bills from recurring bill templates for a specific month.
    """

    month: int = Field(
        ..., ge=1, le=12, description="Month for which to generate bills (1-12)"
    )
    year: int = Field(
        ..., ge=2000, le=3000, description="Year for which to generate bills"
    )
