from datetime import date
from typing import Optional, TypeVar
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.cashflow.forecast_repository import CashflowForecastRepository
from src.repositories.cashflow.metrics_repository import CashflowMetricsRepository
from src.repositories.cashflow.transaction_repository import CashflowTransactionRepository
from src.repositories.factory import RepositoryFactory
from src.services.cashflow.types import CashflowHolidays, CashflowWarningThresholds

# Generic type for repository types
RepositoryType = TypeVar("RepositoryType")


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
        
        # Repository instances to be lazy-loaded
        self._forecast_repo = None
        self._metrics_repo = None
        self._transaction_repo = None

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
    
    # Repository accessors with lazy loading
    
    @property
    async def forecast_repository(self) -> CashflowForecastRepository:
        """
        Get the cashflow forecast repository instance.
        
        Returns:
            CashflowForecastRepository: Cashflow forecast repository
        """
        if self._forecast_repo is None:
            self._forecast_repo = await RepositoryFactory.create_cashflow_forecast_repository(
                self.db
            )
        return self._forecast_repo
    
    @property
    async def metrics_repository(self) -> CashflowMetricsRepository:
        """
        Get the cashflow metrics repository instance.
        
        Returns:
            CashflowMetricsRepository: Cashflow metrics repository
        """
        if self._metrics_repo is None:
            self._metrics_repo = await RepositoryFactory.create_cashflow_metrics_repository(
                self.db
            )
        return self._metrics_repo
    
    @property
    async def transaction_repository(self) -> CashflowTransactionRepository:
        """
        Get the cashflow transaction repository instance.
        
        Returns:
            CashflowTransactionRepository: Cashflow transaction repository
        """
        if self._transaction_repo is None:
            self._transaction_repo = await RepositoryFactory.create_cashflow_transaction_repository(
                self.db
            )
        return self._transaction_repo
