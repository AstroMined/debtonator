"""
Income schema factory functions.

This module provides factory functions for creating valid Income-related
Pydantic schema instances for use in tests.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from src.schemas.income import IncomeCreate, RecurringIncomeCreate
from tests.helpers.schema_factories.base import MEDIUM_AMOUNT, factory_function, utc_now


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


@factory_function(RecurringIncomeCreate)
def create_recurring_income_schema(
    account_id: int,
    source: str = "Monthly Salary",
    amount: Optional[Decimal] = None,
    day_of_month: int = 15,
    category_id: Optional[int] = None,
    auto_deposit: bool = False,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid RecurringIncomeCreate schema instance.

    Args:
        account_id: ID of the account this income belongs to
        source: Source of the recurring income
        amount: Income amount (defaults to 5000.00)
        day_of_month: Day of the month when income occurs (1-30)
        category_id: ID of the income category (optional)
        auto_deposit: Whether to automatically mark as deposited
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create RecurringIncomeCreate schema
    """
    if amount is None:
        amount = Decimal("5000.00")

    # Ensure day_of_month is valid
    if day_of_month > 30:
        day_of_month = 30  # Adjusted to comply with schema validator

    data = {
        "account_id": account_id,
        "source": source,
        "amount": amount,
        "day_of_month": day_of_month,
        "auto_deposit": auto_deposit,
        **kwargs,
    }

    if category_id is not None:
        data["category_id"] = category_id

    return data
