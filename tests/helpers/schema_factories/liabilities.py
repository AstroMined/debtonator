"""
Liability schema factory functions.

This module provides factory functions for creating valid Liability-related
Pydantic schema instances for use in tests.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from src.schemas.liabilities import LiabilityCreate, LiabilityUpdate
from tests.helpers.schema_factories.base import MEDIUM_AMOUNT, factory_function, utc_now


@factory_function(LiabilityCreate)
def create_liability_schema(
    name: str = "Test Liability",
    amount: Optional[Decimal] = None,
    due_date: Optional[datetime] = None,
    paid: bool = False,
    category_id: Optional[int] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid LiabilityCreate schema instance.

    Args:
        name: Liability name
        amount: Liability amount (defaults to 100.00)
        due_date: Due date (defaults to 15 days from now)
        paid: Whether the liability is paid
        category_id: Category ID (optional)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create LiabilityCreate schema
    """
    if amount is None:
        amount = MEDIUM_AMOUNT

    # Default due date to 15 days from now
    if due_date is None:
        now = utc_now()
        due_date = datetime(now.year, now.month, 15, tzinfo=now.tzinfo)
        if now.day > 15:
            if now.month == 12:
                due_date = datetime(now.year + 1, 1, 15, tzinfo=now.tzinfo)
            else:
                due_date = datetime(now.year, now.month + 1, 15, tzinfo=now.tzinfo)

    data = {
        "name": name,
        "amount": amount,
        "due_date": due_date,
        "paid": paid,
        **kwargs,
    }

    if category_id is not None:
        data["category_id"] = category_id

    return data


@factory_function(LiabilityUpdate)
def create_liability_update_schema(
    id: int,
    name: Optional[str] = None,
    amount: Optional[Decimal] = None,
    due_date: Optional[datetime] = None,
    paid: Optional[bool] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid LiabilityUpdate schema instance.

    Args:
        id: ID of the liability to update
        name: New liability name (optional)
        amount: New liability amount (optional)
        due_date: New due date (optional)
        paid: New paid status (optional)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create LiabilityUpdate schema
    """
    data = {"id": id, **kwargs}

    if name is not None:
        data["name"] = name

    if amount is not None:
        data["amount"] = amount

    if due_date is not None:
        data["due_date"] = due_date

    if paid is not None:
        data["paid"] = paid

    return data
