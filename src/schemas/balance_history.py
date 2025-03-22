from datetime import datetime
from decimal import Decimal
from typing import Literal

from pydantic import Field, field_validator

from src.schemas import BaseSchemaValidator, MoneyDecimal


class BalanceHistoryBase(BaseSchemaValidator):
    """
    Base schema for balance history records.

    Contains the core fields for tracking an account's balance at a specific point in time.
    """

    account_id: int = Field(
        ..., gt=0, description="ID of the account this balance history is for"
    )
    balance: MoneyDecimal = Field(..., description="Current balance of the account")
    available_credit: MoneyDecimal | None = Field(
        default=None,
        description="Available credit for credit accounts (null for non-credit accounts)",
    )
    is_reconciled: bool = Field(
        default=False,
        description="Whether this balance has been reconciled with external records",
    )
    notes: str | None = Field(
        None, max_length=500, description="Optional notes about this balance entry"
    )


class BalanceHistoryCreate(BalanceHistoryBase):
    """
    Schema for creating a new balance history record.

    Extends the base schema without adding additional fields.
    """

    pass


class BalanceHistoryUpdate(BalanceHistoryBase):
    """
    Schema for updating an existing balance history record.

    Extends the base schema and makes all fields optional for partial updates.
    """

    account_id: int | None = Field(
        None, gt=0, description="ID of the account this balance history is for"
    )
    balance: MoneyDecimal | None = Field(None, description="Current balance of the account")
    available_credit: MoneyDecimal | None = Field(
        default=None,
        description="Available credit for credit accounts (null for non-credit accounts)",
    )
    is_reconciled: bool | None = Field(
        None,
        description="Whether this balance has been reconciled with external records",
    )
    notes: str | None = Field(
        None, max_length=500, description="Optional notes about this balance entry"
    )


class BalanceHistory(BalanceHistoryBase):
    """
    Schema for a complete balance history record.

    Includes system-generated fields like ID and timestamps.
    All datetime fields are stored in UTC timezone.
    """

    id: int = Field(..., description="Unique identifier for the balance history record")
    timestamp: datetime = Field(
        ..., description="Point in time when this balance was recorded in UTC timezone"
    )
    created_at: datetime = Field(
        ..., description="Date and time when the record was created in UTC timezone"
    )
    updated_at: datetime = Field(
        ...,
        description="Date and time when the record was last updated in UTC timezone",
    )


class BalanceTrend(BaseSchemaValidator):
    """
    Schema for balance trend analysis.

    Contains metrics describing how an account's balance has changed over time.
    All datetime fields are stored in UTC timezone.
    """

    account_id: int = Field(
        ..., description="ID of the account this trend analysis is for"
    )
    start_date: datetime = Field(
        ..., description="Start date of the analysis period in UTC timezone"
    )
    end_date: datetime = Field(
        ..., description="End date of the analysis period in UTC timezone"
    )
    start_balance: MoneyDecimal = Field(
        ..., description="Balance at the start of the period"
    )
    end_balance: MoneyDecimal = Field(
        ..., description="Balance at the end of the period"
    )
    net_change: MoneyDecimal = Field(
        ...,
        description="Change in balance over the period (end_balance - start_balance)",
    )
    average_balance: MoneyDecimal = Field(
        ..., description="Average balance during the period"
    )
    min_balance: MoneyDecimal = Field(
        ..., description="Minimum balance during the period"
    )
    max_balance: MoneyDecimal = Field(
        ..., description="Maximum balance during the period"
    )
    trend_direction: str = Field(
        ..., description="Direction of the trend (increasing, decreasing, or stable)"
    )
    volatility: MoneyDecimal = Field(
        ..., description="Standard deviation of balance changes during the period"
    )

    @field_validator("trend_direction")
    @classmethod
    def validate_trend_direction(cls, value: str) -> str:
        """Validate that trend_direction is one of the allowed values."""
        valid_directions = ["increasing", "decreasing", "stable"]
        if value not in valid_directions:
            raise ValueError(
                f"trend_direction must be one of: {', '.join(valid_directions)}"
            )
        return value

    @field_validator("start_date", "end_date")
    @classmethod
    def validate_date_range(cls, value: datetime, info: any) -> datetime:
        """Validate that end_date is not before start_date."""
        if info.field_name == "end_date" and "start_date" in info.data:
            start_date = info.data["start_date"]
            if value < start_date:
                raise ValueError("end_date must not be before start_date")
        return value

    @field_validator("net_change")
    @classmethod
    def validate_net_change(cls, value: MoneyDecimal, info: any) -> MoneyDecimal:
        """Validate that net_change equals end_balance - start_balance."""
        if "end_balance" in info.data and "start_balance" in info.data:
            expected_net_change = info.data["end_balance"] - info.data["start_balance"]
            if value != expected_net_change:
                raise ValueError("net_change must equal end_balance - start_balance")
        return value
