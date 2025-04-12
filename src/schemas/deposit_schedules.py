from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional

from pydantic import Field

from src.schemas.base_schema import BaseSchemaValidator, MoneyDecimal


class DepositScheduleBase(BaseSchemaValidator):
    """
    Base schema for deposit schedules.

    Contains the common fields required for deposit schedule operations.
    All datetime fields are stored in UTC timezone.
    """

    income_id: int = Field(
        ..., gt=0, description="ID of the income entry associated with this deposit"
    )
    account_id: int = Field(
        ..., gt=0, description="ID of the account where the deposit will be made"
    )
    schedule_date: datetime = Field(
        ..., description="Scheduled date for the deposit in UTC timezone"
    )
    amount: MoneyDecimal = Field(..., gt=0, description="Amount to be deposited")
    source: str = Field(
        default="Other",
        min_length=1,
        max_length=100,
        description="Source of the deposit (e.g., 'Direct Deposit', 'Transfer')",
    )
    recurring: bool = Field(False, description="Whether this is a recurring deposit")
    recurrence_pattern: Optional[Dict] = Field(
        None,
        description="Pattern details for recurring deposits (e.g., frequency, end date)",
    )
    status: str = Field(
        default="pending",
        pattern="^(pending|completed|canceled)$",
        description="Current status of the deposit (pending, completed, or canceled)",
    )

    class Config:
        from_attributes = True

    @classmethod
    def model_validate(cls, obj, *, strict=False, from_attributes=True, context=None):
        """Override to handle both income_id and source fields in legacy data."""
        return super().model_validate(
            obj, strict=strict, from_attributes=from_attributes, context=context
        )

    def model_post_init(self, __context):
        """Validate recurring field and recurrence_pattern consistency."""
        super().model_post_init(__context)

        # Check that recurrence_pattern is provided when recurring is True
        if self.recurring and self.recurrence_pattern is None:
            raise ValueError("Recurrence pattern is required when recurring is True")

        # Check that recurrence_pattern is not provided when recurring is False
        if not self.recurring and self.recurrence_pattern is not None:
            raise ValueError(
                "Recurrence pattern should not be provided when recurring is False"
            )


class DepositScheduleCreate(DepositScheduleBase):
    """
    Schema for creating a new deposit schedule.

    Extends the base schema without adding additional fields.
    """


class DepositScheduleUpdate(BaseSchemaValidator):
    """
    Schema for updating a deposit schedule.

    All fields are optional to allow partial updates.
    All datetime fields are stored in UTC timezone.
    """

    schedule_date: Optional[datetime] = Field(
        None, description="Updated scheduled date for the deposit in UTC timezone"
    )
    amount: Optional[MoneyDecimal] = Field(
        default=None, gt=0, description="Updated deposit amount"
    )
    recurring: Optional[bool] = Field(None, description="Updated recurring status")
    recurrence_pattern: Optional[Dict] = Field(
        None, description="Updated pattern details for recurring deposits"
    )
    status: Optional[str] = Field(
        None,
        pattern="^(pending|completed|canceled)$",
        description="Updated deposit status (pending, completed, or canceled)",
    )


class DepositSchedule(DepositScheduleBase):
    """
    Schema for a complete deposit schedule record.

    Includes system-generated fields like ID and timestamps.
    All datetime fields are stored in UTC timezone.
    """

    id: int = Field(..., description="Unique identifier for the deposit schedule")
    created_at: datetime = Field(
        ..., description="Date and time when the record was created in UTC timezone"
    )
    updated_at: datetime = Field(
        ...,
        description="Date and time when the record was last updated in UTC timezone",
    )


class DepositScheduleResponse(DepositSchedule):
    """
    Schema for API responses containing deposit schedule data.

    Extends the complete deposit schedule record schema with appropriate serialization
    for API responses. All datetime fields are returned in ISO format with UTC timezone.
    """

    class Config:
        json_encoders = {
            # Ensure datetimes are serialized in ISO format with Z suffix for UTC
            datetime: lambda dt: dt.isoformat().replace("+00:00", "Z"),
            # Format Decimal values as floats with 2 decimal places
            Decimal: lambda d: float(d),
        }
