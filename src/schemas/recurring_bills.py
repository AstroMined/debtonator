from datetime import date
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field

class RecurringBillBase(BaseModel):
    """Base schema for recurring bills"""
    bill_name: str = Field(..., min_length=1, max_length=255)
    amount: Decimal = Field(..., gt=0)
    day_of_month: int = Field(..., ge=1, le=31)
    account_id: int
    auto_pay: bool = False

class RecurringBillCreate(RecurringBillBase):
    """Schema for creating a recurring bill"""
    pass

class RecurringBillUpdate(BaseModel):
    """Schema for updating a recurring bill"""
    bill_name: Optional[str] = Field(None, min_length=1, max_length=255)
    amount: Optional[Decimal] = Field(None, gt=0)
    day_of_month: Optional[int] = Field(None, ge=1, le=31)
    account_id: Optional[int] = None
    auto_pay: Optional[bool] = None
    active: Optional[bool] = None

class RecurringBillResponse(RecurringBillBase):
    """Schema for recurring bill responses"""
    id: int
    active: bool
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True

class GenerateBillsRequest(BaseModel):
    """Schema for generating bills from a recurring bill pattern"""
    month: int = Field(..., ge=1, le=12)
    year: int = Field(..., ge=2000, le=3000)
