from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, Union, Any
from pydantic import Field, ConfigDict, field_validator, model_validator

from . import BaseSchemaValidator
from src.core.decimal_precision import DecimalPrecision

class AutoPaySettings(BaseSchemaValidator):
    """
    Schema for auto-pay settings.
    
    Defines the configuration for automatic payments of liabilities including
    timing preferences, payment methods, and notification settings.
    """
    model_config = ConfigDict(from_attributes=True)
    
    preferred_pay_date: Optional[int] = Field(
        None, 
        description="Preferred day of month for payment (1-31)", 
        ge=1, 
        le=31
    )
    days_before_due: Optional[int] = Field(
        None, 
        description="Days before due date to process payment", 
        ge=0, 
        le=30
    )
    payment_method: str = Field(
        ..., 
        min_length=1, 
        max_length=50, 
        description="Payment method to use for auto-pay"
    )
    minimum_balance_required: Optional[Decimal] = BaseSchemaValidator.money_field(
        default=None,
        description="Minimum balance required in account before auto-pay is triggered"
    )
    retry_on_failure: bool = Field(
        default=True, 
        description="Whether to retry failed auto-payments"
    )
    notification_email: Optional[str] = Field(
        None, 
        max_length=255,
        description="Email address to send auto-pay notifications to"
    )

    @model_validator(mode='after')
    def validate_payment_preferences(self) -> 'AutoPaySettings':
        """
        Validates that either preferred_pay_date or days_before_due is set, but not both.
        
        Args:
            None (uses object attributes)
            
        Returns:
            AutoPaySettings: The validated object if validation passes
            
        Raises:
            ValueError: If both preferred_pay_date and days_before_due are set
        """
        if self.preferred_pay_date is not None and self.days_before_due is not None:
            raise ValueError("Cannot set both preferred_pay_date and days_before_due")
        return self


class LiabilityBase(BaseSchemaValidator):
    """
    Base schema for liability data.
    
    Contains the common attributes and validation logic for liabilities 
    throughout the application.
    """
    model_config = ConfigDict(from_attributes=True)
    
    name: str = Field(
        ..., 
        min_length=1, 
        max_length=100, 
        description="Name of the liability"
    )
    amount: Decimal = BaseSchemaValidator.money_field(
        gt=Decimal('0'),
        description="Total amount of the liability"
    )
    due_date: datetime = Field(
        ..., 
        description="Due date of the liability (UTC timezone)"
    )
    description: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=500, 
        description="Optional description of the liability"
    )
    category_id: int = Field(
        ..., 
        description="ID of the category for this liability"
    )
    recurring: bool = Field(
        default=False, 
        description="Whether this is a recurring liability"
    )
    recurring_bill_id: Optional[int] = Field(
        None, 
        description="ID of the associated recurring bill, if this is linked to a recurring bill"
    )
    recurrence_pattern: Optional[Dict] = Field(
        None, 
        description="Pattern for recurring liabilities (schedule and frequency)"
    )
    primary_account_id: int = Field(
        ..., 
        description="ID of the primary account for this liability"
    )
    auto_pay: bool = Field(
        default=False, 
        description="Whether this liability is set for auto-pay"
    )
    auto_pay_settings: Optional[AutoPaySettings] = Field(
        None, 
        description="Auto-pay configuration settings when auto_pay is true"
    )
    last_auto_pay_attempt: Optional[datetime] = Field(
        None, 
        description="Timestamp of last auto-pay attempt (UTC timezone)"
    )
    auto_pay_enabled: bool = Field(
        default=False, 
        description="Whether auto-pay is currently enabled for this liability"
    )
    paid: bool = Field(
        default=False, 
        description="Whether this liability has been paid"
    )

    @field_validator("due_date")
    @classmethod
    def validate_due_date_not_past(cls, value: datetime) -> datetime:
        """
        Validates that due date is not in the past.
        
        Args:
            value: The datetime value to validate
            
        Returns:
            datetime: The validated value
            
        Raises:
            ValueError: If due date is in the past
        """
        if value < datetime.now(value.tzinfo):
            raise ValueError("Due date cannot be in the past")
        return value


