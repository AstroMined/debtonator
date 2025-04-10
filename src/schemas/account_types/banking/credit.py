"""
Credit account schema definitions for polymorphic account validation.

This module defines the schema classes for validating and serializing credit account data,
extending the base account schemas with credit-specific fields and validation.

Implemented as part of ADR-019 Banking Account Types Expansion.
"""

from datetime import datetime
from decimal import Decimal
from typing import Literal, Optional

from pydantic import Field, field_validator

from src.schemas.accounts import AccountBase, AccountResponse
from src.schemas.base_schema import MoneyDecimal, PercentageDecimal


class CreditAccountBase(AccountBase):
    """
    Base schema for credit account data with enhanced validation.

    Contains credit account specific attributes and validation logic.
    """

    # Override account_type to be a fixed literal for credit accounts
    account_type: Literal["credit"] = "credit"

    # Credit-specific fields
    credit_limit: MoneyDecimal = Field(..., description="Total credit limit", gt=0)
    statement_balance: Optional[MoneyDecimal] = Field(
        default=None, description="Current statement balance"
    )
    statement_due_date: Optional[datetime] = Field(
        default=None, description="Payment due date for current statement"
    )
    minimum_payment: Optional[MoneyDecimal] = Field(
        default=None, description="Minimum payment due", ge=0
    )
    apr: Optional[PercentageDecimal] = Field(
        default=None, description="Annual Percentage Rate", ge=0, le=100
    )
    annual_fee: Optional[MoneyDecimal] = Field(
        default=None, description="Annual card fee", ge=0
    )
    rewards_program: Optional[str] = Field(
        default=None, max_length=100, description="Rewards program name"
    )
    autopay_status: Optional[str] = Field(
        default=None,
        description="Autopay status (none, minimum, full_balance, fixed_amount)",
    )
    last_statement_date: Optional[datetime] = Field(
        default=None, description="Date of last statement"
    )

    @field_validator("minimum_payment")
    @classmethod
    def validate_minimum_payment(
        cls, value: Optional[Decimal], info: dict
    ) -> Optional[Decimal]:
        """
        Validate that minimum payment is less than or equal to statement balance if both are provided.

        Args:
            value: The minimum payment value
            info: The validation context

        Returns:
            The validated minimum payment

        Raises:
            ValueError: If minimum payment exceeds statement balance
        """
        statement_balance = info.data.get("statement_balance")

        if (
            value is not None
            and statement_balance is not None
            and value > statement_balance
        ):
            raise ValueError("Minimum payment cannot exceed statement balance")

        return value

    @field_validator("autopay_status")
    @classmethod
    def validate_autopay_status(cls, value: Optional[str]) -> Optional[str]:
        """
        Validate the autopay status is a recognized value.

        Args:
            value: The autopay status to validate

        Returns:
            The validated autopay status

        Raises:
            ValueError: If autopay status is not recognized
        """
        if value is not None:
            valid_statuses = ["none", "minimum", "full_balance", "fixed_amount"]
            if value not in valid_statuses:
                raise ValueError(
                    f"Autopay status must be one of: {', '.join(valid_statuses)}"
                )

        return value

    @field_validator("statement_balance")
    @classmethod
    def validate_statement_balance(
        cls, value: Optional[Decimal], info: dict
    ) -> Optional[Decimal]:
        """
        Validate that statement balance does not exceed credit limit.

        Args:
            value: The statement balance value
            info: The validation context

        Returns:
            The validated statement balance

        Raises:
            ValueError: If statement balance exceeds credit limit
        """
        credit_limit = info.data.get("credit_limit")

        if value is not None and credit_limit is not None and value > credit_limit:
            raise ValueError("Statement balance cannot exceed credit limit")

        return value

    @field_validator("apr")
    @classmethod
    def validate_apr(cls, value: Optional[Decimal]) -> Optional[Decimal]:
        """
        Validate the APR is reasonable.

        Args:
            value: The APR to validate

        Returns:
            The validated APR

        Raises:
            ValueError: If APR is unreasonably high
        """
        # Additional validation beyond the field constraint
        if value is not None and value > 36:
            # This is a warning threshold - some cards can have higher rates but it's unusual
            raise ValueError(
                "APR seems unusually high. Please confirm the rate is correct."
            )

        return value


class CreditAccountCreate(CreditAccountBase):
    """
    Schema for creating a new credit account.

    Extends the base credit account schema for creation operations.
    """


