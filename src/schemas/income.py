from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict
from pydantic import Field, ConfigDict, field_validator, model_validator
from zoneinfo import ZoneInfo

from . import BaseSchemaValidator
from .income_categories import IncomeCategory

class RecurringIncomeBase(BaseSchemaValidator):
    """Base schema for recurring income"""
    model_config = ConfigDict(from_attributes=True)

    source: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Source of the recurring income",
        examples=["Monthly Salary", "Rental Income"]
    )
    amount: Decimal = Field(
        ...,
        ge=Decimal('0.01'),
        max_digits=10,
        decimal_places=2,
        description="Income amount (must be positive and have 2 decimal places)",
        examples=["5000.00", "1200.50"]
    )
    day_of_month: int = Field(
        ...,
        ge=1,
        le=31,
        description="Day of the month when income occurs",
        examples=[1, 15, 30]
    )
    account_id: int = Field(
        ...,
        gt=0,
        description="ID of the account this income belongs to"
    )
    category_id: Optional[int] = Field(
        None,
        gt=0,
        description="ID of the income category (optional)"
    )
    auto_deposit: bool = Field(
        default=False,
        description="Whether to automatically mark as deposited"
    )

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount_precision(cls, v: Decimal) -> Decimal:
        """Ensure amount has exactly 2 decimal places"""
        if not isinstance(v, Decimal):
            v = Decimal(str(v))
        if v.as_tuple().exponent != -2:
            raise ValueError("Amount must have exactly 2 decimal places")
        return v

    @field_validator("day_of_month", mode="before")
    @classmethod
    def validate_day_of_month(cls, v: int) -> int:
        """Additional validation for day of month"""
        if v == 31:
            raise ValueError("Day 31 is not supported as it doesn't exist in all months")
        if v == 30:
            # Add a warning in the documentation about months with less than 30 days
            pass
        return v

class RecurringIncomeCreate(RecurringIncomeBase):
    """Schema for creating a recurring income"""
    pass

class RecurringIncomeUpdate(BaseSchemaValidator):
    """Schema for updating a recurring income"""
    model_config = ConfigDict(from_attributes=True)

    source: Optional[str] = Field(None, min_length=1, max_length=255)
    amount: Optional[Decimal] = Field(None, gt=0)
    day_of_month: Optional[int] = Field(None, ge=1, le=31)
    account_id: Optional[int] = None
    category_id: Optional[int] = None
    auto_deposit: Optional[bool] = None
    active: Optional[bool] = None

class RecurringIncomeResponse(RecurringIncomeBase):
    """Schema for recurring income responses"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    active: bool = True
    created_at: datetime
    updated_at: datetime

class GenerateIncomeRequest(BaseSchemaValidator):
    """Schema for generating income entries from a recurring pattern"""
    model_config = ConfigDict(from_attributes=True)

    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2000, le=3000)

class IncomeBase(BaseSchemaValidator):
    """Base schema for income data"""
    model_config = ConfigDict(from_attributes=True)

    date: datetime = Field(
        ...,
        description="Date of the income (UTC)",
        examples=["2025-03-15T00:00:00Z"]
    )
    source: str = Field(
        ...,
        min_length=1,
        max_length=255,
        description="Source of the income",
        examples=["Salary", "Freelance Work", "Investment"]
    )
    amount: Decimal = Field(
        ...,
        ge=Decimal('0.01'),
        max_digits=10,
        decimal_places=2,
        description="Income amount (must be positive and have 2 decimal places)",
        examples=["1000.00", "5250.50"]
    )
    deposited: bool = Field(
        default=False,
        description="Whether the income has been deposited into the account"
    )
    account_id: int = Field(
        ...,
        gt=0,
        description="ID of the account this income belongs to"
    )
    category_id: Optional[int] = Field(
        None,
        gt=0,
        description="ID of the income category (optional)"
    )

    @field_validator("date", mode="before")
    @classmethod
    def validate_utc_datetime(cls, v: datetime) -> datetime:
        """Ensure datetime is UTC"""
        if not isinstance(v, datetime):
            raise ValueError("Must be a datetime object")
        if v.tzinfo is None:
            raise ValueError("Datetime must be UTC")
        if v.tzinfo != ZoneInfo("UTC"):
            raise ValueError("Datetime must be UTC")
        return v

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount_precision(cls, v: Decimal) -> Decimal:
        """Ensure amount has exactly 2 decimal places"""
        if not isinstance(v, Decimal):
            v = Decimal(str(v))
        if v.as_tuple().exponent != -2:
            raise ValueError("Amount must have exactly 2 decimal places")
        return v

class IncomeCreate(IncomeBase):
    """Schema for creating a new income record"""
    pass

class IncomeUpdate(BaseSchemaValidator):
    """Schema for updating an income record"""
    model_config = ConfigDict(from_attributes=True)

    date: Optional[datetime] = Field(None, description="Date of the income (UTC)")
    source: Optional[str] = Field(None, min_length=1, max_length=255)
    amount: Optional[Decimal] = Field(None, ge=0)
    deposited: Optional[bool] = None
    category_id: Optional[int] = None

class IncomeInDB(IncomeBase):
    """Schema for income record in database"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

