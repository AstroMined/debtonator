from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional

from pydantic import Field, field_validator

from src.schemas import BaseSchemaValidator

class DepositScheduleBase(BaseSchemaValidator):
    """
    Base schema for deposit schedules.
    
    Contains the common fields required for deposit schedule operations.
    All datetime fields are stored in UTC timezone.
    """
    income_id: int = Field(
        ..., 
        gt=0,
        description="ID of the income entry associated with this deposit"
    )
    account_id: int = Field(
        ..., 
        gt=0,
        description="ID of the account where the deposit will be made"
    )
    schedule_date: datetime = Field(
        ...,
        description="Scheduled date for the deposit in UTC timezone"
    )
    amount: Decimal = Field(
        ..., 
        gt=0,
        decimal_places=2,
        description="Amount to be deposited"
    )
    recurring: bool = Field(
        False,
        description="Whether this is a recurring deposit"
    )
    recurrence_pattern: Dict | None = Field(
        None,
        description="Pattern details for recurring deposits (e.g., frequency, end date)"
    )
    status: str = Field(
        ..., 
        pattern="^(pending|completed)$",
        description="Current status of the deposit (pending or completed)"
    )
    
    @field_validator("amount")
    @classmethod
    def validate_amount_precision(cls, value: Decimal) -> Decimal:
        """Validate that the amount has at most 2 decimal places."""
        if value.quantize(Decimal("0.01")) != value:
            raise ValueError("Amount must have at most 2 decimal places")
        return value

class DepositScheduleCreate(DepositScheduleBase):
    """
    Schema for creating a new deposit schedule.
    
    Extends the base schema without adding additional fields.
    """
    pass

class DepositScheduleUpdate(BaseSchemaValidator):
    """
    Schema for updating a deposit schedule.
    
    All fields are optional to allow partial updates.
    All datetime fields are stored in UTC timezone.
    """
    schedule_date: datetime | None = Field(
        None,
        description="Updated scheduled date for the deposit in UTC timezone"
    )
    amount: Decimal | None = Field(
        None, 
        gt=0,
        decimal_places=2,
        description="Updated deposit amount"
    )
    recurring: bool | None = Field(
        None,
        description="Updated recurring status"
    )
    recurrence_pattern: Dict | None = Field(
        None,
        description="Updated pattern details for recurring deposits"
    )
    status: str | None = Field(
        None, 
        pattern="^(pending|completed)$",
        description="Updated deposit status (pending or completed)"
    )
    
    @field_validator("amount")
    @classmethod
    def validate_amount_precision(cls, value: Optional[Decimal]) -> Optional[Decimal]:
        """Validate that the amount has at most 2 decimal places."""
        if value is not None and value.quantize(Decimal("0.01")) != value:
            raise ValueError("Amount must have at most 2 decimal places")
        return value

class DepositSchedule(DepositScheduleBase):
    """
    Schema for a complete deposit schedule record.
    
    Includes system-generated fields like ID and timestamps.
    All datetime fields are stored in UTC timezone.
    """
    id: int = Field(
        ...,
        description="Unique identifier for the deposit schedule"
    )
    created_at: datetime = Field(
        ...,
        description="Date and time when the record was created in UTC timezone"
    )
    updated_at: datetime = Field(
        ...,
        description="Date and time when the record was last updated in UTC timezone"
    )
