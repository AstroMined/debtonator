from datetime import date
from decimal import Decimal
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel, ConfigDict, Field, NonNegativeFloat

class AccountType(str, Enum):
    """Valid account types"""
    CREDIT = "credit"
    CHECKING = "checking"
    SAVINGS = "savings"

class AccountBase(BaseModel):
    """Base schema for account data"""
    name: str = Field(..., description="Account name")
    type: AccountType = Field(..., description="Type of account (credit, checking, savings)")
    available_balance: Decimal = Field(default=0, description="Current available balance")
    available_credit: Optional[Decimal] = Field(None, description="Available credit for credit accounts")
    total_limit: Optional[Decimal] = Field(None, description="Total credit limit for credit accounts")
    last_statement_balance: Optional[Decimal] = Field(None, description="Balance from last statement")
    last_statement_date: Optional[date] = Field(None, description="Date of last statement")

class AccountCreate(AccountBase):
    """Schema for creating a new account"""
    pass

class AccountUpdate(BaseModel):
    """Schema for updating an existing account"""
    name: Optional[str] = None
    type: Optional[AccountType] = None
    available_balance: Optional[Decimal] = None
    available_credit: Optional[Decimal] = None
    total_limit: Optional[Decimal] = None
    last_statement_balance: Optional[Decimal] = None
    last_statement_date: Optional[date] = None

class AccountInDB(AccountBase):
    """Schema for account data as stored in the database"""
    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: date
    updated_at: date

class StatementBalanceHistory(BaseModel):
    """Schema for statement balance history"""
    statement_date: date = Field(..., description="Date of the statement")
    statement_balance: Decimal = Field(..., description="Balance on statement date")
    minimum_payment: Optional[Decimal] = Field(None, description="Minimum payment due")
    due_date: Optional[date] = Field(None, description="Payment due date")

class AccountResponse(AccountInDB):
    """Schema for account data in API responses"""
    pass

class AccountStatementHistoryResponse(BaseModel):
    """Schema for account statement history response"""
    account_id: int = Field(..., description="Account ID")
    account_name: str = Field(..., description="Account name")
    statement_history: List[StatementBalanceHistory] = Field(
        default_list=[],
        description="List of historical statement balances"
    )

class AvailableCreditResponse(BaseModel):
    """Schema for available credit calculation response"""
    account_id: int = Field(..., description="Account ID")
    account_name: str = Field(..., description="Account name")
    total_limit: Decimal = Field(..., description="Total credit limit")
    current_balance: Decimal = Field(..., description="Current account balance")
    pending_transactions: Decimal = Field(..., description="Sum of pending transactions")
    adjusted_balance: Decimal = Field(..., description="Balance adjusted for pending transactions")
    available_credit: Decimal = Field(..., description="Available credit after all adjustments")

    model_config = ConfigDict(from_attributes=True)
