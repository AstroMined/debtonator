"""
Balance reconciliation schema factory functions.

This module provides factory functions for creating valid BalanceReconciliation-related
Pydantic schema instances for use in tests.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from src.schemas.balance_reconciliation import (
    BalanceReconciliationCreate,
    BalanceReconciliationUpdate,
)
from src.utils.datetime_utils import utc_now
from tests.helpers.schema_factories.base_schema_schema_factories import factory_function


@factory_function(BalanceReconciliationCreate)
def create_balance_reconciliation_schema(
    account_id: int,
    previous_balance: Optional[Decimal] = None,
    new_balance: Optional[Decimal] = None,
    reason: str = "Balance correction",
    reconciliation_date: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid BalanceReconciliationCreate schema instance.

    Args:
        account_id: ID of the account
        previous_balance: Previous balance (defaults to 1000.00)
        new_balance: New balance (defaults to 1100.00)
        reason: Reason for reconciliation
        reconciliation_date: Date of reconciliation (defaults to now)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create BalanceReconciliationCreate schema
    """
    if previous_balance is None:
        previous_balance = Decimal("1000.00")

    if new_balance is None:
        new_balance = Decimal("1100.00")

    if reconciliation_date is None:
        reconciliation_date = utc_now()

    # Calculate adjustment amount
    adjustment_amount = new_balance - previous_balance

    data = {
        "account_id": account_id,
        "previous_balance": previous_balance,
        "new_balance": new_balance,
        "adjustment_amount": adjustment_amount,
        "reason": reason,
        "reconciliation_date": reconciliation_date,
        **kwargs,
    }

    return data


@factory_function(BalanceReconciliationUpdate)
def create_balance_reconciliation_update_schema(
    id: int,
    new_balance: Optional[Decimal] = None,
    reason: Optional[str] = None,
    adjustment_amount: Optional[Decimal] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid BalanceReconciliationUpdate schema instance.

    Args:
        id: ID of the reconciliation entry to update
        new_balance: Updated new balance (optional)
        reason: Updated reason (optional)
        adjustment_amount: Updated adjustment amount (optional)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create BalanceReconciliationUpdate schema
    """
    data = {"id": id, **kwargs}

    if new_balance is not None:
        data["new_balance"] = new_balance

    if reason is not None:
        data["reason"] = reason

    if adjustment_amount is not None:
        data["adjustment_amount"] = adjustment_amount

    return data
