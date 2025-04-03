"""
Buy Now Pay Later (BNPL) account schema definitions for polymorphic account validation.

This module defines the schema classes for validating and serializing BNPL account data,
extending the base account schemas with BNPL-specific fields and validation.

Implemented as part of ADR-019 Banking Account Types Expansion.
"""

from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import Field, field_validator

from src.schemas.accounts import AccountBase, AccountResponse
from src.schemas.base_schema import MoneyDecimal


class BNPLAccountBase(AccountBase):
    """
    Base schema for Buy Now Pay Later (BNPL) account data with enhanced validation.

    Contains BNPL specific attributes and validation logic for installment-based accounts
    like Affirm, Klarna, Afterpay, etc.
    """

    # Override account_type to be a fixed literal for BNPL accounts
    account_type: Literal["bnpl"] = "bnpl"

    # BNPL-specific fields
    original_amount: MoneyDecimal = Field(
        ..., description="Original purchase amount", gt=0
    )
    installment_count: int = Field(
        ..., description="Total number of installments", gt=0
    )
    installments_paid: int = Field(
        default=0, description="Number of installments already paid", ge=0
    )
    installment_amount: MoneyDecimal = Field(
        ..., description="Amount per installment", gt=0
    )
    payment_frequency: str = Field(
        ..., description="Payment frequency (weekly, biweekly, monthly)"
    )
    next_payment_date: Optional[datetime] = Field(
        default=None, description="Date of next payment due"
    )
    promotion_info: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Promotional details (e.g., '0% interest for 6 months')",
    )
    late_fee: Optional[MoneyDecimal] = Field(
        default=None, description="Late payment fee amount", ge=0
    )
    bnpl_provider: str = Field(
        ...,
        max_length=50,
        description="BNPL service provider (Affirm, Klarna, Afterpay, etc.)",
    )

    @field_validator("payment_frequency")
    @classmethod
    def validate_payment_frequency(cls, value: str) -> str:
        """
        Validate the payment frequency is a recognized value.

        Args:
            value: The payment frequency to validate

        Returns:
            The validated payment frequency

        Raises:
            ValueError: If payment frequency is not recognized
        """
        valid_frequencies = ["weekly", "biweekly", "monthly"]
        if value not in valid_frequencies:
            raise ValueError(
                f"Payment frequency must be one of: {', '.join(valid_frequencies)}"
            )

        return value

    @field_validator("installments_paid")
    @classmethod
    def validate_installments_paid(cls, value: int, info: dict) -> int:
        """
        Validate the installments paid do not exceed the total installment count.

        Args:
            value: The installments paid count
            info: The validation context

        Returns:
            The validated installments paid count

        Raises:
            ValueError: If installments paid exceeds total installment count
        """
        installment_count = info.data.get("installment_count")

        if installment_count is not None and value > installment_count:
            raise ValueError("Installments paid cannot exceed total installment count")

        return value

    @field_validator("installment_amount")
    @classmethod
    def validate_installment_amount(cls, value: Decimal, info: dict) -> Decimal:
        """
        Validate the installment amount against the original amount and installment count.

        Args:
            value: The installment amount
            info: The validation context

        Returns:
            The validated installment amount

        Raises:
            ValueError: If installment amount * count doesn't reasonably match original amount
        """
        original_amount = info.data.get("original_amount")
        installment_count = info.data.get("installment_count")

        if original_amount is not None and installment_count is not None:
            # Calculate expected installment amount
            expected_amount = original_amount / installment_count

            # Allow for small rounding differences (1 cent per installment)
            tolerance = Decimal("0.01") * installment_count

            if abs(value * installment_count - original_amount) > tolerance:
                raise ValueError(
                    "Installment amount * count should approximately equal original amount"
                )

        return value

    @field_validator("bnpl_provider")
    @classmethod
    def validate_bnpl_provider(cls, value: str) -> str:
        """
        Validate the BNPL provider is a recognized value.

        Args:
            value: The BNPL provider to validate

        Returns:
            The validated BNPL provider

        Raises:
            ValueError: If BNPL provider is not recognized
        """
        valid_providers = [
            "Affirm",
            "Klarna",
            "Afterpay",
            "Zip",
            "Sezzle",
            "PayPal Pay in 4",
            "Uplift",
            "Quadpay",
            "Other",
        ]

        if value not in valid_providers:
            raise ValueError(
                f"BNPL provider must be one of: {', '.join(valid_providers)}"
            )

        return value


class BNPLAccountCreate(BNPLAccountBase):
    """
    Schema for creating a new BNPL account.

    Extends the base BNPL account schema for creation operations.
    """


class BNPLAccountResponse(AccountResponse, BNPLAccountBase):
    """
    Schema for BNPL account data in API responses.

    Extends both the base account response schema and BNPL account base schema
    to include all fields needed for API responses.
    """

    # Inherits fields from both AccountResponse and BNPLAccountBase
