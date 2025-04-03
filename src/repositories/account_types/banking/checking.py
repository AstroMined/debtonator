"""
Checking account repository operations.

This module contains specialized repository operations for checking accounts.
These functions complement the base AccountRepository by providing type-specific
operations that only apply to checking accounts.

Implemented as part of ADR-016 Account Type Expansion and ADR-019 Banking Account Types.
"""

from decimal import Decimal
from typing import List, Optional

from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.checking import CheckingAccount


async def get_all_checking_accounts(
    session: AsyncSession, include_closed: bool = False
) -> List[CheckingAccount]:
    """
    Get all checking accounts.

    Args:
        session: SQLAlchemy async session
        include_closed: Whether to include closed accounts

    Returns:
        List of checking accounts
    """
    query = select(CheckingAccount)

    if not include_closed:
        query = query.where(CheckingAccount.is_closed == False)  # noqa: E712

    result = await session.execute(query)
    return result.scalars().all()


async def get_checking_accounts_with_overdraft(
    session: AsyncSession,
) -> List[CheckingAccount]:
    """
    Get checking accounts with overdraft protection enabled.

    Args:
        session: SQLAlchemy async session

    Returns:
        List of checking accounts with overdraft protection
    """
    query = select(CheckingAccount).where(
        and_(
            CheckingAccount.is_closed == False,  # noqa: E712
            CheckingAccount.has_overdraft_protection == True,  # noqa: E712
        )
    )

    result = await session.execute(query)
    return result.scalars().all()


async def get_checking_accounts_by_balance_range(
    session: AsyncSession, min_balance: Decimal, max_balance: Optional[Decimal] = None
) -> List[CheckingAccount]:
    """
    Get checking accounts within a specific balance range.

    Args:
        session: SQLAlchemy async session
        min_balance: Minimum balance threshold
        max_balance: Optional maximum balance threshold

    Returns:
        List of checking accounts within the balance range
    """
    conditions = [
        CheckingAccount.is_closed == False,  # noqa: E712
        CheckingAccount.available_balance >= min_balance,
    ]

    if max_balance is not None:
        conditions.append(CheckingAccount.available_balance <= max_balance)

    query = select(CheckingAccount).where(and_(*conditions))

    result = await session.execute(query)
    return result.scalars().all()


async def get_checking_accounts_with_international_features(
    session: AsyncSession,
) -> List[CheckingAccount]:
    """
    Get checking accounts with international banking features.

    This includes accounts with IBAN, SWIFT/BIC, sort code, or non-local format.

    Args:
        session: SQLAlchemy async session

    Returns:
        List of checking accounts with international features
    """
    query = select(CheckingAccount).where(
        and_(
            CheckingAccount.is_closed == False,  # noqa: E712
            or_(
                CheckingAccount.iban.is_not(None),
                CheckingAccount.swift_bic.is_not(None),
                CheckingAccount.sort_code.is_not(None),
                CheckingAccount.branch_code.is_not(None),
                CheckingAccount.account_format != "local",
            ),
        )
    )

    result = await session.execute(query)
    return result.scalars().all()


async def get_checking_accounts_without_fees(
    session: AsyncSession,
) -> List[CheckingAccount]:
    """
    Get checking accounts with no monthly fees.

    Args:
        session: SQLAlchemy async session

    Returns:
        List of fee-free checking accounts
    """
    query = select(CheckingAccount).where(
        and_(
            CheckingAccount.is_closed == False,  # noqa: E712
            or_(
                CheckingAccount.monthly_fee == 0,
                CheckingAccount.monthly_fee == None,  # noqa: E711
            ),
        )
    )

    result = await session.execute(query)
    return result.scalars().all()


async def get_interest_bearing_checking_accounts(
    session: AsyncSession,
) -> List[CheckingAccount]:
    """
    Get checking accounts that earn interest.

    Args:
        session: SQLAlchemy async session

    Returns:
        List of interest-bearing checking accounts
    """
    query = select(CheckingAccount).where(
        and_(
            CheckingAccount.is_closed == False,  # noqa: E712
            CheckingAccount.interest_rate.is_not(None),
            CheckingAccount.interest_rate > 0,
        )
    )

    result = await session.execute(query)
    return result.scalars().all()
