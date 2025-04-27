"""
Base repository for cashflow-related operations.

This module provides a base repository with shared functionality for
all cashflow repositories, including common queries and utilities.
"""

from datetime import date
from typing import Type, TypeVar
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from src.common.cashflow_types import CashflowHolidays, CashflowWarningThresholds
from src.repositories.base_repository import BaseRepository
from src.utils.datetime_utils import naive_end_of_day, naive_start_of_day

ModelType = TypeVar("ModelType")


class CashflowBaseRepository(BaseRepository[ModelType, int]):
    """
    Base repository for cashflow-related operations.

    This class provides shared functionality for all cashflow repositories,
    including common queries, warning thresholds, and date utilities.
    """

    def __init__(self, session: AsyncSession, model: Type[ModelType]):
        """
        Initialize base cashflow repository.

        Args:
            session (AsyncSession): SQLAlchemy async session
            model (Type[ModelType]): Model class for this repository
        """
        super().__init__(session, model)
        self._warning_thresholds = CashflowWarningThresholds()
        self._holidays = CashflowHolidays(date.today().year).get_holidays()
        self._timezone = ZoneInfo("UTC")

    def _get_warning_thresholds(self) -> CashflowWarningThresholds:
        """
        Get the current warning thresholds.

        Returns:
            CashflowWarningThresholds: Current warning thresholds
        """
        return self._warning_thresholds

    def _get_holidays(self) -> dict:
        """
        Get the current holiday dates.

        Returns:
            dict: Dictionary of holidays
        """
        return self._holidays

    def _get_timezone(self) -> ZoneInfo:
        """
        Get the repository timezone.

        Returns:
            ZoneInfo: Current timezone (UTC)
        """
        return self._timezone

    def _prepare_date_range(self, start_date, end_date) -> tuple:
        """
        Prepare start and end dates for inclusive date range queries.

        Following ADR-011 for consistent date range handling across the application.

        Args:
            start_date: Start date
            end_date: End date

        Returns:
            tuple: Tuple of naive start and end datetime objects for database queries
        """
        # For database queries, use naive datetimes
        range_start = naive_start_of_day(start_date)
        range_end = naive_end_of_day(end_date)  # Use end_of_day for inclusive range

        return range_start, range_end
