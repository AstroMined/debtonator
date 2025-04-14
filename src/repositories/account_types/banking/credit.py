"""
Credit account repository operations.

This module contains specialized repository operations for credit accounts.
These functions complement the base AccountRepository by providing type-specific
operations that only apply to credit accounts.

Implemented as part of ADR-016 Account Type Expansion and ADR-019 Banking Account Types.
"""

from decimal import Decimal
from typing import Dict, List, Optional

from sqlalchemy import and_, desc, or_, select, func
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.credit import CreditAccount
from src.utils.datetime_utils import naive_days_from_now, naive_utc_now


async def get_all_credit_accounts(
    session: AsyncSession, include_closed: bool = False
) -> List[CreditAccount]:
    """
    Get all credit accounts.

    Args:
        session: SQLAlchemy async session
        include_closed: Whether to include closed accounts

    Returns:
        List of credit accounts
    """
    query = select(CreditAccount)

    if not include_closed:
        query = query.where(CreditAccount.is_closed == False)  # noqa: E712

    result = await session.execute(query)
    return result.scalars().all()


async def get_credit_accounts_with_upcoming_payments(
    session: AsyncSession, days: int = 14
) -> List[CreditAccount]:
    """
    Get credit accounts with payments due in the next X days.

    Args:
        session: SQLAlchemy async session
        days: Number of days to look ahead for due dates

    Returns:
        List of credit accounts with upcoming payments
    """
    # Use naive datetime for database operations
    now = naive_utc_now()
    cutoff = naive_days_from_now(days)  # Use existing naive function for consistency

    query = (
        select(CreditAccount)
        .where(
            and_(
                CreditAccount.is_closed == False,  # noqa: E712
                CreditAccount.statement_due_date.is_not(None),
                CreditAccount.statement_due_date <= cutoff,
                CreditAccount.statement_due_date >= now,
            )
        )
        .order_by(CreditAccount.statement_due_date)
    )

    result = await session.execute(query)
    return result.scalars().all()


async def get_credit_accounts_near_limit(
    session: AsyncSession, threshold_percentage: Decimal = Decimal("0.9")
) -> List[CreditAccount]:
    """
    Find credit accounts near their credit limit.

    Args:
        session: SQLAlchemy async session
        threshold_percentage: Threshold as percentage of credit limit (default 90%)

    Returns:
        List of credit accounts near limit
    """
    query = (
        select(CreditAccount)
        .where(
            and_(
                CreditAccount.is_closed == False,  # noqa: E712
                CreditAccount.credit_limit > 0,
                # Calculate utilization as current_balance / credit_limit
                (CreditAccount.current_balance / CreditAccount.credit_limit)
                >= threshold_percentage,
            )
        )
        .order_by(desc(CreditAccount.current_balance / CreditAccount.credit_limit))
    )

    result = await session.execute(query)
    return result.scalars().all()


async def get_credit_accounts_by_apr_range(
    session: AsyncSession, min_apr: Decimal, max_apr: Optional[Decimal] = None
) -> List[CreditAccount]:
    """
    Get credit accounts within a specific APR range.

    Args:
        session: SQLAlchemy async session
        min_apr: Minimum APR
        max_apr: Optional maximum APR

    Returns:
        List of credit accounts within the APR range
    """
    conditions = [
        CreditAccount.is_closed == False,  # noqa: E712
        CreditAccount.interest_rate >= min_apr,
    ]

    if max_apr is not None:
        conditions.append(CreditAccount.interest_rate <= max_apr)

    query = (
        select(CreditAccount)
        .where(and_(*conditions))
        .order_by(CreditAccount.interest_rate)
    )

    result = await session.execute(query)
    return result.scalars().all()


async def get_credit_accounts_with_rewards(
    session: AsyncSession,
) -> List[CreditAccount]:
    """
    Get credit accounts with rewards programs.

    Args:
        session: SQLAlchemy async session

    Returns:
        List of credit accounts with rewards
    """
    query = (
        select(CreditAccount)
        .where(
            and_(
                CreditAccount.is_closed == False,  # noqa: E712
                CreditAccount.rewards_program.is_not(None),
                CreditAccount.rewards_rate > 0,
            )
        )
        .order_by(desc(CreditAccount.rewards_rate))
    )

    result = await session.execute(query)
    return result.scalars().all()


async def get_credit_accounts_by_utilization(
    session: AsyncSession, min_percent: Decimal = Decimal("0"), max_percent: Decimal = Decimal("100")
) -> List[CreditAccount]:
    """
    Get credit accounts with utilization within the specified percentage range.
    
    Args:
        session: SQLAlchemy async session
        min_percent: Minimum utilization percentage (default: 0%)
        max_percent: Maximum utilization percentage (default: 100%)
        
    Returns:
        List of credit accounts within the utilization range
    """
    # Convert percentages to decimal values (0-1 range)
    min_ratio = min_percent / 100
    max_ratio = max_percent / 100
    
    query = select(CreditAccount).where(
        and_(
            CreditAccount.is_closed == False,  # noqa: E712
            CreditAccount.credit_limit > 0,
            # Calculate utilization as abs(current_balance) / credit_limit
            # Use func.abs() for SQLAlchemy compatibility
            (func.abs(CreditAccount.current_balance) / CreditAccount.credit_limit) >= min_ratio,
            (func.abs(CreditAccount.current_balance) / CreditAccount.credit_limit) <= max_ratio,
        )
    ).order_by(func.abs(CreditAccount.current_balance) / CreditAccount.credit_limit)
    
    result = await session.execute(query)
    return result.scalars().all()


