"""
Deposit schedule schema factory functions.

This module provides factory functions for creating valid DepositSchedule-related
Pydantic schema instances for use in tests.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from src.schemas.deposit_schedules import DepositScheduleCreate, DepositScheduleUpdate
from src.utils.datetime_utils import utc_now
from tests.helpers.schema_factories.base_schema_schema_factories import factory_function


@factory_function(DepositScheduleCreate)
def create_deposit_schedule_schema(
    income_id: int,
    account_id: int,
    schedule_date: Optional[datetime] = None,
    amount: Optional[Decimal] = None,
    recurring: bool = False,
    recurrence_pattern: Optional[Dict] = None,
    status: str = "pending",
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid DepositScheduleCreate schema instance.

    Args:
        income_id: ID of the income entry associated with this deposit
        account_id: ID of the account where the deposit will be made
        schedule_date: Scheduled date for the deposit (defaults to current UTC time)
        amount: Amount to be deposited (defaults to 1000.00)
        recurring: Whether this is a recurring deposit
        recurrence_pattern: Pattern details for recurring deposits (optional)
        status: Current status of the deposit (pending or completed)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create DepositScheduleCreate schema
    """
    if schedule_date is None:
        schedule_date = utc_now()

    if amount is None:
        amount = Decimal("1000.00")

    # Ensure status is valid
    if status not in ["pending", "completed"]:
        status = "pending"

    # Create data with all required fields
    data = {
        "income_id": income_id,
        "account_id": account_id,
        "schedule_date": schedule_date,
        "amount": amount,
        "recurring": recurring,
        "status": status,
        **kwargs,
    }

    if recurrence_pattern is not None:
        data["recurrence_pattern"] = recurrence_pattern

    # Remove source field that may be added by schema default
    # as it's not supported by the DepositSchedule model
    if "source" in data:
        del data["source"]

    return data


@factory_function(DepositScheduleUpdate)
def create_deposit_schedule_update_schema(
    schedule_date: Optional[datetime] = None,
    amount: Optional[Decimal] = None,
    recurring: Optional[bool] = None,
    recurrence_pattern: Optional[Dict] = None,
    status: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid DepositScheduleUpdate schema instance.

    Args:
        schedule_date: Updated scheduled date for the deposit
        amount: Updated deposit amount
        recurring: Updated recurring status
        recurrence_pattern: Updated pattern details for recurring deposits
        status: Updated deposit status (pending, completed, or canceled)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create DepositScheduleUpdate schema
    """
    data = {**kwargs}

    if schedule_date is not None:
        data["schedule_date"] = schedule_date

    if amount is not None:
        data["amount"] = amount

    if recurring is not None:
        data["recurring"] = recurring

    if recurrence_pattern is not None:
        data["recurrence_pattern"] = recurrence_pattern

    if status is not None:
        # Ensure status is valid
        if status in ["pending", "completed", "canceled"]:
            data["status"] = status

    return data
