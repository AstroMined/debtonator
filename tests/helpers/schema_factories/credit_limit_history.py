"""
Credit limit history schema factory functions.

This module provides factory functions for creating valid CreditLimitHistory-related
Pydantic schema instances for use in tests.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from src.schemas.credit_limit_history import (
    AccountCreditLimitHistoryResponse, CreditLimitHistoryCreate,
    CreditLimitHistoryInDB, CreditLimitHistoryUpdate)
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


@factory_function(CreditLimitHistoryInDB)
def create_credit_limit_history_in_db_schema(
    id: int,
    account_id: int,
    credit_limit: Optional[Decimal] = None,
    effective_date: Optional[datetime] = None,
    reason: Optional[str] = None,
    created_at: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid CreditLimitHistoryInDB schema instance.

    Args:
        id: Unique identifier for the credit limit history entry
        account_id: ID of the account
        credit_limit: Credit limit (defaults to 5000.00)
        effective_date: Date when limit became effective (defaults to now)
        reason: Reason for credit limit change (optional)
        created_at: Creation timestamp (defaults to now)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create CreditLimitHistoryInDB schema
    """
    if credit_limit is None:
        credit_limit = Decimal("5000.00")

    if effective_date is None:
        effective_date = utc_now()

    if created_at is None:
        created_at = utc_now()

    data = {
        "id": id,
        "account_id": account_id,
        "credit_limit": credit_limit,
        "effective_date": effective_date,
        "created_at": created_at,
        **kwargs,
    }

    if reason is not None:
        data["reason"] = reason

    return data


@factory_function(AccountCreditLimitHistoryResponse)
def create_account_credit_limit_history_response_schema(
    account_id: int,
    account_name: str = "Test Credit Card",
    current_credit_limit: Optional[Decimal] = None,
    credit_limit_history: Optional[List[CreditLimitHistoryInDB]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid AccountCreditLimitHistoryResponse schema instance.

    Args:
        account_id: Account ID
        account_name: Account name
        current_credit_limit: Current credit limit (defaults to 5000.00)
        credit_limit_history: List of historical credit limit changes
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create AccountCreditLimitHistoryResponse schema
    """
    if current_credit_limit is None:
        current_credit_limit = Decimal("5000.00")

    if credit_limit_history is None:
        # Create history with 3 entries
        credit_limit_history = [
            create_credit_limit_history_in_db_schema(
                id=1,
                account_id=account_id,
                credit_limit=Decimal("5000.00"),
                effective_date=datetime(2024, 1, 15, tzinfo=utc_now().tzinfo),
                reason="Current limit",
            ),
            create_credit_limit_history_in_db_schema(
                id=2,
                account_id=account_id,
                credit_limit=Decimal("4000.00"),
                effective_date=datetime(2023, 7, 10, tzinfo=utc_now().tzinfo),
                reason="Limit increase due to good payment history",
            ),
            create_credit_limit_history_in_db_schema(
                id=3,
                account_id=account_id,
                credit_limit=Decimal("3000.00"),
                effective_date=datetime(2023, 1, 5, tzinfo=utc_now().tzinfo),
                reason="Initial credit limit",
            ),
        ]

    data = {
        "account_id": account_id,
        "account_name": account_name,
        "current_credit_limit": current_credit_limit,
        "credit_limit_history": credit_limit_history,
        **kwargs,
    }

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

    data = {"id": id, "effective_date": effective_date, **kwargs}

    if credit_limit is not None:
        data["credit_limit"] = credit_limit

    if reason is not None:
        data["reason"] = reason

    return data
