from datetime import date
from decimal import Decimal
from typing import List
from pydantic import BaseModel, ConfigDict, Field, validator

class BillSplitBase(BaseModel):
    """Base schema for bill split data"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    amount: Decimal = Field(..., gt=0, description="Split amount must be greater than 0")

class BillSplitCreate(BillSplitBase):
    """Schema for creating a new bill split"""
    liability_id: int = Field(..., gt=0)
    account_id: int = Field(..., gt=0)

    @validator('amount')
    @classmethod
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError("Split amount must be greater than 0")
        return v

class BillSplitUpdate(BillSplitBase):
    """Schema for updating an existing bill split"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class BillSplitInDB(BillSplitBase):
    """Schema for bill split data as stored in the database"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    liability_id: int
    account_id: int
    created_at: date
    updated_at: date

class BillSplitResponse(BillSplitInDB):
    """Schema for bill split data in API responses"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

class BillSplitValidation(BaseModel):
    """Schema for validating bill splits"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    liability_id: int = Field(..., gt=0)
    total_amount: Decimal = Field(..., gt=0)
    splits: List[BillSplitCreate]

    @validator('splits')
    @classmethod
    def validate_splits(cls, v, values):
        if not v:
            raise ValueError("At least one split is required")
        
        total_split = sum(split.amount for split in v)
        if 'total_amount' in values and abs(total_split - values['total_amount']) > Decimal('0.01'):
            raise ValueError(
                f"Sum of splits ({total_split}) must equal total amount ({values['total_amount']})"
            )
        
        return v
