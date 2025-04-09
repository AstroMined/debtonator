"""
Checking account service module.

This module provides specialized service functionality for checking accounts,
including validation and business rule enforcement.

Implemented as part of ADR-016 Account Type Expansion and ADR-019 Banking Account Types.
"""

from decimal import Decimal
from typing import Any, Dict

from sqlalchemy.ext.asyncio import AsyncSession


async def validate_create(session: AsyncSession, data: Dict[str, Any]) -> None:
    """
    Validate checking account creation data.

    Args:
        session: Database session
        data: Account creation data

    Raises:
        ValueError: If validation fails
    """
    # Validate routing number format if provided
    if data.get("routing_number"):
        routing_number = data["routing_number"]

        # US routing numbers are 9 digits
        if not routing_number.isdigit() or len(routing_number) != 9:
            raise ValueError("Routing number must be a 9-digit number")

    # Validate overdraft protection configuration
    if data.get("has_overdraft_protection") and not data.get("overdraft_limit"):
        raise ValueError(
            "Overdraft limit is required when overdraft protection is enabled"
        )


async def validate_update(
    session: AsyncSession, data: Dict[str, Any], existing_account: Any
) -> None:
    """
    Validate checking account update data.

    Args:
        session: Database session
        data: Account update data
        existing_account: Existing account model instance

    Raises:
        ValueError: If validation fails
    """
    # Validate overdraft protection configuration changes
    if "has_overdraft_protection" in data and data["has_overdraft_protection"]:
        # If enabling overdraft protection, require overdraft limit
        if "overdraft_limit" not in data and not getattr(
            existing_account, "overdraft_limit", None
        ):
            raise ValueError(
                "Overdraft limit is required when overdraft protection is enabled"
            )

    # Validate overdraft limit doesn't exceed allowed amount
    if "overdraft_limit" in data and data["overdraft_limit"] > 10000:
        raise ValueError("Overdraft limit cannot exceed $10,000")


async def update_overview(
    session: AsyncSession, account: Any, overview: Dict[str, Decimal]
) -> None:
    """
    Update banking overview with checking account data.

    Args:
        session: Database session
        account: Checking account model instance
        overview: Overview dictionary to update
    """
    # Checking account balance is considered cash
    overview["checking_balance"] += account.available_balance
    overview["total_cash"] += account.available_balance


async def get_upcoming_payments(
    session: AsyncSession, account_id: int, days: int
) -> list:
    """
    Get upcoming payments for checking accounts.

    Checking accounts typically don't have scheduled recurring payments included
    in this overview, as direct debits and automatic payments are handled differently.

    Args:
        session: Database session
        account_id: Account ID to get payments for
        days: Number of days to look ahead

    Returns:
        Empty list as checking accounts don't have built-in scheduled payments
    """
    # Checking accounts don't typically have scheduled built-in payments
    return []


async def prepare_account_data(
    session: AsyncSession, account_data: Dict[str, Any]
) -> None:
    """
    Prepare account data before creating a checking account.

    Args:
        session: Database session
        account_data: Account data to prepare
    """
    # Ensure all checking account fields are properly initialized
    if "overdraft_limit" not in account_data and account_data.get(
        "has_overdraft_protection"
    ):
        # Set default overdraft limit if not specified but protection enabled
        account_data["overdraft_limit"] = Decimal("500.00")
