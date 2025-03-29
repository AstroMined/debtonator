"""
Payment source repository implementation.

This module provides a repository for PaymentSource model CRUD operations and specialized
payment source-related queries.
"""

from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy import and_, desc, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.models.payments import PaymentSource
from src.repositories.base_repository import BaseRepository


class PaymentSourceRepository(BaseRepository[PaymentSource, int]):
    """
    Repository for PaymentSource model operations.

    This repository handles CRUD operations for payment sources and provides specialized
    queries for payment source-related functionality.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session (AsyncSession): SQLAlchemy async session
        """
        super().__init__(session, PaymentSource)

    async def _create(self, obj_in: Dict[str, Any], payment_id: int) -> PaymentSource:
        """
        INTERNAL METHOD: Create a new payment source with required payment_id.

        This is a private method to be used only by PaymentRepository.
        PaymentSources should not be created standalone without a parent Payment.

        This implementation enforces the ADR-017 design where payment sources
        must always exist as part of a payment.

        Args:
            obj_in (Dict[str, Any]): Dictionary containing payment source attributes
            payment_id (int): ID of the parent payment (required)

        Returns:
            PaymentSource: Created payment source object
        """
        # Make a copy of obj_in to avoid modifying the original
        source_data = dict(obj_in)

        # Always use the provided payment_id
        source_data["payment_id"] = payment_id

        # Create the payment source as a proper model instance
        source = PaymentSource(**source_data)
        self.session.add(source)
        await self.session.flush()
        await self.session.refresh(source)
        return source

    async def get_with_relationships(
        self,
        source_id: int,
        include_payment: bool = False,
        include_account: bool = False,
    ) -> Optional[PaymentSource]:
        """
        Get a payment source with specified relationships loaded.

        Args:
            source_id (int): Payment source ID
            include_payment (bool): Load payment relationship
            include_account (bool): Load account relationship

        Returns:
            Optional[PaymentSource]: PaymentSource with loaded relationships or None
        """
        query = select(PaymentSource).where(PaymentSource.id == source_id)

        if include_payment:
            query = query.options(joinedload(PaymentSource.payment))

        if include_account:
            query = query.options(joinedload(PaymentSource.account))

        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_sources_for_payment(
        self, payment_id: int, include_account: bool = False
    ) -> List[PaymentSource]:
        """
        Get sources for a specific payment.

        Args:
            payment_id (int): Payment ID
            include_account (bool): Whether to load account relationship

        Returns:
            List[PaymentSource]: Payment sources for the specified payment
        """
        query = select(PaymentSource).where(PaymentSource.payment_id == payment_id)

        if include_account:
            query = query.options(joinedload(PaymentSource.account))

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_sources_for_account(
        self, account_id: int, include_payment: bool = False, limit: int = 100
    ) -> List[PaymentSource]:
        """
        Get payment sources for a specific account.

        Args:
            account_id (int): Account ID
            include_payment (bool): Whether to load payment relationship
            limit (int): Maximum number of sources to return

        Returns:
            List[PaymentSource]: Payment sources using the specified account
        """
        query = (
            select(PaymentSource)
            .where(PaymentSource.account_id == account_id)
            .limit(limit)
        )

        if include_payment:
            query = query.options(joinedload(PaymentSource.payment))
            query = query.order_by(desc(PaymentSource.payment.payment_date))

        result = await self.session.execute(query)
        return result.scalars().all()

    async def _bulk_create_sources(
        self, sources: List[Dict[str, Any]], payment_id: int
    ) -> List[PaymentSource]:
        """
        INTERNAL METHOD: Create multiple payment sources for a single payment.

        This is a private method to be used only by PaymentRepository.
        PaymentSources should not be created standalone without a parent Payment.

        This implementation enforces the ADR-017 design where payment sources
        must always exist as part of a payment.

        Args:
            sources (List[Dict[str, Any]]): List of source attribute dictionaries
            payment_id (int): ID of the parent payment to assign to all sources

        Returns:
            List[PaymentSource]: List of created payment source objects
        """
        # Create copies of source dicts with payment_id included
        processed_sources = [{**source, "payment_id": payment_id} for source in sources]

        return await self.bulk_create(processed_sources)

    async def get_total_amount_by_account(self, account_id: int) -> Decimal:
        """
        Get total payment amount from a specific account.

        Args:
            account_id (int): Account ID

        Returns:
            Decimal: Total payment amount from this account
        """
        query = select(func.sum(PaymentSource.amount)).where(
            PaymentSource.account_id == account_id
        )

        result = await self.session.execute(query)
        total = result.scalar_one_or_none()
        return total if total is not None else Decimal("0")

    async def delete_sources_for_payment(self, payment_id: int) -> int:
        """
        Delete all sources for a specific payment.

        Args:
            payment_id (int): Payment ID

        Returns:
            int: Number of sources deleted
        """
        # Import here to avoid circular imports
        from sqlalchemy import delete

        result = await self.session.execute(
            delete(PaymentSource).where(PaymentSource.payment_id == payment_id)
        )

        return result.rowcount
