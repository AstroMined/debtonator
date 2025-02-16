from datetime import datetime
from decimal import Decimal
from typing import Optional, List, Dict
from pydantic import Field, ConfigDict

from . import BaseSchemaValidator
from .income_categories import IncomeCategory

class RecurringIncomeBase(BaseSchemaValidator):
    """Base schema for recurring income"""
    model_config = ConfigDict(from_attributes=True)

    source: str = Field(..., min_length=1, max_length=255)
    amount: Decimal = Field(..., gt=0)
    day_of_month: int = Field(..., ge=1, le=31)
    account_id: int = Field(..., description="ID of the account this income belongs to")
    category_id: Optional[int] = Field(None, description="ID of the income category")
    auto_deposit: bool = Field(default=False, description="Whether to automatically mark as deposited")

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

    date: datetime = Field(..., description="Date of the income (UTC)")
    source: str = Field(..., min_length=1, max_length=255)
    amount: Decimal = Field(..., ge=0, description="Income amount")
    deposited: bool = Field(default=False)
    account_id: int = Field(..., description="ID of the account this income belongs to")
    category_id: Optional[int] = Field(None, description="ID of the income category")

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

    start_date: Optional[datetime] = Field(None, description="Start date for filtering (UTC)")
    end_date: Optional[datetime] = Field(None, description="End date for filtering (UTC)")
    source: Optional[str] = None
    deposited: Optional[bool] = None
    min_amount: Optional[Decimal] = Field(None, ge=0)
    max_amount: Optional[Decimal] = Field(None, ge=0)
    account_id: Optional[int] = None
    category_id: Optional[int] = None
