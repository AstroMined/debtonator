from datetime import datetime
from decimal import Decimal
from typing import Optional

from pydantic import Field, field_validator

from src.schemas import BaseSchemaValidator

class PaymentScheduleBase(BaseSchemaValidator):
    """
    Base schema for payment schedules.
    
    Contains the common fields required for payment schedule operations.
    All datetime fields are stored in UTC timezone.
    """
    liability_id: int = Field(
        ...,
        gt=0,
        description="ID of the liability this payment is for"
    )
    scheduled_date: datetime = Field(
        ...,
        description="Scheduled date for the payment in UTC timezone"
    )
    amount: Decimal = Field(
        ...,
        gt=0,
        decimal_places=2,
        description="Amount to be paid"
    )
    account_id: int = Field(
        ...,
        gt=0,
        description="ID of the account from which payment will be made"
    )
    description: str | None = Field(
        None,
        max_length=500,
        description="Optional description of the payment"
    )
    auto_process: bool = Field(
        False,
        description="Whether this payment should be automatically processed"
    )
    
    @field_validator("amount")
    @classmethod
    def validate_amount_precision(cls, value: Decimal) -> Decimal:
        """Validate that the amount has at most 2 decimal places."""
        if value.quantize(Decimal("0.01")) != value:
            raise ValueError("Amount must have at most 2 decimal places")
        return value

class PaymentScheduleCreate(PaymentScheduleBase):
    """
    Schema for creating a new payment schedule.
    
    Extends the base schema without adding additional fields.
    """
    pass

class PaymentScheduleUpdate(BaseSchemaValidator):
    """
    Schema for updating a payment schedule.
    
    All fields are optional to allow partial updates.
    All datetime fields are stored in UTC timezone.
    """
    scheduled_date: datetime | None = Field(
        None,
        description="Updated scheduled date for the payment in UTC timezone"
    )
    amount: Decimal | None = Field(
        None,
        gt=0,
        decimal_places=2,
        description="Updated payment amount"
    )
    account_id: int | None = Field(
        None,
        gt=0,
        description="Updated account ID for the payment"
    )
    description: str | None = Field(
        None,
        max_length=500,
        description="Updated description of the payment"
    )
    auto_process: bool | None = Field(
        None,
        description="Updated auto-process setting"
    )
    processed: bool | None = Field(
        None,
        description="Updated processed status"
    )
    
    @field_validator("amount")
    @classmethod
    def validate_amount_precision(cls, value: Optional[Decimal]) -> Optional[Decimal]:
        """Validate that the amount has at most 2 decimal places."""
        if value is not None and value.quantize(Decimal("0.01")) != value:
            raise ValueError("Amount must have at most 2 decimal places")
        return value

class PaymentSchedule(PaymentScheduleBase):
    """
    Schema for a complete payment schedule record.
    
    Includes system-generated fields like ID, processing status, and timestamps.
    All datetime fields are stored in UTC timezone.
    """
    id: int = Field(
        ...,
        description="Unique identifier for the payment schedule"
    )
    processed: bool = Field(
        False,
        description="Whether this payment has been processed"
    )
    processed_date: datetime | None = Field(
        None,
        description="Date and time when the payment was processed in UTC timezone"
    )
    created_at: datetime = Field(
        ...,
        description="Date and time when the record was created in UTC timezone"
    )
    updated_at: datetime = Field(
        ...,
        description="Date and time when the record was last updated in UTC timezone"
    )
