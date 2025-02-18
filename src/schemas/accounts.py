from datetime import datetime
from decimal import Decimal
from typing import Optional, List
from enum import Enum
from pydantic import ConfigDict, Field, field_validator
from . import BaseSchemaValidator

class AccountType(str, Enum):
    """Valid account types"""
    CREDIT = "credit"
    CHECKING = "checking"
    SAVINGS = "savings"

class AccountBase(BaseSchemaValidator):
    """Base schema for account data with enhanced validation"""
    name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Account name (1-50 characters)"
    )
    type: AccountType = Field(
        ...,
        description="Type of account (credit, checking, savings)"
    )
    available_balance: Decimal = Field(
        default=0,
        decimal_places=2,
        description="Current available balance"
    )
    available_credit: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Available credit for credit accounts"
    )
    total_limit: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Total credit limit for credit accounts"
    )
    last_statement_balance: Optional[Decimal] = Field(
        None,
        decimal_places=2,
        description="Balance from last statement"
    )
    last_statement_date: Optional[datetime] = Field(
        None,
        description="Date of last statement (UTC)"
    )

    @field_validator("total_limit")
    @classmethod
    def validate_total_limit(cls, v: Optional[Decimal], info) -> Optional[Decimal]:
        """Validate total_limit based on account type"""
        if v is not None and info.data.get("type") != AccountType.CREDIT:
            raise ValueError("Total limit can only be set for credit accounts")
        return v

    @field_validator("available_credit")
    @classmethod
    def validate_available_credit(cls, v: Optional[Decimal], info) -> Optional[Decimal]:
        """Validate available_credit based on account type"""
        if v is not None and info.data.get("type") != AccountType.CREDIT:
            raise ValueError("Available credit can only be set for credit accounts")
        return v

class AccountCreate(AccountBase):
    """Schema for creating a new account"""
    pass

class AccountUpdate(BaseSchemaValidator):
    """Schema for updating an existing account"""
    name: Optional[str] = Field(
        None,
        min_length=1,
        max_length=50,
        description="Account name (1-50 characters)"
    )
    type: Optional[AccountType] = Field(
        None,
        description="Type of account (credit, checking, savings)"
    )
    available_balance: Optional[Decimal] = Field(
        None,
        decimal_places=2,
        description="Current available balance"
    )
    available_credit: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Available credit for credit accounts"
    )
    total_limit: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Total credit limit for credit accounts"
    )
    last_statement_balance: Optional[Decimal] = Field(
        None,
        decimal_places=2,
        description="Balance from last statement"
    )
    last_statement_date: Optional[datetime] = Field(
        None,
        description="Date of last statement (UTC)"
    )

    @field_validator("total_limit")
    @classmethod
    def validate_total_limit(cls, v: Optional[Decimal], info) -> Optional[Decimal]:
        """Validate total_limit based on account type"""
        if v is not None and info.data.get("type") == AccountType.CREDIT:
            return v
        elif v is not None:
            raise ValueError("Total limit can only be set for credit accounts")
        return v

    @field_validator("available_credit")
    @classmethod
    def validate_available_credit(cls, v: Optional[Decimal], info) -> Optional[Decimal]:
        """Validate available_credit based on account type"""
        if v is not None and info.data.get("type") == AccountType.CREDIT:
            return v
        elif v is not None:
            raise ValueError("Available credit can only be set for credit accounts")
        return v

class AccountInDB(AccountBase):
    """Schema for account data as stored in the database"""
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., gt=0, description="Account ID")
    created_at: datetime
    updated_at: datetime

class StatementBalanceHistory(BaseSchemaValidator):
    """Schema for statement balance history"""
    statement_date: datetime = Field(
        ...,
        description="Date of the statement (UTC)"
    )
    statement_balance: Decimal = Field(
        ...,
        decimal_places=2,
        description="Balance on statement date"
    )
    minimum_payment: Optional[Decimal] = Field(
        None,
        ge=0,
        decimal_places=2,
        description="Minimum payment due"
    )
    due_date: Optional[datetime] = Field(
        None,
        description="Payment due date (UTC)"
    )

class AccountResponse(AccountInDB):
    """Schema for account data in API responses"""
    pass

class AccountStatementHistoryResponse(BaseSchemaValidator):
    """Schema for account statement history response"""
    account_id: int = Field(..., description="Account ID")
    account_name: str = Field(..., description="Account name")
    statement_history: List[StatementBalanceHistory] = Field(
        default_list=[],
        description="List of historical statement balances"
    )

class AvailableCreditResponse(BaseSchemaValidator):
    """Schema for available credit calculation response"""
    account_id: int = Field(
        ...,
        gt=0,
        description="Account ID"
    )
    account_name: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Account name"
    )
    total_limit: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        description="Total credit limit"
    )
    current_balance: Decimal = Field(
        ...,
        decimal_places=2,
        description="Current account balance"
    )
    pending_transactions: Decimal = Field(
        ...,
        decimal_places=2,
        description="Sum of pending transactions"
    )
    adjusted_balance: Decimal = Field(
        ...,
        decimal_places=2,
        description="Balance adjusted for pending transactions"
    )
    available_credit: Decimal = Field(
        ...,
        ge=0,
        decimal_places=2,
        description="Available credit after all adjustments"
    )

    model_config = ConfigDict(from_attributes=True)
