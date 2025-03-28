"""
Payment repository implementation.

This module provides a repository for Payment model CRUD operations and specialized
payment-related queries.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple, Union

from sqlalchemy import and_, between, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.models.payments import Payment, PaymentSource
from src.repositories.base import BaseRepository


class PaymentRepository(BaseRepository[Payment, int]):
    """
    Repository for Payment model operations.

    This repository handles CRUD operations for payments and provides specialized
    queries for payment-related functionality.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session (AsyncSession): SQLAlchemy async session
        """
        super().__init__(session, Payment)

    async def create(self, obj_in: Dict[str, Any]) -> Payment:
        """
        Create a new payment with required payment sources using ORM relationships.

        This method implements the ADR-017 design where a payment must always have
        at least one payment source, and payment sources can only exist as part of a payment.

        It uses SQLAlchemy's relationship handling to automatically manage the
        foreign key relationships between Payment and PaymentSource, creating
        the payment and its sources in a single transaction.

        Args:
            obj_in (Dict[str, Any]): Dictionary containing payment attributes
                and a required 'sources' key with a list of payment source data

        Returns:
            Payment: Created payment with sources attached

        Raises:
            ValueError: If no payment sources are provided
        """
        # Extract sources from the input
        sources_data = obj_in.pop("sources", [])

        # Validate that at least one source is provided
        if not sources_data:
            raise ValueError("A payment must have at least one payment source")

        # Create the payment instance
        payment = Payment(**obj_in)

        # Create and associate source instances directly via the relationship
        for source_data in sources_data:
            # Create the source and associate with payment using the ORM relationship
            # No need to set payment_id manually - SQLAlchemy handles it
            source = PaymentSource(**source_data)
            # Associate with payment through the relationship
            payment.sources.append(source)

        # Add the parent to the session - cascade takes care of children
        self.session.add(payment)
        await self.session.flush()

        # Refresh and eagerly load sources
        await self.session.refresh(payment, ["sources"])

        return payment

    async def get_with_sources(self, payment_id: int) -> Optional[Payment]:
        """
        Get a payment with its payment sources loaded.

        Args:
            payment_id (int): Payment ID

        Returns:
            Optional[Payment]: Payment with loaded sources or None
        """
        result = await self.session.execute(
            select(Payment)
            .options(selectinload(Payment.sources))
            .where(Payment.id == payment_id)
        )
        return result.scalars().first()

    async def get_with_relationships(
        self,
        payment_id: int,
        include_sources: bool = False,
        include_liability: bool = False,
        include_income: bool = False,
    ) -> Optional[Payment]:
        """
        Get a payment with specified relationships loaded.

        Args:
            payment_id (int): Payment ID
            include_sources (bool): Load payment sources
            include_liability (bool): Load associated liability
            include_income (bool): Load associated income

        Returns:
            Optional[Payment]: Payment with loaded relationships or None
        """
        query = select(Payment).where(Payment.id == payment_id)

        if include_sources:
            query = query.options(selectinload(Payment.sources))

        if include_liability:
            query = query.options(joinedload(Payment.liability))

        if include_income:
            query = query.options(joinedload(Payment.income))

        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_payments_for_bill(
        self, liability_id: int, include_sources: bool = False
    ) -> List[Payment]:
        """
        Get payments for a specific bill/liability.

        Args:
            liability_id (int): Liability ID
            include_sources (bool): Whether to load payment sources

        Returns:
            List[Payment]: Payments for the specified bill
        """
        query = (
            select(Payment)
            .where(Payment.liability_id == liability_id)
            .order_by(desc(Payment.payment_date))
        )

        if include_sources:
            query = query.options(selectinload(Payment.sources))

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_payments_for_account(
        self, account_id: int, include_sources: bool = False
    ) -> List[Payment]:
        """
        Get payments that include a specific account as a source.

        Args:
            account_id (int): Account ID
            include_sources (bool): Whether to load payment sources

        Returns:
            List[Payment]: Payments that use the specified account
        """
        # We need to join with PaymentSource to find payments using this account
        from src.models.payments import PaymentSource

        query = (
            select(Payment)
            .join(PaymentSource, PaymentSource.payment_id == Payment.id)
            .where(PaymentSource.account_id == account_id)
            .order_by(desc(Payment.payment_date))
        )

        if include_sources:
            query = query.options(selectinload(Payment.sources))

        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def get_payments_in_date_range(
        self, start_date: datetime, end_date: datetime, include_sources: bool = False
    ) -> List[Payment]:
        """
        Get payments within a specific date range.

        Args:
            start_date (datetime): Start date (inclusive)
            end_date (datetime): End date (inclusive)
            include_sources (bool): Whether to load payment sources

        Returns:
            List[Payment]: Payments within the date range
        """
        query = (
            select(Payment)
            .where(
                and_(
                    Payment.payment_date >= start_date, Payment.payment_date <= end_date
                )
            )
            .order_by(Payment.payment_date)
        )

        if include_sources:
            query = query.options(selectinload(Payment.sources))

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_payments_by_category(
        self, category: str, limit: int = 100, include_sources: bool = False
    ) -> List[Payment]:
        """
        Get payments by category.

        Args:
            category (str): Payment category
            limit (int): Maximum number of payments to return
            include_sources (bool): Whether to load payment sources

        Returns:
            List[Payment]: Payments in the specified category
        """
        query = (
            select(Payment)
            .where(Payment.category == category)
            .order_by(desc(Payment.payment_date))
            .limit(limit)
        )

        if include_sources:
            query = query.options(selectinload(Payment.sources))

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_total_amount_in_range(
        self, start_date: datetime, end_date: datetime, category: Optional[str] = None
    ) -> Decimal:
        """
        Get total payment amount in a date range, optionally filtered by category.

        Args:
            start_date (datetime): Start date (inclusive)
            end_date (datetime): End date (inclusive)
            category (str, optional): Filter by payment category

        Returns:
            Decimal: Total payment amount
        """
        query = select(func.sum(Payment.amount)).where(
            between(Payment.payment_date, start_date, end_date)
        )

        if category:
            query = query.where(Payment.category == category)

        result = await self.session.execute(query)
        total = result.scalar_one_or_none()
        return total if total is not None else Decimal("0")

    async def get_recent_payments(
        self, days: int = 30, limit: int = 20, include_sources: bool = False
    ) -> List[Payment]:
        """
        Get recent payments from the last specified number of days.

        Args:
            days (int): Number of days to look back
            limit (int): Maximum number of payments to return
            include_sources (bool): Whether to load payment sources

        Returns:
            List[Payment]: Recent payments
        """
        cutoff_date = datetime.utcnow() - timedelta(days=days)

        query = (
            select(Payment)
            .where(Payment.payment_date >= cutoff_date)
            .order_by(desc(Payment.payment_date))
            .limit(limit)
        )

        if include_sources:
            query = query.options(selectinload(Payment.sources))

        result = await self.session.execute(query)
        return result.scalars().all()
