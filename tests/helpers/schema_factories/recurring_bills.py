"""
Recurring bill schema factory functions.

This module provides factory functions for creating valid RecurringBill-related
Pydantic schema instances for use in tests.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from src.schemas.recurring_bills import (
    GenerateBillsRequest,
    RecurringBillCreate,
    RecurringBillResponse,
    RecurringBillUpdate,
)
from tests.helpers.schema_factories.base import MEDIUM_AMOUNT, factory_function
from src.utils.datetime_utils import utc_now


@factory_function(RecurringBillCreate)
def create_recurring_bill_schema(
    account_id: int,
    category_id: int,
    bill_name: str = "Test Monthly Bill",
    amount: Optional[Decimal] = None,
    day_of_month: int = 15,
    auto_pay: bool = False,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid RecurringBillCreate schema instance.

    Args:
        account_id: ID of the account associated with this bill
        category_id: ID of the category associated with this bill
        bill_name: Name of the recurring bill
        amount: Amount of the recurring bill (defaults to 100.00)
        day_of_month: Day of the month when the bill is due (1-31)
        auto_pay: Whether the bill is set up for automatic payment
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create RecurringBillCreate schema
    """
    if amount is None:
        amount = MEDIUM_AMOUNT

    data = {
        "account_id": account_id,
        "category_id": category_id,
        "bill_name": bill_name,
        "amount": amount,
        "day_of_month": day_of_month,
        "auto_pay": auto_pay,
        **kwargs,
    }

    return data


@factory_function(RecurringBillUpdate)
def create_recurring_bill_update_schema(
    id: int,
    bill_name: Optional[str] = None,
    amount: Optional[Decimal] = None,
    day_of_month: Optional[int] = None,
    account_id: Optional[int] = None,
    category_id: Optional[int] = None,
    auto_pay: Optional[bool] = None,
    active: Optional[bool] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid RecurringBillUpdate schema instance.

    Args:
        id: ID of the recurring bill to update
        bill_name: Updated name of the recurring bill (optional)
        amount: Updated amount of the recurring bill (optional)
        day_of_month: Updated day of the month for the bill (optional)
        account_id: Updated ID of the associated account (optional)
        category_id: Updated ID of the associated category (optional)
        auto_pay: Updated automatic payment setting (optional)
        active: Updated active status (optional)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create RecurringBillUpdate schema
    """
    data = {**kwargs}

    if bill_name is not None:
        data["bill_name"] = bill_name

    if amount is not None:
        data["amount"] = amount

    if day_of_month is not None:
        data["day_of_month"] = day_of_month

    if account_id is not None:
        data["account_id"] = account_id

    if category_id is not None:
        data["category_id"] = category_id

    if auto_pay is not None:
        data["auto_pay"] = auto_pay

    if active is not None:
        data["active"] = active

    return data


@factory_function(RecurringBillResponse)
def create_recurring_bill_response_schema(
    id: int,
    account_id: int,
    category_id: int,
    bill_name: str = "Test Monthly Bill",
    amount: Optional[Decimal] = None,
    day_of_month: int = 15,
    auto_pay: bool = False,
    active: bool = True,
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid RecurringBillResponse schema instance.

    Args:
        id: Unique identifier for the recurring bill
        account_id: ID of the account associated with this bill
        category_id: ID of the category associated with this bill
        bill_name: Name of the recurring bill
        amount: Amount of the recurring bill (defaults to 100.00)
        day_of_month: Day of the month when the bill is due (1-31)
        auto_pay: Whether the bill is set up for automatic payment
        active: Whether the recurring bill is active
        created_at: Creation timestamp (defaults to now)
        updated_at: Last update timestamp (defaults to now)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create RecurringBillResponse schema
    """
    if amount is None:
        amount = MEDIUM_AMOUNT

    if created_at is None:
        created_at = utc_now()

    if updated_at is None:
        updated_at = utc_now()

    data = {
        "id": id,
        "account_id": account_id,
        "category_id": category_id,
        "bill_name": bill_name,
        "amount": amount,
        "day_of_month": day_of_month,
        "auto_pay": auto_pay,
        "active": active,
        "created_at": created_at,
        "updated_at": updated_at,
        **kwargs,
    }

    return data


@factory_function(GenerateBillsRequest)
def create_generate_bills_request_schema(
    month: int = 1,
    year: int = 2025,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid GenerateBillsRequest schema instance.

    Args:
        month: Month for which to generate bills (1-12)
        year: Year for which to generate bills
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create GenerateBillsRequest schema
    """
    data = {
        "month": month,
        "year": year,
        **kwargs,
    }

    return data
