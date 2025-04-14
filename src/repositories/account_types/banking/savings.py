"""
Savings account repository operations.

This module contains specialized repository operations for savings accounts.
These functions complement the base AccountRepository by providing type-specific
operations that only apply to savings accounts.

Implemented as part of ADR-016 Account Type Expansion and ADR-019 Banking Account Types.
"""

from decimal import Decimal
from typing import List, Optional

from sqlalchemy import and_, desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.savings import SavingsAccount


async def get_all_savings_accounts(
    session: AsyncSession, include_closed: bool = False
) -> List[SavingsAccount]:
    """
    Get all savings accounts.

    Args:
        session: SQLAlchemy async session
        include_closed: Whether to include closed accounts

    Returns:
        List of savings accounts
    """
    query = select(SavingsAccount)

    if not include_closed:
        query = query.where(SavingsAccount.is_closed == False)  # noqa: E712

    result = await session.execute(query)
    return result.scalars().all()


async def get_high_yield_savings_accounts(
    session: AsyncSession, minimum_rate: Decimal = Decimal("0.015")
) -> List[SavingsAccount]:
    """
    Get high-yield savings accounts that meet the minimum interest rate.

    Args:
        session: SQLAlchemy async session
        minimum_rate: Minimum annual interest rate (default: 1.5%)

    Returns:
        List of high-yield savings accounts
    """
    query = (
        select(SavingsAccount)
        .where(
            and_(
                SavingsAccount.is_closed == False,  # noqa: E712
                SavingsAccount.interest_rate >= minimum_rate,
            )
        )
        .order_by(desc(SavingsAccount.interest_rate))
    )

    result = await session.execute(query)
    return result.scalars().all()


async def get_savings_accounts_with_withdrawal_limits(
    session: AsyncSession,
) -> List[SavingsAccount]:
    """
    Get savings accounts with withdrawal limits.

    Args:
        session: SQLAlchemy async session

    Returns:
        List of savings accounts with withdrawal limitations
    """
    query = select(SavingsAccount).where(
        and_(
            SavingsAccount.is_closed == False,  # noqa: E712
            or_(
                SavingsAccount.monthly_withdrawal_limit.is_not(None),
                SavingsAccount.has_withdrawal_penalty == True,  # noqa: E712
            ),
        )
    )

    result = await session.execute(query)
    return result.scalars().all()


async def get_savings_accounts_by_balance_tier(
    session: AsyncSession,
    tier_thresholds: List[Decimal] = [
        Decimal("1000"),
        Decimal("10000"),
        Decimal("50000"),
    ],
) -> dict[str, List[SavingsAccount]]:
    """
    Get savings accounts grouped by balance tiers.

    Args:
        session: SQLAlchemy async session
        tier_thresholds: Balance thresholds defining the tiers (default: [1000, 10000, 50000])
                        This creates tiers: 0-999, 1000-9999, 10000-49999, 50000+

    Returns:
        Dictionary with tier labels as keys and lists of savings accounts as values
    """
    # Get all active savings accounts
    query = select(SavingsAccount).where(
        SavingsAccount.is_closed == False
    )  # noqa: E712
    result = await session.execute(query)
    accounts = result.scalars().all()

    # Initialize result dictionary with tier labels
    tier_names = [
        f"tier_below_{tier_thresholds[0]}",
        *[
            f"tier_{tier_thresholds[i]}_to_{tier_thresholds[i+1]-1}"
            for i in range(len(tier_thresholds) - 1)
        ],
        f"tier_above_{tier_thresholds[-1]}",
    ]
    result_dict = {tier: [] for tier in tier_names}

    # Categorize accounts into tiers
    for account in accounts:
        balance = account.available_balance

        # Determine which tier this account belongs in
        if balance < tier_thresholds[0]:
            result_dict[tier_names[0]].append(account)
        elif balance >= tier_thresholds[-1]:
            result_dict[tier_names[-1]].append(account)
        else:
            for i in range(len(tier_thresholds) - 1):
                if tier_thresholds[i] <= balance < tier_thresholds[i + 1]:
                    result_dict[tier_names[i + 1]].append(account)
                    break

    return result_dict


async def get_savings_accounts_by_interest_rate_range(
    session: AsyncSession, min_rate: Decimal, max_rate: Optional[Decimal] = None
) -> List[SavingsAccount]:
    """
    Get savings accounts within a specific interest rate range.

    Args:
        session: SQLAlchemy async session
        min_rate: Minimum interest rate
        max_rate: Optional maximum interest rate

    Returns:
        List of savings accounts within the interest rate range
    """
    conditions = [
        SavingsAccount.is_closed == False,  # noqa: E712
        SavingsAccount.interest_rate >= min_rate,
    ]

    if max_rate is not None:
        conditions.append(SavingsAccount.interest_rate <= max_rate)

    query = (
        select(SavingsAccount)
        .where(and_(*conditions))
        .order_by(SavingsAccount.interest_rate)
    )

    result = await session.execute(query)
    return result.scalars().all()


async def get_savings_accounts_by_interest_rate_threshold(
    session: AsyncSession, threshold: Decimal
) -> List[SavingsAccount]:
    """
    Get savings accounts with interest rate above a specified threshold.
    
    Args:
        session: SQLAlchemy async session
        threshold: Minimum interest rate threshold
        
    Returns:
        List of savings accounts with interest rate above threshold
    """
    query = (
        select(SavingsAccount)
        .where(
            and_(
                SavingsAccount.is_closed == False,  # noqa: E712
                SavingsAccount.interest_rate.is_not(None),
                SavingsAccount.interest_rate >= threshold,
            )
        )
        .order_by(desc(SavingsAccount.interest_rate))
    )
    
    result = await session.execute(query)
    return result.scalars().all()


