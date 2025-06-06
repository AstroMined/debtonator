"""
Account schema definitions for the API.

This module defines the schema classes for account data validation and serialization.
Includes schemas for creating, updating, and retrieving accounts, as well as specialized
response formats for different account-related operations.

Updates as part of ADR-016 Account Type Expansion to support polymorphic account types.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Callable, List, Optional

from pydantic import ConfigDict, Field

from src.registry.account_types import (
    RegistryNotInitializedException,
    account_type_registry,
)
from src.schemas.base_schema import BaseSchemaValidator, MoneyDecimal


# Common validation functions
def validate_account_type(account_type: str, feature_flag_service=None) -> str:
    """
    Validates that an account type is registered and available.

    Args:
        account_type: The account type to validate
        feature_flag_service: Optional feature flag service to check if type is enabled

    Returns:
        str: The validated account type

    Raises:
        ValueError: If account type is not valid or not available
        RegistryNotInitializedException: If registry has not been initialized
    """
    try:
        # This will raise RegistryNotInitializedException if registry not initialized
        valid_types = account_type_registry.get_all_types(feature_flag_service)
        valid_type_ids = [t["id"] for t in valid_types]

        if not account_type_registry.is_valid_account_type(
            account_type, feature_flag_service
        ):
            valid_types_str = ", ".join(valid_type_ids)
            raise ValueError(f"Invalid account type. Must be one of: {valid_types_str}")

        return account_type

    except RegistryNotInitializedException as e:
        # Propagate the error - this is a system initialization issue that
        # should be caught and handled at a higher level
        import logging

        logger = logging.getLogger(__name__)
        logger.error(f"Registry error during account type validation: {str(e)}")
        raise


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
        account_type = info.data.get("account_type")

        if value is not None:
            if account_type == "credit":
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
    ... if required else None,
    description="Type of account (from account type registry)",
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
    account_type: str = account_type_field(required=True)
    description: Optional[str] = Field(
        default=None, max_length=255, description="Optional description for the account"
    )

    # Balance fields
    current_balance: MoneyDecimal = Field(
        default=Decimal("0"), description="Current balance"
    )
    available_balance: MoneyDecimal = Field(
        default=Decimal("0"), description="Available balance"
    )

    # New fields from ADR-016
    institution: Optional[str] = Field(
        default=None, max_length=100, description="Financial institution name"
    )
    currency: str = Field(
        default="USD",
        min_length=3,
        max_length=3,
        description="ISO 4217 currency code (e.g., USD, EUR, GBP)",
    )
    is_closed: bool = Field(default=False, description="Whether the account is closed")
    account_number: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Account number (may be masked for security)",
    )
    url: Optional[str] = Field(
        default=None, max_length=255, description="URL for the account's web portal"
    )
    logo_path: Optional[str] = Field(
        default=None, max_length=255, description="Path to the account's logo image"
    )

    # Performance optimization fields
    next_action_date: Optional[datetime] = datetime_field(
        required=False, name="Date of next required action (payment due, etc.)"
    )
    next_action_amount: Optional[MoneyDecimal] = Field(
        default=None, description="Amount associated with next action"
    )

    # Removed account_type validator to avoid conflicts with discriminated unions
    # Validation now happens at the service layer


class AccountUpdate(AccountBase):
    """
    Schema for updating an existing account.

    Contains all fields from AccountBase but makes them optional for partial updates.
    """

    name: Optional[str] = account_name_field(required=False)
    account_type: Optional[str] = account_type_field(required=False)
    description: Optional[str] = Field(
        default=None, max_length=255, description="Optional description for the account"
    )

    # Balance fields
    current_balance: Optional[MoneyDecimal] = Field(
        default=None, description="Current balance"
    )
    available_balance: Optional[MoneyDecimal] = Field(
        default=None, description="Available balance"
    )

    # New fields from ADR-016
    institution: Optional[str] = Field(
        default=None, max_length=100, description="Financial institution name"
    )
    currency: Optional[str] = Field(
        default=None,
        min_length=3,
        max_length=3,
        description="ISO 4217 currency code (e.g., USD, EUR, GBP)",
    )
    is_closed: Optional[bool] = Field(
        default=None, description="Whether the account is closed"
    )
    account_number: Optional[str] = Field(
        default=None,
        max_length=50,
        description="Account number (may be masked for security)",
    )
    url: Optional[str] = Field(
        default=None, max_length=255, description="URL for the account's web portal"
    )
    logo_path: Optional[str] = Field(
        default=None, max_length=255, description="Path to the account's logo image"
    )

    # Credit-specific fields have been moved to the CreditAccount schema

    # Performance optimization fields
    next_action_date: Optional[datetime] = datetime_field(
        required=False, name="Date of next required action (payment due, etc.)"
    )
    next_action_amount: Optional[MoneyDecimal] = Field(
        default=None, description="Amount associated with next action"
    )

    # Removed account_type validator to avoid conflicts with discriminated unions
    # Validation now happens at the service layer


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
    Base schema for all account types. For specific account type responses,
    use the type-specific schemas in src/schemas/account_types/
    """


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
