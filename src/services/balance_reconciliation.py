"""
Balance reconciliation service.

This module provides a service for managing manual adjustments to account balances,
with proper tracking of reconciliation history and audit reasons.
"""

from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.balance_reconciliation import BalanceReconciliation
from src.repositories.accounts import AccountRepository
from src.repositories.balance_reconciliation import BalanceReconciliationRepository
from src.schemas.balance_reconciliation import (
    BalanceReconciliationCreate,
    BalanceReconciliationUpdate,
)
from src.services.base import BaseService
from src.utils.datetime_utils import utc_now


class BalanceReconciliationError(Exception):
    """Base exception for balance reconciliation operations."""

    def __init__(self, message: str, account_id: Optional[int] = None):
        self.account_id = account_id
        self.message = message
        super().__init__(self.message)


class BalanceReconciliationService(BaseService):
    """
    Service for handling balance reconciliation operations.

    This service manages manual adjustments to account balances,
    including balance reconciliation records, adjustment tracking,
    and account balance updates.
    """

    def __init__(
        self,
        session: AsyncSession,
        feature_flag_service: Optional[Any] = None,
        config_provider: Optional[Any] = None,
    ):
        """
        Initialize the balance reconciliation service.

        Args:
            session: Database session for operations
            feature_flag_service: Optional feature flag service
            config_provider: Optional configuration provider
        """
        super().__init__(session, feature_flag_service, config_provider)

    async def create_reconciliation(
        self, reconciliation_data: BalanceReconciliationCreate
    ) -> BalanceReconciliation:
        """
        Create a new balance reconciliation record and update account balance.

        This method tracks balance adjustments with proper audit history and
        updates the account's current balance.

        Args:
            reconciliation_data: Data for the new reconciliation record

        Returns:
            The newly created reconciliation record

        Raises:
            BalanceReconciliationError: If account not found or validation fails
        """
        # Get repositories
        account_repo = await self._get_repository(AccountRepository)
        reconciliation_repo = await self._get_repository(
            BalanceReconciliationRepository
        )

        # Get the account
        account = await account_repo.get(reconciliation_data.account_id)
        if not account:
            raise BalanceReconciliationError(
                f"Account with id {reconciliation_data.account_id} not found",
                account_id=reconciliation_data.account_id,
            )

        # Calculate adjustment amount if not already set
        adjustment_amount = reconciliation_data.adjustment_amount
        if adjustment_amount is None:
            adjustment_amount = (
                reconciliation_data.new_balance - reconciliation_data.previous_balance
            )

        # Create reconciliation record data
        reconciliation_data_dict = reconciliation_data.model_dump()

        # Add adjustment amount if not in original data
        if (
            "adjustment_amount" not in reconciliation_data_dict
            or reconciliation_data_dict["adjustment_amount"] is None
        ):
            reconciliation_data_dict["adjustment_amount"] = adjustment_amount

        # Add reconciliation date with proper UTC time
        reconciliation_data_dict["reconciliation_date"] = utc_now()

        # Create the reconciliation record
        reconciliation = await reconciliation_repo.create(reconciliation_data_dict)

        # Update account balance
        await account_repo.update(
            account.id, {"available_balance": reconciliation_data.new_balance}
        )

        return reconciliation

    async def get_reconciliation(
        self, reconciliation_id: int
    ) -> Optional[BalanceReconciliation]:
        """
        Get a specific reconciliation record with account relationship loaded.

        Args:
            reconciliation_id: ID of the reconciliation record

        Returns:
            Reconciliation record or None if not found
        """
        reconciliation_repo = await self._get_repository(
            BalanceReconciliationRepository
        )
        return await reconciliation_repo.get_with_account(reconciliation_id)

    async def get_account_reconciliations(
        self, account_id: int, limit: int = 100, offset: int = 0
    ) -> List[BalanceReconciliation]:
        """
        Get reconciliation history for an account with pagination.

        Args:
            account_id: ID of the account
            limit: Maximum number of records to return
            offset: Number of records to skip

        Returns:
            List of reconciliation records
        """
        reconciliation_repo = await self._get_repository(
            BalanceReconciliationRepository
        )
        return await reconciliation_repo.get_by_account(account_id, limit)

    async def update_reconciliation(
        self, reconciliation_id: int, update_data: BalanceReconciliationUpdate
    ) -> Optional[BalanceReconciliation]:
        """
        Update a reconciliation record.

        Note: Only the reason field can be updated to maintain audit integrity.

        Args:
            reconciliation_id: ID of the reconciliation record
            update_data: Data to update

        Returns:
            Updated reconciliation record or None if not found
        """
        reconciliation_repo = await self._get_repository(
            BalanceReconciliationRepository
        )

        # Get the existing record
        reconciliation = await reconciliation_repo.get(reconciliation_id)
        if not reconciliation:
            return None

        # Prepare update dict with only allowed fields
        update_dict: Dict[str, Any] = {}
        if update_data.reason is not None:
            update_dict["reason"] = update_data.reason
            update_dict["updated_at"] = utc_now()

        # Only update if there are changes
        if update_dict:
            return await reconciliation_repo.update(reconciliation_id, update_dict)

        return reconciliation

    async def delete_reconciliation(self, reconciliation_id: int) -> bool:
        """
        Delete a reconciliation record.

        Args:
            reconciliation_id: ID of the reconciliation record

        Returns:
            True if deleted, False if not found
        """
        reconciliation_repo = await self._get_repository(
            BalanceReconciliationRepository
        )

        # Check if the record exists
        reconciliation = await reconciliation_repo.get(reconciliation_id)
        if not reconciliation:
            return False

        # Delete the record
        return await reconciliation_repo.delete(reconciliation_id)

    async def get_latest_reconciliation(
        self, account_id: int
    ) -> Optional[BalanceReconciliation]:
        """
        Get the most recent reconciliation for an account.

        Args:
            account_id: ID of the account

        Returns:
            Most recent reconciliation record or None if none found
        """
        reconciliation_repo = await self._get_repository(
            BalanceReconciliationRepository
        )
        return await reconciliation_repo.get_most_recent(account_id)

    async def get_reconciliations_by_date_range(
        self, account_id: int, start_date, end_date
    ) -> List[BalanceReconciliation]:
        """
        Get reconciliation records within a date range.

        Args:
            account_id: ID of the account
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            List of reconciliation records in the date range
        """
        reconciliation_repo = await self._get_repository(
            BalanceReconciliationRepository
        )
        return await reconciliation_repo.get_by_date_range(
            account_id, start_date, end_date
        )

    async def get_largest_adjustments(
        self, account_id: Optional[int] = None, limit: int = 10
    ) -> List[BalanceReconciliation]:
        """
        Get largest balance adjustments by absolute value.

        Args:
            account_id: Optional ID of the account to filter by
            limit: Maximum number of records to return

        Returns:
            List of reconciliation records with largest adjustments
        """
        reconciliation_repo = await self._get_repository(
            BalanceReconciliationRepository
        )
        return await reconciliation_repo.get_largest_adjustments(account_id, limit)

    async def get_total_adjustment_amount(
        self, account_id: int, start_date=None, end_date=None
    ) -> float:
        """
        Calculate total adjustment amount for an account, optionally within a date range.

        Args:
            account_id: ID of the account
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering

        Returns:
            Total adjustment amount
        """
        reconciliation_repo = await self._get_repository(
            BalanceReconciliationRepository
        )
        return await reconciliation_repo.get_total_adjustment_amount(
            account_id, start_date, end_date
        )

    async def get_adjustment_count_by_reason(
        self, account_id: Optional[int] = None
    ) -> Dict[str, int]:
        """
        Count adjustments grouped by reason.

        Args:
            account_id: Optional ID of the account to filter by

        Returns:
            Dictionary mapping reason to count
        """
        reconciliation_repo = await self._get_repository(
            BalanceReconciliationRepository
        )
        return await reconciliation_repo.get_adjustment_count_by_reason(account_id)

    async def get_reconciliation_frequency(
        self, account_id: int, lookback_days: int = 365
    ) -> float:
        """
        Calculate average days between reconciliations.

        Args:
            account_id: ID of the account
            lookback_days: Number of days to look back

        Returns:
            Average days between reconciliations or 0 if insufficient data
        """
        reconciliation_repo = await self._get_repository(
            BalanceReconciliationRepository
        )
        return await reconciliation_repo.get_reconciliation_frequency(
            account_id, lookback_days
        )
