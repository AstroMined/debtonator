"""
Credit limit history schema factory functions.

This module provides factory functions for creating valid CreditLimitHistory-related
Pydantic schema instances for use in tests.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, Optional

from src.schemas.credit_limit_history import (
    CreditLimitHistoryCreate,
    CreditLimitHistoryUpdate,
)
from tests.helpers.schema_factories.base import factory_function, utc_now


@factory_function(CreditLimitHistoryCreate)
def create_credit_limit_history_schema(
    account_id: int,
    credit_limit: Optional[Decimal] = None,
    effective_date: Optional[datetime] = None,
    reason: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid CreditLimitHistoryCreate schema instance.

    Args:
        account_id: ID of the account
        credit_limit: Credit limit (defaults to 5000.00)
        effective_date: Date when limit became effective (defaults to now)
        reason: Reason for credit limit change (optional)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create CreditLimitHistoryCreate schema
    """
    if credit_limit is None:
        credit_limit = Decimal("5000.00")

    if effective_date is None:
        effective_date = utc_now()

    data = {
        "account_id": account_id,
        "credit_limit": credit_limit,
        "effective_date": effective_date,
        **kwargs,
    }

    if reason is not None:
        data["reason"] = reason

    return data


@factory_function(CreditLimitHistoryUpdate)
def create_credit_limit_history_update_schema(
    id: int,
    effective_date: Optional[datetime] = None,
    credit_limit: Optional[Decimal] = None,
    reason: Optional[str] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid CreditLimitHistoryUpdate schema instance.

    Args:
        id: ID of the credit limit history entry to update
        effective_date: Updated effective date (required)
        credit_limit: New credit limit (optional)
        reason: New reason (optional)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create CreditLimitHistoryUpdate schema
    """
    # Default effective_date to now if not provided
    if effective_date is None:
        effective_date = utc_now()
        
    data = {
        "id": id, 
        "effective_date": effective_date,
        **kwargs
    }

    if credit_limit is not None:
        data["credit_limit"] = credit_limit

    if reason is not None:
        data["reason"] = reason

    return data
