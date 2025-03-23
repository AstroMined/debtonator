"""
Account schema definitions for the API.

This module defines the schema classes for account data validation and serialization.
Includes schemas for creating, updating, and retrieving accounts, as well as specialized
response formats for different account-related operations.
"""

from datetime import datetime
from decimal import Decimal
from enum import Enum
from typing import Any, Callable, Dict, List, Optional

from pydantic import ConfigDict, Field, field_validator

from . import (BaseSchemaValidator, IntMoneyDict, MoneyDecimal,
               PercentageDecimal)


class AccountType(str, Enum):
    """
    Valid account types.

    Defines the allowed types of accounts in the system.
    """

    CREDIT = "credit"
    CHECKING = "checking"
    SAVINGS = "savings"


# Common validation functions


def validate_credit_account_field(field_name: str) -> Callable:
    """
    Creates a validator function that ensures a field is only set for credit accounts.

    Args:
        field_name: Name of the field being validated

    Returns:
        Callable: A validator function for the specified field
    """

    def validator(value: Optional[Decimal], info: Any) -> Optional[Decimal]:
        """
        Validates that the field is only set for credit accounts.

        Args:
            value: The field value to validate
            info: Validation context with all data

        Returns:
            Optional[Decimal]: The validated value

        Raises:
            ValueError: If value is set for a non-credit account
        """
        account_type = info.data.get("type")

        if value is not None:
            if account_type == AccountType.CREDIT:
                return value
            elif account_type is not None:  # Only validate if we have account type
                raise ValueError(
                    f"{field_name.replace('_', ' ').title()} can only be set for credit accounts"
                )

        return value

    return validator


# Common field definitions
account_name_field = lambda required: Field(
    ... if required else None,
    min_length=1,
    max_length=50,
    description="Account name (1-50 characters)",
)

account_type_field = lambda required: Field(
    ... if required else None, description="Type of account (credit, checking, savings)"
)

datetime_field = lambda required, name: Field(
    ... if required else None, description=f"{name} (UTC timezone)"
)


class AccountBase(BaseSchemaValidator):
    """
    Base schema for account data with enhanced validation.

    Contains the common attributes and validation logic for account data.
    """

    name: str = account_name_field(required=True)
    type: AccountType = account_type_field(required=True)
    description: Optional[str] = Field(
        default=None, max_length=255, description="Optional description for the account"
    )
    available_balance: MoneyDecimal = Field(
        default=Decimal("0"), description="Current available balance"
    )
    available_credit: Optional[MoneyDecimal] = Field(
        default=None, description="Available credit for credit accounts", ge=0
    )
    total_limit: Optional[MoneyDecimal] = Field(
        default=None, description="Total credit limit for credit accounts", ge=0
    )
    last_statement_balance: Optional[MoneyDecimal] = Field(
        default=None, description="Balance from last statement"
    )
    last_statement_date: Optional[datetime] = datetime_field(
        required=False, name="Date of last statement"
    )

    @field_validator("total_limit")
    @classmethod
    def validate_total_limit(
        cls, value: Optional[Decimal], info: Any
    ) -> Optional[Decimal]:
        """
        Validate total_limit based on account type.

        Args:
            value: The total credit limit value to validate
            info: Validation context with all data

        Returns:
            Optional[Decimal]: The validated value

        Raises:
            ValueError: If value is set for a non-credit account
        """
        return validate_credit_account_field("total_limit")(value, info)

    @field_validator("available_credit")
    @classmethod
    def validate_available_credit(
        cls, value: Optional[Decimal], info: Any
    ) -> Optional[Decimal]:
        """
        Validate available_credit based on account type.

        Args:
            value: The available credit value to validate
            info: Validation context with all data

        Returns:
            Optional[Decimal]: The validated value

        Raises:
            ValueError: If value is set for a non-credit account
        """
        return validate_credit_account_field("available_credit")(value, info)


class AccountCreate(AccountBase):
    """
    Schema for creating a new account.

    Extends the base account schema without adding additional fields.
    """

    pass


