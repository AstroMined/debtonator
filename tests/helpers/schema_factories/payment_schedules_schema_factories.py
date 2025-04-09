"""
Payment schedule schema factory functions.

This module provides factory functions for creating valid PaymentSchedule-related
Pydantic schema instances for use in tests.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, Optional

from src.schemas.payment_schedules import PaymentScheduleCreate, PaymentScheduleUpdate
from src.utils.datetime_utils import utc_now
from tests.helpers.schema_factories.base_schema_schema_factories import (
    MEDIUM_AMOUNT,
    factory_function,
)


@factory_function(PaymentScheduleCreate)
def create_payment_schedule_schema(
    liability_id: int,
    account_id: int,
    scheduled_date: Optional[datetime] = None,
    amount: Optional[Decimal] = None,
    description: Optional[str] = None,
    auto_process: bool = False,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid PaymentScheduleCreate schema instance.

    Args:
        liability_id: ID of the liability this payment is for
        account_id: ID of the account from which payment will be made
        scheduled_date: Scheduled date for the payment (defaults to 7 days from now)
        amount: Amount to be paid (defaults to 100.00)
        description: Optional description of the payment
        auto_process: Whether this payment should be automatically processed
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create PaymentScheduleCreate schema
    """
    if scheduled_date is None:
        scheduled_date = utc_now() + timedelta(days=7)

    if amount is None:
        amount = MEDIUM_AMOUNT

    data = {
        "liability_id": liability_id,
        "account_id": account_id,
        "scheduled_date": scheduled_date,
        "amount": amount,
        "auto_process": auto_process,
        **kwargs,
    }

    if description is not None:
        data["description"] = description

    return data


@factory_function(PaymentScheduleUpdate)
def create_payment_schedule_update_schema(
    scheduled_date: Optional[datetime] = None,
    amount: Optional[Decimal] = None,
    account_id: Optional[int] = None,
    description: Optional[str] = None,
    auto_process: Optional[bool] = None,
    processed: Optional[bool] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid PaymentScheduleUpdate schema instance.

    Args:
        scheduled_date: Updated scheduled date for the payment
        amount: Updated payment amount
        account_id: Updated account ID for the payment
        description: Updated description of the payment
        auto_process: Updated auto-process setting
        processed: Updated processed status
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create PaymentScheduleUpdate schema
    """
    data = {**kwargs}

    if scheduled_date is not None:
        data["scheduled_date"] = scheduled_date

    if amount is not None:
        data["amount"] = amount

    if account_id is not None:
        data["account_id"] = account_id

    if description is not None:
        data["description"] = description

    if auto_process is not None:
        data["auto_process"] = auto_process

    if processed is not None:
        data["processed"] = processed

    return data
