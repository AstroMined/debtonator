"""
Payment pattern repository implementation.

This module provides a repository for payment pattern analysis operations,
implementing specialized queries for payment pattern detection and analysis.
"""

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import List, Optional, Tuple

import numpy as np
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.payments import Payment, PaymentSource
from src.repositories.base_repository import BaseRepository
from src.utils.datetime_utils import (
    ensure_utc,
    naive_end_of_day,
    naive_start_of_day,
    utc_now,
)


class PaymentPatternRepository(BaseRepository[Payment, int]):
    """
    Repository for payment pattern analysis operations.
    
    This repository provides specialized queries for analyzing payment patterns,
    including frequency metrics, amount statistics, and pattern detection.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.
        
        Args:
            session (AsyncSession): SQLAlchemy async session
        """
        super().__init__(session, Payment)

    async def get_payments_with_filters(
        self,
        liability_id: Optional[int] = None,
        account_id: Optional[int] = None,
        category_id: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        order_by_asc: bool = True,
        include_sources: bool = False,
    ) -> List[Payment]:
        """
        Get payments with various filter criteria.
        
        Args:
            liability_id (Optional[int]): Filter by liability/bill ID
            account_id (Optional[int]): Filter by account ID
            category_id (Optional[str]): Filter by category ID
            start_date (Optional[datetime]): Start date filter (inclusive)
            end_date (Optional[datetime]): End date filter (inclusive)
            order_by_asc (bool): Sort by payment date ascending if True, descending if False
            include_sources (bool): Include payment sources in the result
            
        Returns:
            List[Payment]: Filtered payments
        """
        # Build base query
        query = select(Payment)
        
        # Add filters
        if liability_id is not None:
            query = query.where(Payment.liability_id == liability_id)
            
        if account_id is not None:
            query = query.join(Payment.sources).filter(
                PaymentSource.account_id == account_id
            )
            
        if category_id is not None:
            query = query.filter(
                Payment.category.ilike(f"%{category_id}%")
            )
            
        if start_date is not None:
            # Ensure UTC timezone awareness
            start_date = ensure_utc(start_date)
            # Use naive datetime for database query
            db_start_date = naive_start_of_day(start_date)
            query = query.where(Payment.payment_date >= db_start_date)
            
        if end_date is not None:
            # Ensure UTC timezone awareness
            end_date = ensure_utc(end_date)
            # Use naive datetime for database query
            db_end_date = naive_end_of_day(end_date)
            query = query.where(Payment.payment_date <= db_end_date)
        
        # Add ordering
        if order_by_asc:
            query = query.order_by(Payment.payment_date.asc())
        else:
            query = query.order_by(Payment.payment_date.desc())
            
        # Add relationship loading if requested
        if include_sources:
            query = query.options(selectinload(Payment.sources))
            
        # Execute query
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_bill_payments(
        self, 
        liability_id: int, 
        include_sources: bool = False,
    ) -> List[Payment]:
        """
        Get all payments for a specific bill/liability.
        
        Args:
            liability_id (int): Liability/bill ID
            include_sources (bool): Include payment sources in the result
            
        Returns:
            List[Payment]: Payments for the specified bill
        """
        return await self.get_payments_with_filters(
            liability_id=liability_id,
            include_sources=include_sources,
            order_by_asc=True,  # Ascending order for pattern analysis
        )
    
    async def calculate_payment_frequency_metrics(
        self, payments: List[Payment]
    ) -> Tuple[float, float, int, int]:
        """
        Calculate frequency metrics for a list of payments.
        
        Args:
            payments (List[Payment]): List of payments to analyze
            
        Returns:
            Tuple[float, float, int, int]: Tuple containing:
                - average_days_between: Average number of days between payments
                - std_dev_days: Standard deviation of days between payments
                - min_days: Minimum days between payments
                - max_days: Maximum days between payments
        """
        if len(payments) < 2:
            return (0.0, 0.0, 0, 0)

        # Calculate days between consecutive payments
        days_between = []
        payment_dates = []

        # Ensure all payment dates are timezone-aware
        for payment in payments:
            payment_date = payment.payment_date
            if not payment_date.tzinfo:
                payment_date = payment_date.replace(tzinfo=timezone.utc)
            payment_dates.append(payment_date)

        # Sort dates to ensure correct interval calculation
        payment_dates.sort()

        # Check if all payments are on the same day
        if (max(payment_dates) - min(payment_dates)).days == 0:
            return (0.0, 0.0, 0, 0)

        # Calculate intervals between consecutive payments
        for i in range(len(payment_dates) - 1):
            delta = (payment_dates[i + 1] - payment_dates[i]).days
            if delta > 0:  # Only count non-zero intervals
                days_between.append(delta)

        if not days_between:  # If no valid intervals found
            return (0.0, 0.0, 0, 0)

        # Calculate metrics
        mean_days = float(np.mean(days_between))
        std_dev = float(np.std(days_between))
        min_days = min(days_between)
        max_days = max(days_between)

        return (mean_days, std_dev, min_days, max_days)
    
    async def calculate_amount_statistics(
        self, payments: List[Payment]
    ) -> Tuple[Decimal, Decimal, Decimal, Decimal, Decimal]:
        """
        Calculate amount statistics for a list of payments.
        
        Args:
            payments (List[Payment]): List of payments to analyze
            
        Returns:
            Tuple[Decimal, Decimal, Decimal, Decimal, Decimal]: Tuple containing:
                - average_amount: Average payment amount
                - std_dev_amount: Standard deviation of payment amounts
                - min_amount: Minimum payment amount
                - max_amount: Maximum payment amount
                - total_amount: Total amount of all payments
        """
        if not payments:
            return (
                Decimal("0"),
                Decimal("0"),
                Decimal("0"),
                Decimal("0"),
                Decimal("0"),
            )

        amounts = [payment.amount for payment in payments]
        
        average_amount = Decimal(str(np.mean(amounts)))
        std_dev_amount = Decimal(str(np.std(amounts)))
        min_amount = min(amounts)
        max_amount = max(amounts)
        total_amount = sum(amounts)
        
        return (average_amount, std_dev_amount, min_amount, max_amount, total_amount)
    
    async def get_date_range_for_pattern_analysis(
        self, 
        payments: List[Payment],
        default_start_date: Optional[datetime] = None,
        default_end_date: Optional[datetime] = None,
    ) -> Tuple[datetime, datetime]:
        """
        Get optimal date range for pattern analysis based on payment dates.
        
        Args:
            payments (List[Payment]): List of payments to analyze
            default_start_date (Optional[datetime]): Default start date if no payments
            default_end_date (Optional[datetime]): Default end date if no payments
            
        Returns:
            Tuple[datetime, datetime]: Start and end dates for analysis period
        """
        # Get current UTC time if defaults not provided
        now = utc_now()
        default_start = default_start_date or now
        default_end = default_end_date or now
        
        if not payments:
            return (ensure_utc(default_start), ensure_utc(default_end))
        
        # Get payment dates and ensure they have timezone info
        payment_dates = []
        for payment in payments:
            payment_date = payment.payment_date
            if not payment_date.tzinfo:
                payment_date = payment_date.replace(tzinfo=timezone.utc)
            payment_dates.append(payment_date)
        
        if not payment_dates:
            return (ensure_utc(default_start), ensure_utc(default_end))
        
        # Include the full day for both start and end dates in UTC
        min_date = min(payment_dates)
        max_date = max(payment_dates)

        # Set time components for start/end dates
        start_date = min_date.replace(
            hour=0, minute=0, second=0, microsecond=0
        ) - timedelta(days=1)
        end_date = max_date.replace(
            hour=23, minute=59, second=59, microsecond=999999
        )
        
        return (ensure_utc(start_date), ensure_utc(end_date))
    
    async def get_most_common_category(self, payments: List[Payment]) -> Optional[str]:
        """
        Get the most common category from a list of payments.
        
        Args:
            payments (List[Payment]): List of payments to analyze
            
        Returns:
            Optional[str]: Most common category or None if no categories
        """
        if not payments:
            return None

        # Get the most common category
        categories = {}
        for payment in payments:
            if payment.category:
                categories[payment.category] = categories.get(payment.category, 0) + 1

        if not categories:
            return None

        most_common = max(categories.items(), key=lambda x: x[1])[0]
        return most_common
