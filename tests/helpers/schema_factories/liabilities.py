"""
Liability schema factory functions.

This module provides factory functions for creating valid Liability-related
Pydantic schema instances for use in tests.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Optional

from src.models.liabilities import LiabilityStatus
from src.schemas.liabilities import LiabilityCreate, LiabilityUpdate


def create_liability_schema(
    name: str = "Test Liability",
    amount: Optional[Decimal] = None,
    category_id: int = 1,
    primary_account_id: int = 1,
    due_date_days: int = 30,
    recurring: bool = False,
    auto_pay: bool = False,
    **kwargs: Any,
) -> LiabilityCreate:
    """
    Create a valid LiabilityCreate schema instance.

    Args:
        name: Liability name
        amount: Total amount (defaults to 200.00)
        category_id: Category ID
        primary_account_id: Primary account ID
        due_date_days: Days from now for due date (defaults to 30)
        recurring: Whether this is a recurring liability
        auto_pay: Whether auto-pay is enabled
        **kwargs: Additional fields to override

    Returns:
        LiabilityCreate: Validated schema instance
    """
    if amount is None:
        amount = Decimal("200.00")

    # Create a future due date with UTC timezone
    due_date = datetime.now(timezone.utc) + timedelta(days=due_date_days)

    data = {
        "name": name,
        "amount": amount,
        "due_date": due_date,
        "category_id": category_id,
        "primary_account_id": primary_account_id,
        "recurring": recurring,
        "auto_pay": auto_pay,
        "status": LiabilityStatus.PENDING,
        **kwargs,
    }

    return LiabilityCreate(**data)


def create_liability_update_schema(
    id: int,
    name: Optional[str] = None,
    amount: Optional[Decimal] = None,
    status: Optional[LiabilityStatus] = None,
    **kwargs: Any,
) -> LiabilityUpdate:
    """
    Create a valid LiabilityUpdate schema instance.

    Args:
        id: ID of the liability to update
        name: New liability name (optional)
        amount: New amount (optional)
        status: New status (optional)
        **kwargs: Additional fields to override

    Returns:
        LiabilityUpdate: Validated schema instance
    """
    data = {"id": id, **kwargs}

    if name is not None:
        data["name"] = name

    if amount is not None:
        data["amount"] = amount

    if status is not None:
        data["status"] = status

    return LiabilityUpdate(**data)
