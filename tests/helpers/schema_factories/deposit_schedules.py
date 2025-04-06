"""
Deposit schedule schema factory functions.

This module provides factory functions for creating valid DepositSchedule-related
Pydantic schema instances for use in tests.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from src.schemas.deposit_schedules import DepositScheduleCreate
from tests.helpers.schema_factories.base import factory_function
from src.utils.datetime_utils import utc_now


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

    return data
