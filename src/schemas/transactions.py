from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field

from src.models.transaction_history import TransactionType

class TransactionBase(BaseModel):
    """Base schema for transaction data"""
    amount: Decimal = Field(..., description="Transaction amount")
    transaction_type: TransactionType = Field(..., description="Type of transaction (credit/debit)")
    description: Optional[str] = Field(None, description="Transaction description")
    transaction_date: datetime = Field(..., description="Date of the transaction")

class TransactionCreate(TransactionBase):
    """Schema for creating a new transaction"""
    pass

class TransactionUpdate(TransactionBase):
    """Schema for updating an existing transaction"""
    amount: Optional[Decimal] = None
    transaction_type: Optional[TransactionType] = None
    transaction_date: Optional[datetime] = None

class TransactionInDB(TransactionBase):
    """Schema for transaction data as stored in the database"""
    id: int
    account_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        """Pydantic config"""
        from_attributes = True

class Transaction(TransactionInDB):
    """Schema for transaction data returned to the client"""
    pass

class TransactionList(BaseModel):
    """Schema for list of transactions"""
    items: list[Transaction]
    total: int
