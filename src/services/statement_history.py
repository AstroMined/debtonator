from datetime import datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.statement_history import StatementHistory
from src.repositories.accounts import AccountRepository
from src.repositories.statement_history import StatementHistoryRepository
from src.services.base import BaseService
from src.utils.datetime_utils import ensure_utc, utc_now


class StatementService(BaseService):
    """
    Service for managing statement history records.

    This service is responsible for business logic related to StatementHistory
    models, including due date calculation, validation, and querying. It follows
    ADR-012 by keeping business logic out of the model layer and ADR-014 by
    using the repository pattern for data access.
    """

    def __init__(
        self,
        session: AsyncSession,
        feature_flag_service: Optional[Any] = None,
        config_provider: Optional[Any] = None,
    ):
        """
        Initialize the service with a database session and optional dependencies.

        Args:
            session: SQLAlchemy async session
            feature_flag_service: Optional feature flag service
            config_provider: Optional configuration provider
        """
        super().__init__(session, feature_flag_service, config_provider)

    def calculate_due_date(self, statement_date: datetime) -> datetime:
        """
        Calculate the due date based on a statement date.

        This method replaces the business logic that was previously in the
        StatementHistory.__init__ method, following ADR-012 requirements.

        Args:
            statement_date: The statement date

        Returns:
            datetime: The calculated due date (25 days after statement date)
        """
        # Ensure the date is UTC-aware per ADR-011
        statement_date = ensure_utc(statement_date)
        return statement_date + timedelta(days=25)

    async def create_statement(
        self,
        account_id: int,
        statement_date: datetime,
        statement_balance: Decimal,
        minimum_payment: Optional[Decimal] = None,
        due_date: Optional[datetime] = None,
    ) -> StatementHistory:
        """
        Create a new statement history record.

        If due_date is not provided, it will be calculated automatically.

        Args:
            account_id: ID of the account
            statement_date: Date of the statement (UTC-aware)
            statement_balance: Balance on the statement
            minimum_payment: Optional minimum payment amount
            due_date: Optional due date (if not provided, will be calculated)

        Returns:
            StatementHistory: The created statement history record

        Raises:
            ValueError: If the account does not exist
        """
        # Ensure UTC-aware datetimes
        statement_date = ensure_utc(statement_date)
        if due_date is not None:
            due_date = ensure_utc(due_date)

        # Verify account exists using account repository
        account_repo = await self._get_repository(AccountRepository)
        account = await account_repo.get(account_id)

        if not account:
            raise ValueError(f"Account with ID {account_id} not found")

        # Calculate due date if not provided
        if due_date is None:
            due_date = self.calculate_due_date(statement_date)

        # Create statement data dictionary
        statement_data = {
            "account_id": account_id,
            "statement_date": statement_date,
            "statement_balance": statement_balance,
            "minimum_payment": minimum_payment,
            "due_date": due_date,
        }

        # Use repository to create statement
        statement_repo = await self._get_repository(StatementHistoryRepository)
        statement = await statement_repo.create(statement_data)

        return statement

    async def get_statement(self, statement_id: int) -> Optional[StatementHistory]:
        """
        Get a statement by ID.

        Args:
            statement_id: ID of the statement to retrieve

        Returns:
            Optional[StatementHistory]: The statement if found, None otherwise
        """
        statement_repo = await self._get_repository(StatementHistoryRepository)
        return await statement_repo.get(statement_id)

    async def get_with_account(self, statement_id: int) -> Optional[StatementHistory]:
        """
        Get a statement with its associated account.

        Args:
            statement_id: ID of the statement to retrieve

        Returns:
            Optional[StatementHistory]: The statement with account if found, None otherwise
        """
        statement_repo = await self._get_repository(StatementHistoryRepository)
        return await statement_repo.get_with_account(statement_id)

    async def get_account_statements(
        self, account_id: int, limit: int = 12
    ) -> List[StatementHistory]:
        """
        Get statements for a specific account, ordered by date (newest first).

        Args:
            account_id: ID of the account
            limit: Maximum number of statements to return

        Returns:
            List[StatementHistory]: List of statement records
        """
        statement_repo = await self._get_repository(StatementHistoryRepository)
        return await statement_repo.get_by_account(account_id, limit=limit)

    async def update_statement(
        self, statement_id: int, update_data: Dict[str, Any]
    ) -> Optional[StatementHistory]:
        """
        Update a statement history record.

        Args:
            statement_id: ID of the statement to update
            update_data: Dictionary of fields to update

        Returns:
            Optional[StatementHistory]: Updated statement if found, None otherwise
        """
        statement_repo = await self._get_repository(StatementHistoryRepository)

        # Handle date fields to ensure UTC awareness
        if "statement_date" in update_data:
            update_data["statement_date"] = ensure_utc(update_data["statement_date"])
        if "due_date" in update_data:
            update_data["due_date"] = ensure_utc(update_data["due_date"])

        return await statement_repo.update(statement_id, update_data)

    async def get_by_date_range(
        self, account_id: int, start_date: datetime, end_date: datetime
    ) -> List[StatementHistory]:
        """
        Get statements within a date range.

        Args:
            account_id: Account ID to filter by
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            List[StatementHistory]: Statements within the date range
        """
        # Ensure UTC-aware datetimes
        start_date = ensure_utc(start_date)
        end_date = ensure_utc(end_date)

        statement_repo = await self._get_repository(StatementHistoryRepository)
        return await statement_repo.get_by_date_range(account_id, start_date, end_date)

    async def get_latest_statement(self, account_id: int) -> Optional[StatementHistory]:
        """
        Get the latest statement for an account.

        Args:
            account_id: Account ID

        Returns:
            Optional[StatementHistory]: Latest statement if any, None otherwise
        """
        statement_repo = await self._get_repository(StatementHistoryRepository)
        return await statement_repo.get_latest_statement(account_id)

    async def get_statements_with_due_dates(
        self, start_date: datetime, end_date: datetime
    ) -> List[StatementHistory]:
        """
        Get statements with due dates in the specified range.

        Args:
            start_date: Start date (inclusive)
            end_date: End date (inclusive)

        Returns:
            List[StatementHistory]: Statements with due dates in range
        """
        # Ensure UTC-aware datetimes
        start_date = ensure_utc(start_date)
        end_date = ensure_utc(end_date)

        statement_repo = await self._get_repository(StatementHistoryRepository)
        return await statement_repo.get_statements_with_due_dates(start_date, end_date)

    async def get_upcoming_statements(self, days: int = 30) -> List[Dict[str, Any]]:
        """
        Get upcoming statements due within specified days with their accounts.

        Args:
            days: Number of days to look ahead

        Returns:
            List[Dict[str, Any]]: List of statement and account information
        """
        statement_repo = await self._get_repository(StatementHistoryRepository)
        statement_account_pairs = (
            await statement_repo.get_upcoming_statements_with_accounts(days)
        )

        # Transform to a more usable format
        result = []
        for statement, account in statement_account_pairs:
            result.append(
                {
                    "statement": statement,
                    "account": account,
                    "days_until_due": (
                        (statement.due_date - utc_now()).days
                        if statement.due_date
                        else None
                    ),
                }
            )

        return result

    async def get_average_statement_balance(
        self, account_id: int, months: int = 6
    ) -> Optional[Decimal]:
        """
        Get average statement balance over specified months.

        Args:
            account_id: Account ID
            months: Number of months to average

        Returns:
            Optional[Decimal]: Average statement balance or None if no statements
        """
        statement_repo = await self._get_repository(StatementHistoryRepository)
        return await statement_repo.get_average_statement_balance(account_id, months)

    async def get_statement_trend(
        self, account_id: int, months: int = 12
    ) -> List[tuple[datetime, Decimal]]:
        """
        Get statement balance trend over time.

        Args:
            account_id: Account ID
            months: Number of months of history

        Returns:
            List[tuple[datetime, Decimal]]: List of (date, balance) tuples
        """
        statement_repo = await self._get_repository(StatementHistoryRepository)
        return await statement_repo.get_statement_trend(account_id, months)

    async def get_minimum_payment_trend(
        self, account_id: int, months: int = 12
    ) -> List[tuple[datetime, Optional[Decimal]]]:
        """
        Get minimum payment trend over time.

        Args:
            account_id: Account ID
            months: Number of months of history

        Returns:
            List[tuple[datetime, Optional[Decimal]]]: List of (date, min_payment) tuples
        """
        statement_repo = await self._get_repository(StatementHistoryRepository)
        return await statement_repo.get_minimum_payment_trend(account_id, months)

    async def get_total_minimum_payments_due(
        self, due_date_start: datetime, due_date_end: datetime
    ) -> Decimal:
        """
        Get total minimum payments due within a date range.

        Args:
            due_date_start: Start date for due dates
            due_date_end: End date for due dates

        Returns:
            Decimal: Total minimum payments due
        """
        # Ensure UTC-aware datetimes
        due_date_start = ensure_utc(due_date_start)
        due_date_end = ensure_utc(due_date_end)

        statement_repo = await self._get_repository(StatementHistoryRepository)
        return await statement_repo.get_total_minimum_payments_due(
            due_date_start, due_date_end
        )

    async def get_statement_by_date(
        self, account_id: int, statement_date: datetime
    ) -> Optional[StatementHistory]:
        """
        Get statement by specific date.

        Args:
            account_id: Account ID
            statement_date: Statement date

        Returns:
            Optional[StatementHistory]: Statement if found, None otherwise
        """
        # Ensure UTC-aware datetime
        statement_date = ensure_utc(statement_date)

        statement_repo = await self._get_repository(StatementHistoryRepository)
        return await statement_repo.get_statement_by_date(
            account_id, statement_date.date()
        )
