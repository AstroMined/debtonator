"""
Account schema factory functions.

This module provides factory functions for creating valid Account-related
Pydantic schema instances for use in tests.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional

from src.schemas.accounts import (
    AccountCreate,
    AccountInDB,
    AccountResponse,
    AccountStatementHistoryResponse,
    AccountUpdate,
    AvailableCreditResponse,
    StatementBalanceHistory,
)
from tests.helpers.schema_factories.base import factory_function, utc_now


@factory_function(AccountCreate)
def create_account_schema(
    name: str = "Test Account",
    account_type: str = "checking",
    available_balance: Optional[Decimal] = None,
    total_limit: Optional[Decimal] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid AccountCreate schema instance.

    Args:
        name: Account name
        account_type: Account type (checking, savings, credit)
        available_balance: Available balance (defaults based on account type)
        total_limit: Credit limit (only used for credit accounts)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create AccountCreate schema
    """
    if available_balance is None:
        if account_type == "credit":
            available_balance = Decimal("-500.00")
        else:
            available_balance = Decimal("1000.00")

    data = {
        "name": name,
        "type": account_type,
        "available_balance": available_balance,
        **kwargs,
    }

    # Add total_limit for credit accounts
    if account_type == "credit":
        if total_limit is None:
            total_limit = Decimal("5000.00")
        data["total_limit"] = total_limit

    return data


