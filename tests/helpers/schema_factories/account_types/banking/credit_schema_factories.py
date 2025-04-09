"""
Credit account schema factory functions.

This module provides factory functions for creating valid CreditAccount-related
Pydantic schema instances for use in tests.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, Optional

from src.schemas.account_types.banking.credit import (
    CreditAccountCreate,
    CreditAccountResponse,
)
from src.utils.datetime_utils import utc_now
from tests.helpers.schema_factories.base_schema_schema_factories import (
    COMMON_AMOUNTS,
    factory_function,
)


@factory_function(CreditAccountCreate)
def create_credit_account_schema(
    name: str = "Test Credit Card",
    current_balance: Optional[Decimal] = None,
    available_balance: Optional[Decimal] = None,
    institution: str = "Test Bank",
    credit_limit: Optional[Decimal] = None,
    statement_balance: Optional[Decimal] = None,
    statement_due_date: Optional[datetime] = None,
    minimum_payment: Optional[Decimal] = None,
    apr: Optional[Decimal] = None,
    annual_fee: Optional[Decimal] = None,
    rewards_program: Optional[str] = None,
    autopay_status: Optional[str] = None,
    last_statement_date: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid CreditAccountCreate schema instance.

    Args:
        name: Account name
        current_balance: Current account balance (negative for credit accounts, defaults to -500.00)
        available_balance: Available balance (defaults to calculated based on credit_limit and current_balance)
        institution: Bank or financial institution name
        credit_limit: Total credit limit (defaults to 5000.00)
        statement_balance: Current statement balance
        statement_due_date: Payment due date for current statement
        minimum_payment: Minimum payment due
        apr: Annual Percentage Rate (defaults to 15.99%)
        annual_fee: Annual card fee
        rewards_program: Rewards program name
        autopay_status: Autopay status (none, minimum, full_balance, fixed_amount)
        last_statement_date: Date of last statement
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create CreditAccountCreate schema
    """
    # Set defaults for key fields
    if credit_limit is None:
        credit_limit = COMMON_AMOUNTS["huge"] / Decimal("2")  # 5000.00

    # For credit accounts, current_balance is negative to represent amount owed
    if current_balance is None:
        current_balance = -COMMON_AMOUNTS["medium"] * Decimal("5")  # -500.00

    # Calculate available balance if not provided
    if available_balance is None:
        available_balance = (
            credit_limit + current_balance
        )  # current_balance is negative

    # Create dict with required fields
    data = {
        "name": name,
        "account_type": "credit",  # This is a literal in the schema
        "current_balance": current_balance,
        "available_balance": available_balance,
        "institution": institution,
        "credit_limit": credit_limit,
    }

    # Add optional fields if provided
    if statement_balance is not None:
        data["statement_balance"] = statement_balance
    else:
        # Default statement balance is the same as current balance
        data["statement_balance"] = abs(current_balance)

    now = utc_now()

    if last_statement_date is not None:
        data["last_statement_date"] = last_statement_date
    else:
        # Default last statement date is 15 days ago
        data["last_statement_date"] = now - timedelta(days=15)

    if statement_due_date is not None:
        data["statement_due_date"] = statement_due_date
    else:
        # Default due date is 10 days from now
        data["statement_due_date"] = now + timedelta(days=10)

    if minimum_payment is not None:
        data["minimum_payment"] = minimum_payment
    else:
        # Default minimum payment is 2% of statement balance or $25, whichever is greater
        min_payment = max(
            abs(data["statement_balance"]) * Decimal("0.02"), Decimal("25.00")
        )
        data["minimum_payment"] = min_payment

    if apr is not None:
        data["apr"] = apr
    else:
        data["apr"] = Decimal("15.99")  # Default APR

    if annual_fee is not None:
        data["annual_fee"] = annual_fee

    if rewards_program is not None:
        data["rewards_program"] = rewards_program

    if autopay_status is not None:
        data["autopay_status"] = autopay_status

    # Add any additional fields from kwargs
    data.update(kwargs)

    return data


@factory_function(CreditAccountResponse)
def create_credit_account_response_schema(
    id: int = 1,
    name: str = "Test Credit Card",
    current_balance: Optional[Decimal] = None,
    available_balance: Optional[Decimal] = None,
    institution: str = "Test Bank",
    credit_limit: Optional[Decimal] = None,
    statement_balance: Optional[Decimal] = None,
    statement_due_date: Optional[datetime] = None,
    minimum_payment: Optional[Decimal] = None,
    apr: Optional[Decimal] = None,
    annual_fee: Optional[Decimal] = None,
    rewards_program: Optional[str] = None,
    autopay_status: Optional[str] = None,
    last_statement_date: Optional[datetime] = None,
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid CreditAccountResponse schema instance.

    Args:
        id: Account ID
        name: Account name
        current_balance: Current account balance (negative for credit accounts, defaults to -500.00)
        available_balance: Available balance (defaults to calculated based on credit_limit and current_balance)
        institution: Bank or financial institution name
        credit_limit: Total credit limit (defaults to 5000.00)
        statement_balance: Current statement balance
        statement_due_date: Payment due date for current statement
        minimum_payment: Minimum payment due
        apr: Annual Percentage Rate (defaults to 15.99%)
        annual_fee: Annual card fee
        rewards_program: Rewards program name
        autopay_status: Autopay status (none, minimum, full_balance, fixed_amount)
        last_statement_date: Date of last statement
        created_at: Creation timestamp (defaults to now)
        updated_at: Last update timestamp (defaults to now)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create CreditAccountResponse schema
    """
    if created_at is None:
        created_at = utc_now()

    if updated_at is None:
        updated_at = utc_now()

    # Use the create schema factory to generate the base data
    base_data = create_credit_account_schema(
        name=name,
        current_balance=current_balance,
        available_balance=available_balance,
        institution=institution,
        credit_limit=credit_limit,
        statement_balance=statement_balance,
        statement_due_date=statement_due_date,
        minimum_payment=minimum_payment,
        apr=apr,
        annual_fee=annual_fee,
        rewards_program=rewards_program,
        autopay_status=autopay_status,
        last_statement_date=last_statement_date,
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
