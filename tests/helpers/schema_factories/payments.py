"""
Payment schema factory functions.

This module provides factory functions for creating valid Payment-related
Pydantic schema instances for use in tests.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from src.schemas.payments import PaymentCreate, PaymentUpdate
from tests.helpers.schema_factories.base import MEDIUM_AMOUNT, factory_function, utc_now


@factory_function(PaymentCreate)
def create_payment_schema(
    liability_id: int,
    amount: Optional[Decimal] = None,
    payment_date: Optional[datetime] = None,
    account_id: int = 1,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid PaymentCreate schema instance.

    Args:
        liability_id: ID of the liability being paid
        amount: Payment amount (defaults to 100.00)
        payment_date: Date of payment (defaults to now)
        account_id: ID of the account making the payment
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create PaymentCreate schema
    """
    if amount is None:
        amount = MEDIUM_AMOUNT

    if payment_date is None:
        payment_date = utc_now()

    data = {
        "liability_id": liability_id,
        "amount": amount,
        "payment_date": payment_date,
        "account_id": account_id,
        **kwargs,
    }

    return data


@factory_function(PaymentUpdate)
def create_payment_update_schema(
    id: int,
    amount: Optional[Decimal] = None,
    payment_date: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid PaymentUpdate schema instance.

    Args:
        id: ID of the payment to update
        amount: New payment amount (optional)
        payment_date: New payment date (optional)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create PaymentUpdate schema
    """
    data = {"id": id, **kwargs}

    if amount is not None:
        data["amount"] = amount

    if payment_date is not None:
        data["payment_date"] = payment_date

    return data
