"""
Bill split schema factory functions.

This module provides factory functions for creating valid BillSplit-related
Pydantic schema instances for use in tests.
"""

from decimal import Decimal
from typing import Any, Dict, Optional

from src.schemas.bill_splits import BillSplitCreate, BillSplitUpdate
from tests.helpers.schema_factories.base import MEDIUM_AMOUNT, factory_function


@factory_function(BillSplitCreate)
def create_bill_split_schema(
    liability_id: int, 
    account_id: int, 
    amount: Optional[Decimal] = None, 
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Create a valid BillSplitCreate schema instance.

    Args:
        liability_id: ID of the liability
        account_id: ID of the account
        amount: Split amount (defaults to 100.00)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create BillSplitCreate schema
    """
    if amount is None:
        amount = MEDIUM_AMOUNT

    data = {
        "liability_id": liability_id,
        "account_id": account_id,
        "amount": amount,
        **kwargs,
    }

    return data


@factory_function(BillSplitUpdate)
def create_bill_split_update_schema(
    id: int, 
    amount: Optional[Decimal] = None, 
    **kwargs: Any
) -> Dict[str, Any]:
    """
    Create a valid BillSplitUpdate schema instance.

    Args:
        id: ID of the bill split to update
        amount: New split amount (defaults to 150.00)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create BillSplitUpdate schema
    """
    if amount is None:
        amount = Decimal("150.00")

    data = {"id": id, "amount": amount, **kwargs}

    return data
