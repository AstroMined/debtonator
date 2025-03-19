from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Any, Annotated
from pydantic import Field, ConfigDict, field_validator, model_validator

from . import BaseSchemaValidator, MoneyDecimal
from src.core.decimal_precision import DecimalPrecision

# Common validation function for decimal precision
def validate_decimal_precision(value: Decimal, decimal_places: int = 2) -> Decimal:
    """
    Validates that a Decimal value has at most the specified number of decimal places.
    
    Implements the API boundary rule from ADR-013 by ensuring inputs have at most
    2 decimal places for consistency with user expectations.
    
    Args:
        value: The Decimal value to validate
        decimal_places: Maximum number of decimal places allowed (default: 2)
        
    Returns:
        Decimal: The validated value
        
    Raises:
        ValueError: If value has more than the allowed decimal places
    """
    if decimal_places == 2:
        # Use the DecimalPrecision utility for standard API boundary validation
        if not DecimalPrecision.validate_input_precision(value):
            raise ValueError("Amount must have at most 2 decimal places")
    else:
        # For non-standard precision requirements, fall back to manual check
        if isinstance(value, Decimal) and value.as_tuple().exponent < -decimal_places:
            raise ValueError(f"Amount must have at most {decimal_places} decimal places")
    return value

class PaymentSourceBase(BaseSchemaValidator):
    """
    Base schema for payment source data.
    
    Represents a portion of a payment coming from a specific account.
    """
    model_config = ConfigDict(from_attributes=True)
    
    account_id: int = Field(
        ..., 
        gt=0, 
        description="ID of the account used for payment"
    )
    amount: MoneyDecimal = Field(
        ..., 
        gt=Decimal('0'), 
        description="Amount paid from this account"
    )

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount_precision(cls, value: Decimal) -> Decimal:
        """
        Validates that amount has at most 2 decimal places.
        
        Args:
            value: The Decimal value to validate
            
        Returns:
            Decimal: The validated value
            
        Raises:
            ValueError: If value has more than 2 decimal places
        """
        return validate_decimal_precision(value)

class PaymentSourceCreate(PaymentSourceBase):
    """
    Schema for creating a new payment source.
    
    Used when creating a payment source as part of a new payment.
    """
    pass

class PaymentSourceInDB(PaymentSourceBase):
    """
    Schema for payment source data as stored in the database.
    
    Extends the base payment source schema with database-specific fields.
    """
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(
        ...,
        description="Unique identifier for the payment source"
    )
    payment_id: int = Field(
        ...,
        description="ID of the parent payment"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the payment source was created (UTC timezone)"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when the payment source was last updated (UTC timezone)"
    )

class PaymentSourceResponse(PaymentSourceInDB):
    """
    Schema for payment source data in API responses.
    
    Used for returning payment source data in API responses.
    """
    pass

class PaymentBase(BaseSchemaValidator):
    """
    Base schema for payment data.
    
    Defines the common attributes for payment records.
    """
    model_config = ConfigDict(from_attributes=True)
    
    amount: MoneyDecimal = Field(
        ..., 
        gt=Decimal('0'), 
        description="Total payment amount"
    )
    payment_date: datetime = Field(
        ..., 
        description="Date and time of payment (UTC timezone)"
    )
    description: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=500, 
        description="Optional payment description"
    )
    category: str = Field(
        ..., 
        min_length=1, 
        max_length=100, 
        description="Payment category (e.g., 'Bill Payment', 'Credit Card')"
    )

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount_precision(cls, value: Decimal) -> Decimal:
        """
        Validates that amount has at most 2 decimal places.
        
        Args:
            value: The Decimal value to validate
            
        Returns:
            Decimal: The validated value
            
        Raises:
            ValueError: If value has more than 2 decimal places
        """
        return validate_decimal_precision(value)

# Common validation function for payment sources
def validate_payment_sources(sources: List[PaymentSourceCreate], payment_amount: Optional[Decimal] = None) -> List[PaymentSourceCreate]:
    """
    Validates payment sources for consistency and correctness.
    
    Args:
        sources: List of payment sources to validate
        payment_amount: Expected total payment amount (optional)
        
    Returns:
        List[PaymentSourceCreate]: The validated sources
        
    Raises:
        ValueError: If validation fails for any reason
    """
    if not sources:
        raise ValueError("At least one payment source is required")
        
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