@factory_function(AccountInDB)
def create_account_in_db_schema(
    id: int,
    name: str = "Test Account",
    account_type: str = "checking",
    available_balance: Optional[Decimal] = None,
    total_limit: Optional[Decimal] = None,
    last_statement_balance: Optional[Decimal] = None,
    last_statement_date: Optional[datetime] = None,
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid AccountInDB schema instance.

    Args:
        id: Account ID (unique identifier)
        name: Account name
        account_type: Account type (checking, savings, credit)
        available_balance: Available balance (defaults based on account type)
        total_limit: Credit limit (only used for credit accounts)
        last_statement_balance: Balance from last statement (optional)
        last_statement_date: Date of last statement (optional)
        created_at: Creation timestamp (defaults to now)
        updated_at: Last update timestamp (defaults to now)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create AccountInDB schema
    """
    if available_balance is None:
        if account_type == "credit":
            available_balance = Decimal("-500.00")
        else:
            available_balance = Decimal("1000.00")

    if created_at is None:
        created_at = utc_now()

    if updated_at is None:
        updated_at = utc_now()

    data = {
        "id": id,
        "name": name,
        "type": account_type,
        "available_balance": available_balance,
        "created_at": created_at,
        "updated_at": updated_at,
        **kwargs,
    }

    # Add credit account specific fields
    if account_type == "credit":
        if total_limit is None:
            total_limit = Decimal("5000.00")
        data["total_limit"] = total_limit

        # Calculate available credit if not provided
        if "available_credit" not in data and "available_credit" not in kwargs:
            available_credit = (
                total_limit + available_balance
            )  # Balance is negative for credit
            data["available_credit"] = available_credit

    # Add statement related fields if provided
    if last_statement_balance is not None:
        data["last_statement_balance"] = last_statement_balance

    if last_statement_date is not None:
        data["last_statement_date"] = last_statement_date

    return data


@factory_function(AccountResponse)
def create_account_response_schema(
    id: int,
    name: str = "Test Account",
    account_type: str = "checking",
    available_balance: Optional[Decimal] = None,
    total_limit: Optional[Decimal] = None,
    last_statement_balance: Optional[Decimal] = None,
    last_statement_date: Optional[datetime] = None,
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid AccountResponse schema instance.

    Args:
        id: Account ID (unique identifier)
        name: Account name
        account_type: Account type (checking, savings, credit)
        available_balance: Available balance (defaults based on account type)
        total_limit: Credit limit (only used for credit accounts)
        last_statement_balance: Balance from last statement (optional)
        last_statement_date: Date of last statement (optional)
        created_at: Creation timestamp (defaults to now)
        updated_at: Last update timestamp (defaults to now)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create AccountResponse schema
    """
    # Use the AccountInDB factory since they have the same structure
    return create_account_in_db_schema(
        id=id,
        name=name,
        account_type=account_type,
        available_balance=available_balance,
        total_limit=total_limit,
        last_statement_balance=last_statement_balance,
        last_statement_date=last_statement_date,
        created_at=created_at,
        updated_at=updated_at,
        **kwargs,
    )


@factory_function(StatementBalanceHistory)
def create_statement_balance_history_schema(
    statement_date: Optional[datetime] = None,
    statement_balance: Optional[Decimal] = None,
    minimum_payment: Optional[Decimal] = None,
    due_date: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid StatementBalanceHistory schema instance.

    Args:
        statement_date: Date of the statement (defaults to first of current month)
        statement_balance: Balance on statement date (defaults to 500.00)
        minimum_payment: Minimum payment due (defaults to 10% of balance)
        due_date: Payment due date (defaults to 25 days after statement date)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create StatementBalanceHistory schema
    """
    now = utc_now()

    # Default to first of current month for statement date
    if statement_date is None:
        statement_date = datetime(now.year, now.month, 1, tzinfo=now.tzinfo)

    if statement_balance is None:
        statement_balance = Decimal("500.00")

    if minimum_payment is None:
        # Default minimum payment to 10% of balance or $25, whichever is greater
        minimum_payment = max(statement_balance * Decimal("0.1"), Decimal("25.00"))

    if due_date is None:
        # Default due date to 25 days after statement date
        due_date_day = min(statement_date.day + 25, 28)  # Avoid invalid day in month
        due_date = datetime(
            statement_date.year,
            statement_date.month,
            due_date_day,
            tzinfo=statement_date.tzinfo,
        )

    data = {
        "statement_date": statement_date,
        "statement_balance": statement_balance,
        "minimum_payment": minimum_payment,
        "due_date": due_date,
        **kwargs,
    }

    return data


@factory_function(AccountStatementHistoryResponse)
def create_account_statement_history_response_schema(
    account_id: int,
    account_name: str = "Test Credit Card",
    statement_history: Optional[List[StatementBalanceHistory]] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid AccountStatementHistoryResponse schema instance.

    Args:
        account_id: Account ID (unique identifier)
        account_name: Account name
        statement_history: List of historical statement balances (creates 3 if None)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create AccountStatementHistoryResponse schema
    """
    now = utc_now()

    if statement_history is None:
        # Create 3 months of statement history
        statement_history = [
            create_statement_balance_history_schema(
                statement_date=datetime(now.year, now.month, 1, tzinfo=now.tzinfo),
                statement_balance=Decimal("500.00"),
            ),
            create_statement_balance_history_schema(
                statement_date=datetime(now.year, now.month - 1, 1, tzinfo=now.tzinfo),
                statement_balance=Decimal("450.00"),
            ),
            create_statement_balance_history_schema(
                statement_date=datetime(now.year, now.month - 2, 1, tzinfo=now.tzinfo),
                statement_balance=Decimal("400.00"),
            ),
        ]

    data = {
        "account_id": account_id,
        "account_name": account_name,
        "statement_history": statement_history,
        **kwargs,
    }

    return data


@factory_function(AvailableCreditResponse)
def create_available_credit_response_schema(
    account_id: int,
    account_name: str = "Test Credit Card",
    total_limit: Optional[Decimal] = None,
    current_balance: Optional[Decimal] = None,
    pending_transactions: Optional[Decimal] = None,
    adjusted_balance: Optional[Decimal] = None,
    available_credit: Optional[Decimal] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid AvailableCreditResponse schema instance.

    Args:
        account_id: Account ID (unique identifier)
        account_name: Account name
        total_limit: Total credit limit (defaults to 5000.00)
        current_balance: Current account balance (defaults to -1500.00)
        pending_transactions: Sum of pending transactions (defaults to 200.00)
        adjusted_balance: Balance adjusted for pending transactions (calculated if None)
        available_credit: Available credit after all adjustments (calculated if None)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create AvailableCreditResponse schema
    """
    if total_limit is None:
        total_limit = Decimal("5000.00")

    if current_balance is None:
        current_balance = Decimal("-1500.00")  # Negative for credit accounts

    if pending_transactions is None:
        pending_transactions = Decimal("200.00")

    if adjusted_balance is None:
        # Calculate adjusted balance based on current balance and pending transactions
        adjusted_balance = current_balance - pending_transactions

    if available_credit is None:
        # Calculate available credit based on total limit and adjusted balance
        available_credit = total_limit + adjusted_balance  # Balance is negative

    data = {
        "account_id": account_id,
        "account_name": account_name,
        "total_limit": total_limit,
        "current_balance": current_balance,
        "pending_transactions": pending_transactions,
        "adjusted_balance": adjusted_balance,
        "available_credit": available_credit,
        **kwargs,
    }

    return data


@factory_function(AccountUpdate)
def create_account_update_schema(
    id: int,
    name: Optional[str] = None,
    available_balance: Optional[Decimal] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid AccountUpdate schema instance.

    Args:
        id: ID of the account to update
        name: New account name (optional)
        available_balance: New available balance (optional)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create AccountUpdate schema
    """
    data = {"id": id, **kwargs}

    if name is not None:
        data["name"] = name

    if available_balance is not None:
        data["available_balance"] = available_balance

    return data
