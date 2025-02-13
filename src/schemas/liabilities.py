from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional, Dict, Union
from pydantic import BaseModel, Field, ConfigDict, validator

class AutoPaySettings(BaseModel):
    """Schema for auto-pay settings"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    preferred_pay_date: Optional[int] = Field(None, description="Preferred day of month for payment (1-31)", ge=1, le=31)
    days_before_due: Optional[int] = Field(None, description="Days before due date to process payment", ge=0)
    payment_method: str = Field(..., description="Payment method to use for auto-pay")
    minimum_balance_required: Optional[Decimal] = Field(None, description="Minimum balance required in account")
    retry_on_failure: bool = Field(default=True, description="Whether to retry failed auto-payments")
    notification_email: Optional[str] = Field(None, description="Email for auto-pay notifications")

    @validator('preferred_pay_date')
    def validate_preferred_pay_date(cls, v):
        if v is not None and (v < 1 or v > 31):
            raise ValueError('Preferred pay date must be between 1 and 31')
        return v

from typing import List, Optional, Dict
from pydantic import BaseModel, Field, ConfigDict

class LiabilityBase(BaseModel):
    """Base schema for liability data"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    name: str = Field(..., description="Name of the liability")
    amount: Decimal = Field(..., description="Total amount of the liability")
    due_date: date = Field(..., description="Due date of the liability")
    description: Optional[str] = Field(None, description="Optional description")
    category: str = Field(..., description="Category of the liability")
    recurring: bool = Field(default=False, description="Whether this is a recurring liability")
    recurring_bill_id: Optional[int] = Field(None, description="ID of the associated recurring bill")
    recurrence_pattern: Optional[Dict] = Field(None, description="Pattern for recurring liabilities")
    primary_account_id: int = Field(..., description="ID of the primary account for this liability")
    auto_pay: bool = Field(default=False, description="Whether this liability is set for auto-pay")
    auto_pay_settings: Optional[AutoPaySettings] = Field(None, description="Auto-pay configuration settings")
    last_auto_pay_attempt: Optional[datetime] = Field(None, description="Timestamp of last auto-pay attempt")
    auto_pay_enabled: bool = Field(default=False, description="Whether auto-pay is currently enabled")
    paid: bool = Field(default=False, description="Whether this liability has been paid")

class LiabilityCreate(LiabilityBase):
    """Schema for creating a new liability"""
    pass

class LiabilityUpdate(BaseModel):
    """Schema for updating an existing liability"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    name: Optional[str] = None
    amount: Optional[Decimal] = None
    due_date: Optional[date] = None
    description: Optional[str] = None
    category: Optional[str] = None
    recurring: Optional[bool] = None
    recurrence_pattern: Optional[Dict] = None
    auto_pay: Optional[bool] = None
    auto_pay_settings: Optional[AutoPaySettings] = None
    auto_pay_enabled: Optional[bool] = None

class AutoPayUpdate(BaseModel):
    """Schema for updating auto-pay settings"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    enabled: bool = Field(..., description="Whether to enable or disable auto-pay")
    settings: Optional[AutoPaySettings] = Field(None, description="Auto-pay settings to update")

class LiabilityInDB(LiabilityBase):
    """Schema for liability data as stored in the database"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    created_at: datetime
    updated_at: datetime

class LiabilityResponse(LiabilityInDB):
    """Schema for liability data in API responses"""
    pass

class LiabilityDateRange(BaseModel):
    """Schema for specifying a date range for liability queries"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    start_date: date = Field(..., description="Start date for liability range")
    end_date: date = Field(..., description="End date for liability range")