class PaymentCreate(PaymentBase):
    """
    Schema for creating a new payment.
    
    Includes references to related entities and payment sources.
    """
    liability_id: Optional[int] = Field(
        None, 
        description="ID of the associated liability, if this payment is for a liability"
    )
    income_id: Optional[int] = Field(
        None, 
        description="ID of the associated income, if this payment is from an income source"
    )
    sources: List[PaymentSourceCreate] = Field(
        ..., 
        description="Payment sources (accounts from which the payment is drawn)"
    )

    @field_validator("sources")
    @classmethod
    def validate_sources(cls, sources: List[PaymentSourceCreate], info: Any) -> List[PaymentSourceCreate]:
        """
        Validate that payment sources total matches payment amount and no duplicate accounts.
        
        Args:
            sources: List of payment sources to validate
            info: Validation context with all data
            
        Returns:
            List[PaymentSourceCreate]: The validated sources
            
        Raises:
            ValueError: If validation fails for any reason
        """
        return validate_payment_sources(sources, info.data.get('amount'))

class PaymentUpdate(BaseSchemaValidator):
    """
    Schema for updating an existing payment.
    
    All fields are optional to allow partial updates.
    """
    model_config = ConfigDict(from_attributes=True)
    
    amount: Optional[MoneyDecimal] = Field(
        None,
        gt=Decimal('0'),
        description="Total payment amount"
    )
    payment_date: Optional[datetime] = Field(
        None,
        description="Date and time of payment (UTC timezone)"
    )
    description: Optional[str] = Field(
        None,
        min_length=1,
        max_length=500,
        description="Optional payment description"
    )
    category: Optional[str] = Field(
        None,
        min_length=1,
        max_length=100,
        description="Payment category (e.g., 'Bill Payment', 'Credit Card')"
    )
    sources: Optional[List[PaymentSourceCreate]] = Field(
        None,
        description="Payment sources (accounts from which the payment is drawn)"
    )

    @field_validator("amount", mode="before")
    @classmethod
    def validate_amount_precision(cls, value: Optional[Decimal]) -> Optional[Decimal]:
        """
        Validates that amount has at most 2 decimal places if provided.
        
        Args:
            value: The optional Decimal value to validate
            
        Returns:
            Optional[Decimal]: The validated value
            
        Raises:
            ValueError: If value has more than 2 decimal places
        """
        if value is not None:
            return validate_decimal_precision(value)
        return value

    @field_validator("sources")
    @classmethod
    def validate_sources_update(cls, sources: Optional[List[PaymentSourceCreate]], info: Any) -> Optional[List[PaymentSourceCreate]]:
        """
        Validate payment sources if they are being updated.
        
        Args:
            sources: Optional list of payment sources to validate
            info: Validation context with all data
            
        Returns:
            Optional[List[PaymentSourceCreate]]: The validated sources
            
        Raises:
            ValueError: If validation fails for any reason
        """
        if sources is not None:
            return validate_payment_sources(sources, info.data.get('amount'))
        return sources

class PaymentInDB(PaymentBase):
    """
    Schema for payment data as stored in the database.
    
    Extends the base payment schema with database-specific fields.
    """
    model_config = ConfigDict(from_attributes=True, populate_by_name=True)

    id: int = Field(
        ...,
        description="Unique identifier for the payment"
    )
    liability_id: Optional[int] = Field(
        None,
        description="ID of the associated liability, if any"
    )
    income_id: Optional[int] = Field(
        None,
        description="ID of the associated income, if any"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the payment was created (UTC timezone)"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when the payment was last updated (UTC timezone)"
    )
    sources: List[PaymentSourceResponse] = Field(
        default_factory=list,
        description="Payment sources associated with this payment"
    )

class PaymentResponse(PaymentInDB):
    """
    Schema for payment data in API responses.
    
    Used for returning payment data in API responses.
    """
    pass

class PaymentDateRange(BaseSchemaValidator):
    """
    Schema for specifying a date range for payment queries.
    
    Used when filtering payments by date range.
    """
    model_config = ConfigDict(from_attributes=True)
    
    start_date: datetime = Field(
        ..., 
        description="Start date and time for payment range (UTC timezone)"
    )
    end_date: datetime = Field(
        ..., 
        description="End date and time for payment range (UTC timezone)"
    )

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, end_date: datetime, info: Any) -> datetime:
        """
        Validates that end_date is after start_date.
        
        Args:
            end_date: The end date to validate
            info: Validation context with all data
            
        Returns:
            datetime: The validated end date
            
        Raises:
            ValueError: If end date is not after start date
        """
        start_date = info.data.get('start_date')
        if start_date is not None and end_date <= start_date:
            raise ValueError("End date must be after start date")
        return end_date
