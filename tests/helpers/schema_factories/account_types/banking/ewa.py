"""
Earned Wage Access (EWA) account schema factory functions.

This module provides factory functions for creating valid EWAAccount-related
Pydantic schema instances for use in tests.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, Optional

from src.schemas.account_types.banking.ewa import (
    EWAAccountCreate,
    EWAAccountResponse,
)
from tests.helpers.schema_factories.base import COMMON_AMOUNTS, factory_function
from src.utils.datetime_utils import utc_now


@factory_function(EWAAccountCreate)
def create_ewa_account_schema(
    name: str = "Test EWA Account",
    current_balance: Optional[Decimal] = None,
    available_balance: Optional[Decimal] = None,
    institution: str = "DailyPay",
    provider: str = "DailyPay",
    max_advance_percentage: Optional[Decimal] = None,
    per_transaction_fee: Optional[Decimal] = None,
    pay_period_start: Optional[datetime] = None,
    pay_period_end: Optional[datetime] = None,
    next_payday: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid EWAAccountCreate schema instance.

    Args:
        name: Account name
        current_balance: Current account balance (defaults to 150.00, representing advanced wages)
        available_balance: Available balance (defaults to 0 for EWA accounts)
        institution: Financial institution name
        provider: EWA service provider (Payactiv, DailyPay, etc.)
        max_advance_percentage: Maximum percent of paycheck available for advance (defaults to 50%)
        per_transaction_fee: Fee charged per advance transaction
        pay_period_start: Start date of current pay period
        pay_period_end: End date of current pay period
        next_payday: Date of next regular payday
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create EWAAccountCreate schema
    """
    # Set defaults
    now = utc_now()
    
    if current_balance is None:
        current_balance = COMMON_AMOUNTS["medium"] * Decimal("1.5")  # 150.00
    
    # For EWA accounts, available balance is typically 0 as it's an advance against earnings
    if available_balance is None:
        available_balance = Decimal("0")
    
    if max_advance_percentage is None:
        max_advance_percentage = Decimal("50.0")  # 50% - common maximum
    
    if per_transaction_fee is None:
        per_transaction_fee = Decimal("1.99")  # Common fee amount
    
    # Set up reasonable pay period dates if not provided
    # Default pattern: two-week pay period, currently in the middle of it
    if pay_period_start is None:
        pay_period_start = now - timedelta(days=7)  # Started a week ago
    
    if pay_period_end is None:
        if pay_period_start:
            pay_period_end = pay_period_start + timedelta(days=14)  # Two-week period
        else:
            pay_period_end = now + timedelta(days=7)  # Ends a week from now
    
    if next_payday is None:
        if pay_period_end:
            next_payday = pay_period_end + timedelta(days=3)  # Payday a few days after period ends
        else:
            next_payday = now + timedelta(days=10)  # About a week and half from now

    data = {
        "name": name,
        "account_type": "ewa",  # This is a literal in the schema
        "current_balance": current_balance,
        "available_balance": available_balance,
        "institution": institution,
        "provider": provider,
        "max_advance_percentage": max_advance_percentage,
        "per_transaction_fee": per_transaction_fee,
        "pay_period_start": pay_period_start,
        "pay_period_end": pay_period_end,
        "next_payday": next_payday,
    }

    # Add any additional fields from kwargs
    data.update(kwargs)

    return data


@factory_function(EWAAccountResponse)
def create_ewa_account_response_schema(
    id: int = 1,
    name: str = "Test EWA Account",
    current_balance: Optional[Decimal] = None,
    available_balance: Optional[Decimal] = None,
    institution: str = "DailyPay",
    provider: str = "DailyPay",
    max_advance_percentage: Optional[Decimal] = None,
    per_transaction_fee: Optional[Decimal] = None,
    pay_period_start: Optional[datetime] = None,
    pay_period_end: Optional[datetime] = None,
    next_payday: Optional[datetime] = None,
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid EWAAccountResponse schema instance.

    Args:
        id: Account ID
        name: Account name
        current_balance: Current account balance (defaults to 150.00, representing advanced wages)
        available_balance: Available balance (defaults to 0 for EWA accounts)
        institution: Financial institution name
        provider: EWA service provider (Payactiv, DailyPay, etc.)
        max_advance_percentage: Maximum percent of paycheck available for advance (defaults to 50%)
        per_transaction_fee: Fee charged per advance transaction
        pay_period_start: Start date of current pay period
        pay_period_end: End date of current pay period
        next_payday: Date of next regular payday
        created_at: Creation timestamp (defaults to now)
        updated_at: Last update timestamp (defaults to now)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create EWAAccountResponse schema
    """
    if created_at is None:
        created_at = utc_now()

    if updated_at is None:
        updated_at = utc_now()

    # Use the create schema factory to generate the base data
    base_data = create_ewa_account_schema(
        name=name,
        current_balance=current_balance,
        available_balance=available_balance,
        institution=institution,
        provider=provider,
        max_advance_percentage=max_advance_percentage,
        per_transaction_fee=per_transaction_fee,
        pay_period_start=pay_period_start,
        pay_period_end=pay_period_end,
        next_payday=next_payday,
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
