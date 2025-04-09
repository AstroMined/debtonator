"""
RecurringIncome schema factory functions.

This module provides factory functions for creating valid RecurringIncome-related
Pydantic schema instances for use in tests.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from src.schemas.recurring_income import (
    RecurringIncomeCreate,
    RecurringIncomeInDB,
    RecurringIncomeResponse,
    RecurringIncomeUpdate,
)
from src.utils.datetime_utils import utc_now
from tests.helpers.schema_factories.base_schema_schema_factories import (
    MEDIUM_AMOUNT,
    factory_function,
)


@factory_function(RecurringIncomeCreate)
def create_recurring_income_schema(
    source: str = "Monthly Salary",
    amount: Optional[Decimal] = None,
    day_of_month: int = 15,
    account_id: int = 1,
    category_id: Optional[int] = None,
    auto_deposit: bool = False,
    active: bool = True,  # Used internally but not in schema
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid RecurringIncomeCreate schema instance.

    Args:
        source (str): Name of the income source
        amount (Optional[Decimal]): Income amount (defaults to 1000.00)
        day_of_month (int): Day of the month when income is received
        account_id (int): ID of the account for this income
        category_id (Optional[int]): Optional category ID
        auto_deposit (bool): Whether to auto-deposit this income
        active (bool): Whether this recurring income is active (not in schema)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create RecurringIncomeCreate schema
    """
    if amount is None:
        amount = MEDIUM_AMOUNT * Decimal("10")  # 1000.00

    data = {
        "source": source,
        "amount": amount,
        "day_of_month": day_of_month,
        "account_id": account_id,
        "auto_deposit": auto_deposit,
        **kwargs,
    }

    if category_id is not None:
        data["category_id"] = category_id

    return data


@factory_function(RecurringIncomeUpdate)
def create_recurring_income_update_schema(
    source: Optional[str] = None,
    amount: Optional[Decimal] = None,
    day_of_month: Optional[int] = None,
    account_id: Optional[int] = None,
    category_id: Optional[int] = None,
    auto_deposit: Optional[bool] = None,
    active: Optional[bool] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid RecurringIncomeUpdate schema instance.

    Args:
        source (Optional[str]): Name of the income source
        amount (Optional[Decimal]): Income amount
        day_of_month (Optional[int]): Day of the month when income is received
        account_id (Optional[int]): ID of the account for this income
        category_id (Optional[int]): Optional category ID
        auto_deposit (Optional[bool]): Whether to auto-deposit this income
        active (Optional[bool]): Whether this recurring income is active
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create RecurringIncomeUpdate schema
    """
    data = {**kwargs}

    if source is not None:
        data["source"] = source

    if amount is not None:
        data["amount"] = amount

    if day_of_month is not None:
        data["day_of_month"] = day_of_month

    if account_id is not None:
        data["account_id"] = account_id

    if category_id is not None:
        data["category_id"] = category_id

    if auto_deposit is not None:
        data["auto_deposit"] = auto_deposit

    if active is not None:
        data["active"] = active

    return data


@factory_function(RecurringIncomeInDB)
def create_recurring_income_in_db_schema(
    id: int = 1,
    source: str = "Monthly Salary",
    amount: Optional[Decimal] = None,
    day_of_month: int = 15,
    account_id: int = 1,
    category_id: Optional[int] = None,
    auto_deposit: bool = False,
    active: bool = True,
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid RecurringIncomeInDB schema instance.

    Args:
        id (int): ID of the recurring income
        source (str): Name of the income source
        amount (Optional[Decimal]): Income amount (defaults to 1000.00)
        day_of_month (int): Day of the month when income is received
        account_id (int): ID of the account for this income
        category_id (Optional[int]): Optional category ID
        auto_deposit (bool): Whether to auto-deposit this income
        active (bool): Whether this recurring income is active
        created_at (Optional[datetime]): Creation timestamp (UTC)
        updated_at (Optional[datetime]): Last update timestamp (UTC)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create RecurringIncomeInDB schema
    """
    if amount is None:
        amount = MEDIUM_AMOUNT * Decimal("10")  # 1000.00

    if created_at is None:
        created_at = utc_now()

    if updated_at is None:
        updated_at = created_at

    data = {
        "id": id,
        "source": source,
        "amount": amount,
        "day_of_month": day_of_month,
        "account_id": account_id,
        "auto_deposit": auto_deposit,
        "active": active,
        "created_at": created_at,
        "updated_at": updated_at,
        **kwargs,
    }

    if category_id is not None:
        data["category_id"] = category_id

    return data


@factory_function(RecurringIncomeResponse)
def create_recurring_income_response_schema(
    id: int = 1,
    source: str = "Monthly Salary",
    amount: Optional[Decimal] = None,
    day_of_month: int = 15,
    account_id: int = 1,
    category_id: Optional[int] = None,
    auto_deposit: bool = False,
    active: bool = True,
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None,
    account: Optional[
        Dict[str, Any]
    ] = None,  # Used for internal processing, not in schema
    category: Optional[
        Dict[str, Any]
    ] = None,  # Used for internal processing, not in schema
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid RecurringIncomeResponse schema instance.

    Args:
        id (int): ID of the recurring income
        source (str): Name of the income source
        amount (Optional[Decimal]): Income amount (defaults to 1000.00)
        day_of_month (int): Day of the month when income is received
        account_id (int): ID of the account for this income
        category_id (Optional[int]): Optional category ID
        auto_deposit (bool): Whether to auto-deposit this income
        active (bool): Whether this recurring income is active
        created_at (Optional[datetime]): Creation timestamp (UTC)
        updated_at (Optional[datetime]): Last update timestamp (UTC)
        account (Optional[Dict[str, Any]]): Account information (not in schema)
        category (Optional[Dict[str, Any]]): Category information (not in schema)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create RecurringIncomeResponse schema
    """
    if amount is None:
        amount = MEDIUM_AMOUNT * Decimal("10")  # 1000.00

    if created_at is None:
        created_at = utc_now()

    if updated_at is None:
        updated_at = created_at

    # These are used internally but not in schema
    if account is None and account_id is not None:
        account = {
            "id": account_id,
            "name": f"Account {account_id}",
            "account_type": "checking",
            "active": True,
        }

    if category is None and category_id is not None:
        category = {"id": category_id, "name": f"Category {category_id}"}

    data = {
        "id": id,
        "source": source,
        "amount": amount,
        "day_of_month": day_of_month,
        "account_id": account_id,
        "auto_deposit": auto_deposit,
        "active": active,
        "created_at": created_at,
        "updated_at": updated_at,
        **kwargs,
    }

    if category_id is not None:
        data["category_id"] = category_id

    # Account and category are used by the factory but not included
    # in the schema fields - the data is used for lookups

    return data
