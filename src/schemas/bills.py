from datetime import date
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

from .bill_splits import BillSplitResponse

class BillBase(BaseModel):
    """Base schema for bill data"""
    bill_name: str = Field(..., description="Name of the bill")
    amount: Decimal = Field(..., description="Total amount of the bill")
    month: str = Field(..., description="Month of the bill")
    day_of_month: int = Field(..., description="Day of the month the bill is due")
    account_id: int = Field(..., description="Primary account ID for the bill")
    account_name: str = Field(..., description="Primary account name")
    auto_pay: bool = Field(default=False, description="Whether the bill is on auto-pay")

class BillCreate(BillBase):
    """Schema for creating a new bill"""
    splits: Optional[List[BillSplitResponse]] = None

class BillUpdate(BaseModel):
    """Schema for updating an existing bill"""
    bill_name: Optional[str] = None
    amount: Optional[Decimal] = None
    month: Optional[str] = None
    day_of_month: Optional[int] = None
    account_id: Optional[int] = None
    account_name: Optional[str] = None
    auto_pay: Optional[bool] = None
    paid: Optional[bool] = None
    paid_date: Optional[date] = None
    splits: Optional[List[BillSplitResponse]] = None

class BillInDB(BillBase):
    """Schema for bill data as stored in the database"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    due_date: date
    paid_date: Optional[date] = None
    up_to_date: bool
    paid: bool = False
    created_at: date
    updated_at: date
    splits: List[BillSplitResponse] = []

class BillResponse(BillInDB):
    """Schema for bill data in API responses"""
    pass

class BillDateRange(BaseModel):
    """Schema for specifying a date range for bill queries"""
    start_date: date = Field(..., description="Start date for bill range")
    end_date: date = Field(..., description="End date for bill range")
