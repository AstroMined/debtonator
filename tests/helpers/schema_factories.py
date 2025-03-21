"""
Schema factory functions for tests.

This module provides factory functions that generate valid Pydantic schema instances
for use in tests. Using these factories ensures that all repository tests follow
the proper validation flow by passing data through Pydantic schemas first.

Each factory function:
1. Creates a valid schema instance with reasonable defaults
2. Allows overriding specific fields as needed
3. Returns a validated schema ready for use

Usage:
    # Create a schema with defaults
    bill_schema = create_bill_split_schema(liability_id=1, account_id=2)

    # Pass to repository after validation
    validated_data = bill_schema.model_dump()
    result = await bill_split_repository.create(validated_data)
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, Optional

from src.models.liabilities import LiabilityStatus
from src.models.transaction_history import TransactionType
from src.schemas.accounts import AccountCreate, AccountUpdate
from src.schemas.balance_reconciliation import (
    BalanceReconciliationCreate,
    BalanceReconciliationUpdate,
)
from src.schemas.bill_splits import BillSplitCreate, BillSplitUpdate
from src.schemas.credit_limit_history import (
    CreditLimitHistoryCreate,
    CreditLimitHistoryUpdate,
)
from src.schemas.liabilities import LiabilityCreate, LiabilityUpdate
from src.schemas.payments import PaymentCreate, PaymentUpdate
from src.schemas.transaction_history import (
    TransactionHistoryCreate,
    TransactionHistoryUpdate,
)


def create_bill_split_schema(
    liability_id: int, account_id: int, amount: Optional[Decimal] = None, **kwargs: Any
) -> BillSplitCreate:
    """
    Create a valid BillSplitCreate schema instance.

    Args:
        liability_id: ID of the liability
        account_id: ID of the account
        amount: Split amount (defaults to 100.00)
        **kwargs: Additional fields to override

    Returns:
        BillSplitCreate: Validated schema instance
    """
    if amount is None:
        amount = Decimal("100.00")

    data = {
        "liability_id": liability_id,
        "account_id": account_id,
        "amount": amount,
        **kwargs,
    }

    return BillSplitCreate(**data)


def create_bill_split_update_schema(
    id: int, amount: Optional[Decimal] = None, **kwargs: Any
) -> BillSplitUpdate:
    """
    Create a valid BillSplitUpdate schema instance.

    Args:
        id: ID of the bill split to update
        amount: New split amount (defaults to 150.00)
        **kwargs: Additional fields to override

    Returns:
        BillSplitUpdate: Validated schema instance
    """
    if amount is None:
        amount = Decimal("150.00")

    data = {"id": id, "amount": amount, **kwargs}

    return BillSplitUpdate(**data)


def create_liability_schema(
    name: str = "Test Liability",
    amount: Optional[Decimal] = None,
    category_id: int = 1,
    primary_account_id: int = 1,
    due_date_days: int = 30,
    recurring: bool = False,
    auto_pay: bool = False,
    **kwargs: Any,
) -> LiabilityCreate:
    """
    Create a valid LiabilityCreate schema instance.

    Args:
        name: Liability name
        amount: Total amount (defaults to 200.00)
        category_id: Category ID
        primary_account_id: Primary account ID
        due_date_days: Days from now for due date (defaults to 30)
        recurring: Whether this is a recurring liability
        auto_pay: Whether auto-pay is enabled
        **kwargs: Additional fields to override

    Returns:
        LiabilityCreate: Validated schema instance
    """
    if amount is None:
        amount = Decimal("200.00")

    # Create a future due date with UTC timezone
    due_date = datetime.now(timezone.utc) + timedelta(days=due_date_days)

    data = {
        "name": name,
        "amount": amount,
        "due_date": due_date,
        "category_id": category_id,
        "primary_account_id": primary_account_id,
        "recurring": recurring,
        "auto_pay": auto_pay,
        "status": LiabilityStatus.PENDING,
        **kwargs,
    }

    return LiabilityCreate(**data)


def create_account_schema(
    name: str = "Test Account",
    account_type: str = "checking",
    available_balance: Optional[Decimal] = None,
    total_limit: Optional[Decimal] = None,
    **kwargs: Any,
) -> AccountCreate:
    """
    Create a valid AccountCreate schema instance.

    Args:
        name: Account name
        account_type: Account type (checking, savings, credit)
        available_balance: Available balance (defaults based on account type)
        total_limit: Credit limit (only used for credit accounts)
        **kwargs: Additional fields to override

    Returns:
        AccountCreate: Validated schema instance
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

    return AccountCreate(**data)


