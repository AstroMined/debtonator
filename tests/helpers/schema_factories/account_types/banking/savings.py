"""
Savings account schema factory functions.

This module provides factory functions for creating valid SavingsAccount-related
Pydantic schema instances for use in tests.
"""

from decimal import Decimal
from typing import Any, Dict, Optional

from src.schemas.account_types.banking.savings import (
    SavingsAccountCreate,
    SavingsAccountResponse,
)
from tests.helpers.schema_factories.base import COMMON_AMOUNTS, factory_function
from src.utils.datetime_utils import utc_now


@factory_function(SavingsAccountCreate)
def create_savings_account_schema(
    name: str = "Test Savings Account",
    current_balance: Optional[Decimal] = None,
    available_balance: Optional[Decimal] = None,
    institution: str = "Test Bank",
    interest_rate: Optional[Decimal] = None,
    compound_frequency: Optional[str] = None,
    interest_earned_ytd: Optional[Decimal] = None,
    withdrawal_limit: Optional[int] = None,
    minimum_balance: Optional[Decimal] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid SavingsAccountCreate schema instance.

    Args:
        name: Account name
        current_balance: Current account balance (defaults to 2500.00)
        available_balance: Available balance (defaults to same as current_balance)
        institution: Bank or financial institution name
        interest_rate: Annual interest rate as a decimal (defaults to 0.02 for 2%)
        compound_frequency: Interest compounding frequency (daily, monthly, quarterly, annually)
        interest_earned_ytd: Interest earned year-to-date
        withdrawal_limit: Maximum number of withdrawals per period
        minimum_balance: Minimum balance required to avoid fees
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create SavingsAccountCreate schema
    """
    if current_balance is None:
        current_balance = COMMON_AMOUNTS["large"] * Decimal("2.5")  # 2500.00

    if available_balance is None:
        available_balance = current_balance

    data = {
        "name": name,
        "account_type": "savings",  # This is a literal in the schema
        "current_balance": current_balance,
        "available_balance": available_balance,
        "institution": institution,
    }

    # Add optional fields if provided
    if interest_rate is not None:
        data["interest_rate"] = interest_rate
    else:
        data["interest_rate"] = Decimal("0.02")  # Default 2.0% interest rate

    if compound_frequency is not None:
        data["compound_frequency"] = compound_frequency
    else:
        data["compound_frequency"] = "monthly"  # Default monthly compounding

    if interest_earned_ytd is not None:
        data["interest_earned_ytd"] = interest_earned_ytd

    if withdrawal_limit is not None:
        data["withdrawal_limit"] = withdrawal_limit
    else:
        data["withdrawal_limit"] = 6  # Default limit of 6 withdrawals per month (common in US)

    if minimum_balance is not None:
        data["minimum_balance"] = minimum_balance
    else:
        data["minimum_balance"] = COMMON_AMOUNTS["medium"]  # 100.00

    # Add any additional fields from kwargs
    data.update(kwargs)

    return data


@factory_function(SavingsAccountResponse)
def create_savings_account_response_schema(
    id: int = 1,
    name: str = "Test Savings Account",
    current_balance: Optional[Decimal] = None,
    available_balance: Optional[Decimal] = None,
    institution: str = "Test Bank",
    interest_rate: Optional[Decimal] = None,
    compound_frequency: Optional[str] = None,
    interest_earned_ytd: Optional[Decimal] = None,
    withdrawal_limit: Optional[int] = None,
    minimum_balance: Optional[Decimal] = None,
    created_at: Optional[Any] = None,
    updated_at: Optional[Any] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid SavingsAccountResponse schema instance.

    Args:
        id: Account ID
        name: Account name
        current_balance: Current account balance (defaults to 2500.00)
        available_balance: Available balance (defaults to same as current_balance)
        institution: Bank or financial institution name
        interest_rate: Annual interest rate (defaults to 2.0%)
        compound_frequency: Interest compounding frequency (daily, monthly, quarterly, annually)
        interest_earned_ytd: Interest earned year-to-date
        withdrawal_limit: Maximum number of withdrawals per period
        minimum_balance: Minimum balance required to avoid fees
        created_at: Creation timestamp (defaults to now)
        updated_at: Last update timestamp (defaults to now)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create SavingsAccountResponse schema
    """
    if created_at is None:
        created_at = utc_now()

    if updated_at is None:
        updated_at = utc_now()

    # Use the create schema factory to generate the base data
    base_data = create_savings_account_schema(
        name=name,
        current_balance=current_balance,
        available_balance=available_balance,
        institution=institution,
        interest_rate=interest_rate,
        compound_frequency=compound_frequency,
        interest_earned_ytd=interest_earned_ytd,
        withdrawal_limit=withdrawal_limit,
        minimum_balance=minimum_balance,
    )

    # Convert the Pydantic model to a dictionary
    base_dict = base_data.model_dump()

    # Add response-specific fields
    response_data = {
        "id": id,
        "created_at": created_at,
        "updated_at": updated_at,
        **base_dict,
    }

    # Add any additional fields from kwargs
    response_data.update(kwargs)

    return response_data
