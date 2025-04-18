"""
Checking account schema definitions for polymorphic account validation.

This module defines the schema classes for validating and serializing checking account data,
extending the base account schemas with checking-specific fields and validation.

Implemented as part of ADR-019 Banking Account Types Expansion.
"""

from decimal import Decimal
from typing import Literal, Optional

from pydantic import Field, field_validator

from src.schemas.accounts import AccountBase, AccountResponse
from src.schemas.base_schema import MoneyDecimal, PercentageDecimal


class CheckingAccountBase(AccountBase):
    """
    Base schema for checking account data with enhanced validation.

    Contains checking account specific attributes and validation logic.
    """

    # Override account_type to be a fixed literal for checking accounts
    account_type: Literal["checking"] = "checking"

    # Checking-specific fields
    routing_number: Optional[str] = Field(
        default=None, max_length=50, description="Account routing number"
    )
    has_overdraft_protection: bool = Field(
        default=False, description="Whether overdraft protection is enabled"
    )
    overdraft_limit: Optional[MoneyDecimal] = Field(
        default=None,
        description="Maximum overdraft amount (when protection is enabled)",
        ge=0,
    )
    monthly_fee: Optional[MoneyDecimal] = Field(
        default=None, description="Monthly account maintenance fee", ge=0
    )
    interest_rate: Optional[PercentageDecimal] = Field(
        default=None,
        description="Annual interest rate (if interest-bearing)",
        ge=0,
        le=100,
    )

    # International banking fields
    iban: Optional[str] = Field(
        default=None, max_length=50, description="International Bank Account Number"
    )
    swift_bic: Optional[str] = Field(
        default=None,
        max_length=20,
        description="SWIFT/BIC code for international transfers",
    )
    sort_code: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Sort code (used in UK and other countries)",
    )
    branch_code: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Branch code (used in various countries)",
    )
    account_format: str = Field(
        default="local", description="Account number format (local, iban, etc.)"
    )

    @field_validator("overdraft_limit")
    @classmethod
    def validate_overdraft_limit(
        cls, value: Optional[Decimal], info: dict
    ) -> Optional[Decimal]:
        """
        Validate that overdraft_limit is set when overdraft protection is enabled.

        Args:
            value: The overdraft limit value
            info: The validation context

        Returns:
            The validated overdraft limit

        Raises:
            ValueError: If overdraft protection is enabled but no limit is provided
        """
        has_protection = info.data.get("has_overdraft_protection", False)

        if has_protection and value is None:
            raise ValueError(
                "Overdraft limit is required when overdraft protection is enabled"
            )

        if not has_protection and value is not None:
            raise ValueError(
                "Overdraft limit cannot be set when overdraft protection is disabled"
            )

        return value

    @field_validator("routing_number")
    @classmethod
    def validate_routing_number(cls, value: Optional[str]) -> Optional[str]:
        """
        Validate the routing number format if provided.

        Args:
            value: The routing number to validate

        Returns:
            The validated routing number

        Raises:
            ValueError: If routing number is not in valid format
        """
        if value is not None and len(value) > 0:
            # Basic format validation - should be enhanced with country-specific validation
            if not value.isdigit() or len(value) < 8:
                raise ValueError("Routing number must be at least 8 digits")

        return value

    @field_validator("account_format")
    @classmethod
    def validate_account_format(cls, value: str) -> str:
        """
        Validate the account format is a recognized value.

        Args:
            value: The account format to validate

        Returns:
            The validated account format

        Raises:
            ValueError: If account format is not recognized
        """
        valid_formats = ["local", "iban", "swift", "sort_code", "branch_code"]
        if value not in valid_formats:
            raise ValueError(
                f"Account format must be one of: {', '.join(valid_formats)}"
            )

        return value


class CheckingAccountCreate(CheckingAccountBase):
    """
    Schema for creating a new checking account.

    Extends the base checking account schema for creation operations.
    """


