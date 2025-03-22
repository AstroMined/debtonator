"""
Payment schema factory functions.

This module provides factory functions for creating valid Payment-related
Pydantic schema instances for use in tests.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Optional

from src.schemas.payments import PaymentCreate, PaymentUpdate


def create_payment_schema(
    liability_id: int,
    amount: Optional[Decimal] = None,
    payment_date: Optional[datetime] = None,
    **kwargs: Any,
) -> PaymentCreate:
    """
    Create a valid PaymentCreate schema instance.

    Args:
        liability_id: ID of the liability being paid
        amount: Payment amount (defaults to 100.00)
        payment_date: Date of payment (defaults to today)
        **kwargs: Additional fields to override

    Returns:
        PaymentCreate: Validated schema instance
    """
    if amount is None:
        amount = Decimal("100.00")

    if payment_date is None:
        payment_date = datetime.utcnow()

    data = {
        "liability_id": liability_id,
        "amount": amount,
        "payment_date": payment_date,
        **kwargs,
    }

    return PaymentCreate(**data)


def create_payment_update_schema(
    id: int,
    amount: Optional[Decimal] = None,
    payment_date: Optional[datetime] = None,
    **kwargs: Any,
) -> PaymentUpdate:
    """
    Create a valid PaymentUpdate schema instance.

    Args:
        id: ID of the payment to update
        amount: New payment amount (optional)
        payment_date: New payment date (optional)
        **kwargs: Additional fields to override

    Returns:
        PaymentUpdate: Validated schema instance
    """
    data = {"id": id, **kwargs}

    if amount is not None:
        data["amount"] = amount

    if payment_date is not None:
        data["payment_date"] = payment_date

    return PaymentUpdate(**data)
