"""
Earned Wage Access (EWA) account schema definitions for polymorphic account validation.

This module defines the schema classes for validating and serializing EWA account data,
extending the base account schemas with EWA-specific fields and validation.

Implemented as part of ADR-019 Banking Account Types Expansion.
"""

from datetime import datetime
from typing import Literal, Optional

from pydantic import Field, field_validator

from src.schemas.accounts import AccountBase, AccountResponse
from src.schemas.base_schema import MoneyDecimal, PercentageDecimal
from src.utils.datetime_utils import ensure_utc


class EWAAccountBase(AccountBase):
    """
    Base schema for Earned Wage Access (EWA) account data with enhanced validation.

    Contains EWA specific attributes and validation logic for early access to earned wages
    through providers like Payactiv, DailyPay, etc.
    """

    # Override account_type to be a fixed literal for EWA accounts
    account_type: Literal["ewa"] = "ewa"

    # EWA-specific fields
    provider: str = Field(
        ...,
        max_length=50,
        description="EWA service provider (Payactiv, DailyPay, etc.)",
    )
    max_advance_percentage: Optional[PercentageDecimal] = Field(
        default=None,
        description="Maximum percent of paycheck available for advance",
        ge=0,
        le=100,
    )
    per_transaction_fee: Optional[MoneyDecimal] = Field(
        default=None, description="Fee charged per advance transaction", ge=0
    )
    pay_period_start: Optional[datetime] = Field(
        default=None, description="Start date of current pay period"
    )
    pay_period_end: Optional[datetime] = Field(
        default=None, description="End date of current pay period"
    )
    next_payday: Optional[datetime] = Field(
        default=None, description="Date of next regular payday"
    )

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, value: str) -> str:
        """
        Validate the EWA provider is a recognized value.

        Args:
            value: The EWA provider to validate

        Returns:
            The validated EWA provider

        Raises:
            ValueError: If EWA provider is not recognized
        """
        valid_providers = [
            "Payactiv",
            "DailyPay",
            "Earnin",
            "Even",
            "FlexWage",
            "Branch",
            "Instant",
            "Rain",
            "Other",
        ]

        if value not in valid_providers:
            raise ValueError(
                f"EWA provider must be one of: {', '.join(valid_providers)}"
            )

        return value

    # Removed reasonableness validator for max_advance_percentage
    # The basic range constraint (0-100%) is still applied by the PercentageDecimal type

    @field_validator("pay_period_end")
    @classmethod
    def validate_pay_period_end(
        cls, value: Optional[datetime], info: dict
    ) -> Optional[datetime]:
        """
        Validate the pay period end date is after the start date.

        Args:
            value: The pay period end date
            info: The validation context

        Returns:
            The validated pay period end date

        Raises:
            ValueError: If pay period end date is before start date
        """
        pay_period_start = info.data.get("pay_period_start")

        if (
            pay_period_start is not None
            and value is not None
            and value < pay_period_start
        ):
            raise ValueError("Pay period end date must be after start date")

        return value

    @field_validator("next_payday")
    @classmethod
    def validate_next_payday(
        cls, value: Optional[datetime], info: dict
    ) -> Optional[datetime]:
        """
        Normalize the next payday datetime to UTC.

        Note: Previously included validation that required next payday to be after
        pay period end date, but this was removed as per ADR-027. Different employers
        have various payment schedules that may not align with this constraint.

        Args:
            value: The next payday date
            info: The validation context

        Returns:
            The validated next payday date with proper timezone handling
        """
        # Skip normalization if value is missing
        if value is None:
            return value

        # Use project's datetime utilities to properly handle timezone awareness
        # and ensure consistent UTC representation according to ADR-011
        normalized_value = ensure_utc(value)

        return normalized_value


class EWAAccountCreate(EWAAccountBase):
    """
    Schema for creating a new EWA account.

    Extends the base EWA account schema for creation operations.
    """


