from datetime import date
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from .types import CashflowHolidays, CashflowWarningThresholds


class BaseService:
    """Base service with shared functionality for cashflow services."""

    def __init__(self, db: AsyncSession):
        """Initialize the base service.

        Args:
            db: SQLAlchemy async session for database operations
        """
        self.db = db
        self._warning_thresholds = CashflowWarningThresholds()
        self._holidays = CashflowHolidays(date.today().year).get_holidays()
        self._timezone = ZoneInfo("UTC")

    def _get_warning_thresholds(self) -> CashflowWarningThresholds:
        """Get the current warning thresholds."""
        return self._warning_thresholds

    def _get_holidays(self) -> dict:
        """Get the current holiday dates."""
        return self._holidays

    def _get_timezone(self) -> ZoneInfo:
        """Get the service timezone."""
        return self._timezone

    async def _validate_session(self) -> bool:
        """Validate that the database session is active and usable.

        Returns:
            bool: True if session is valid, False otherwise
        """
        try:
            # Attempt a simple query to verify session
            await self.db.connection()
            return True
        except Exception:
            return False