class CheckingAccountUpdate(AccountBase):
    """
    Schema for updating an existing checking account.

    Contains all fields that can be updated for a checking account,
    with all fields being optional.
    """

    # Override name to make it optional
    name: Optional[str] = Field(
        default=None,
        min_length=1,
        max_length=50,
        description="Account name (1-50 characters)",
    )

    # Override account_type to be a fixed literal for checking accounts
    account_type: Optional[Literal["checking"]] = None

    # Override balance fields to be None by default (don't update if not provided)
    current_balance: Optional[MoneyDecimal] = Field(
        default=None, description="Current balance"
    )
    available_balance: Optional[MoneyDecimal] = Field(
        default=None, description="Available balance"
    )

    # Checking-specific fields
    routing_number: Optional[str] = Field(
        default=None, max_length=50, description="Account routing number"
    )
    has_overdraft_protection: Optional[bool] = Field(
        default=None, description="Whether overdraft protection is enabled"
    )
    overdraft_limit: Optional[MoneyDecimal] = Field(
        default=None,
        description="Maximum overdraft amount (when protection is enabled)",
        ge=0,
    )
    monthly_fee: Optional[MoneyDecimal] = Field(
        default=None, description="Monthly account maintenance fee", ge=0
    )
    interest_rate: Optional[PercentageDecimal] = Field(
        default=None,
        description="Annual interest rate (if interest-bearing)",
        ge=0,
        le=100,
    )

    # International banking fields
    iban: Optional[str] = Field(
        default=None, max_length=50, description="International Bank Account Number"
    )
    swift_bic: Optional[str] = Field(
        default=None,
        max_length=20,
        description="SWIFT/BIC code for international transfers",
    )
    sort_code: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Sort code (used in UK and other countries)",
    )
    branch_code: Optional[str] = Field(
        default=None,
        max_length=20,
        description="Branch code (used in various countries)",
    )
    account_format: Optional[str] = Field(
        default=None, description="Account number format (local, iban, etc.)"
    )

    @field_validator("overdraft_limit")
    @classmethod
    def validate_overdraft_limit(
        cls, value: Optional[Decimal], info: dict
    ) -> Optional[Decimal]:
        """
        Validate that overdraft_limit is set when overdraft protection is enabled.

        Args:
            value: The overdraft limit value
            info: The validation context

        Returns:
            The validated overdraft limit

        Raises:
            ValueError: If overdraft protection is enabled but no limit is provided
        """
        if value is None:
            return None

        has_protection = info.data.get("has_overdraft_protection")

        # If has_overdraft_protection is not being updated, we can't validate
        if has_protection is None:
            return value

        if has_protection and value is None:
            raise ValueError(
                "Overdraft limit is required when overdraft protection is enabled"
            )

        if not has_protection and value is not None:
            raise ValueError(
                "Overdraft limit cannot be set when overdraft protection is disabled"
            )

        return value

    @field_validator("routing_number")
    @classmethod
    def validate_routing_number(cls, value: Optional[str]) -> Optional[str]:
        """
        Validate the routing number format if provided.

        Args:
            value: The routing number to validate

        Returns:
            The validated routing number

        Raises:
            ValueError: If routing number is not in valid format
        """
        if value is None:
            return None

        if len(value) > 0:
            # Basic format validation - should be enhanced with country-specific validation
            if not value.isdigit() or len(value) < 8:
                raise ValueError("Routing number must be at least 8 digits")

        return value

    @field_validator("account_format")
    @classmethod
    def validate_account_format(cls, value: Optional[str]) -> Optional[str]:
        """
        Validate the account format is a recognized value.

        Args:
            value: The account format to validate

        Returns:
            The validated account format

        Raises:
            ValueError: If account format is not recognized
        """
        if value is None:
            return None

        valid_formats = ["local", "iban", "swift", "sort_code", "branch_code"]
        if value not in valid_formats:
            raise ValueError(
                f"Account format must be one of: {', '.join(valid_formats)}"
            )

        return value


class CheckingAccountResponse(CheckingAccountBase, AccountResponse):
    """
    Schema for checking account data in API responses.

    Extends both the base account response schema and checking account base schema
    to include all fields needed for API responses.

    Note: The inheritance order is important - CheckingAccountBase must come first
    to ensure the Literal["checking"] type for account_type is used instead of the
    string type from AccountResponse. This is required for discriminated unions in Pydantic v2.
    """

    # Explicitly redeclare the account_type field to ensure the Literal type is used
    account_type: Literal["checking"] = "checking"
