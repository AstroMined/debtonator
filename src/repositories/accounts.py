"""
Account repository implementation.

This module provides a base repository for account operations, focused on common
functionality that applies to accounts of all types. Specialized operations for
specific account types are implemented in type-specific modules.

Enhanced as part of ADR-016, ADR-019, and ADR-024 implementation.
"""

from datetime import datetime
from decimal import Decimal
from typing import List, Optional, TypeVar

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_polymorphic

from src.models.accounts import Account
from src.registry.account_types import account_type_registry
from src.repositories.polymorphic_base_repository import PolymorphicBaseRepository
from src.utils.datetime_utils import ensure_utc  # Added UTC datetime compliance

# Type variable for polymorphic account types
AccountType = TypeVar("AccountType", bound=Account)


class AccountRepository(PolymorphicBaseRepository[Account, int]):
    # Set the discriminator field for accounts
    discriminator_field = "account_type"

    # Set the registry for account types
    registry = account_type_registry
    """
    Base repository for account operations.

    This repository handles common CRUD operations for accounts that apply to
    all account types. Specialized operations for specific account types are
    implemented in dedicated modules following the Repository Module Pattern.

    Implements ADR-016 (Account Type Expansion), ADR-019 (Banking Account Types),
    and ADR-024 (Feature Flag System).

    NOTE: This repository uses the create_typed_entity and update_typed_entity
    methods from PolymorphicBaseRepository to ensure proper handling of
    polymorphic identities.
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
            after_date (datetime, optional): Filter statements after this date.
                Must be a timezone-aware datetime (UTC).

        Returns:
            List[Account]: Accounts with statement history loaded
        """
        # Ensure UTC timezone awareness for datetime parameter
        if after_date is not None:
            after_date = ensure_utc(after_date)
            # For database operations, strip timezone
            after_date = after_date.replace(tzinfo=None)

        query = (
            select(Account)
            .outerjoin(Account.statement_history)
            .options(selectinload(Account.statement_history))
        )

        # Note: The actual filtering by date needs to be handled differently
        # since statement_history is a relationship, not a direct field

        result = await self.session.execute(query)
        return result.unique().scalars().all()

    async def get_active_accounts(self) -> List[Account]:
        """
        Get all active accounts.

        Returns:
            List[Account]: List of active accounts (not closed)
        """
        result = await self.session.execute(
            select(Account)
            .where(Account.is_closed == False)  # noqa: E712
            .order_by(Account.name)
        )
        return result.scalars().all()

    async def get_by_type(self, account_type: str) -> List[Account]:
        """
        Get accounts by type.

        Args:
            account_type (str): Account type to filter by

        Returns:
            List[Account]: List of accounts matching the specified type

        Note:
            Feature flag validation is now handled by the FeatureFlagRepositoryProxy layer.
        """
        # Query for the specific account type
        query = select(Account).where(Account.account_type == account_type)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_with_type(self, account_id: int) -> Optional[Account]:
        """
        Get account by ID, ensuring type-specific data is loaded.

        This method uses polymorphic loading to ensure all type-specific
        fields are populated in the returned object.

        Args:
            account_id (int): Account ID

        Returns:
            Optional[Account]: Account instance with type-specific data or None
        """
        # Load all polymorphic types - this ensures we get the specific type's data
        poly_account = with_polymorphic(Account, "*")

        result = await self.session.execute(
            select(poly_account).where(poly_account.id == account_id)
        )
        return result.scalars().first()

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

        # For credit accounts, recalculate available credit and next action amount
        if account.account_type == "credit":
            credit_account = await self.get_with_type(account_id)
            if (
                hasattr(credit_account, "credit_limit")
                and credit_account.credit_limit is not None
            ):
                # Recalculate available credit
                credit_account.available_credit = credit_account.credit_limit - abs(account.available_balance)
                # Set next_action_amount field for credit available
                if hasattr(account, "next_action_amount"):
                    account.next_action_amount = credit_account.available_credit
                # Make sure we use the updated account for flush and return
                account = credit_account

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
            statement_date (datetime): Statement date, must be a timezone-aware 
                datetime (UTC)

        Returns:
            Optional[Account]: Updated account or None if not found
        """
        account = await self.get(account_id)
        if not account:
            return None

        # Ensure UTC timezone awareness for datetime parameter
        statement_date = ensure_utc(statement_date)
        
        # For database operations, strip timezone
        db_statement_date = statement_date.replace(tzinfo=None)

        # Get the account type
        account_type = account.account_type

        # Use update_typed_entity to ensure proper polymorphic identity
        return await self.update_typed_entity(
            account_id,
            account_type,
            {
                "last_statement_balance": statement_balance,
                "last_statement_date": db_statement_date,
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

    async def get_accounts_by_currency(
        self, currency: str, include_closed: bool = False
    ) -> List[Account]:
        """
        Get accounts with a specific currency.

        Args:
            currency (str): ISO 4217 currency code (e.g., USD, EUR)
            include_closed (bool): Whether to include closed accounts

        Returns:
            List[Account]: Accounts with the specified currency

        Note:
            Feature flag validation for MULTI_CURRENCY_SUPPORT_ENABLED is now handled
            by the FeatureFlagRepositoryProxy layer.
        """

        query = select(Account).where(Account.currency == currency)

        if not include_closed:
            query = query.where(Account.is_closed == False)  # noqa: E712

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_accounts_with_international_fields(
        self, include_closed: bool = False
    ) -> List[Account]:
        """
        Get accounts that have international banking fields set.

        Args:
            include_closed (bool): Whether to include closed accounts

        Returns:
            List[Account]: Accounts with international banking fields

        Note:
            Feature flag validation for INTERNATIONAL_ACCOUNT_SUPPORT_ENABLED is now handled
            by the FeatureFlagRepositoryProxy layer.
        """

        # Use with_polymorphic to query across all account types
        PolyAccount = with_polymorphic(Account, "*")

        # Build a query for accounts with any international fields set
        query = select(PolyAccount).where(
            or_(
                PolyAccount.swift_bic.is_not(None),
                PolyAccount.iban.is_not(None),
                PolyAccount.sort_code.is_not(None),
                PolyAccount.branch_code.is_not(None),
                PolyAccount.account_format != "local",
            )
        )

        if not include_closed:
            query = query.where(PolyAccount.is_closed == False)  # noqa: E712

        result = await self.session.execute(query)
        return result.scalars().all()

    async def delete(self, id: int) -> bool:
        """
        Soft delete an account by marking it as closed.

        This overrides the base repository's delete method to implement
        soft deletion for accounts, maintaining data integrity while
        allowing "deletion" functionality.

        Args:
            id (int): Account ID

        Returns:
            bool: True if soft deleted, False if not found
        """
        # Get the account
        account = await self.get(id)
        if not account:
            return False

        # Mark as closed (soft delete)
        account.is_closed = True
        self.session.add(account)
        await self.session.flush()

        return True
