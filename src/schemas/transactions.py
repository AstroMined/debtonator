from datetime import datetime
from decimal import Decimal
from typing import Optional
from pydantic import BaseModel, Field, field_validator, ConfigDict
from zoneinfo import ZoneInfo

from src.models.transaction_history import TransactionType

class TransactionBase(BaseModel):
    """Base schema for transaction data"""
    amount: Decimal = Field(..., description="Transaction amount")
    transaction_type: TransactionType = Field(..., description="Type of transaction (credit/debit)")
    description: Optional[str] = Field(None, description="Transaction description")
    transaction_date: datetime = Field(..., description="Date of the transaction (UTC)")

    @field_validator("transaction_date", mode="before")
    @classmethod
    def validate_transaction_date(cls, value: datetime) -> datetime:
        """Ensure transaction date is UTC"""
        if not isinstance(value, datetime):
            raise ValueError("Transaction date must be a datetime object")
        if value.tzinfo is None:
            raise ValueError("Transaction date must be timezone-aware")
        if value.tzinfo != ZoneInfo("UTC"):
            raise ValueError("Transaction date must be in UTC timezone")
        return value

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

    model_config = ConfigDict(from_attributes=True)

    @field_validator("created_at", "updated_at", mode="before")
    @classmethod
    def validate_timestamps(cls, value: datetime) -> datetime:
        """Ensure timestamps are UTC"""
        if not isinstance(value, datetime):
            raise ValueError("Timestamp must be a datetime object")
        if value.tzinfo is None:
            raise ValueError("Timestamp must be timezone-aware")
        if value.tzinfo != ZoneInfo("UTC"):
            raise ValueError("Timestamp must be in UTC timezone")
        return value

class Transaction(TransactionInDB):
    """Schema for transaction data returned to the client"""
    pass

class TransactionList(BaseModel):
    """Schema for list of transactions"""
    items: list[Transaction]
    total: int

    model_config = ConfigDict(from_attributes=True)
