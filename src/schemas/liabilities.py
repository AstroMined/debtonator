from datetime import datetime
from decimal import Decimal
from typing import Dict, Optional

from pydantic import ConfigDict, Field, model_validator

from src.constants import DEFAULT_CATEGORY_ID
from src.schemas.base_schema import BaseSchemaValidator, MoneyDecimal
from src.utils.datetime_utils import ensure_utc


class AutoPaySettings(BaseSchemaValidator):
    """
    Schema for auto-pay settings.

    Defines the configuration for automatic payments of liabilities including
    timing preferences, payment methods, and notification settings.
    """

    model_config = ConfigDict(from_attributes=True)

    preferred_pay_date: Optional[int] = Field(
        None, description="Preferred day of month for payment (1-31)", ge=1, le=31
    )
    days_before_due: Optional[int] = Field(
        None, description="Days before due date to process payment", ge=0, le=30
    )
    payment_method: str = Field(
        ...,
        min_length=1,
        max_length=50,
        description="Payment method to use for auto-pay",
    )
    minimum_balance_required: Optional[MoneyDecimal] = Field(
        default=None,
        description="Minimum balance required in account before auto-pay is triggered",
    )
    retry_on_failure: bool = Field(
        default=True, description="Whether to retry failed auto-payments"
    )
    notification_email: Optional[str] = Field(
        None,
        max_length=255,
        description="Email address to send auto-pay notifications to",
    )

    @model_validator(mode="after")
    def validate_payment_preferences(self) -> "AutoPaySettings":
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
        ..., min_length=1, max_length=100, description="Name of the liability"
    )
    amount: MoneyDecimal = Field(
        ..., gt=Decimal("0"), description="Total amount of the liability"
    )
    due_date: datetime = Field(
        ..., description="Due date of the liability (UTC timezone)"
    )
    description: Optional[str] = Field(
        None,
        min_length=1,
        max_length=500,
        description="Optional description of the liability",
    )
    category_id: int = Field(..., description="ID of the category for this liability")
    recurring: bool = Field(
        default=False, description="Whether this is a recurring liability"
    )
    recurring_bill_id: Optional[int] = Field(
        None,
        description="ID of the associated recurring bill, if this is linked to a recurring bill",
    )
    recurrence_pattern: Optional[Dict] = Field(
        None, description="Pattern for recurring liabilities (schedule and frequency)"
    )
    primary_account_id: int = Field(
        ..., description="ID of the primary account for this liability"
    )
    auto_pay: bool = Field(
        default=False, description="Whether this liability is set for auto-pay"
    )
    auto_pay_settings: Optional[AutoPaySettings] = Field(
        None, description="Auto-pay configuration settings when auto_pay is true"
    )
    last_auto_pay_attempt: Optional[datetime] = Field(
        None, description="Timestamp of last auto-pay attempt (UTC timezone)"
    )
    auto_pay_enabled: bool = Field(
        default=False,
        description="Whether auto-pay is currently enabled for this liability",
    )
    paid: bool = Field(
        default=False, description="Whether this liability has been paid"
    )


class LiabilityCreate(LiabilityBase):
    """
    Schema for creating a new liability.

    Extends the base liability schema with default category ID
    when none is provided, used specifically for creation operations.
    """

    category_id: int = Field(
        default=DEFAULT_CATEGORY_ID,
        description="ID of the category for this liability, defaults to 'Uncategorized'",
    )


class LiabilityUpdate(BaseSchemaValidator):
    """
    Schema for updating an existing liability.

    Contains all fields from LiabilityBase but makes them optional
    to allow partial updates.
    """

    model_config = ConfigDict(from_attributes=True)

    name: Optional[str] = Field(
        None, min_length=1, max_length=100, description="Name of the liability"
    )
    amount: Optional[MoneyDecimal] = Field(
        default=None, gt=Decimal("0"), description="Total amount of the liability"
    )
    due_date: Optional[datetime] = Field(
        None, description="Due date of the liability (UTC timezone)"
    )
    description: Optional[str] = Field(
        None,
        min_length=1,
        max_length=500,
        description="Optional description of the liability",
    )
    category_id: Optional[int] = Field(
        None, description="ID of the category for this liability"
    )
    recurring: Optional[bool] = Field(
        None, description="Whether this is a recurring liability"
    )
    recurrence_pattern: Optional[Dict] = Field(
        None, description="Pattern for recurring liabilities (schedule and frequency)"
    )
    auto_pay: Optional[bool] = Field(
        None, description="Whether this liability is set for auto-pay"
    )
    auto_pay_settings: Optional[AutoPaySettings] = Field(
        None, description="Auto-pay configuration settings when auto_pay is true"
    )
    auto_pay_enabled: Optional[bool] = Field(
        None, description="Whether auto-pay is currently enabled for this liability"
    )


class AutoPayUpdate(BaseSchemaValidator):
    """
    Schema for updating auto-pay settings.

    Used to enable/disable auto-pay and update its configuration.
    """

    model_config = ConfigDict(from_attributes=True)

    enabled: bool = Field(..., description="Whether to enable or disable auto-pay")
    settings: Optional[AutoPaySettings] = Field(
        None, description="Auto-pay settings to update when enabled is true"
    )


class LiabilityInDB(LiabilityBase):
    """
    Schema for liability data as stored in the database.

    Extends the base liability schema with database-specific fields.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., description="Unique identifier for the liability")
    created_at: datetime = Field(
        ..., description="Timestamp when the liability was created (UTC timezone)"
    )
    updated_at: datetime = Field(
        ..., description="Timestamp when the liability was last updated (UTC timezone)"
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
        ..., description="Start date for liability range (UTC timezone)"
    )
    end_date: datetime = Field(
        ..., description="End date for liability range (UTC timezone)"
    )

    @model_validator(mode="after")
    def validate_date_range(self) -> "LiabilityDateRange":
        """
        Validates that end_date is after start_date.

        Uses ensure_utc to ensure both dates have UTC timezone before comparison,
        following ADR-011 requirements for datetime standardization.

        Returns:
            LiabilityDateRange: The validated object if validation passes

        Raises:
            ValueError: If end date is not after start date
        """
        # Ensure both dates have UTC timezone before comparison
        start_date = ensure_utc(self.start_date)
        end_date = ensure_utc(self.end_date)

        if end_date <= start_date:
            raise ValueError("End date must be after start date")

        return self
