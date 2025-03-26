"""
Account repository implementation.

This module provides a repository for Account model CRUD operations and specialized
account-related queries.
"""

from datetime import datetime
from decimal import Decimal
from typing import Any, Dict, List, Optional, Union

from sqlalchemy import and_, desc, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload, selectinload

from src.models.accounts import Account
from src.models.statement_history import StatementHistory
from src.repositories.base import BaseRepository


class AccountRepository(BaseRepository[Account, int]):
    """
    Repository for Account model operations.

    This repository handles CRUD operations for accounts and provides specialized
    queries for account-related functionality.
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session (AsyncSession): SQLAlchemy async session
        """
        super().__init__(session, Account)

    async def get_by_name(self, name: str) -> Optional[Account]:
        """
        Get account by name.

        Args:
            name (str): Account name to search for

        Returns:
            Optional[Account]: Account with matching name or None
        """
        result = await self.session.execute(select(Account).where(Account.name == name))
        return result.scalars().first()

    async def get_with_statement_history(self, account_id: int) -> Optional[Account]:
        """
        Get account with statement history.

        Args:
            account_id (int): Account ID

        Returns:
            Optional[Account]: Account with loaded statement history or None
        """
        result = await self.session.execute(
            select(Account)
            .options(selectinload(Account.statement_history))
            .where(Account.id == account_id)
        )
        return result.scalars().first()

    async def get_with_relationships(
        self,
        account_id: int,
        include_statements: bool = False,
        include_balance_history: bool = False,
        include_credit_limit_history: bool = False,
        include_payment_schedules: bool = False,
    ) -> Optional[Account]:
        """
        Get account with specified relationships loaded.

        Args:
            account_id (int): Account ID
            include_statements (bool): Load statement history
            include_balance_history (bool): Load balance history
            include_credit_limit_history (bool): Load credit limit history
            include_payment_schedules (bool): Load payment schedules

        Returns:
            Optional[Account]: Account with loaded relationships or None
        """
        query = select(Account).where(Account.id == account_id)

        if include_statements:
            query = query.options(selectinload(Account.statement_history))

        if include_balance_history:
            query = query.options(selectinload(Account.balance_history))

        if include_credit_limit_history:
            query = query.options(selectinload(Account.credit_limit_history))

        if include_payment_schedules:
            query = query.options(selectinload(Account.payment_schedules))

        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_accounts_with_statements(
        self, after_date: Optional[datetime] = None
    ) -> List[Account]:
        """
        Get accounts with their statement history.

        Args:
            after_date (datetime, optional): Filter statements after this date

        Returns:
            List[Account]: Accounts with statement history loaded
        """
        query = (
            select(Account)
            .outerjoin(Account.statement_history)
            .options(selectinload(Account.statement_history))
        )

        if after_date:
            query = query.where(StatementHistory.statement_date >= after_date)

        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def get_active_accounts(self) -> List[Account]:
        """
        Get all active accounts.

        Returns:
            List[Account]: List of active accounts
        """
        # Implementation note: Currently returns all accounts
        # In the future, we might add an 'active' flag to Account model
        result = await self.session.execute(select(Account).order_by(Account.name))
        return result.scalars().all()

    async def get_by_type(self, account_type: str) -> List[Account]:
        """
        Get accounts by type.

        Args:
            account_type (str): Account type to filter by

        Returns:
            List[Account]: List of accounts matching the specified type
        """
        result = await self.session.execute(
            select(Account).where(Account.type == account_type)
        )
        return result.scalars().all()

    async def update_balance(
        self, account_id: int, amount_change: Decimal
    ) -> Optional[Account]:
        """
        Update account balance by adding the specified amount change.

        Args:
            account_id (int): Account ID
            amount_change (Decimal): Amount to add to current balance (negative to subtract)

        Returns:
            Optional[Account]: Updated account or None if not found
        """
        account = await self.get(account_id)
        if not account:
            return None

        account.available_balance += amount_change

        # For credit accounts, recalculate available credit
        if account.type == "credit" and account.total_limit is not None:
            # Initialize available_credit to 0 if it's None
            if account.available_credit is None:
                account.available_credit = Decimal("0.0")
            
            account.available_credit = account.total_limit - abs(
                account.available_balance
            )

        await self.session.flush()
        await self.session.refresh(account)
        return account

    async def update_statement_balance(
        self, account_id: int, statement_balance: Decimal, statement_date: datetime
    ) -> Optional[Account]:
        """
        Update account's statement balance and date.

        Args:
            account_id (int): Account ID
            statement_balance (Decimal): New statement balance
            statement_date (datetime): Statement date

        Returns:
            Optional[Account]: Updated account or None if not found
        """
        return await self.update(
            account_id,
            {
                "last_statement_balance": statement_balance,
                "last_statement_date": statement_date,
            },
        )

    async def find_accounts_with_low_balance(self, threshold: Decimal) -> List[Account]:
        """
        Find accounts with balance below threshold.

        Args:
            threshold (Decimal): Balance threshold

        Returns:
            List[Account]: Accounts with balance below threshold
        """
        result = await self.session.execute(
            select(Account)
            .where(Account.available_balance < threshold)
            .order_by(Account.available_balance)
        )
        return result.scalars().all()

    async def find_credit_accounts_near_limit(
        self, threshold_percentage: Decimal = Decimal("0.9")
    ) -> List[Account]:
        """
        Find credit accounts near their credit limit.

        Args:
            threshold_percentage (Decimal): Threshold as percentage of credit limit

        Returns:
            List[Account]: Credit accounts near limit
        """
        # This query finds credit accounts where available_credit is less than
        # (1 - threshold_percentage) * total_limit
        result = await self.session.execute(
            select(Account)
            .where(
                and_(
                    Account.type == "credit",
                    Account.total_limit.is_not(None),
                    Account.available_credit
                    <= (1 - threshold_percentage) * Account.total_limit,
                )
            )
            .order_by(desc(Account.available_credit))
        )
        return result.scalars().all()
