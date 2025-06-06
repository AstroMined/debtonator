"""
Statement history schema factory functions.

This module provides factory functions for creating valid StatementHistory-related
Pydantic schema instances for use in tests.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, Optional

from src.schemas.statement_history import StatementHistoryCreate, StatementHistoryUpdate
from src.utils.datetime_utils import utc_now
from tests.helpers.schema_factories.base_schema_schema_factories import factory_function


@factory_function(StatementHistoryCreate)
def create_statement_history_schema(
    account_id: int,
    statement_date: Optional[datetime] = None,
    statement_balance: Optional[Decimal] = None,
    minimum_payment: Optional[Decimal] = None,
    due_date: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid StatementHistoryCreate schema instance.

    Args:
        account_id: ID of the associated account
        statement_date: Date of the statement (defaults to current UTC time)
        statement_balance: Balance on statement date (defaults to 500.00)
        minimum_payment: Minimum payment due (optional)
        due_date: Payment due date (defaults to statement_date + 25 days if not provided)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create StatementHistoryCreate schema
    """
    if statement_date is None:
        statement_date = utc_now()

    if statement_balance is None:
        statement_balance = Decimal("500.00")

    data = {
        "account_id": account_id,
        "statement_date": statement_date,
        "statement_balance": statement_balance,
        **kwargs,
    }

    if minimum_payment is not None:
        data["minimum_payment"] = minimum_payment

    if due_date is not None:
        data["due_date"] = due_date
    elif minimum_payment is not None:
        # If minimum_payment is set but due_date is not, default to 25 days after statement
        data["due_date"] = statement_date + timedelta(days=25)

    return data


@factory_function(StatementHistoryUpdate)
def create_statement_history_update_schema(
    statement_balance: Optional[Decimal] = None,
    minimum_payment: Optional[Decimal] = None,
    due_date: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid StatementHistoryUpdate schema instance.

    Args:
        statement_balance: Updated balance on statement date (optional)
        minimum_payment: Updated minimum payment due (optional)
        due_date: Updated payment due date (optional)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create StatementHistoryUpdate schema
    """
    data = {**kwargs}

    if statement_balance is not None:
        data["statement_balance"] = statement_balance

    if minimum_payment is not None:
        data["minimum_payment"] = minimum_payment

    if due_date is not None:
        data["due_date"] = due_date

    return data
