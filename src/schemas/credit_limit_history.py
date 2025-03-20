from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import Field

from src.schemas import BaseSchemaValidator, MoneyDecimal

class CreditLimitHistoryBase(BaseSchemaValidator):
    """
    Base schema for credit limit history.
    
    Contains the core fields for credit limit history entries.
    All datetime fields are stored in UTC timezone.
    """
    credit_limit: MoneyDecimal = Field(
        ...,
        gt=0,
        description="Credit limit amount in dollars"
    )
    effective_date: datetime = Field(
        ..., 
        description="Date when this credit limit became effective in UTC timezone"
    )
    reason: Optional[str] = Field(
        None, 
        max_length=500,
        description="Reason for credit limit change"
    )

class CreditLimitHistoryCreate(CreditLimitHistoryBase):
    """
    Schema for creating a new credit limit history entry.
    
    Extends the base schema with account_id field.
    """
    account_id: int = Field(
        ...,
        description="ID of the account this credit limit applies to"
    )

class CreditLimitHistoryUpdate(BaseSchemaValidator):
    """
    Schema for updating a credit limit history entry.
    
    Contains all fields that can be updated.
    """
    id: int = Field(..., description="ID of the credit limit history to update")
    credit_limit: Optional[MoneyDecimal] = Field(
        None,
        gt=0,
        description="Credit limit amount in dollars"
    )
    effective_date: Optional[datetime] = Field(
        None, 
        description="Date when this credit limit became effective in UTC timezone"
    )
    reason: Optional[str] = Field(
        None, 
        max_length=500,
        description="Reason for credit limit change"
    )

class CreditLimitHistoryInDB(CreditLimitHistoryBase):
    """
    Schema for credit limit history as stored in the database.
    
    Includes system-generated fields like ID, account_id, and creation timestamp.
    All datetime fields are stored in UTC timezone.
    """
    id: int = Field(
        ...,
        description="Unique identifier for the credit limit history entry"
    )
    account_id: int = Field(
        ...,
        description="ID of the account this credit limit applies to"
    )
    created_at: datetime = Field(
        ...,
        description="Date and time when this record was created in UTC timezone"
    )

class AccountCreditLimitHistoryResponse(BaseSchemaValidator):
    """
    Schema for account credit limit history response.
    
    Contains account information with its complete credit limit history.
    All datetime fields are stored in UTC timezone.
    """
    account_id: int = Field(
        ..., 
        description="Account ID"
    )
    account_name: str = Field(
        ..., 
        description="Account name"
    )
    current_credit_limit: MoneyDecimal = Field(
        ...,
        description="Current credit limit in dollars"
    )
    credit_limit_history: List[CreditLimitHistoryInDB] = Field(
        default_factory=list,
        description="List of historical credit limit changes"
    )