class CreditAccountUpdate(AccountBase):
    """
    Schema for updating an existing credit account.

    Contains all fields that can be updated for a credit account,
    with all fields being optional.
    """

    # Override account_type to be a fixed literal for credit accounts
    account_type: Optional[Literal["credit"]] = None

    # Credit-specific fields
    credit_limit: Optional[MoneyDecimal] = Field(
        default=None, description="Total credit limit", gt=0
    )
    statement_balance: Optional[MoneyDecimal] = Field(
        default=None, description="Current statement balance"
    )
    statement_due_date: Optional[datetime] = Field(
        default=None, description="Payment due date for current statement"
    )
    minimum_payment: Optional[MoneyDecimal] = Field(
        default=None, description="Minimum payment due", ge=0
    )
    apr: Optional[PercentageDecimal] = Field(
        default=None, description="Annual Percentage Rate", ge=0, le=100
    )
    annual_fee: Optional[MoneyDecimal] = Field(
        default=None, description="Annual card fee", ge=0
    )
    rewards_program: Optional[str] = Field(
        default=None, max_length=100, description="Rewards program name"
    )
    autopay_status: Optional[str] = Field(
        default=None,
        description="Autopay status (none, minimum, full_balance, fixed_amount)",
    )
    last_statement_date: Optional[datetime] = Field(
        default=None, description="Date of last statement"
    )

    @field_validator("minimum_payment")
    @classmethod
    def validate_minimum_payment(
        cls, value: Optional[Decimal], info: dict
    ) -> Optional[Decimal]:
        """
        Validate that minimum payment is less than or equal to statement balance if both are provided.

        Args:
            value: The minimum payment value
            info: The validation context

        Returns:
            The validated minimum payment

        Raises:
            ValueError: If minimum payment exceeds statement balance
        """
        if value is None:
            return None

        statement_balance = info.data.get("statement_balance")

        if statement_balance is not None and value > statement_balance:
            raise ValueError("Minimum payment cannot exceed statement balance")

        return value

    @field_validator("autopay_status")
    @classmethod
    def validate_autopay_status(cls, value: Optional[str]) -> Optional[str]:
        """
        Validate the autopay status is a recognized value.

        Args:
            value: The autopay status to validate

        Returns:
            The validated autopay status

        Raises:
            ValueError: If autopay status is not recognized
        """
        if value is None:
            return None

        valid_statuses = ["none", "minimum", "full_balance", "fixed_amount"]
        if value not in valid_statuses:
            raise ValueError(
                f"Autopay status must be one of: {', '.join(valid_statuses)}"
            )

        return value

    @field_validator("statement_balance")
    @classmethod
    def validate_statement_balance(
        cls, value: Optional[Decimal], info: dict
    ) -> Optional[Decimal]:
        """
        Validate that statement balance does not exceed credit limit.

        Args:
            value: The statement balance value
            info: The validation context

        Returns:
            The validated statement balance

        Raises:
            ValueError: If statement balance exceeds credit limit
        """
        if value is None:
            return None

        credit_limit = info.data.get("credit_limit")

        if credit_limit is not None and value > credit_limit:
            raise ValueError("Statement balance cannot exceed credit limit")

        return value

    @field_validator("apr")
    @classmethod
    def validate_apr(cls, value: Optional[Decimal]) -> Optional[Decimal]:
        """
        Validate the APR is reasonable.

        Args:
            value: The APR to validate

        Returns:
            The validated APR

        Raises:
            ValueError: If APR is unreasonably high
        """
        if value is None:
            return None

        # Additional validation beyond the field constraint
        if value > 36:
            # This is a warning threshold - some cards can have higher rates but it's unusual
            raise ValueError(
                "APR seems unusually high. Please confirm the rate is correct."
            )

        return value


class CreditAccountResponse(CreditAccountBase, AccountResponse):
    """
    Schema for credit account data in API responses.

    Extends both the base account response schema and credit account base schema
    to include all fields needed for API responses.

    Note: The inheritance order is important - CreditAccountBase must come first
    to ensure the Literal["credit"] type for account_type is used instead of the
    string type from AccountResponse. This is required for discriminated unions in Pydantic v2.
    """

    # Explicitly redeclare the account_type field to ensure the Literal type is used
    account_type: Literal["credit"] = "credit"
