"""
Balance history schema factory functions.

This module provides factory functions for creating valid BalanceHistory-related
Pydantic schema instances for use in tests.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from src.schemas.balance_history import BalanceHistoryCreate, BalanceHistoryUpdate
from tests.helpers.schema_factories.base import (MEDIUM_AMOUNT,
                                                 factory_function, utc_now)


@factory_function(BalanceHistoryCreate)
def create_balance_history_schema(
    account_id: int,
    balance: Optional[Decimal] = None,
    available_credit: Optional[Decimal] = None,
    is_reconciled: bool = False,
    notes: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid BalanceHistoryCreate schema instance.

    Args:
        account_id: ID of the account
        balance: Current balance (defaults to 1000.00)
        available_credit: Available credit for credit accounts (optional)
        is_reconciled: Whether this balance is reconciled
        notes: Optional notes about the balance entry
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create BalanceHistoryCreate schema
    """
    if balance is None:
        balance = Decimal("1000.00")

    data = {
        "account_id": account_id,
        "balance": balance,
        "is_reconciled": is_reconciled,
        **kwargs,
    }

    if available_credit is not None:
        data["available_credit"] = available_credit

    if notes is not None:
        data["notes"] = notes

    return data

@factory_function(BalanceHistoryUpdate)
def create_balance_history_update_schema(
    balance: Optional[Decimal] = None,
    available_credit: Optional[Decimal] = None,
    is_reconciled: Optional[bool] = None,
    notes: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid BalanceHistoryUpdate schema instance.

    Args:
        balance: Current balance (optional)
        available_credit: Available credit for credit accounts (optional)
        is_reconciled: Whether this balance is reconciled (optional)
        notes: Optional notes about the balance entry
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create BalanceHistoryUpdate schema
    """
    data = {}

    if balance is not None:
        data["balance"] = balance

    if available_credit is not None:
        data["available_credit"] = available_credit

    if is_reconciled is not None:
        data["is_reconciled"] = is_reconciled

    if notes is not None:
        data["notes"] = notes

    return data
