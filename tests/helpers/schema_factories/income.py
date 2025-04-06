"""
Income schema factory functions.

This module provides factory functions for creating valid Income-related
Pydantic schema instances for use in tests.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from src.schemas.income import IncomeCreate
from tests.helpers.schema_factories.base import factory_function
from src.utils.datetime_utils import utc_now


@factory_function(IncomeCreate)
def create_income_schema(
    account_id: int,
    date: Optional[datetime] = None,
    source: str = "Test Income",
    amount: Optional[Decimal] = None,
    deposited: bool = False,
    category_id: Optional[int] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid IncomeCreate schema instance.

    Args:
        account_id: ID of the account this income belongs to
        date: Date of the income (defaults to current UTC time)
        source: Source of the income
        amount: Income amount (defaults to 1000.00)
        deposited: Whether the income has been deposited
        category_id: ID of the income category (optional)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create IncomeCreate schema
    """
    if date is None:
        date = utc_now()

    if amount is None:
        amount = Decimal("1000.00")

    data = {
        "account_id": account_id,
        "date": date,
        "source": source,
        "amount": amount,
        "deposited": deposited,
        **kwargs,
    }

    if category_id is not None:
        data["category_id"] = category_id

    return data
