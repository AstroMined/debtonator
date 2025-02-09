from datetime import date
from decimal import Decimal
from pydantic import BaseModel, ConfigDict

class BillSplitBase(BaseModel):
    """Base schema for bill split data"""
    amount: Decimal

class BillSplitCreate(BillSplitBase):
    """Schema for creating a new bill split"""
    bill_id: int
    account_id: int

class BillSplitUpdate(BillSplitBase):
    """Schema for updating an existing bill split"""
    pass

class BillSplitInDB(BillSplitBase):
    """Schema for bill split data as stored in the database"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    bill_id: int
    account_id: int
    created_at: date
    updated_at: date

class BillSplitResponse(BillSplitInDB):
    """Schema for bill split data in API responses"""
    pass
