"""
Payment app account schema definitions for polymorphic account validation.

This module defines the schema classes for validating and serializing payment app account data,
extending the base account schemas with payment app-specific fields and validation.

Implemented as part of ADR-019 Banking Account Types Expansion.
"""

from typing import Literal, Optional

from pydantic import Field, field_validator, model_validator

from src.schemas.accounts import AccountBase, AccountResponse
from src.schemas.base_schema import MoneyDecimal


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
        Validate the card last four digits format.

        Args:
            value: The card last four digits
            info: The validation context

        Returns:
            The validated card last four digits

        Raises:
            ValueError: If card last four digits are not in the correct format
        """
        # Only validate format if value is provided
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
            except ValueError as exc:
                raise ValueError(
                    "Linked account IDs must be a comma-separated list of integers"
                ) from exc

        return value
        
    @model_validator(mode="after")
    def validate_card_last_four_with_debit_card(self) -> "PaymentAppAccountBase":
        """
        Validate that card_last_four is provided when has_debit_card is True,
        and not provided when has_debit_card is False.
        
        This cross-field validation ensures consistency between the two fields.
        If card_last_four is provided without has_debit_card being explicitly set,
        has_debit_card is implicitly set to True.
        """
        # If card_last_four is provided, implicitly set has_debit_card to True
        # This handles the case where card_last_four is provided without explicitly setting has_debit_card
        if self.card_last_four is not None:
            # Check if has_debit_card was explicitly set to False
            if "__pydantic_fields_set__" in self.__dict__:
                fields_set = self.__dict__["__pydantic_fields_set__"]
                if "has_debit_card" not in fields_set:
                    # Implicitly set has_debit_card to True
                    object.__setattr__(self, "has_debit_card", True)
                    return self
        
        # If has_debit_card is True, card_last_four must be provided
        if self.has_debit_card and not self.card_last_four:
            raise ValueError("Card last four digits are required when debit card is enabled")
            
        # If has_debit_card is False, card_last_four must not be provided
        if not self.has_debit_card and self.card_last_four:
            raise ValueError("Card last four digits cannot be provided when debit card is not enabled")
            
        return self


class PaymentAppAccountCreate(PaymentAppAccountBase):
    """
    Schema for creating a new payment app account.

    Extends the base payment app account schema for creation operations.
    """


class PaymentAppAccountUpdate(AccountBase):
    """
    Schema for updating an existing payment app account.

    Contains all fields that can be updated for a payment app account,
    with all fields being optional.
    """

    # Override name to make it optional
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="Account name (1-50 characters)",
    )

    # Override account_type to be a fixed literal for payment app accounts
    account_type: Optional[Literal["payment_app"]] = None

    # Override balance fields to be None by default (don't update if not provided)
    current_balance: Optional[MoneyDecimal] = Field(
        default=None, description="Current balance"
    )
    available_balance: Optional[MoneyDecimal] = Field(
        default=None, description="Available balance"
    )

    # Payment app-specific fields
    platform: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Payment platform (PayPal, Venmo, Cash App, etc.)",
    )
    has_debit_card: Optional[bool] = Field(
        default=None, description="Whether account has an associated debit card"
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
    supports_direct_deposit: Optional[bool] = Field(
        default=None, description="Whether account supports direct deposit"
    )
    supports_crypto: Optional[bool] = Field(
        default=None, description="Whether account supports cryptocurrency"
    )

    @field_validator("platform")
    @classmethod
    def validate_platform(cls, value: Optional[str]) -> Optional[str]:
        """
        Validate the payment platform is a recognized value.

        Args:
            value: The payment platform to validate

        Returns:
            The validated payment platform

        Raises:
            ValueError: If payment platform is not recognized
        """
        if value is None:
            return None

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
        Validate the card last four digits format.

        Args:
            value: The card last four digits
            info: The validation context

        Returns:
            The validated card last four digits

        Raises:
            ValueError: If card last four digits are not in the correct format
        """
        if value is None:
            return None

        # Only validate format if value is provided
        if not value.isdigit():
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
        if value is None:
            return None

        # Verify format is comma-separated integers
        try:
            ids = [int(id_str.strip()) for id_str in value.split(",")]

            # Rebuilt clean comma-separated list
            return ",".join(str(id) for id in ids)
        except ValueError as exc:
            raise ValueError(
                "Linked account IDs must be a comma-separated list of integers"
            ) from exc
            
    @model_validator(mode="after")
    def validate_card_last_four_with_debit_card(self) -> "PaymentAppAccountUpdate":
        """
        Validate that card_last_four is provided when has_debit_card is True,
        and not provided when has_debit_card is False.
        
        This cross-field validation ensures consistency between the two fields.
        If card_last_four is provided without has_debit_card being explicitly set,
        has_debit_card is implicitly set to True.
        """
        # If card_last_four is provided, implicitly set has_debit_card to True
        # This handles the case where card_last_four is provided without explicitly setting has_debit_card
        if self.card_last_four is not None:
            # Check if has_debit_card was explicitly set to False
            if "__pydantic_fields_set__" in self.__dict__:
                fields_set = self.__dict__["__pydantic_fields_set__"]
                if "has_debit_card" not in fields_set:
                    # Implicitly set has_debit_card to True
                    object.__setattr__(self, "has_debit_card", True)
                    return self
        
        # Only validate if has_debit_card is explicitly set
        if self.has_debit_card is True and not self.card_last_four:
            raise ValueError("Card last four digits are required when debit card is enabled")
            
        if self.has_debit_card is False and self.card_last_four:
            raise ValueError("Card last four digits cannot be provided when debit card is not enabled")
            
        return self


class PaymentAppAccountResponse(PaymentAppAccountBase, AccountResponse):
    """
    Schema for payment app account data in API responses.

    Extends both the base account response schema and payment app account base schema
    to include all fields needed for API responses.

    Note: The inheritance order is important - PaymentAppAccountBase must come first
    to ensure the Literal["payment_app"] type for account_type is used instead of the
    string type from AccountResponse. This is required for discriminated unions in Pydantic v2.
    """

    # Explicitly redeclare the account_type field to ensure the Literal type is used
    account_type: Literal["payment_app"] = "payment_app"