async def get_credit_accounts_with_open_statements(
    session: AsyncSession
) -> List[CreditAccount]:
    """
    Get credit accounts with open statements that have a balance and due date.
    
    Args:
        session: SQLAlchemy async session
        
    Returns:
        List of credit accounts with open statements
    """
    query = select(CreditAccount).where(
        and_(
            CreditAccount.is_closed == False,  # noqa: E712
            CreditAccount.statement_balance.is_not(None),
            CreditAccount.statement_due_date.is_not(None),
        )
    ).order_by(CreditAccount.statement_due_date)
    
    result = await session.execute(query)
    return result.scalars().all()


async def get_credit_accounts_without_statements(
    session: AsyncSession
) -> List[CreditAccount]:
    """
    Get credit accounts without open statements (missing balance or due date).
    
    Args:
        session: SQLAlchemy async session
        
    Returns:
        List of credit accounts without open statements
    """
    query = select(CreditAccount).where(
        and_(
            CreditAccount.is_closed == False,  # noqa: E712
            or_(
                CreditAccount.statement_balance.is_(None),
                CreditAccount.statement_due_date.is_(None),
            )
        )
    ).order_by(CreditAccount.name)
    
    result = await session.execute(query)
    return result.scalars().all()


async def get_credit_accounts_with_autopay(
    session: AsyncSession
) -> List[CreditAccount]:
    """
    Get credit accounts with autopay enabled (any status other than 'none').
    
    Args:
        session: SQLAlchemy async session
        
    Returns:
        List of credit accounts with autopay enabled
    """
    query = select(CreditAccount).where(
        and_(
            CreditAccount.is_closed == False,  # noqa: E712
            CreditAccount.autopay_status.is_not(None),
            CreditAccount.autopay_status != "none",
        )
    ).order_by(CreditAccount.name)
    
    result = await session.execute(query)
    return result.scalars().all()


async def get_credit_utilization_by_account(
    session: AsyncSession,
) -> List[Dict[str, any]]:
    """
    Get credit utilization metrics for all credit accounts.

    Args:
        session: SQLAlchemy async session

    Returns:
        List of dictionaries with account ID, name, limit, balance, and utilization percentage
    """
    # Query all active credit accounts
    query = select(CreditAccount).where(
        and_(
            CreditAccount.is_closed == False,  # noqa: E712
            CreditAccount.credit_limit > 0,
        )
    )

    result = await session.execute(query)
    accounts = result.scalars().all()

    # Calculate utilization for each account
    utilization_data = []
    for account in accounts:
        if account.credit_limit > 0:
            utilization = abs(account.current_balance) / account.credit_limit

            utilization_data.append(
                {
                    "id": account.id,
                    "name": account.name,
                    "credit_limit": account.credit_limit,
                    "current_balance": abs(account.current_balance),
                    "utilization_percentage": utilization * 100,
                    "available_credit": account.credit_limit
                    - abs(account.current_balance),
                }
            )

    # Sort by utilization percentage (highest first)
    utilization_data.sort(key=lambda x: x["utilization_percentage"], reverse=True)

    return utilization_data


async def get_credit_accounts_with_past_due_payments(
    session: AsyncSession,
) -> List[CreditAccount]:
    """
    Get credit accounts with past due payments.

    Args:
        session: SQLAlchemy async session

    Returns:
        List of credit accounts with past due payments
    """
    now = naive_utc_now()

    query = select(CreditAccount).where(
        and_(
            CreditAccount.is_closed == False,  # noqa: E712
            CreditAccount.statement_due_date < now,
            CreditAccount.last_statement_balance > 0,
            CreditAccount.payment_status.in_(["due", "past_due", "late"]),
        )
    )

    result = await session.execute(query)
    return result.scalars().all()


async def calculate_total_credit_metrics(session: AsyncSession) -> Dict[str, Decimal]:
    """
    Calculate aggregated metrics across all credit accounts.

    Args:
        session: SQLAlchemy async session

    Returns:
        Dictionary with total credit metrics:
        - total_credit_limit: Sum of all credit limits
        - total_balance: Sum of all balances
        - total_available_credit: Sum of all available credit
        - average_utilization: Average utilization across accounts
        - highest_utilization: Highest utilization percentage
        - lowest_utilization: Lowest utilization percentage
    """
    # Query all active credit accounts
    query = select(CreditAccount).where(
        and_(
            CreditAccount.is_closed == False,  # noqa: E712
            CreditAccount.credit_limit > 0,
        )
    )

    result = await session.execute(query)
    accounts = result.scalars().all()

    # Calculate aggregated metrics
    total_credit_limit = sum(account.credit_limit for account in accounts)
    total_balance = sum(abs(account.current_balance) for account in accounts)
    total_available_credit = total_credit_limit - total_balance

    # Calculate utilization metrics
    utilization_percentages = [
        (abs(account.current_balance) / account.credit_limit) * 100
        for account in accounts
        if account.credit_limit > 0
    ]

    average_utilization = (
        sum(utilization_percentages) / len(utilization_percentages)
        if utilization_percentages
        else Decimal("0")
    )
    highest_utilization = (
        max(utilization_percentages) if utilization_percentages else Decimal("0")
    )
    lowest_utilization = (
        min(utilization_percentages) if utilization_percentages else Decimal("0")
    )

    return {
        "total_credit_limit": total_credit_limit,
        "total_balance": total_balance,
        "total_available_credit": total_available_credit,
        "average_utilization": average_utilization,
        "highest_utilization": highest_utilization,
        "lowest_utilization": lowest_utilization,
        "num_accounts": len(accounts),
    }
