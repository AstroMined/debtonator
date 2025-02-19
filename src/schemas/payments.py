from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import Field, ConfigDict, field_validator

from . import BaseSchemaValidator

class PaymentSourceBase(BaseSchemaValidator):
    """Base schema for payment source data"""
    model_config = ConfigDict(from_attributes=True)
    
    account_id: int = Field(..., gt=0, description="ID of the account used for payment")
    amount: Decimal = Field(..., gt=Decimal('0'), description="Amount paid from this account")

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount_precision(cls, value: Decimal) -> Decimal:
        """Validates that amount has at most 2 decimal places."""
        if isinstance(value, Decimal) and value.as_tuple().exponent < -2:
            raise ValueError("Amount must have at most 2 decimal places")
        return value

class PaymentSourceCreate(PaymentSourceBase):
    """Schema for creating a new payment source"""
    pass

class PaymentSourceInDB(PaymentSourceBase):
    """Schema for payment source data as stored in the database"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    payment_id: int
    created_at: datetime
    updated_at: datetime

class PaymentSourceResponse(PaymentSourceInDB):
    """Schema for payment source data in API responses"""
    pass

class PaymentBase(BaseSchemaValidator):
    """Base schema for payment data"""
    model_config = ConfigDict(from_attributes=True)
    
    amount: Decimal = Field(..., gt=Decimal('0'), description="Total payment amount")
    payment_date: datetime = Field(..., description="Date and time of payment (UTC)")
    description: Optional[str] = Field(None, min_length=1, max_length=500, description="Optional payment description")
    category: str = Field(..., min_length=1, max_length=100, description="Payment category")

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount_precision(cls, value: Decimal) -> Decimal:
        """Validates that amount has at most 2 decimal places."""
        if isinstance(value, Decimal) and value.as_tuple().exponent < -2:
            raise ValueError("Amount must have at most 2 decimal places")
        return value

class PaymentCreate(PaymentBase):
    """Schema for creating a new payment"""
    liability_id: Optional[int] = Field(None, description="ID of the associated liability")
    income_id: Optional[int] = Field(None, description="ID of the associated income")
    sources: List[PaymentSourceCreate] = Field(..., description="Payment sources")

    @field_validator("sources")
    @classmethod
    def validate_sources(cls, sources: List[PaymentSourceCreate], info) -> List[PaymentSourceCreate]:
        """Validate that payment sources total matches payment amount and no duplicate accounts."""
        if not sources:
            raise ValueError("At least one payment source is required")
            
        total_sources = sum(source.amount for source in sources)
        amount = info.data.get('amount', Decimal('0'))
        if abs(total_sources - amount) > Decimal('0.01'):
            raise ValueError(
                f"Sum of payment sources ({total_sources}) must equal payment amount ({amount})"
            )
            
        # Check for duplicate accounts
        account_ids = [source.account_id for source in sources]
        if len(account_ids) != len(set(account_ids)):
            raise ValueError("Duplicate account IDs in payment sources")
            
        return sources

class PaymentUpdate(BaseSchemaValidator):
    """Schema for updating an existing payment"""
    model_config = ConfigDict(from_attributes=True)
    
    amount: Optional[Decimal] = None
    payment_date: Optional[datetime] = None
    description: Optional[str] = None
    category: Optional[str] = None
    sources: Optional[List[PaymentSourceCreate]] = None

    @field_validator("sources")
    @classmethod
    def validate_sources_update(cls, sources: Optional[List[PaymentSourceCreate]], info) -> Optional[List[PaymentSourceCreate]]:
        """Validate that payment sources total matches payment amount if sources are being updated."""
        if sources is not None:
            if not sources:
                raise ValueError("At least one payment source is required")
                
            payment_amount = info.data.get('amount')
            if payment_amount is not None:
                total_sources = sum(source.amount for source in sources)
                if abs(total_sources - payment_amount) > Decimal('0.01'):
                    raise ValueError(
                        f"Sum of payment sources ({total_sources}) must equal payment amount ({payment_amount})"
                    )
                
            # Check for duplicate accounts
            account_ids = [source.account_id for source in sources]
            if len(account_ids) != len(set(account_ids)):
                raise ValueError("Duplicate account IDs in payment sources")
                
        return sources

class PaymentInDB(PaymentBase):
    """Schema for payment data as stored in the database"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int
    liability_id: Optional[int]
    income_id: Optional[int]
    created_at: datetime
    updated_at: datetime
    sources: List[PaymentSourceResponse] = Field(default_factory=list)

class PaymentResponse(PaymentInDB):
    """Schema for payment data in API responses"""
    pass

class PaymentDateRange(BaseSchemaValidator):
    """Schema for specifying a date range for payment queries"""
    model_config = ConfigDict(from_attributes=True)
    
    start_date: datetime = Field(..., description="Start date and time for payment range (UTC)")
    end_date: datetime = Field(..., description="End date and time for payment range (UTC)")

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, end_date: datetime, info) -> datetime:
        """Validates that end_date is after start_date."""
        start_date = info.data.get('start_date')
        if start_date is not None and end_date <= start_date:
            raise ValueError("End date must be after start date")
        return end_date