class AccountUpdate(BaseSchemaValidator):
    """
    Schema for updating an existing account.

    Contains all fields from AccountBase but makes them optional for partial updates.
    """

    name: Optional[str] = account_name_field(required=False)
    type: Optional[AccountType] = account_type_field(required=False)
    description: Optional[str] = Field(
        default=None, max_length=255, description="Optional description for the account"
    )
    available_balance: Optional[MoneyDecimal] = Field(
        default=None, description="Current available balance"
    )
    available_credit: Optional[MoneyDecimal] = Field(
        default=None, description="Available credit for credit accounts", ge=0
    )
    total_limit: Optional[MoneyDecimal] = Field(
        default=None, description="Total credit limit for credit accounts", ge=0
    )
    last_statement_balance: Optional[MoneyDecimal] = Field(
        default=None, description="Balance from last statement"
    )
    last_statement_date: Optional[datetime] = datetime_field(
        required=False, name="Date of last statement"
    )

    @field_validator("total_limit")
    @classmethod
    def validate_total_limit(
        cls, value: Optional[Decimal], info: Any
    ) -> Optional[Decimal]:
        """
        Validate total_limit based on account type.

        Args:
            value: The total credit limit value to validate
            info: Validation context with all data

        Returns:
            Optional[Decimal]: The validated value

        Raises:
            ValueError: If value is set for a non-credit account
        """
        return validate_credit_account_field("total_limit")(value, info)

    @field_validator("available_credit")
    @classmethod
    def validate_available_credit(
        cls, value: Optional[Decimal], info: Any
    ) -> Optional[Decimal]:
        """
        Validate available_credit based on account type.

        Args:
            value: The available credit value to validate
            info: Validation context with all data

        Returns:
            Optional[Decimal]: The validated value

        Raises:
            ValueError: If value is set for a non-credit account
        """
        return validate_credit_account_field("available_credit")(value, info)


class AccountInDB(AccountBase):
    """
    Schema for account data as stored in the database.

    Extends the base account schema with database-specific fields.
    """

    model_config = ConfigDict(from_attributes=True)

    id: int = Field(..., gt=0, description="Account ID (unique identifier)")
    created_at: datetime = Field(
        ..., description="Timestamp when the account was created (UTC timezone)"
    )
    updated_at: datetime = Field(
        ..., description="Timestamp when the account was last updated (UTC timezone)"
    )


class StatementBalanceHistory(BaseSchemaValidator):
    """
    Schema for statement balance history.

    Represents a historical record of an account's statement balances.
    """

    statement_date: datetime = Field(
        ..., description="Date of the statement (UTC timezone)"
    )
    statement_balance: MoneyDecimal = Field(
        ..., description="Balance on statement date"
    )
    minimum_payment: Optional[MoneyDecimal] = Field(
        default=None, description="Minimum payment due", ge=0
    )
    due_date: Optional[datetime] = Field(
        None, description="Payment due date (UTC timezone)"
    )


class AccountResponse(AccountInDB):
    """
    Schema for account data in API responses.

    Extends the database account schema for API response formatting.
    """

    pass


class AccountStatementHistoryResponse(BaseSchemaValidator):
    """
    Schema for account statement history response.

    Used for returning a complete history of account statements.
    """

    account_id: int = Field(..., description="Account ID (unique identifier)")
    account_name: str = Field(..., description="Account name")
    statement_history: List[StatementBalanceHistory] = Field(
        default_factory=list, description="List of historical statement balances"
    )


class AvailableCreditResponse(BaseSchemaValidator):
    """
    Schema for available credit calculation response.

    Used for providing detailed credit information for credit accounts.
    Implements ADR-013 using MoneyDecimal type with 2 decimal places.
    """

    account_id: int = Field(..., gt=0, description="Account ID (unique identifier)")
    account_name: str = Field(
        ..., min_length=1, max_length=50, description="Account name"
    )
    total_limit: MoneyDecimal = Field(..., description="Total credit limit", gt=0)
    current_balance: MoneyDecimal = Field(..., description="Current account balance")
    pending_transactions: MoneyDecimal = Field(
        ..., description="Sum of pending transactions"
    )
    adjusted_balance: MoneyDecimal = Field(
        ..., description="Balance adjusted for pending transactions"
    )
    available_credit: MoneyDecimal = Field(
        ..., description="Available credit after all adjustments", ge=0
    )

    model_config = ConfigDict(from_attributes=True)
