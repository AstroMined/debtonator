"""
Balance history service implementation.

This module provides a service for managing balance history records.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from statistics import mean, stdev
from typing import List, Optional, Tuple, Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.balance_history import BalanceHistory
from src.repositories.accounts import AccountRepository
from src.repositories.balance_history import BalanceHistoryRepository
from src.schemas.balance_history import BalanceHistoryCreate, BalanceTrend
from src.services.base import BaseService
from src.services.feature_flags import FeatureFlagService
from src.utils.datetime_utils import ensure_utc, utc_now
from src.utils.decimal_precision import DecimalPrecision


class BalanceHistoryService(BaseService):
    """
    Service for managing balance history records.
    
    This service provides methods for recording, retrieving, and analyzing
    balance history data. It follows the repository pattern for data access
    and inherits from BaseService for standardized repository management.
    """
    
    def __init__(
        self,
        session: AsyncSession,
        feature_flag_service: Optional[FeatureFlagService] = None,
        config_provider: Optional[Any] = None,
    ):
        """
        Initialize balance history service with database session and optional dependencies.
        
        Args:
            session (AsyncSession): SQLAlchemy async session
            feature_flag_service (Optional[FeatureFlagService]): Feature flag service for feature toggling
            config_provider (Optional[Any]): Configuration provider
        """
        super().__init__(session, feature_flag_service, config_provider)

    async def record_balance_change(
        self, balance_data: BalanceHistoryCreate, timestamp: Optional[datetime] = None
    ) -> BalanceHistory:
        """
        Record a new balance history entry.
        
        Args:
            balance_data (BalanceHistoryCreate): Balance history data
            timestamp (Optional[datetime]): Timestamp for the record (defaults to current UTC time)
            
        Returns:
            BalanceHistory: Created balance history record
            
        Raises:
            ValueError: If account does not exist
        """
        # Get repositories
        account_repo = await self._get_repository(AccountRepository)
        balance_repo = await self._get_repository(BalanceHistoryRepository)
        
        # Verify account exists
        account = await account_repo.get(balance_data.account_id)
        if not account:
            raise ValueError(f"Account {balance_data.account_id} not found")

        # Ensure proper timestamp with UTC awareness 
        if timestamp:
            current_time = ensure_utc(timestamp)
        else:
            current_time = utc_now()
        
        # Create database entry (convert to dict and add timestamp)
        entry_data = balance_data.model_dump()
        entry_data["timestamp"] = current_time
        
        # Use repository to create record
        return await balance_repo.create(entry_data)

    async def get_balance_history(
        self,
        account_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[BalanceHistory]:
        """
        Get balance history for an account within a date range.
        
        Args:
            account_id (int): Account ID
            start_date (Optional[datetime]): Start date (inclusive)
            end_date (Optional[datetime]): End date (inclusive)
            
        Returns:
            List[BalanceHistory]: Balance history records within date range
        """
        balance_repo = await self._get_repository(BalanceHistoryRepository)

        # If date range is specified, use specialized repository method
        if start_date and end_date:
            start_date = ensure_utc(start_date)
            end_date = ensure_utc(end_date)
            return await balance_repo.get_by_date_range(account_id, start_date, end_date)
        
        # Otherwise get all history for the account (limited to recent records)
        return await balance_repo.get_by_account(account_id)

    async def get_balance_trend(
        self, account_id: int, start_date: datetime, end_date: datetime
    ) -> BalanceTrend:
        """
        Calculate balance trends for an account within a date range.
        
        Args:
            account_id (int): Account ID
            start_date (datetime): Start date (inclusive)
            end_date (datetime): End date (inclusive)
            
        Returns:
            BalanceTrend: Calculated balance trend statistics
            
        Raises:
            ValueError: If no balance history found for account
        """
        # Ensure UTC timezone awareness
        start_date = ensure_utc(start_date)
        end_date = ensure_utc(end_date)
        
        # Get balance history from repository
        balance_repo = await self._get_repository(BalanceHistoryRepository)
        history = await balance_repo.get_by_date_range(account_id, start_date, end_date)

        if not history:
            raise ValueError(f"No balance history found for account {account_id}")

        balances = [float(entry.balance) for entry in history]

        # Calculate basic statistics with proper precision
        start_balance = DecimalPrecision.round_for_calculation(
            Decimal(str(balances[0]))
        )
        end_balance = DecimalPrecision.round_for_calculation(Decimal(str(balances[-1])))
        net_change = DecimalPrecision.round_for_calculation(end_balance - start_balance)
        avg_balance = DecimalPrecision.round_for_calculation(
            Decimal(str(mean(balances)))
        )
        min_balance = DecimalPrecision.round_for_calculation(
            Decimal(str(min(balances)))
        )
        max_balance = DecimalPrecision.round_for_calculation(
            Decimal(str(max(balances)))
        )

        # Calculate volatility (standard deviation) with proper precision
        volatility = DecimalPrecision.round_for_calculation(
            Decimal(str(stdev(balances))) if len(balances) > 1 else Decimal("0")
        )

        # Determine trend direction - use a slightly higher threshold for "stable" with 4 decimal places
        if abs(net_change) < Decimal("0.0001"):
            trend_direction = "stable"
        else:
            trend_direction = "increasing" if net_change > 0 else "decreasing"

        # The values will be automatically rounded to 2 decimal places for display
        # by the Pydantic schema when returned in API responses
        return BalanceTrend(
            account_id=account_id,
            start_date=start_date,
            end_date=end_date,
            start_balance=start_balance,
            end_balance=end_balance,
            net_change=net_change,
            average_balance=avg_balance,
            min_balance=min_balance,
            max_balance=max_balance,
            trend_direction=trend_direction,
            volatility=volatility,
        )

    async def mark_reconciled(
        self, balance_history_id: int, notes: Optional[str] = None
    ) -> BalanceHistory:
        """
        Mark a balance history entry as reconciled.
        
        Args:
            balance_history_id (int): Balance history entry ID
            notes (Optional[str]): Optional notes to add to the entry
            
        Returns:
            BalanceHistory: Updated balance history record
            
        Raises:
            ValueError: If balance history entry not found
        """
        balance_repo = await self._get_repository(BalanceHistoryRepository)
        
        # Use repository method to mark as reconciled
        updated = await balance_repo.mark_as_reconciled(balance_history_id, True)
        if not updated:
            raise ValueError(f"Balance history entry {balance_history_id} not found")
            
        # If notes provided, add them
        if notes:
            updated = await balance_repo.add_balance_note(balance_history_id, notes)
            
        return updated

    async def get_unreconciled_entries(
        self,
        account_id: int,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> List[BalanceHistory]:
        """
        Get unreconciled balance history entries for an account.
        
        Args:
            account_id (int): Account ID
            start_date (Optional[datetime]): Start date (inclusive)
            end_date (Optional[datetime]): End date (inclusive)
            
        Returns:
            List[BalanceHistory]: Unreconciled balance history entries
        """
        # Get all entries first
        entries = await self.get_balance_history(account_id, start_date, end_date)
        
        # Filter for unreconciled entries
        return [entry for entry in entries if not entry.is_reconciled]
        
    async def get_min_max_balance(
        self, account_id: int, days: int = 30
    ) -> Tuple[Optional[BalanceHistory], Optional[BalanceHistory]]:
        """
        Get minimum and maximum balance records within specified days.
        
        Args:
            account_id (int): Account ID
            days (int): Number of days to look back
            
        Returns:
            Tuple[Optional[BalanceHistory], Optional[BalanceHistory]]: Min and max balance records
        """
        balance_repo = await self._get_repository(BalanceHistoryRepository)
        return await balance_repo.get_min_max_balance(account_id, days)
        
    async def get_balance_trend_data(
        self, account_id: int, days: int = 30
    ) -> List[Tuple[datetime, Decimal]]:
        """
        Get balance trend data for visualization.
        
        Args:
            account_id (int): Account ID
            days (int): Number of days of history
            
        Returns:
            List[Tuple[datetime, Decimal]]: List of (timestamp, balance) tuples
        """
        balance_repo = await self._get_repository(BalanceHistoryRepository)
        return await balance_repo.get_balance_trend(account_id, days)
        
    async def get_average_balance(
        self, account_id: int, days: int = 30
    ) -> Optional[Decimal]:
        """
        Get average balance over specified period.
        
        Args:
            account_id (int): Account ID
            days (int): Number of days to average
            
        Returns:
            Optional[Decimal]: Average balance or None
        """
        balance_repo = await self._get_repository(BalanceHistoryRepository)
        return await balance_repo.get_average_balance(account_id, days)
        
    async def find_missing_days(
        self, account_id: int, days: int = 30
    ) -> List[datetime.date]:
        """
        Find days with no balance records within a period.
        
        Args:
            account_id (int): Account ID
            days (int): Number of days to check
            
        Returns:
            List[date]: List of dates with no balance records
        """
        balance_repo = await self._get_repository(BalanceHistoryRepository)
        return await balance_repo.get_missing_days(account_id, days)
        
    async def get_history_with_relationships(
        self, balance_id: int
    ) -> Optional[BalanceHistory]:
        """
        Get balance history with account relationship loaded.
        
        Args:
            balance_id (int): Balance history ID
            
        Returns:
            Optional[BalanceHistory]: Balance history with account or None
        """
        balance_repo = await self._get_repository(BalanceHistoryRepository)
        return await balance_repo.get_with_account(balance_id)
        
    async def get_available_credit_trend(
        self, account_id: int, days: int = 30
    ) -> List[Tuple[datetime, Optional[Decimal]]]:
        """
        Get available credit trend over time.
        
        Args:
            account_id (int): Account ID
            days (int): Number of days of history
            
        Returns:
            List[Tuple[datetime, Optional[Decimal]]]: List of (timestamp, available_credit) tuples
        """
        balance_repo = await self._get_repository(BalanceHistoryRepository)
        return await balance_repo.get_available_credit_trend(account_id, days)
