"""
Balance reconciliation schema factory functions.

This module provides factory functions for creating valid BalanceReconciliation-related
Pydantic schema instances for use in tests.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from src.schemas.balance_reconciliation import (
    BalanceReconciliationCreate,
    BalanceReconciliationUpdate,
)


def create_balance_reconciliation_schema(
    account_id: int,
    previous_balance: Optional[Decimal] = None,
    new_balance: Optional[Decimal] = None,
    reason: str = "Balance correction",
    reconciliation_date: Optional[datetime] = None,
    **kwargs: Any,
) -> BalanceReconciliationCreate:
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
        BalanceReconciliationCreate: Validated schema instance
    """
    if previous_balance is None:
        previous_balance = Decimal("1000.00")

    if new_balance is None:
        new_balance = Decimal("1100.00")

    if reconciliation_date is None:
        reconciliation_date = datetime.utcnow()

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

    return BalanceReconciliationCreate(**data)


def create_balance_reconciliation_update_schema(
    id: int,
    new_balance: Optional[Decimal] = None,
    reason: Optional[str] = None,
    **kwargs: Any,
) -> BalanceReconciliationUpdate:
    """
    Create a valid BalanceReconciliationUpdate schema instance.

    Args:
        id: ID of the reconciliation entry to update
        new_balance: Updated new balance (optional)
        reason: Updated reason (optional)
        **kwargs: Additional fields to override

    Returns:
        BalanceReconciliationUpdate: Validated schema instance
    """
    data = {"id": id, **kwargs}

    if new_balance is not None:
        data["new_balance"] = new_balance

    if reason is not None:
        data["reason"] = reason

    return BalanceReconciliationUpdate(**data)
