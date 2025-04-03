"""
Payment app account schema definitions for polymorphic account validation.

This module defines the schema classes for validating and serializing payment app account data,
extending the base account schemas with payment app-specific fields and validation.

Implemented as part of ADR-019 Banking Account Types Expansion.
"""

from typing import Literal, Optional

from pydantic import Field, field_validator

from src.schemas.accounts import AccountBase, AccountResponse


class PaymentAppAccountBase(AccountBase):
    """
    Base schema for payment app account data with enhanced validation.

    Contains payment app specific attributes and validation logic for digital wallet platforms
    like PayPal, Venmo, Cash App, etc.
    """

    # Override account_type to be a fixed literal for payment app accounts
    account_type: Literal["payment_app"] = "payment_app"

    # Payment app-specific fields
    platform: str = Field(
        ...,
        max_length=50,
        description="Payment platform (PayPal, Venmo, Cash App, etc.)",
    )
    has_debit_card: bool = Field(
        default=False, description="Whether account has an associated debit card"
    )
    card_last_four: Optional[str] = Field(
        default=None,
        max_length=4,
        min_length=4,
        description="Last four digits of associated card (if any)",
    )
    linked_account_ids: Optional[str] = Field(
        default=None,
        max_length=255,
        description="Comma-separated list of linked account IDs",
    )
    supports_direct_deposit: bool = Field(
        default=False, description="Whether account supports direct deposit"
    )
    supports_crypto: bool = Field(
        default=False, description="Whether account supports cryptocurrency"
    )

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, value: str) -> str:
        """
        Validate the payment platform is a recognized value.

        Args:
            value: The payment platform to validate

        Returns:
            The validated payment platform

        Raises:
            ValueError: If payment platform is not recognized
        """
        valid_platforms = [
            "PayPal",
            "Venmo",
            "Cash App",
            "Zelle",
            "Apple Pay",
            "Google Pay",
            "Revolut",
            "Wise",
            "Square",
            "Stripe",
            "Other",
        ]

        if value not in valid_platforms:
            raise ValueError(f"Platform must be one of: {', '.join(valid_platforms)}")

        return value

    @field_validator("card_last_four")
    @classmethod
    def validate_card_last_four(cls, value: Optional[str], info: dict) -> Optional[str]:
        """
        Validate the card last four digits are provided when debit card is enabled.

        Args:
            value: The card last four digits
            info: The validation context

        Returns:
            The validated card last four digits

        Raises:
            ValueError: If debit card is enabled but last four digits are not provided
                       or if last four digits are provided but debit card is not enabled
        """
        has_debit_card = info.data.get("has_debit_card", False)

        if has_debit_card and not value:
            raise ValueError(
                "Card last four digits are required when debit card is enabled"
            )

        if not has_debit_card and value:
            raise ValueError(
                "Card last four digits cannot be provided when debit card is not enabled"
            )

        if value is not None and not value.isdigit():
            raise ValueError("Card last four digits must contain only numbers")

        return value

    @field_validator("linked_account_ids")
    @classmethod
    def validate_linked_account_ids(cls, value: Optional[str]) -> Optional[str]:
        """
        Validate the linked account IDs format.

        Args:
            value: The linked account IDs to validate

        Returns:
            The validated linked account IDs

        Raises:
            ValueError: If linked account IDs are not in the correct format
        """
        if value is not None:
            # Verify format is comma-separated integers
            try:
                ids = [int(id_str.strip()) for id_str in value.split(",")]

                # Rebuilt clean comma-separated list
                return ",".join(str(id) for id in ids)
            except ValueError:
                raise ValueError(
                    "Linked account IDs must be a comma-separated list of integers"
                )

        return value


class PaymentAppAccountCreate(PaymentAppAccountBase):
    """
    Schema for creating a new payment app account.

    Extends the base payment app account schema for creation operations.
    """


class PaymentAppAccountResponse(AccountResponse, PaymentAppAccountBase):
    """
    Schema for payment app account data in API responses.

    Extends both the base account response schema and payment app account base schema
    to include all fields needed for API responses.
    """

    # Inherits fields from both AccountResponse and PaymentAppAccountBase
