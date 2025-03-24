"""
PaymentSource schema factory functions.

This module provides factory functions for creating valid PaymentSource-related
Pydantic schema instances for use in tests.
"""

from decimal import Decimal
from typing import Any, Dict, Optional

from src.schemas.payments import PaymentSourceCreate, PaymentSourceCreateNested, PaymentSourceUpdate
from tests.helpers.schema_factories.base import factory_function


@factory_function(PaymentSourceCreateNested)
def create_payment_source_nested_schema(
    account_id: int = 1,
    amount: Optional[Decimal] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid PaymentSourceCreateNested schema instance.

    Args:
        account_id: ID of the account used for payment
        amount: Amount paid from this account (defaults to 100.00)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create PaymentSourceCreateNested schema
    """
    if amount is None:
        amount = Decimal("100.00")

    data = {
        "account_id": account_id,
        "amount": amount,
        **kwargs,
    }

    return data


@factory_function(PaymentSourceCreate)
def create_payment_source_schema(
    account_id: int = 1,
    amount: Optional[Decimal] = None,
    payment_id: Optional[int] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid PaymentSourceCreate schema instance.

    Args:
        account_id: ID of the account used for payment
        amount: Amount paid from this account (defaults to 100.00)
        payment_id: ID of the payment this source belongs to (required)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create PaymentSourceCreate schema
    """
    if amount is None:
        amount = Decimal("100.00")

    if payment_id is None:
        raise ValueError("payment_id is required for PaymentSourceCreate")

    data = {
        "account_id": account_id,
        "amount": amount,
        "payment_id": payment_id,
        **kwargs,
    }
    
    return data


@factory_function(PaymentSourceUpdate)
def create_payment_source_update_schema(
    id: int,
    account_id: Optional[int] = None,
    amount: Optional[Decimal] = None,
    payment_id: Optional[int] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid PaymentSourceUpdate schema instance.

    Args:
        id: ID of the payment source to update
        account_id: New account ID (optional)
        amount: New amount (optional)
        payment_id: New payment ID (optional)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create PaymentSourceUpdate schema
    """
    data = {"id": id, **kwargs}

    if account_id is not None:
        data["account_id"] = account_id

    if amount is not None:
        data["amount"] = amount
        
    if payment_id is not None:
        data["payment_id"] = payment_id

    return data