class IncomeResponse(IncomeInDB):
    """Schema for income response"""
    model_config = ConfigDict(from_attributes=True)

    category: Optional[IncomeCategory] = None

class IncomeList(BaseSchemaValidator):
    """Schema for list of income records"""
    model_config = ConfigDict(from_attributes=True)

    items: List[IncomeResponse]
    total: int

class IncomeFilters(BaseSchemaValidator):
    """Schema for income filtering parameters"""
    model_config = ConfigDict(from_attributes=True)

    start_date: Optional[datetime] = Field(
        None,
        description="Start date for filtering (UTC)",
        examples=["2025-01-01T00:00:00Z"]
    )
    end_date: Optional[datetime] = Field(
        None,
        description="End date for filtering (UTC)",
        examples=["2025-12-31T23:59:59Z"]
    )
    source: Optional[str] = Field(
        None,
        min_length=1,
        max_length=255,
        description="Filter by income source"
    )
    deposited: Optional[bool] = Field(
        None,
        description="Filter by deposit status"
    )
    min_amount: Optional[Decimal] = Field(
        None,
        ge=Decimal('0.01'),
        max_digits=10,
        decimal_places=2,
        description="Minimum amount filter"
    )
    max_amount: Optional[Decimal] = Field(
        None,
        ge=Decimal('0.01'),
        max_digits=10,
        decimal_places=2,
        description="Maximum amount filter"
    )

    account_id: Optional[int] = Field(
        None,
        gt=0,
        description="Filter by account ID"
    )
    category_id: Optional[int] = Field(
        None,
        gt=0,
        description="Filter by category ID"
    )

    @field_validator("min_amount", "max_amount", mode="before")
    @classmethod
    def validate_amount_precision(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """Ensure amount has exactly 2 decimal places when provided"""
        if v is None:
            return v
        if not isinstance(v, Decimal):
            v = Decimal(str(v))
        if v.as_tuple().exponent != -2:
            raise ValueError("Amount must have exactly 2 decimal places")
        return v

    @field_validator("start_date", "end_date", mode="before")
    @classmethod
    def validate_filter_datetime(cls, v: Optional[datetime]) -> Optional[datetime]:
        """Ensure datetime is UTC when provided"""
        if v is None:
            return v
        if not isinstance(v, datetime):
            raise ValueError("Must be a datetime object")
        if v.tzinfo is None:
            raise ValueError("Datetime must be UTC")
        if v.tzinfo != ZoneInfo("UTC"):
            raise ValueError("Datetime must be UTC")
        return v

    @model_validator(mode="after")
    def validate_date_range(self) -> "IncomeFilters":
        """Ensure end_date is after start_date if both are provided"""
        if self.start_date and self.end_date:
            if self.end_date <= self.start_date:
                raise ValueError("end_date must be after start_date")
        return self

    @model_validator(mode="after")
    def validate_amount_range(self) -> "IncomeFilters":
        """Ensure max_amount is greater than min_amount if both are provided"""
        if self.min_amount and self.max_amount:
            if self.max_amount <= self.min_amount:
                raise ValueError("max_amount must be greater than min_amount")
        return self
