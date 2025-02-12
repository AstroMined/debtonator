from datetime import date
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class CreditLimitHistoryBase(BaseModel):
    """Base schema for credit limit history"""
    credit_limit: Decimal = Field(..., description="Credit limit amount")
    effective_date: date = Field(..., description="Date when this credit limit became effective")
    reason: Optional[str] = Field(None, description="Reason for credit limit change")

class CreditLimitHistoryCreate(CreditLimitHistoryBase):
    """Schema for creating a new credit limit history entry"""
    pass

class CreditLimitHistoryInDB(CreditLimitHistoryBase):
    """Schema for credit limit history as stored in the database"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    account_id: int
    created_at: date

class CreditLimitUpdate(BaseModel):
    """Schema for updating an account's credit limit"""
    credit_limit: Decimal = Field(..., description="New credit limit amount")
    effective_date: date = Field(..., description="Date when this credit limit becomes effective")
    reason: Optional[str] = Field(None, description="Reason for credit limit change")

class AccountCreditLimitHistoryResponse(BaseModel):
    """Schema for account credit limit history response"""
    account_id: int = Field(..., description="Account ID")
    account_name: str = Field(..., description="Account name")
    current_credit_limit: Decimal = Field(..., description="Current credit limit")
    credit_limit_history: List[CreditLimitHistoryInDB] = Field(
        default_list=[],
        description="List of historical credit limit changes"
    )
