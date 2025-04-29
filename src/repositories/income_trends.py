"""
Income Trends Repository Module.

This module provides repository implementation for income trends analysis operations.
It encapsulates all data access operations for income trends, following the repository
pattern as specified in ADR-014.
"""

from collections import defaultdict
from datetime import datetime
from typing import Dict, List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.income import Income
from src.repositories.base_repository import BaseRepository
from src.utils.datetime_utils import ensure_utc, naive_end_of_day, naive_start_of_day


class IncomeTrendsRepository(BaseRepository[Income, int]):
    """Repository for income trends operations.

    This repository handles data access operations specific to income trends analysis,
    providing methods to retrieve and process income data for pattern detection and
    statistical analysis.

    All datetime operations follow ADR-011 compliance, using proper timezone handling.
    """

    def __init__(self, session: AsyncSession):
        """Initialize the repository with a database session.

        Args:
            session: SQLAlchemy async session for database operations
        """
        super().__init__(session, Income)

    async def get_income_records(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        source: Optional[str] = None,
    ) -> List[Income]:
        """Get income records with optional filtering.

        This method retrieves income records that match the provided filters.
        All datetime parameters are processed to ensure proper timezone handling
        according to ADR-011.

        Args:
            start_date: Optional start date filter (UTC timezone)
            end_date: Optional end date filter (UTC timezone)
            source: Optional income source filter

        Returns:
            List of income records matching the criteria
        """
        query = select(self.model_class)

        # Apply date filters with proper timezone handling
        if start_date:
            # For database operations, we need to use naive datetimes
            # but ensure we're handling timezone information properly per ADR-011
            start_date_naive = naive_start_of_day(ensure_utc(start_date))
            query = query.where(self.model_class.date >= start_date_naive)

        if end_date:
            # For database operations, we need to use naive datetimes
            # but ensure we're handling timezone information properly per ADR-011
            end_date_naive = naive_end_of_day(ensure_utc(end_date))
            query = query.where(self.model_class.date <= end_date_naive)

        # Apply source filter if provided
        if source:
            query = query.where(self.model_class.source == source)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def group_records_by_source(
        self, records: List[Income]
    ) -> Dict[str, List[Income]]:
        """Group income records by source.

        Args:
            records: List of income records to group

        Returns:
            Dictionary mapping sources to lists of records
        """
        source_records: Dict[str, List[Income]] = defaultdict(list)
        for record in records:
            source_records[record.source].append(record)
        return source_records

    async def get_min_max_dates(
        self, records: List[Income]
    ) -> tuple[datetime, datetime]:
        """Get the minimum and maximum dates from a list of income records.

        Args:
            records: List of income records to analyze

        Returns:
            Tuple of (min_date, max_date) representing the data range
        """
        if not records:
            raise ValueError("Cannot determine date range from empty record list")

        return min(r.date for r in records), max(r.date for r in records)

    async def get_records_by_month(
        self, records: List[Income]
    ) -> Dict[int, List[Income]]:
        """Group income records by month.

        Args:
            records: List of income records to group

        Returns:
            Dictionary mapping months (1-12) to lists of records
        """
        monthly_records: Dict[int, List[Income]] = defaultdict(list)
        for record in records:
            monthly_records[record.date.month].append(record)
        return monthly_records
