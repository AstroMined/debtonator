from datetime import date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field

class IncomeBase(BaseModel):
    """Base schema for income data"""
    date: date
    source: str = Field(..., min_length=1, max_length=255)
    amount: Decimal = Field(..., ge=0, description="Income amount")
    deposited: bool = Field(default=False)
    account_id: int = Field(..., description="ID of the account this income belongs to")

class IncomeCreate(IncomeBase):
    """Schema for creating a new income record"""
    pass

class IncomeUpdate(BaseModel):
    """Schema for updating an income record"""
    date: Optional[date] = None
    source: Optional[str] = Field(None, min_length=1, max_length=255)
    amount: Optional[Decimal] = Field(None, ge=0)
    deposited: Optional[bool] = None

class IncomeInDB(IncomeBase):
    """Schema for income record in database"""
    id: int
    created_at: date
    updated_at: date

    class Config:
        from_attributes = True

class IncomeResponse(IncomeInDB):
    """Schema for income response"""
    pass

class IncomeList(BaseModel):
    """Schema for list of income records"""
    items: List[IncomeResponse]
    total: int

class IncomeFilters(BaseModel):
    """Schema for income filtering parameters"""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    source: Optional[str] = None
    deposited: Optional[bool] = None
    min_amount: Optional[Decimal] = Field(None, ge=0)
    max_amount: Optional[Decimal] = Field(None, ge=0)
    account_id: Optional[int] = None
