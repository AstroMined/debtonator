from datetime import datetime
from decimal import Decimal
from typing import List, Optional

from pydantic import Field

from src.schemas import BaseSchemaValidator

class CreditLimitHistoryBase(BaseSchemaValidator):
    """
    Base schema for credit limit history.
    
    Contains the core fields for credit limit history entries.
    All datetime fields are stored in UTC timezone.
    """
    credit_limit: Decimal = BaseSchemaValidator.money_field(
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
    
    Extends the base schema without adding additional fields.
    """
    pass

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

class CreditLimitUpdate(BaseSchemaValidator):
    """
    Schema for updating an account's credit limit.
    
    Contains all fields needed to create a new credit limit history entry.
    All datetime fields are stored in UTC timezone.
    """
    credit_limit: Decimal = BaseSchemaValidator.money_field(
        gt=0,
        description="New credit limit amount in dollars"
    )
    effective_date: datetime = Field(
        ..., 
        description="Date when this credit limit becomes effective in UTC timezone"
    )
    reason: Optional[str] = Field(
        None, 
        max_length=500,
        description="Reason for credit limit change"
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
    current_credit_limit: Decimal = BaseSchemaValidator.money_field(
        description="Current credit limit in dollars"
    )
    credit_limit_history: List[CreditLimitHistoryInDB] = Field(
        default_factory=list,
        description="List of historical credit limit changes"
    )
