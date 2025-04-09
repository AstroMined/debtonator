"""
Repository operations for Buy Now Pay Later (BNPL) accounts.

This module provides specialized query operations for BNPL accounts.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.bnpl import BNPLAccount
from src.utils.datetime_utils import days_from_now, utc_now


async def get_bnpl_accounts_with_upcoming_payments(
    session: AsyncSession, days: int = 14
):
    """Get BNPL accounts with payments due in the next X days."""
    now = utc_now()
    cutoff = days_from_now(days)

    stmt = (
        select(BNPLAccount)
        .where(
            BNPLAccount.next_payment_date <= cutoff,
            BNPLAccount.next_payment_date >= now,
            BNPLAccount.is_closed == False,
            BNPLAccount.installments_paid < BNPLAccount.installment_count,
        )
        .order_by(BNPLAccount.next_payment_date)
    )

    result = await session.execute(stmt)
    return result.scalars().all()


async def get_bnpl_accounts_by_provider(session: AsyncSession, provider: str):
    """Get BNPL accounts by provider."""
    stmt = select(BNPLAccount).where(
        BNPLAccount.bnpl_provider == provider, BNPLAccount.is_closed == False
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_bnpl_accounts_with_remaining_installments(
    session: AsyncSession, min_remaining: int = 1
):
    """Get BNPL accounts with at least min_remaining installments remaining."""
    stmt = select(BNPLAccount).where(
        BNPLAccount.installment_count - BNPLAccount.installments_paid >= min_remaining,
        BNPLAccount.is_closed == False,
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_bnpl_accounts_by_payment_frequency(session: AsyncSession, frequency: str):
    """Get BNPL accounts by payment frequency."""
    stmt = select(BNPLAccount).where(
        BNPLAccount.payment_frequency == frequency, BNPLAccount.is_closed == False
    )
    result = await session.execute(stmt)
    return result.scalars().all()
