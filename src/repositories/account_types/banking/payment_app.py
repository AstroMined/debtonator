"""
Repository operations for payment app accounts.

This module provides specialized query operations for PaymentApp accounts.
"""

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.payment_app import PaymentAppAccount


async def get_payment_app_accounts_by_platform(session: AsyncSession, platform: str):
    """Get payment app accounts by platform type."""
    stmt = select(PaymentAppAccount).where(
        PaymentAppAccount.platform == platform, PaymentAppAccount.is_closed == False
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_payment_app_accounts_with_debit_cards(session: AsyncSession):
    """Get payment app accounts that have debit cards."""
    stmt = select(PaymentAppAccount).where(
        PaymentAppAccount.has_debit_card == True, PaymentAppAccount.is_closed == False
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_payment_app_accounts_with_linked_accounts(session: AsyncSession):
    """Get payment app accounts that have linked accounts."""
    stmt = select(PaymentAppAccount).where(
        PaymentAppAccount.linked_account_ids.isnot(None),
        PaymentAppAccount.linked_account_ids != "",
        PaymentAppAccount.is_closed == False,
    )
    result = await session.execute(stmt)
    return result.scalars().all()


async def get_payment_app_accounts_with_direct_deposit(session: AsyncSession):
    """Get payment app accounts that support direct deposit."""
    stmt = select(PaymentAppAccount).where(
        PaymentAppAccount.supports_direct_deposit == True,
        PaymentAppAccount.is_closed == False,
    )
    result = await session.execute(stmt)
    return result.scalars().all()
