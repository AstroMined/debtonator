"""
Transaction history schema factory functions.

This module provides factory functions for creating valid TransactionHistory-related
Pydantic schema instances for use in tests.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from src.schemas.transaction_history import (
    TransactionHistoryCreate,
    TransactionHistoryInDB,
    TransactionHistoryList,
    TransactionHistoryUpdate,
)
from tests.helpers.schema_factories.base import MEDIUM_AMOUNT, factory_function
from src.utils.datetime_utils import utc_now


@factory_function(TransactionHistoryCreate)
def create_transaction_history_schema(
    account_id: int,
    transaction_date: Optional[datetime] = None,
    amount: Optional[Decimal] = None,
    description: str = "Test Transaction",
    transaction_type: str = "debit",
    reference_id: Optional[int] = None,
    reference_type: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid TransactionHistoryCreate schema instance.

    Args:
        account_id: ID of the account
        transaction_date: Date of transaction (defaults to now)
        amount: Transaction amount (defaults to 100.00)
        description: Transaction description
        transaction_type: Type of transaction (debit/credit)
        reference_id: ID of referenced entity (optional)
        reference_type: Type of referenced entity (optional)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create TransactionHistoryCreate schema
    """
    if transaction_date is None:
        transaction_date = utc_now()

    if amount is None:
        amount = MEDIUM_AMOUNT

    data = {
        "account_id": account_id,
        "transaction_date": transaction_date,
        "amount": amount,
        "description": description,
        "transaction_type": transaction_type,
        **kwargs,
    }

    if reference_id is not None:
        data["reference_id"] = reference_id

    if reference_type is not None:
        data["reference_type"] = reference_type

    return data


@factory_function(TransactionHistoryInDB)
def create_transaction_history_in_db_schema(
    id: int,
    account_id: int,
    transaction_date: Optional[datetime] = None,
    amount: Optional[Decimal] = None,
    description: str = "Test Transaction",
    transaction_type: str = "debit",
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid TransactionHistoryInDB schema instance.

    Args:
        id: Unique transaction identifier
        account_id: ID of the account
        transaction_date: Date of transaction (defaults to now)
        amount: Transaction amount (defaults to 100.00)
        description: Transaction description
        transaction_type: Type of transaction (debit/credit)
        created_at: Creation timestamp (defaults to now)
        updated_at: Last update timestamp (defaults to now)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create TransactionHistoryInDB schema
    """
    if transaction_date is None:
        transaction_date = utc_now()

    if amount is None:
        amount = MEDIUM_AMOUNT

    if created_at is None:
        created_at = utc_now()

    if updated_at is None:
        updated_at = utc_now()

    data = {
        "id": id,
        "account_id": account_id,
        "transaction_date": transaction_date,
        "amount": amount,
        "description": description,
        "transaction_type": transaction_type,
        "created_at": created_at,
        "updated_at": updated_at,
        **kwargs,
    }

    return data


@factory_function(TransactionHistoryList)
def create_transaction_history_list_schema(
    items: Optional[List[TransactionHistoryInDB]] = None,
    total: Optional[int] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid TransactionHistoryList schema instance.

    Args:
        items: List of transaction history items (creates 2 if None)
        total: Total number of items available (defaults to len(items))
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create TransactionHistoryList schema
    """
    if items is None:
        # Create sample transaction history items
        items = [
            create_transaction_history_in_db_schema(id=1, account_id=1),
            create_transaction_history_in_db_schema(
                id=2,
                account_id=1,
                amount=MEDIUM_AMOUNT * Decimal("2"),
                transaction_type="credit",
                description="Deposit",
            ),
        ]

    if total is None:
        total = len(items)

    data = {
        "items": items,
        "total": total,
        **kwargs,
    }

    return data


@factory_function(TransactionHistoryUpdate)
def create_transaction_history_update_schema(
    id: int,
    amount: Optional[Decimal] = None,
    description: Optional[str] = None,
    transaction_date: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid TransactionHistoryUpdate schema instance.

    Args:
        id: ID of the transaction history entry to update
        amount: New transaction amount (optional)
        description: New transaction description (optional)
        transaction_date: New transaction date (optional)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create TransactionHistoryUpdate schema
    """
    data = {"id": id, **kwargs}

    if amount is not None:
        data["amount"] = amount

    if description is not None:
        data["description"] = description

    if transaction_date is not None:
        data["transaction_date"] = transaction_date

    return data
