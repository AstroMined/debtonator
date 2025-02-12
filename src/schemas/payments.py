from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from pydantic import BaseModel, Field, ConfigDict

class PaymentSourceBase(BaseModel):
    """Base schema for payment source data"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    account_id: int = Field(..., description="ID of the account used for payment")
    amount: Decimal = Field(..., description="Amount paid from this account")

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

class PaymentBase(BaseModel):
    """Base schema for payment data"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    amount: Decimal = Field(..., description="Total payment amount")
    payment_date: date = Field(..., description="Date of payment")
    description: Optional[str] = Field(None, description="Optional payment description")
    category: str = Field(..., description="Payment category")

class PaymentCreate(PaymentBase):
    """Schema for creating a new payment"""
    liability_id: Optional[int] = Field(None, description="ID of the associated liability")
    income_id: Optional[int] = Field(None, description="ID of the associated income")
    sources: List[PaymentSourceCreate] = Field(..., description="Payment sources")

    def validate_sources(self):
        """Validate that payment sources total matches payment amount"""
        total_sources = sum(source.amount for source in self.sources)
        if total_sources != self.amount:
            raise ValueError(
                f"Sum of payment sources ({total_sources}) must equal payment amount ({self.amount})"
            )

class PaymentUpdate(BaseModel):
    """Schema for updating an existing payment"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    amount: Optional[Decimal] = None
    payment_date: Optional[date] = None
    description: Optional[str] = None
    category: Optional[str] = None
    sources: Optional[List[PaymentSourceCreate]] = None

    def validate_sources(self, payment_amount: Decimal):
        """Validate that payment sources total matches payment amount if sources are being updated"""
        if self.sources is not None:
            total_sources = sum(source.amount for source in self.sources)
            if total_sources != (self.amount or payment_amount):
                raise ValueError(
                    f"Sum of payment sources ({total_sources}) must equal payment amount ({self.amount or payment_amount})"
                )

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

class PaymentDateRange(BaseModel):
    """Schema for specifying a date range for payment queries"""
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)
    
    start_date: date = Field(..., description="Start date for payment range")
    end_date: date = Field(..., description="End date for payment range")
