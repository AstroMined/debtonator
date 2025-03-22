"""
Liability schema factory functions.

This module provides factory functions for creating valid Liability-related
Pydantic schema instances for use in tests.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from src.schemas.liabilities import (
    AutoPaySettings,
    AutoPayUpdate,
    LiabilityCreate,
    LiabilityDateRange,
    LiabilityInDB,
    LiabilityResponse,
    LiabilityUpdate,
)
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


@factory_function(AutoPaySettings)
def create_auto_pay_settings_schema(
    payment_method: str = "ACH Transfer",
    preferred_pay_date: Optional[int] = None,
    days_before_due: Optional[int] = None,
    minimum_balance_required: Optional[Decimal] = None,
    retry_on_failure: bool = True,
    notification_email: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid AutoPaySettings schema instance.

    Args:
        payment_method: Method used for automatic payments
        preferred_pay_date: Preferred day of month for payment (1-31)
        days_before_due: Days before due date to process payment
        minimum_balance_required: Minimum balance required before autopay
        retry_on_failure: Whether to retry failed auto-payments
        notification_email: Email for autopay notifications
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create AutoPaySettings schema
    """
    data = {
        "payment_method": payment_method,
        "retry_on_failure": retry_on_failure,
        **kwargs,
    }

    # Cannot set both preferred_pay_date and days_before_due
    if preferred_pay_date is not None:
        data["preferred_pay_date"] = preferred_pay_date
    elif days_before_due is not None:
        data["days_before_due"] = days_before_due
    else:
        # Default to 5 days before due
        data["days_before_due"] = 5

    if minimum_balance_required is not None:
        data["minimum_balance_required"] = minimum_balance_required

    if notification_email is not None:
        data["notification_email"] = notification_email

    return data


@factory_function(AutoPayUpdate)
def create_auto_pay_update_schema(
    enabled: bool = True,
    settings: Optional[AutoPaySettings] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid AutoPayUpdate schema instance.

    Args:
        enabled: Whether to enable or disable auto-pay
        settings: Auto-pay settings when enabled is true
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create AutoPayUpdate schema
    """
    data = {
        "enabled": enabled,
        **kwargs,
    }

    if settings is not None:
        data["settings"] = settings
    elif enabled:  # Create default settings if enabled is true
        data["settings"] = create_auto_pay_settings_schema()

    return data


@factory_function(LiabilityInDB)
def create_liability_in_db_schema(
    id: int,
    name: str = "Test Liability",
    amount: Optional[Decimal] = None,
    due_date: Optional[datetime] = None,
    category_id: int = 1,
    primary_account_id: int = 1,
    paid: bool = False,
    recurring: bool = False,
    auto_pay: bool = False,
    auto_pay_enabled: bool = False,
    auto_pay_settings: Optional[AutoPaySettings] = None,
    recurring_bill_id: Optional[int] = None,
    last_auto_pay_attempt: Optional[datetime] = None,
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid LiabilityInDB schema instance.

    Args:
        id: Unique identifier for the liability
        name: Liability name
        amount: Liability amount (defaults to 100.00)
        due_date: Due date (defaults to 15 days from now)
        category_id: ID of the category for this liability
        primary_account_id: ID of the primary account
        paid: Whether the liability has been paid
        recurring: Whether this is a recurring liability
        auto_pay: Whether this liability is set for auto-pay
        auto_pay_enabled: Whether auto-pay is currently enabled
        auto_pay_settings: Auto-pay configuration settings
        recurring_bill_id: ID of associated recurring bill
        last_auto_pay_attempt: Timestamp of last auto-pay attempt
        created_at: Creation timestamp (defaults to now)
        updated_at: Last update timestamp (defaults to now)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create LiabilityInDB schema
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

    if created_at is None:
        created_at = utc_now()

    if updated_at is None:
        updated_at = utc_now()

    data = {
        "id": id,
        "name": name,
        "amount": amount,
        "due_date": due_date,
        "category_id": category_id,
        "primary_account_id": primary_account_id,
        "paid": paid,
        "recurring": recurring,
        "auto_pay": auto_pay,
        "auto_pay_enabled": auto_pay_enabled,
        "created_at": created_at,
        "updated_at": updated_at,
        **kwargs,
    }

    if auto_pay and auto_pay_settings is None and "auto_pay_settings" not in kwargs:
        data["auto_pay_settings"] = create_auto_pay_settings_schema()
    elif auto_pay_settings is not None:
        data["auto_pay_settings"] = auto_pay_settings

    if recurring_bill_id is not None:
        data["recurring_bill_id"] = recurring_bill_id

    if last_auto_pay_attempt is not None:
        data["last_auto_pay_attempt"] = last_auto_pay_attempt

    return data


@factory_function(LiabilityResponse)
def create_liability_response_schema(
    id: int,
    name: str = "Test Liability",
    amount: Optional[Decimal] = None,
    due_date: Optional[datetime] = None,
    category_id: int = 1,
    primary_account_id: int = 1,
    paid: bool = False,
    recurring: bool = False,
    auto_pay: bool = False,
    auto_pay_enabled: bool = False,
    auto_pay_settings: Optional[AutoPaySettings] = None,
    recurring_bill_id: Optional[int] = None,
    last_auto_pay_attempt: Optional[datetime] = None,
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid LiabilityResponse schema instance.

    Args:
        id: Unique identifier for the liability
        name: Liability name
        amount: Liability amount (defaults to 100.00)
        due_date: Due date (defaults to 15 days from now)
        category_id: ID of the category for this liability
        primary_account_id: ID of the primary account
        paid: Whether the liability has been paid
        recurring: Whether this is a recurring liability
        auto_pay: Whether this liability is set for auto-pay
        auto_pay_enabled: Whether auto-pay is currently enabled
        auto_pay_settings: Auto-pay configuration settings
        recurring_bill_id: ID of associated recurring bill
        last_auto_pay_attempt: Timestamp of last auto-pay attempt
        created_at: Creation timestamp (defaults to now)
        updated_at: Last update timestamp (defaults to now)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create LiabilityResponse schema
    """
    # Use the LiabilityInDB factory since they have the same structure
    return create_liability_in_db_schema(
        id=id,
        name=name,
        amount=amount,
        due_date=due_date,
        category_id=category_id,
        primary_account_id=primary_account_id,
        paid=paid,
        recurring=recurring,
        auto_pay=auto_pay,
        auto_pay_enabled=auto_pay_enabled,
        auto_pay_settings=auto_pay_settings,
        recurring_bill_id=recurring_bill_id,
        last_auto_pay_attempt=last_auto_pay_attempt,
        created_at=created_at,
        updated_at=updated_at,
        **kwargs,
    )


@factory_function(LiabilityDateRange)
def create_liability_date_range_schema(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid LiabilityDateRange schema instance.

    Args:
        start_date: Start date for the range (defaults to first of current month)
        end_date: End date for the range (defaults to last day of next month)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create LiabilityDateRange schema
    """
    now = utc_now()

    if start_date is None:
        # Default to first day of current month
        start_date = datetime(now.year, now.month, 1, tzinfo=now.tzinfo)

    if end_date is None:
        # Default to last day of next month
        if now.month == 12:
            end_date = datetime(now.year + 1, 1, 28, 23, 59, 59, tzinfo=now.tzinfo)
        else:
            end_date = datetime(
                now.year, now.month + 1, 28, 23, 59, 59, tzinfo=now.tzinfo
            )

    data = {
        "start_date": start_date,
        "end_date": end_date,
        **kwargs,
    }

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
