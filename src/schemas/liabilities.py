from datetime import date, datetime
from decimal import Decimal
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
    recurrence_pattern: Optional[Dict] = Field(None, description="Pattern for recurring liabilities")
    primary_account_id: int = Field(..., description="ID of the primary account for this liability")

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