async def get_savings_accounts_with_minimum_balance(
    session: AsyncSession
) -> List[SavingsAccount]:
    """
    Get savings accounts that have minimum balance requirements.
    
    Args:
        session: SQLAlchemy async session
        
    Returns:
        List of savings accounts with minimum balance requirements
    """
    query = (
        select(SavingsAccount)
        .where(
            and_(
                SavingsAccount.is_closed == False,  # noqa: E712
                SavingsAccount.minimum_balance.is_not(None),
                SavingsAccount.minimum_balance > 0,
            )
        )
        .order_by(desc(SavingsAccount.minimum_balance))
    )
    
    result = await session.execute(query)
    return result.scalars().all()


async def get_savings_accounts_below_minimum_balance(
    session: AsyncSession
) -> List[SavingsAccount]:
    """
    Get savings accounts with balance below their minimum balance requirement.
    
    Args:
        session: SQLAlchemy async session
        
    Returns:
        List of savings accounts below their minimum balance
    """
    query = (
        select(SavingsAccount)
        .where(
            and_(
                SavingsAccount.is_closed == False,  # noqa: E712
                SavingsAccount.minimum_balance.is_not(None),
                SavingsAccount.minimum_balance > 0,
                SavingsAccount.available_balance < SavingsAccount.minimum_balance,
            )
        )
        .order_by(desc(SavingsAccount.minimum_balance - SavingsAccount.available_balance))
    )
    
    result = await session.execute(query)
    return result.scalars().all()


async def get_highest_yield_savings_accounts(
    session: AsyncSession, limit: int = 5
) -> List[SavingsAccount]:
    """
    Get the highest yield savings accounts, limited to a specified number.
    
    Args:
        session: SQLAlchemy async session
        limit: Maximum number of accounts to return (default: 5)
        
    Returns:
        List of highest yield savings accounts, sorted by interest rate descending
    """
    query = (
        select(SavingsAccount)
        .where(
            and_(
                SavingsAccount.is_closed == False,  # noqa: E712
                SavingsAccount.interest_rate.is_not(None),
                SavingsAccount.interest_rate > 0,
            )
        )
        .order_by(desc(SavingsAccount.interest_rate))
        .limit(limit)
    )
    
    result = await session.execute(query)
    return result.scalars().all()


async def get_savings_accounts_by_interest_rate_threshold(
    session: AsyncSession, threshold: Decimal
) -> List[SavingsAccount]:
    """
    Get savings accounts with interest rate above a specified threshold.
    
    Args:
        session: SQLAlchemy async session
        threshold: Minimum interest rate threshold
        
    Returns:
        List of savings accounts with interest rate above threshold
    """
    query = (
        select(SavingsAccount)
        .where(
            and_(
                SavingsAccount.is_closed == False,  # noqa: E712
                SavingsAccount.interest_rate.is_not(None),
                SavingsAccount.interest_rate >= threshold,
            )
        )
        .order_by(desc(SavingsAccount.interest_rate))
    )
    
    result = await session.execute(query)
    return result.scalars().all()


async def get_savings_accounts_with_minimum_balance(
    session: AsyncSession
) -> List[SavingsAccount]:
    """
    Get savings accounts that have minimum balance requirements.
    
    Args:
        session: SQLAlchemy async session
        
    Returns:
        List of savings accounts with minimum balance requirements
    """
    query = (
        select(SavingsAccount)
        .where(
            and_(
                SavingsAccount.is_closed == False,  # noqa: E712
                SavingsAccount.minimum_balance.is_not(None),
                SavingsAccount.minimum_balance > 0,
            )
        )
        .order_by(desc(SavingsAccount.minimum_balance))
    )
    
    result = await session.execute(query)
    return result.scalars().all()


async def get_savings_accounts_below_minimum_balance(
    session: AsyncSession
) -> List[SavingsAccount]:
    """
    Get savings accounts with balance below their minimum balance requirement.
    
    Args:
        session: SQLAlchemy async session
        
    Returns:
        List of savings accounts below their minimum balance
    """
    query = (
        select(SavingsAccount)
        .where(
            and_(
                SavingsAccount.is_closed == False,  # noqa: E712
                SavingsAccount.minimum_balance.is_not(None),
                SavingsAccount.minimum_balance > 0,
                SavingsAccount.available_balance < SavingsAccount.minimum_balance,
            )
        )
        .order_by(desc(SavingsAccount.minimum_balance - SavingsAccount.available_balance))
    )
    
    result = await session.execute(query)
    return result.scalars().all()


async def get_highest_yield_savings_accounts(
    session: AsyncSession, limit: int = 5
) -> List[SavingsAccount]:
    """
    Get the highest yield savings accounts, limited to a specified number.
    
    Args:
        session: SQLAlchemy async session
        limit: Maximum number of accounts to return (default: 5)
        
    Returns:
        List of highest yield savings accounts, sorted by interest rate descending
    """
    query = (
        select(SavingsAccount)
        .where(
            and_(
                SavingsAccount.is_closed == False,  # noqa: E712
                SavingsAccount.interest_rate.is_not(None),
                SavingsAccount.interest_rate > 0,
            )
        )
        .order_by(desc(SavingsAccount.interest_rate))
        .limit(limit)
    )
    
    result = await session.execute(query)
    return result.scalars().all()
