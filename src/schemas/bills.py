from datetime import date
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

from .bill_splits import BillSplitResponse

class BillSplitInput(BaseModel):
    """Schema for bill split input during bill creation/update"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    account_id: int
    amount: Decimal

class BillBase(BaseModel):
    """Base schema for bill data"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    bill_name: str = Field(..., description="Name of the bill")
    amount: Decimal = Field(..., description="Total amount of the bill")
    month: str = Field(..., description="Month of the bill")
    day_of_month: int = Field(..., description="Day of the month the bill is due")
    account_id: int = Field(..., description="Primary account ID for the bill")
    account_name: str = Field(..., description="Primary account name")
    auto_pay: bool = Field(default=False, description="Whether the bill is on auto-pay")

class BillCreate(BillBase):
    """Schema for creating a new bill"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    splits: Optional[List[BillSplitInput]] = Field(default_factory=list)

class BillUpdate(BaseModel):
    """Schema for updating an existing bill"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    bill_name: Optional[str] = None
    amount: Optional[Decimal] = None
    month: Optional[str] = None
    day_of_month: Optional[int] = None
    account_id: Optional[int] = None
    account_name: Optional[str] = None
    auto_pay: Optional[bool] = None
    paid: Optional[bool] = None
    paid_date: Optional[date] = None
    splits: Optional[List[BillSplitInput]] = None

class BillInDB(BillBase):
    """Schema for bill data as stored in the database"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    due_date: date
    paid_date: Optional[date] = None
    up_to_date: bool
    paid: bool = False
    created_at: date
    updated_at: date
    splits: List[BillSplitResponse] = Field(default_factory=list)

class BillResponse(BillInDB):
    """Schema for bill data in API responses"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class BillDateRange(BaseModel):
    """Schema for specifying a date range for bill queries"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    start_date: date = Field(..., description="Start date for bill range")
    end_date: date = Field(..., description="End date for bill range")
