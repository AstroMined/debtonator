from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Union
from pydantic import Field, ConfigDict, field_validator

from . import BaseSchemaValidator

# Forward declarations
class LiabilityBase(BaseSchemaValidator):
    """Base schema for liability data"""
    model_config = ConfigDict(from_attributes=True)
    
    name: str = Field(..., min_length=1, max_length=100, description="Name of the liability")
    amount: Decimal = Field(..., gt=Decimal('0'), description="Total amount of the liability")
    due_date: datetime = Field(..., description="Due date of the liability (UTC)")

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount_precision(cls, value: Decimal) -> Decimal:
        """Validates that amount has at most 2 decimal places."""
        if isinstance(value, Decimal) and value.as_tuple().exponent < -2:
            raise ValueError("Amount must have at most 2 decimal places")
        return value

    @field_validator("due_date")
    @classmethod
    def validate_due_date_not_past(cls, value: datetime) -> datetime:
        """Validates that due date is not in the past."""
        if value < datetime.now(value.tzinfo):
            raise ValueError("Due date cannot be in the past")
        return value

    description: Optional[str] = Field(None, min_length=1, max_length=500, description="Optional description")
    category_id: int = Field(..., description="ID of the category for this liability")
    recurring: bool = Field(default=False, description="Whether this is a recurring liability")
    recurring_bill_id: Optional[int] = Field(None, description="ID of the associated recurring bill")
    recurrence_pattern: Optional[Dict] = Field(None, description="Pattern for recurring liabilities")
    primary_account_id: int = Field(..., description="ID of the primary account for this liability")
    auto_pay: bool = Field(default=False, description="Whether this liability is set for auto-pay")
    auto_pay_settings: Optional["AutoPaySettings"] = Field(None, description="Auto-pay configuration settings")
    last_auto_pay_attempt: Optional[datetime] = Field(None, description="Timestamp of last auto-pay attempt (UTC)")
    auto_pay_enabled: bool = Field(default=False, description="Whether auto-pay is currently enabled")
    paid: bool = Field(default=False, description="Whether this liability has been paid")

class AutoPaySettings(BaseSchemaValidator):
    """Schema for auto-pay settings"""
    model_config = ConfigDict(from_attributes=True)
    
    preferred_pay_date: Optional[int] = Field(None, description="Preferred day of month for payment (1-31)", ge=1, le=31)
    days_before_due: Optional[int] = Field(None, description="Days before due date to process payment", ge=0, le=30)
    payment_method: str = Field(..., min_length=1, max_length=50, description="Payment method to use for auto-pay")

    @field_validator("days_before_due")
    @classmethod
    def validate_days_before_due(cls, value: Optional[int]) -> Optional[int]:
        """Validates that either preferred_pay_date or days_before_due is set, but not both."""
        if value is not None and 'preferred_pay_date' in cls.__fields__:
            raise ValueError("Cannot set both preferred_pay_date and days_before_due")
        return value
    minimum_balance_required: Optional[Decimal] = Field(None, description="Minimum balance required in account")
    retry_on_failure: bool = Field(default=True, description="Whether to retry failed auto-payments")
    notification_email: Optional[str] = Field(None, description="Email for auto-pay notifications")

class LiabilityCreate(LiabilityBase):
    """Schema for creating a new liability"""
    pass

class LiabilityUpdate(BaseSchemaValidator):
    """Schema for updating an existing liability"""
    model_config = ConfigDict(from_attributes=True)
    
    name: Optional[str] = None
    amount: Optional[Decimal] = None
    due_date: Optional[datetime] = None
    description: Optional[str] = None
    category_id: Optional[int] = None
    recurring: Optional[bool] = None
    recurrence_pattern: Optional[Dict] = None
    auto_pay: Optional[bool] = None
    auto_pay_settings: Optional[AutoPaySettings] = None
    auto_pay_enabled: Optional[bool] = None

class AutoPayUpdate(BaseSchemaValidator):
    """Schema for updating auto-pay settings"""
    model_config = ConfigDict(from_attributes=True)
    
    enabled: bool = Field(..., description="Whether to enable or disable auto-pay")
    settings: Optional[AutoPaySettings] = Field(None, description="Auto-pay settings to update")

class LiabilityInDB(LiabilityBase):
    """Schema for liability data as stored in the database"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime

class LiabilityResponse(LiabilityInDB):
    """Schema for liability data in API responses"""
    model_config = ConfigDict(from_attributes=True)

class LiabilityDateRange(BaseSchemaValidator):
    """Schema for specifying a date range for liability queries"""
    model_config = ConfigDict(from_attributes=True)
    
    start_date: datetime = Field(..., description="Start date for liability range (UTC)")
    end_date: datetime = Field(..., description="End date for liability range (UTC)")

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, end_date: datetime, info) -> datetime:
        """Validates that end_date is after start_date."""
        start_date = info.data.get('start_date')
        if start_date is not None and end_date <= start_date:
            raise ValueError("End date must be after start date")
        return end_date
