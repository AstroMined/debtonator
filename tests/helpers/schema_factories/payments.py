"""
Payment schema factory functions.

This module provides factory functions for creating valid Payment-related
Pydantic schema instances for use in tests.
"""

from datetime import datetime, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union

from src.schemas.payments import (
    PaymentCreate,
    PaymentDateRange,
    PaymentSourceCreate,
    PaymentUpdate,
)
from tests.helpers.schema_factories.base import MEDIUM_AMOUNT, factory_function, utc_now
from tests.helpers.schema_factories.payment_sources import create_payment_source_schema


@factory_function(PaymentCreate)
def create_payment_schema(
    amount: Optional[Decimal] = None,
    payment_date: Optional[datetime] = None,
    category: str = "Bill Payment",
    description: Optional[str] = "Test payment description",
    liability_id: Optional[int] = None,
    income_id: Optional[int] = None,
    sources: Optional[List[Union[PaymentSourceCreate, Dict[str, Any]]]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid PaymentCreate schema instance.

    Args:
        amount: Payment amount (defaults to 100.00)
        payment_date: Date of payment (defaults to now)
        category: Payment category
        description: Optional payment description
        liability_id: ID of the liability being paid (optional)
        income_id: ID of the income being paid (optional)
        sources: List of payment sources (will create one default source if None)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create PaymentCreate schema
    """
    if amount is None:
        amount = MEDIUM_AMOUNT

    if payment_date is None:
        payment_date = utc_now()

    data = {
        "amount": amount,
        "payment_date": payment_date,
        "category": category,
        "description": description,
        **kwargs,
    }

    if liability_id is not None:
        data["liability_id"] = liability_id

    if income_id is not None:
        data["income_id"] = income_id

    # If no sources provided, create a single source with the full amount
    if sources is None:
        data["sources"] = [create_payment_source_schema(amount=amount)]
    else:
        # Convert any dict sources to schemas if needed
        source_schemas = []
        for source in sources:
            if isinstance(source, dict):
                source_schemas.append(create_payment_source_schema(**source))
            else:
                source_schemas.append(source)
        data["sources"] = source_schemas

    return data


@factory_function(PaymentUpdate)
def create_payment_update_schema(
    id: int,
    amount: Optional[Decimal] = None,
    payment_date: Optional[datetime] = None,
    category: Optional[str] = None,
    description: Optional[str] = None,
    sources: Optional[List[Union[PaymentSourceCreate, Dict[str, Any]]]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid PaymentUpdate schema instance.

    Args:
        id: ID of the payment to update
        amount: New payment amount (optional)
        payment_date: New payment date (optional)
        category: New payment category (optional)
        description: New payment description (optional)
        sources: New payment sources (optional)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create PaymentUpdate schema
    """
    data = {"id": id, **kwargs}

    if amount is not None:
        data["amount"] = amount

    if payment_date is not None:
        data["payment_date"] = payment_date

    if category is not None:
        data["category"] = category

    if description is not None:
        data["description"] = description

    if sources is not None:
        # Convert any dict sources to schemas if needed
        source_schemas = []
        for source in sources:
            if isinstance(source, dict):
                source_schemas.append(create_payment_source_schema(**source))
            else:
                source_schemas.append(source)
        data["sources"] = source_schemas

    return data


@factory_function(PaymentDateRange)
def create_payment_date_range_schema(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid PaymentDateRange schema instance.

    Args:
        start_date: Start date for the range (defaults to 30 days ago)
        end_date: End date for the range (defaults to now)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create PaymentDateRange schema
    """
    now = utc_now()

    if start_date is None:
        # Default to 30 days ago
        start_date = datetime(
            now.year, now.month, 1, tzinfo=timezone.utc
        )  # First day of current month

    if end_date is None:
        # Default to now
        end_date = now

    data = {
        "start_date": start_date,
        "end_date": end_date,
        **kwargs,
    }

    return data
