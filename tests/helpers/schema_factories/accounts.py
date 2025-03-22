"""
Account schema factory functions.

This module provides factory functions for creating valid Account-related
Pydantic schema instances for use in tests.
"""

from decimal import Decimal
from typing import Any, Optional

from src.schemas.accounts import AccountCreate, AccountUpdate


def create_account_schema(
    name: str = "Test Account",
    account_type: str = "checking",
    available_balance: Optional[Decimal] = None,
    total_limit: Optional[Decimal] = None,
    **kwargs: Any,
) -> AccountCreate:
    """
    Create a valid AccountCreate schema instance.

    Args:
        name: Account name
        account_type: Account type (checking, savings, credit)
        available_balance: Available balance (defaults based on account type)
        total_limit: Credit limit (only used for credit accounts)
        **kwargs: Additional fields to override

    Returns:
        AccountCreate: Validated schema instance
    """
    if available_balance is None:
        if account_type == "credit":
            available_balance = Decimal("-500.00")
        else:
            available_balance = Decimal("1000.00")

    data = {
        "name": name,
        "type": account_type,
        "available_balance": available_balance,
        **kwargs,
    }

    # Add total_limit for credit accounts
    if account_type == "credit":
        if total_limit is None:
            total_limit = Decimal("5000.00")
        data["total_limit"] = total_limit

    return AccountCreate(**data)


def create_account_update_schema(
    id: int,
    name: Optional[str] = None,
    available_balance: Optional[Decimal] = None,
    **kwargs: Any,
) -> AccountUpdate:
    """
    Create a valid AccountUpdate schema instance.

    Args:
        id: ID of the account to update
        name: New account name (optional)
        available_balance: New available balance (optional)
        **kwargs: Additional fields to override

    Returns:
        AccountUpdate: Validated schema instance
    """
    data = {"id": id, **kwargs}

    if name is not None:
        data["name"] = name

    if available_balance is not None:
        data["available_balance"] = available_balance

    return AccountUpdate(**data)
