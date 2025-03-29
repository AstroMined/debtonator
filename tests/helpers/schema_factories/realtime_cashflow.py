"""
Realtime cashflow schema factory functions.

This module provides factory functions for creating valid realtime cashflow
Pydantic schema instances for use in tests.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

from src.schemas.realtime_cashflow import (
    AccountBalance,
    AccountType,
    RealtimeCashflow,
    RealtimeCashflowResponse,
)
from tests.helpers.schema_factories.base import MEDIUM_AMOUNT, factory_function, utc_now


@factory_function(AccountBalance)
def create_account_balance_schema(
    account_id: int,
    name: str = "Test Account",
    type: AccountType = AccountType.CHECKING,
    current_balance: Optional[Decimal] = None,
    available_credit: Optional[Decimal] = None,
    total_limit: Optional[Decimal] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid AccountBalance schema instance.

    Args:
        account_id: Unique identifier for the account
        name: Name of the account
        type: Type of the account (checking, savings, credit)
        current_balance: Current balance of the account
        available_credit: Available credit (required for credit accounts)
        total_limit: Total credit limit (required for credit accounts)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create AccountBalance schema
    """
    if current_balance is None:
        if type == AccountType.CREDIT:
            current_balance = MEDIUM_AMOUNT * Decimal("-5")  # -500.00
        else:
            current_balance = MEDIUM_AMOUNT * Decimal("10")  # 1000.00

    data = {
        "account_id": account_id,
        "name": name,
        "type": type,
        "current_balance": current_balance,
        **kwargs,
    }

    # Credit accounts require these fields
    if type == AccountType.CREDIT:
        if available_credit is None:
            available_credit = MEDIUM_AMOUNT * Decimal("45")  # 4500.00
        if total_limit is None:
            total_limit = MEDIUM_AMOUNT * Decimal("50")  # 5000.00
        data["available_credit"] = available_credit
        data["total_limit"] = total_limit
    elif available_credit is not None:
        data["available_credit"] = available_credit
    elif total_limit is not None:
        data["total_limit"] = total_limit

    return data


@factory_function(RealtimeCashflow)
def create_realtime_cashflow_schema(
    timestamp: Optional[datetime] = None,
    account_balances: Optional[List[Dict[str, Any]]] = None,
    total_available_funds: Optional[Decimal] = None,
    total_available_credit: Optional[Decimal] = None,
    total_liabilities_due: Optional[Decimal] = None,
    net_position: Optional[Decimal] = None,
    next_bill_due: Optional[datetime] = None,
    days_until_next_bill: Optional[int] = None,
    minimum_balance_required: Optional[Decimal] = None,
    projected_deficit: Optional[Decimal] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid RealtimeCashflow schema instance.

    Args:
        timestamp: When this cashflow snapshot was created (defaults to current UTC time)
        account_balances: List of account balances
        total_available_funds: Total funds available (defaults to 1000.00)
        total_available_credit: Total available credit (defaults to 4500.00)
        total_liabilities_due: Total amount due (defaults to 500.00)
        net_position: Net financial position (calculated if not provided)
        next_bill_due: Date when the next bill is due
        days_until_next_bill: Number of days until the next bill is due
        minimum_balance_required: Minimum balance required (defaults to 200.00)
        projected_deficit: Projected deficit amount
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create RealtimeCashflow schema
    """
    if timestamp is None:
        timestamp = utc_now()

    if account_balances is None:
        # Create sample account balances: one checking and one credit account
        account_balances = [
            create_account_balance_schema(
                account_id=1,
                name="Main Checking",
                type=AccountType.CHECKING,
                current_balance=MEDIUM_AMOUNT * Decimal("10"),  # 1000.00
            ).model_dump(),
            create_account_balance_schema(
                account_id=2,
                name="Credit Card",
                type=AccountType.CREDIT,
                current_balance=MEDIUM_AMOUNT * Decimal("-5"),  # -500.00
                available_credit=MEDIUM_AMOUNT * Decimal("45"),  # 4500.00
                total_limit=MEDIUM_AMOUNT * Decimal("50"),  # 5000.00
            ).model_dump(),
        ]

    if total_available_funds is None:
        # Sum of positive balances
        total_available_funds = MEDIUM_AMOUNT * Decimal("10")  # 1000.00

    if total_available_credit is None:
        # Sum of available_credit across credit accounts
        total_available_credit = MEDIUM_AMOUNT * Decimal("45")  # 4500.00

    if total_liabilities_due is None:
        total_liabilities_due = MEDIUM_AMOUNT * Decimal("5")  # 500.00

    if net_position is None:
        # Calculate net position from total_available_funds and total_liabilities_due
        net_position = total_available_funds - total_liabilities_due  # 500.00

    if minimum_balance_required is None:
        minimum_balance_required = MEDIUM_AMOUNT * Decimal("2")  # 200.00

    data = {
        "timestamp": timestamp,
        "account_balances": account_balances,
        "total_available_funds": total_available_funds,
        "total_available_credit": total_available_credit,
        "total_liabilities_due": total_liabilities_due,
        "net_position": net_position,
        "minimum_balance_required": minimum_balance_required,
        **kwargs,
    }

    if next_bill_due is not None:
        data["next_bill_due"] = next_bill_due

        # If days_until_next_bill is not explicitly provided, calculate it
        if days_until_next_bill is None:
            days_until_next_bill = (next_bill_due - timestamp).days
        data["days_until_next_bill"] = days_until_next_bill
    elif days_until_next_bill is not None:
        data["days_until_next_bill"] = days_until_next_bill
        data["next_bill_due"] = timestamp + timedelta(days=days_until_next_bill)

    if projected_deficit is not None:
        data["projected_deficit"] = projected_deficit

    return data


@factory_function(RealtimeCashflowResponse)
def create_realtime_cashflow_response_schema(
    data: Optional[Dict[str, Any]] = None,
    last_updated: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid RealtimeCashflowResponse schema instance.

    Args:
        data: Real-time cashflow analysis data
        last_updated: When this response was generated (defaults to current UTC time)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create RealtimeCashflowResponse schema
    """
    if data is None:
        data = create_realtime_cashflow_schema().model_dump()

    if last_updated is None:
        last_updated = utc_now()

    response_data = {
        "data": data,
        "last_updated": last_updated,
        **kwargs,
    }

    return response_data
