"""
Transaction history schema factory functions.

This module provides factory functions for creating valid TransactionHistory-related
Pydantic schema instances for use in tests.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from src.models.transaction_history import TransactionType
from src.schemas.transaction_history import (
    TransactionHistoryCreate,
    TransactionHistoryUpdate,
)


def create_transaction_history_schema(
    account_id: int,
    amount: Optional[Decimal] = None,
    transaction_type: TransactionType = TransactionType.CREDIT,
    description: Optional[str] = None,
    transaction_date: Optional[datetime] = None,
    **kwargs: Any,
) -> TransactionHistoryCreate:
    """
    Create a valid TransactionHistoryCreate schema instance.

    Args:
        account_id: ID of the account
        amount: Transaction amount (defaults to 100.00)
        transaction_type: Type of transaction (credit or debit)
        description: Transaction description
        transaction_date: Date of transaction (defaults to now)
        **kwargs: Additional fields to override

    Returns:
        TransactionHistoryCreate: Validated schema instance
    """
    if amount is None:
        amount = Decimal("100.00")

    if transaction_date is None:
        transaction_date = datetime.utcnow()

    data = {
        "account_id": account_id,
        "amount": amount,
        "transaction_type": transaction_type,
        "transaction_date": transaction_date,
        **kwargs,
    }

    if description is not None:
        data["description"] = description

    return TransactionHistoryCreate(**data)


def create_transaction_history_update_schema(
    id: int,
    amount: Optional[Decimal] = None,
    description: Optional[str] = None,
    **kwargs: Any,
) -> TransactionHistoryUpdate:
    """
    Create a valid TransactionHistoryUpdate schema instance.

    Args:
        id: ID of the transaction history entry to update
        amount: New amount (optional)
        description: New description (optional)
        **kwargs: Additional fields to override

    Returns:
        TransactionHistoryUpdate: Validated schema instance
    """
    data = {"id": id, **kwargs}

    if amount is not None:
        data["amount"] = amount

    if description is not None:
        data["description"] = description

    return TransactionHistoryUpdate(**data)