def create_payment_schema(
    liability_id: int,
    amount: Optional[Decimal] = None,
    payment_date: Optional[datetime] = None,
    **kwargs: Any,
) -> PaymentCreate:
    """
    Create a valid PaymentCreate schema instance.

    Args:
        liability_id: ID of the liability being paid
        amount: Payment amount (defaults to 100.00)
        payment_date: Date of payment (defaults to today)
        **kwargs: Additional fields to override

    Returns:
        PaymentCreate: Validated schema instance
    """
    if amount is None:
        amount = Decimal("100.00")

    if payment_date is None:
        payment_date = datetime.now(timezone.utc)

    data = {
        "liability_id": liability_id,
        "amount": amount,
        "payment_date": payment_date,
        **kwargs,
    }

    return PaymentCreate(**data)


def create_credit_limit_history_schema(
    account_id: int,
    credit_limit: Optional[Decimal] = None,
    effective_date: Optional[datetime] = None,
    reason: Optional[str] = None,
    **kwargs: Any,
) -> CreditLimitHistoryCreate:
    """
    Create a valid CreditLimitHistoryCreate schema instance.

    Args:
        account_id: ID of the account
        credit_limit: Credit limit (defaults to 5000.00)
        effective_date: Date when limit became effective (defaults to now)
        reason: Reason for credit limit change (optional)
        **kwargs: Additional fields to override

    Returns:
        CreditLimitHistoryCreate: Validated schema instance
    """
    if credit_limit is None:
        credit_limit = Decimal("5000.00")

    if effective_date is None:
        effective_date = datetime.now(timezone.utc)

    data = {
        "account_id": account_id,
        "credit_limit": credit_limit,
        "effective_date": effective_date,
        **kwargs,
    }

    if reason is not None:
        data["reason"] = reason

    return CreditLimitHistoryCreate(**data)


def create_balance_reconciliation_schema(
    account_id: int,
    previous_balance: Optional[Decimal] = None,
    new_balance: Optional[Decimal] = None,
    reason: str = "Balance correction",
    reconciliation_date: Optional[datetime] = None,
    **kwargs: Any,
) -> BalanceReconciliationCreate:
    """
    Create a valid BalanceReconciliationCreate schema instance.

    Args:
        account_id: ID of the account
        previous_balance: Previous balance (defaults to 1000.00)
        new_balance: New balance (defaults to 1100.00)
        reason: Reason for reconciliation
        reconciliation_date: Date of reconciliation (defaults to now)
        **kwargs: Additional fields to override

    Returns:
        BalanceReconciliationCreate: Validated schema instance
    """
    if previous_balance is None:
        previous_balance = Decimal("1000.00")

    if new_balance is None:
        new_balance = Decimal("1100.00")

    if reconciliation_date is None:
        reconciliation_date = datetime.now(timezone.utc)

    # Calculate adjustment amount
    adjustment_amount = new_balance - previous_balance

    data = {
        "account_id": account_id,
        "previous_balance": previous_balance,
        "new_balance": new_balance,
        "adjustment_amount": adjustment_amount,
        "reason": reason,
        "reconciliation_date": reconciliation_date,
        **kwargs,
    }

    return BalanceReconciliationCreate(**data)


def create_transaction_history_schema(
    account_id: int,
    amount: Optional[Decimal] = None,
    transaction_type: TransactionType = TransactionType.CREDIT,
    description: Optional[str] = None,
    transaction_date: Optional[datetime] = None,
    **kwargs: Any,
) -> TransactionHistoryCreate:
    """
    Create a valid TransactionHistoryCreate schema instance.

    Args:
        account_id: ID of the account
        amount: Transaction amount (defaults to 100.00)
        transaction_type: Type of transaction (credit or debit)
        description: Transaction description
        transaction_date: Date of transaction (defaults to now)
        **kwargs: Additional fields to override

    Returns:
        TransactionHistoryCreate: Validated schema instance
    """
    if amount is None:
        amount = Decimal("100.00")

    if transaction_date is None:
        transaction_date = datetime.now(timezone.utc)

    data = {
        "account_id": account_id,
        "amount": amount,
        "transaction_type": transaction_type,
        "transaction_date": transaction_date,
        **kwargs,
    }

    if description is not None:
        data["description"] = description

    return TransactionHistoryCreate(**data)