class LiabilityCreate(LiabilityBase):
    """
    Schema for creating a new liability.
    
    Extends the base liability schema without adding additional fields,
    used specifically for creation operations.
    """
    pass


class LiabilityUpdate(BaseSchemaValidator):
    """
    Schema for updating an existing liability.
    
    Contains all fields from LiabilityBase but makes them optional
    to allow partial updates.
    """
    model_config = ConfigDict(from_attributes=True)
    
    name: Optional[str] = Field(
        None,
        min_length=1, 
        max_length=100, 
        description="Name of the liability"
    )
    amount: Optional[Decimal] = BaseSchemaValidator.money_field(
        default=None,
        gt=Decimal('0'), 
        description="Total amount of the liability"
    )
    due_date: Optional[datetime] = Field(
        None, 
        description="Due date of the liability (UTC timezone)"
    )
    description: Optional[str] = Field(
        None, 
        min_length=1, 
        max_length=500, 
        description="Optional description of the liability"
    )
    category_id: Optional[int] = Field(
        None, 
        description="ID of the category for this liability"
    )
    recurring: Optional[bool] = Field(
        None, 
        description="Whether this is a recurring liability"
    )
    recurrence_pattern: Optional[Dict] = Field(
        None, 
        description="Pattern for recurring liabilities (schedule and frequency)"
    )
    auto_pay: Optional[bool] = Field(
        None, 
        description="Whether this liability is set for auto-pay"
    )
    auto_pay_settings: Optional[AutoPaySettings] = Field(
        None, 
        description="Auto-pay configuration settings when auto_pay is true"
    )
    auto_pay_enabled: Optional[bool] = Field(
        None, 
        description="Whether auto-pay is currently enabled for this liability"
    )

    @field_validator("due_date")
    @classmethod
    def validate_due_date_not_past(cls, value: Optional[datetime]) -> Optional[datetime]:
        """
        Validates that due date is not in the past.
        
        Args:
            value: The optional datetime value to validate
            
        Returns:
            Optional[datetime]: The validated value
            
        Raises:
            ValueError: If due date is in the past
        """
        if value is not None and value < datetime.now(value.tzinfo):
            raise ValueError("Due date cannot be in the past")
        return value


class AutoPayUpdate(BaseSchemaValidator):
    """
    Schema for updating auto-pay settings.
    
    Used to enable/disable auto-pay and update its configuration.
    """
    model_config = ConfigDict(from_attributes=True)
    
    enabled: bool = Field(
        ..., 
        description="Whether to enable or disable auto-pay"
    )
    settings: Optional[AutoPaySettings] = Field(
        None, 
        description="Auto-pay settings to update when enabled is true"
    )


class LiabilityInDB(LiabilityBase):
    """
    Schema for liability data as stored in the database.
    
    Extends the base liability schema with database-specific fields.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int = Field(
        ...,
        description="Unique identifier for the liability"
    )
    created_at: datetime = Field(
        ...,
        description="Timestamp when the liability was created (UTC timezone)"
    )
    updated_at: datetime = Field(
        ...,
        description="Timestamp when the liability was last updated (UTC timezone)"
    )


class LiabilityResponse(LiabilityInDB):
    """
    Schema for liability data in API responses.
    
    Extends the database schema for proper serialization in API responses.
    """
    model_config = ConfigDict(from_attributes=True)


class LiabilityDateRange(BaseSchemaValidator):
    """
    Schema for specifying a date range for liability queries.
    
    Used for filtering liabilities by date range in API requests.
    """
    model_config = ConfigDict(from_attributes=True)
    
    start_date: datetime = Field(
        ..., 
        description="Start date for liability range (UTC timezone)"
    )
    end_date: datetime = Field(
        ..., 
        description="End date for liability range (UTC timezone)"
    )

    @field_validator("end_date")
    @classmethod
    def validate_date_range(cls, end_date: datetime, info: Any) -> datetime:
        """
        Validates that end_date is after start_date.
        
        Args:
            end_date: The end date to validate
            info: The validation context containing all data
            
        Returns:
            datetime: The validated end date
            
        Raises:
            ValueError: If end date is not after start date
        """
        start_date = info.data.get('start_date')
        if start_date is not None and end_date <= start_date:
            raise ValueError("End date must be after start date")
        return end_date
