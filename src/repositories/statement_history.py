"""
Statement history repository implementation.

This module provides a repository for StatementHistory model CRUD operations and specialized
statement history-related queries.
"""

from datetime import date, datetime, timedelta
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.models.accounts import Account
from src.models.statement_history import StatementHistory
from src.repositories.base_repository import BaseRepository


class StatementHistoryRepository(BaseRepository[StatementHistory, int]):
    """
    Repository for StatementHistory model operations.

    This repository handles CRUD operations for statement history records and provides specialized
    queries for statement history-related functionality.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session (AsyncSession): SQLAlchemy async session
        """
        super().__init__(session, StatementHistory)

    async def get_by_account(
        self, account_id: int, limit: int = 12
    ) -> List[StatementHistory]:
        """
        Get statement history for an account.

        Args:
            account_id (int): Account ID
            limit (int): Maximum number of statements to return

        Returns:
            List[StatementHistory]: List of statement history records
        """
        return await self.get_by_account_ordered(
            account_id=account_id, order_by_desc=True, limit=limit
        )

    async def get_by_account_ordered(
        self, account_id: int, order_by_desc: bool = False, limit: int = 12
    ) -> List[StatementHistory]:
        """
        Get statement history for an account with ordering option.

        Args:
            account_id (int): Account ID
            order_by_desc (bool): Order by statement_date descending if True
            limit (int): Maximum number of statements to return

        Returns:
            List[StatementHistory]: List of statement history records
        """
        query = select(StatementHistory).where(
            StatementHistory.account_id == account_id
        )

        if order_by_desc:
            query = query.order_by(desc(StatementHistory.statement_date))
        else:
            query = query.order_by(StatementHistory.statement_date)

        query = query.limit(limit)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_latest_statement(self, account_id: int) -> Optional[StatementHistory]:
        """
        Get latest statement for an account.

        Args:
            account_id (int): Account ID

        Returns:
            Optional[StatementHistory]: Latest statement or None
        """
        result = await self.session.execute(
            select(StatementHistory)
            .where(StatementHistory.account_id == account_id)
            .order_by(desc(StatementHistory.statement_date))
            .limit(1)
        )
        return result.scalars().first()

    async def get_with_account(self, statement_id: int) -> Optional[StatementHistory]:
        """
        Get statement history with associated account.

        Args:
            statement_id (int): Statement history ID

        Returns:
            Optional[StatementHistory]: Statement with account or None
        """
        result = await self.session.execute(
            select(StatementHistory)
            .options(joinedload(StatementHistory.account))
            .where(StatementHistory.id == statement_id)
        )
        return result.scalars().first()

    async def get_by_date_range(
        self, account_id: int, start_date: datetime, end_date: datetime
    ) -> List[StatementHistory]:
        """
        Get statement history within a date range.

        Args:
            account_id (int): Account ID
            start_date (datetime): Start date (inclusive)
            end_date (datetime): End date (inclusive)

        Returns:
            List[StatementHistory]: List of statement history records
        """
        result = await self.session.execute(
            select(StatementHistory)
            .where(
                and_(
                    StatementHistory.account_id == account_id,
                    StatementHistory.statement_date >= start_date,
                    StatementHistory.statement_date <= end_date,
                )
            )
            .order_by(desc(StatementHistory.statement_date))
        )
        return result.scalars().all()

    async def get_statements_with_due_dates(
        self, start_date: datetime, end_date: datetime
    ) -> List[StatementHistory]:
        """
        Get statements with due dates in specified range.

        Args:
            start_date (datetime): Start date (inclusive)
            end_date (datetime): End date (inclusive)

        Returns:
            List[StatementHistory]: List of statements with due dates in range
        """
        result = await self.session.execute(
            select(StatementHistory)
            .where(
                and_(
                    StatementHistory.due_date.is_not(None),
                    StatementHistory.due_date >= start_date,
                    StatementHistory.due_date <= end_date,
                )
            )
            .order_by(StatementHistory.due_date)
        )
        return result.scalars().all()

    async def get_upcoming_statements_with_accounts(
        self, days: int = 30
    ) -> List[Tuple[StatementHistory, Account]]:
        """
        Get upcoming statements due within specified days with their accounts.

        Args:
            days (int): Number of days to look ahead

        Returns:
            List[Tuple[StatementHistory, Account]]: List of (statement, account) tuples
        """
        today = datetime.now()
        end_date = today + timedelta(days=days)

        result = await self.session.execute(
            select(StatementHistory, Account)
            .join(Account, StatementHistory.account_id == Account.id)
            .where(
                and_(
                    StatementHistory.due_date.is_not(None),
                    StatementHistory.due_date >= today,
                    StatementHistory.due_date <= end_date,
                )
            )
            .order_by(StatementHistory.due_date)
        )
        return result.all()

    async def get_statements_with_minimum_payment(
        self, account_id: int, limit: int = 12
    ) -> List[StatementHistory]:
        """
        Get statements with minimum payment information.

        Args:
            account_id (int): Account ID
            limit (int): Maximum number of statements to return

        Returns:
            List[StatementHistory]: List of statements with minimum payment
        """
        result = await self.session.execute(
            select(StatementHistory)
            .where(
                and_(
                    StatementHistory.account_id == account_id,
                    StatementHistory.minimum_payment.is_not(None),
                )
            )
            .order_by(desc(StatementHistory.statement_date))
            .limit(limit)
        )
        return result.scalars().all()

    async def get_average_statement_balance(
        self, account_id: int, months: int = 6
    ) -> Optional[Decimal]:
        """
        Get average statement balance over specified months.

        Args:
            account_id (int): Account ID
            months (int): Number of months to average

        Returns:
            Optional[Decimal]: Average statement balance or None
        """
        # Get the latest statements up to the specified number of months
        statements = await self.get_by_account(account_id, limit=months)

        if not statements:
            return None

        # Calculate average
        total = sum(stmt.statement_balance for stmt in statements)
        return total / len(statements) if statements else None

    async def get_statement_trend(
        self, account_id: int, months: int = 12
    ) -> List[Tuple[datetime, Decimal]]:
        """
        Get statement balance trend over time.

        Args:
            account_id (int): Account ID
            months (int): Number of months of history

        Returns:
            List[Tuple[datetime, Decimal]]: List of (date, balance) tuples
        """
        statements = await self.get_by_account(account_id, limit=months)
        return [(stmt.statement_date, stmt.statement_balance) for stmt in statements]

    async def get_minimum_payment_trend(
        self, account_id: int, months: int = 12
    ) -> List[Tuple[datetime, Optional[Decimal]]]:
        """
        Get minimum payment trend over time.

        Args:
            account_id (int): Account ID
            months (int): Number of months of history

        Returns:
            List[Tuple[datetime, Optional[Decimal]]]: List of (date, min_payment) tuples
        """
        statements = await self.get_by_account(account_id, limit=months)
        return [(stmt.statement_date, stmt.minimum_payment) for stmt in statements]

    async def get_total_minimum_payments_due(
        self, due_date_start: datetime, due_date_end: datetime
    ) -> Decimal:
        """
        Get total minimum payments due within a date range.

        Args:
            due_date_start (datetime): Start date for due dates
            due_date_end (datetime): End date for due dates

        Returns:
            Decimal: Total minimum payments due
        """
        result = await self.session.execute(
            select(func.sum(StatementHistory.minimum_payment)).where(
                and_(
                    StatementHistory.due_date.is_not(None),
                    StatementHistory.minimum_payment.is_not(None),
                    StatementHistory.due_date >= due_date_start,
                    StatementHistory.due_date <= due_date_end,
                )
            )
        )
        total = result.scalar_one_or_none()
        return total or Decimal("0")

    async def get_statement_by_date(
        self, account_id: int, statement_date: date
    ) -> Optional[StatementHistory]:
        """
        Get statement by specific date.

        Args:
            account_id (int): Account ID
            statement_date (date): Statement date

        Returns:
            Optional[StatementHistory]: Statement or None
        """
        # We need to find statements on the given date, ignoring time components
        result = await self.session.execute(
            select(StatementHistory).where(
                and_(
                    StatementHistory.account_id == account_id,
                    func.date(StatementHistory.statement_date) == statement_date,
                )
            )
        )
        return result.scalars().first()
