"""
Repository operations for Earned Wage Access (EWA) accounts.

This module provides specialized query operations for EWA accounts.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.ewa import EWAAccount
from src.utils.datetime_utils import utc_now, days_from_now


async def get_ewa_accounts_approaching_payday(
    session: AsyncSession, days: int = 7
):
    """Get EWA accounts with upcoming paydays in the next X days."""
    now = utc_now()
    cutoff = days_from_now(days)
    
    stmt = select(EWAAccount).where(
        EWAAccount.next_payday <= cutoff,
        EWAAccount.next_payday >= now,
        EWAAccount.is_closed == False
    ).order_by(EWAAccount.next_payday)
    
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_ewa_accounts_by_provider(session: AsyncSession, provider: str):
    """Get EWA accounts by provider."""
    stmt = select(EWAAccount).where(
        EWAAccount.provider == provider,
        EWAAccount.is_closed == False
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_ewa_accounts_by_advance_percentage(
    session: AsyncSession, min_percentage: float, max_percentage: float
):
    """Get EWA accounts with max advance percentage within the given range."""
    stmt = select(EWAAccount).where(
        EWAAccount.max_advance_percentage >= min_percentage,
        EWAAccount.max_advance_percentage <= max_percentage,
        EWAAccount.is_closed == False
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_ewa_accounts_with_no_transaction_fee(session: AsyncSession):
    """Get EWA accounts with no transaction fee."""
    stmt = select(EWAAccount).where(
        (EWAAccount.per_transaction_fee == 0) | (EWAAccount.per_transaction_fee == None),
        EWAAccount.is_closed == False
    )
    result = await session.execute(stmt)
    return result.scalars().all()
