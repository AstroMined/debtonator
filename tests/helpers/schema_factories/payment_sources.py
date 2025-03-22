"""
PaymentSource schema factory functions.

This module provides factory functions for creating valid PaymentSource-related
Pydantic schema instances for use in tests.
"""

from decimal import Decimal
from typing import Any, Dict, Optional

from src.schemas.payments import PaymentSourceCreate
from tests.helpers.schema_factories.base import factory_function


@factory_function(PaymentSourceCreate)
def create_payment_source_schema(
    account_id: int = 1,
    amount: Optional[Decimal] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid PaymentSourceCreate schema instance.

    Args:
        account_id: ID of the account used for payment
        amount: Amount paid from this account (defaults to 100.00)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create PaymentSourceCreate schema
    """
    if amount is None:
        amount = Decimal("100.00")

    data = {
        "account_id": account_id,
        "amount": amount,
        **kwargs,
    }

    return data
