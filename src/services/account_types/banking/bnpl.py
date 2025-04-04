"""
Buy Now, Pay Later (BNPL) account service module.

This module provides specialized service functionality for BNPL accounts,
including validation, lifecycle management, and payment scheduling.

Implemented as part of ADR-016 Account Type Expansion and ADR-019 Banking Account Types.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession


async def validate_create(session: AsyncSession, data: Dict[str, Any]) -> None:
    """
    Validate BNPL account creation data.

    Args:
        session: Database session
        data: Account creation data
        
    Raises:
        ValueError: If validation fails
    """
    # Installment count is required for BNPL accounts
    if "installment_count" not in data or not data["installment_count"]:
        raise ValueError("Installment count is required for BNPL accounts")
    
    if data["installment_count"] <= 0:
        raise ValueError("Installment count must be greater than zero")
    
    # Validate installment count is within reasonable range
    if data["installment_count"] > 48:
        raise ValueError("Installment count cannot exceed 48 months (4 years)")
    
    # Validate payment frequency
    if "payment_frequency" in data:
        valid_frequencies = ["weekly", "biweekly", "monthly"]
        if data["payment_frequency"] not in valid_frequencies:
            raise ValueError(f"Payment frequency must be one of: {', '.join(valid_frequencies)}")
    
    # Validate next payment date is in the future for new accounts
    if "next_payment_date" in data:
        next_payment_date = data["next_payment_date"]
        now = datetime.now(timezone.utc)
        
        if next_payment_date < now:
            raise ValueError("Next payment date must be in the future")
    
    # Validate installments paid does not exceed installment count
    if "installments_paid" in data and data["installments_paid"] > data["installment_count"]:
        raise ValueError("Installments paid cannot exceed total installment count")
    
    # Validate current balance matches expected balance based on remaining installments
    if all(k in data for k in ["installment_count", "installments_paid", "installment_amount"]):
        remaining = data["installment_count"] - data["installments_paid"]
        expected_balance = remaining * data["installment_amount"]
        
        if "current_balance" in data and abs(data["current_balance"] - expected_balance) > Decimal("0.01"):
            # Auto-correct the balance with a small warning
            data["current_balance"] = expected_balance


async def validate_update(session: AsyncSession, data: Dict[str, Any], existing_account: Any) -> None:
    """
    Validate BNPL account update data.

    Args:
        session: Database session
        data: Account update data
        existing_account: Existing account model instance
        
    Raises:
        ValueError: If validation fails
    """
    # For existing accounts, validate installment changes
    if "installment_count" in data:
        # Cannot reduce installment count below already paid installments
        if (data["installment_count"] < 
                getattr(existing_account, "installments_paid", 0)):
            raise ValueError("Cannot reduce installment count below already paid installments")
    
    # Validate installments paid update
    if "installments_paid" in data:
        # Cannot set installments paid higher than total installment count
        installment_count = data.get("installment_count", 
                              getattr(existing_account, "installment_count", 0))
        if data["installments_paid"] > installment_count:
            raise ValueError("Installments paid cannot exceed total installment count")
    
    # Validate payment frequency update
    if "payment_frequency" in data:
        valid_frequencies = ["weekly", "biweekly", "monthly"]
        if data["payment_frequency"] not in valid_frequencies:
            raise ValueError(f"Payment frequency must be one of: {', '.join(valid_frequencies)}")
    
    # Validate current balance update
    if "current_balance" in data and "installment_amount" not in data:
        # Current balance should match remaining installments × installment amount
        installment_count = data.get("installment_count", 
                              getattr(existing_account, "installment_count", 0))
        installments_paid = data.get("installments_paid", 
                              getattr(existing_account, "installments_paid", 0))
        installment_amount = getattr(existing_account, "installment_amount", Decimal("0"))
        
        remaining = installment_count - installments_paid
        expected_balance = remaining * installment_amount
        
        if abs(data["current_balance"] - expected_balance) > Decimal("0.01"):
            # Auto-correct the balance with a small warning
            data["current_balance"] = expected_balance


async def update_overview(session: AsyncSession, account: Any, overview: Dict[str, Decimal]) -> None:
    """
    Update banking overview with BNPL account data.

    Args:
        session: Database session
        account: BNPL account model instance
        overview: Overview dictionary to update
    """
    # BNPL balance is considered debt
    overview["bnpl_balance"] += account.current_balance
    overview["total_debt"] += account.current_balance


async def get_upcoming_payments(session: AsyncSession, account_id: int, days: int) -> List[Dict[str, Any]]:
    """
    Get upcoming payments for BNPL accounts.

    Args:
        session: Database session
        account_id: Account ID to get payments for
        days: Number of days to look ahead

    Returns:
        List of upcoming payments
    """
    from src.repositories.factory import RepositoryFactory
    
    # Get the repository with this session
    account_repo = RepositoryFactory.create_account_repository(session)
    account = await account_repo.get_with_type(account_id)
    
    if not account or account.account_type != "bnpl" or account.is_closed:
        return []
    
    upcoming_payments = []
    now = datetime.now(timezone.utc)
    end_date = now + timedelta(days=days)
    
    # Only include upcoming payments if not all installments are paid
    if (account.installments_paid < account.installment_count and 
            account.next_payment_date and 
            now <= account.next_payment_date <= end_date):
        
        upcoming_payments.append({
            "account_id": account.id,
            "account_name": account.name,
            "account_type": "bnpl",
            "due_date": account.next_payment_date,
            "amount": account.installment_amount,
            "full_amount": account.installment_amount,
            "payment_type": "installment",
            "remaining_installments": account.installment_count - account.installments_paid
        })
    
    return upcoming_payments


async def update_bnpl_status(session: AsyncSession, account_id: int) -> Optional[Any]:
    """
    Update BNPL account status based on payment dates.
    
    This function handles the lifecycle of BNPL accounts:
    - Increments installments_paid if payment date has passed
    - Updates next_payment_date based on payment frequency
    - Updates current_balance based on remaining installments
    - Marks account as closed when all installments are paid

    Args:
        session: Database session
        account_id: Account ID to update

    Returns:
        Updated account or None if not found
    """
    from src.repositories.factory import RepositoryFactory
    
    # Get the repository with this session
    account_repo = RepositoryFactory.create_account_repository(session)
    account = await account_repo.get_with_type(account_id)
    
    if not account or account.account_type != "bnpl":
        return None
    
    now = datetime.now(timezone.utc)
    
    # Only update if payment date has passed and not all installments are paid
    if (account.next_payment_date and 
            account.next_payment_date < now and 
            account.installments_paid < account.installment_count):
        
        # Calculate new next payment date based on frequency
        if account.payment_frequency == "weekly":
            next_payment_date = account.next_payment_date + timedelta(days=7)
        elif account.payment_frequency == "biweekly":
            next_payment_date = account.next_payment_date + timedelta(days=14)
        elif account.payment_frequency == "monthly":
            # Handle month boundary correctly
            next_payment_date = account.next_payment_date.replace(
                month=(account.next_payment_date.month % 12) + 1,
                year=account.next_payment_date.year + (account.next_payment_date.month == 12)
            )
        else:
            # Default to biweekly
            next_payment_date = account.next_payment_date + timedelta(days=14)
        
        # Prepare update data
        update_data = {
            "installments_paid": account.installments_paid + 1,
            "next_payment_date": next_payment_date
        }
        
        # Check if this was the last installment
        if account.installments_paid + 1 >= account.installment_count:
            update_data["is_closed"] = True
            update_data["current_balance"] = Decimal("0")
        else:
            # Update current balance based on remaining installments
            remaining = account.installment_count - (account.installments_paid + 1)
            update_data["current_balance"] = account.installment_amount * remaining
        
        # Update the account
        return await account_repo.update_typed_account(account_id, "bnpl", update_data)
    
    return account


async def prepare_account_data(session: AsyncSession, account_data: Dict[str, Any]) -> None:
    """
    Prepare account data before creating a BNPL account.

    Args:
        session: Database session
        account_data: Account data to prepare
    """
    # Set defaults for BNPL accounts if not provided
    if "payment_frequency" not in account_data:
        account_data["payment_frequency"] = "monthly"
    
    if "installments_paid" not in account_data:
        account_data["installments_paid"] = 0
    
    # Calculate current balance if not provided
    if ("current_balance" not in account_data and 
            "installment_amount" in account_data and 
            "installment_count" in account_data):
        remaining = account_data["installment_count"] - account_data.get("installments_paid", 0)
        account_data["current_balance"] = account_data["installment_amount"] * remaining
    
    # Set next payment date if not provided
    if "next_payment_date" not in account_data:
        # Default to 1 month from now
        account_data["next_payment_date"] = datetime.now(timezone.utc) + timedelta(days=30)
