from datetime import date
from typing import Any, Optional, TypeVar
from zoneinfo import ZoneInfo

from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.cashflow.forecast_repository import CashflowForecastRepository
from src.repositories.cashflow.metrics_repository import CashflowMetricsRepository
from src.repositories.cashflow.transaction_repository import CashflowTransactionRepository
from src.services.base import BaseService as AppBaseService
from src.services.cashflow.types import CashflowHolidays, CashflowWarningThresholds
from src.services.feature_flags import FeatureFlagService

# Generic type for repository types
RepositoryType = TypeVar("RepositoryType")


class BaseService(AppBaseService):
    """Base service with shared functionality for cashflow services."""

    def __init__(
        self, 
        session: AsyncSession,
        feature_flag_service: Optional[FeatureFlagService] = None,
        config_provider: Optional[Any] = None
    ):
        """Initialize the base service.

        Args:
            session: SQLAlchemy async session for database operations
            feature_flag_service: Optional feature flag service for repository proxies
            config_provider: Optional config provider for feature flags
        """
        super().__init__(session, feature_flag_service, config_provider)
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
            await self._session.connection()
            return True
        except Exception:
            return False
    
    # Repository accessors with lazy loading using BaseService._get_repository
    
    @property
    async def forecast_repository(self) -> CashflowForecastRepository:
        """
        Get the cashflow forecast repository instance.
        
        Returns:
            CashflowForecastRepository: Cashflow forecast repository
        """
        return await self._get_repository(CashflowForecastRepository)
    
    @property
    async def metrics_repository(self) -> CashflowMetricsRepository:
        """
        Get the cashflow metrics repository instance.
        
        Returns:
            CashflowMetricsRepository: Cashflow metrics repository
        """
        return await self._get_repository(CashflowMetricsRepository)
    
    @property
    async def transaction_repository(self) -> CashflowTransactionRepository:
        """
        Get the cashflow transaction repository instance.
        
        Returns:
            CashflowTransactionRepository: Cashflow transaction repository
        """
        return await self._get_repository(CashflowTransactionRepository)