class EWAAccountUpdate(AccountBase):
    """
    Schema for updating an existing EWA account.

    Contains all fields that can be updated for an EWA account,
    with all fields being optional.
    """

    # Override name to make it optional
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="Account name (1-50 characters)",
    )

    # Override account_type to be a fixed literal for EWA accounts
    account_type: Optional[Literal["ewa"]] = None

    # Override balance fields to be None by default (don't update if not provided)
    current_balance: Optional[MoneyDecimal] = Field(
        default=None, description="Current balance"
    )
    available_balance: Optional[MoneyDecimal] = Field(
        default=None, description="Available balance"
    )

    # EWA-specific fields
    provider: Optional[str] = Field(
        default=None,
        max_length=50,
        description="EWA service provider (Payactiv, DailyPay, etc.)",
    )
    max_advance_percentage: Optional[PercentageDecimal] = Field(
        default=None,
        description="Maximum percent of paycheck available for advance",
        ge=0,
        le=100,
    )
    per_transaction_fee: Optional[MoneyDecimal] = Field(
        default=None, description="Fee charged per advance transaction", ge=0
    )
    pay_period_start: Optional[datetime] = Field(
        default=None, description="Start date of current pay period"
    )
    pay_period_end: Optional[datetime] = Field(
        default=None, description="End date of current pay period"
    )
    next_payday: Optional[datetime] = Field(
        default=None, description="Date of next regular payday"
    )

    @field_validator("provider")
    @classmethod
    def validate_provider(cls, value: Optional[str]) -> Optional[str]:
        """
        Validate the EWA provider is a recognized value.

        Args:
            value: The EWA provider to validate

        Returns:
            The validated EWA provider

        Raises:
            ValueError: If EWA provider is not recognized
        """
        if value is None:
            return None

        valid_providers = [
            "Payactiv",
            "DailyPay",
            "Earnin",
            "Even",
            "FlexWage",
            "Branch",
            "Instant",
            "Rain",
            "Other",
        ]

        if value not in valid_providers:
            raise ValueError(
                f"EWA provider must be one of: {', '.join(valid_providers)}"
            )

        return value

    # Removed reasonableness validator for max_advance_percentage
    # The basic range constraint (0-100%) is still applied by the PercentageDecimal type

    @field_validator("pay_period_end")
    @classmethod
    def validate_pay_period_end(
        cls, value: Optional[datetime], info: dict
    ) -> Optional[datetime]:
        """
        Validate the pay period end date is after the start date.

        Args:
            value: The pay period end date
            info: The validation context

        Returns:
            The validated pay period end date

        Raises:
            ValueError: If pay period end date is before start date
        """
        if value is None:
            return None

        pay_period_start = info.data.get("pay_period_start")

        if pay_period_start is not None and value < pay_period_start:
            raise ValueError("Pay period end date must be after start date")

        return value

    @field_validator("next_payday")
    @classmethod
    def validate_next_payday(
        cls, value: Optional[datetime], info: dict
    ) -> Optional[datetime]:
        """
        Normalize the next payday datetime to UTC.

        Args:
            value: The next payday date
            info: The validation context

        Returns:
            The validated next payday date with proper timezone handling
        """
        # Skip normalization if value is missing
        if value is None:
            return value

        # Use project's datetime utilities to properly handle timezone awareness
        # and ensure consistent UTC representation according to ADR-011
        normalized_value = ensure_utc(value)

        return normalized_value


class EWAAccountResponse(EWAAccountBase, AccountResponse):
    """
    Schema for EWA account data in API responses.

    Extends both the base account response schema and EWA account base schema
    to include all fields needed for API responses.

    Note: The inheritance order is important - EWAAccountBase must come first
    to ensure the Literal["ewa"] type for account_type is used instead of the
    string type from AccountResponse. This is required for discriminated unions in Pydantic v2.
    """

    # Explicitly redeclare the account_type field to ensure the Literal type is used
    account_type: Literal["ewa"] = "ewa"
