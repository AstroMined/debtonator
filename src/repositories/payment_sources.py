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
from src.repositories.base import BaseRepository


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
        
    async def create(self, obj_in: Dict[str, Any]) -> PaymentSource:
        """
        Create a new payment source ensuring all required fields are present.
        
        This overrides the base create method to properly validate the presence
        of required payment_id and account_id before creating the source.

        Args:
            obj_in (Dict[str, Any]): Dictionary containing payment source attributes

        Returns:
            PaymentSource: Created payment source object
            
        Raises:
            ValueError: If payment_id is missing
        """
        # Ensure payment_id is present - this is a required field
        if "payment_id" not in obj_in or obj_in["payment_id"] is None:
            raise ValueError("payment_id is required for creating PaymentSource objects")
            
        # Create the payment source as a proper model instance
        source = PaymentSource(**obj_in)
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

    async def bulk_create_sources(
        self, sources: List[Dict[str, Any]]
    ) -> List[PaymentSource]:
        """
        Create multiple payment sources in one operation.

        Args:
            sources (List[Dict[str, Any]]): List of source attribute dictionaries

        Returns:
            List[PaymentSource]: List of created payment source objects
        """
        return await self.bulk_create(sources)

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
