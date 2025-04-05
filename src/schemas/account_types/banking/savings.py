"""
Savings account schema definitions for polymorphic account validation.

This module defines the schema classes for validating and serializing savings account data,
extending the base account schemas with savings-specific fields and validation.

Implemented as part of ADR-019 Banking Account Types Expansion.
"""

from decimal import Decimal
from typing import Literal, Optional

from pydantic import Field, field_validator

from src.schemas.accounts import AccountBase, AccountResponse
from src.schemas.base_schema import MoneyDecimal, PercentageDecimal


class SavingsAccountBase(AccountBase):
    """
    Base schema for savings account data with enhanced validation.

    Contains savings account specific attributes and validation logic.
    """

    # Override account_type to be a fixed literal for savings accounts
    account_type: Literal["savings"] = "savings"

    # Savings-specific fields
    interest_rate: Optional[PercentageDecimal] = Field(
        default=None, description="Annual interest rate", ge=0, le=1
    )
    routing_number: Optional[str] = Field(
        default=None, max_length=50, description="Bank routing number"
    )
    compound_frequency: Optional[str] = Field(
        default=None,
        description="Interest compounding frequency (daily, monthly, quarterly, annually)",
    )
    interest_earned_ytd: Optional[MoneyDecimal] = Field(
        default=None, description="Interest earned year-to-date", ge=0
    )
    withdrawal_limit: Optional[int] = Field(
        default=None, description="Maximum number of withdrawals per period", ge=0
    )
    minimum_balance: Optional[MoneyDecimal] = Field(
        default=None, description="Minimum balance required to avoid fees", ge=0
    )

    @field_validator("compound_frequency")
    @classmethod
    def validate_compound_frequency(cls, value: Optional[str]) -> Optional[str]:
        """
        Validate the compound frequency is a recognized value.

        Args:
            value: The compound frequency to validate

        Returns:
            The validated compound frequency

        Raises:
            ValueError: If compound frequency is not recognized
        """
        if value is not None:
            valid_frequencies = ["daily", "monthly", "quarterly", "annually"]
            if value not in valid_frequencies:
                raise ValueError(
                    f"Compound frequency must be one of: {', '.join(valid_frequencies)}"
                )

        return value

    @field_validator("interest_rate")
    @classmethod
    def validate_interest_rate(cls, value: Optional[Decimal]) -> Optional[Decimal]:
        """
        Validate the interest rate is reasonable.

        Args:
            value: The interest rate to validate

        Returns:
            The validated interest rate

        Raises:
            ValueError: If interest rate is unreasonably high
        """
        # Additional validation beyond the field constraint
        if value is not None and value > 20:
            # Warn about unusually high interest rates
            raise ValueError(
                "Interest rate seems unusually high. Please confirm the rate is correct."
            )

        return value


class SavingsAccountCreate(SavingsAccountBase):
    """
    Schema for creating a new savings account.

    Extends the base savings account schema for creation operations.
    """


class SavingsAccountResponse(SavingsAccountBase, AccountResponse):
    """
    Schema for savings account data in API responses.

    Extends both the base account response schema and savings account base schema
    to include all fields needed for API responses.
    
    Note: The inheritance order is important - SavingsAccountBase must come first
    to ensure the Literal["savings"] type for account_type is used instead of the
    string type from AccountResponse. This is required for discriminated unions in Pydantic v2.
    """

    # Explicitly redeclare the account_type field to ensure the Literal type is used
    account_type: Literal["savings"] = "savings"
