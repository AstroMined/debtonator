"""
Account repository implementation.

This module provides a base repository for account operations, focused on common
functionality that applies to accounts of all types. Specialized operations for
specific account types are implemented in type-specific modules.

Enhanced as part of ADR-016, ADR-019, and ADR-024 implementation.
"""

from datetime import datetime
from decimal import Decimal
from typing import Dict, List, Optional, TypeVar

from sqlalchemy import or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload, with_polymorphic

from src.models.accounts import Account
from src.repositories.base_repository import BaseRepository

# Type variable for polymorphic account types
AccountType = TypeVar("AccountType", bound=Account)


class AccountRepository(BaseRepository[Account, int]):
    """
    Base repository for account operations.

    This repository handles common CRUD operations for accounts that apply to
    all account types. Specialized operations for specific account types are
    implemented in dedicated modules following the Repository Module Pattern.

    Implements ADR-016 (Account Type Expansion), ADR-019 (Banking Account Types),
    and ADR-024 (Feature Flag System).
    """

    def __init__(self, session: AsyncSession):
        """
        Initialize repository with database session.

        Args:
            session (AsyncSession): SQLAlchemy async session
        """
        super().__init__(session, Account)
        
    def _needs_polymorphic_loading(self) -> bool:
        """
        Override to enable polymorphic loading for Account entities.
        
        Account is a polymorphic base class with multiple derived types,
        so we need to ensure all entities load correctly with their polymorphic identity.
        
        Returns:
            bool: True to enable polymorphic loading
        """
        return True

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

    async def get_by_type(
        self, account_type: str
    ) -> List[Account]:
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

        # For credit accounts, recalculate next action amount for available credit
        if account.account_type == "credit":
            credit_account = await self.get_with_type(account_id)
            if (
                hasattr(credit_account, "credit_limit")
                and credit_account.credit_limit is not None
            ):
                diff = credit_account.credit_limit - abs(account.available_balance)
                # Set next_action_amount field for credit available
                if hasattr(account, "next_action_amount"):
                    account.next_action_amount = diff

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

    async def create_typed_account(
        self,
        account_type: str,
        data: Dict,
        account_type_registry=None,
    ) -> Account:
        """
        Create a new account of the specified type.

        Args:
            account_type (str): Account type to create
            data (Dict): Account data dictionary
            account_type_registry: Optional registry to get model class

        Returns:
            Account: Created account - will be the specific subclass instance

        Raises:
            ValueError: If account type is invalid

        Note:
            Feature flag validation is now handled by the FeatureFlagRepositoryProxy layer.
        """

        # Use global registry if none provided
        if account_type_registry is None:
            from src.registry.account_types import account_type_registry as global_registry
            account_type_registry = global_registry
            
        # Get model class from registry
        model_class = account_type_registry.get_model_class(account_type)
        
        # Raise error if no model class found - registry should be source of truth
        if not model_class:
            raise ValueError(f"No model class registered for account type '{account_type}'")
        
        # Start with a clean data copy
        data_copy = data.copy()
        data_copy["account_type"] = account_type
        
        # For specialized types, inspect the model to get valid fields
        valid_fields = set()
        
        # Get fields from the model class hierarchy
        current_class = model_class
        while hasattr(current_class, "__table__") and current_class != object:
            if hasattr(current_class, "__table__"):
                for column in current_class.__table__.columns:
                    valid_fields.add(column.key)
                    
            current_class = current_class.__base__
            if not hasattr(current_class, "__table__"):
                break
                
        filtered_data = {
            k: v for k, v in data_copy.items()
            if k in valid_fields or k == "account_type"  # Always include account_type
        }
        
        # Create the instance with filtered data
        db_obj = model_class(**filtered_data)
        self.session.add(db_obj)
        
        # Flush to get an ID but don't refresh yet - will get a fresh instance 
        await self.session.flush()
        
        # Get ID for later query
        created_id = db_obj.id
        
        # Detach the object to ensure we get a fresh instance
        self.session.expunge(db_obj)
        
        # Query using the specific model class to ensure correct type loading
        stmt = select(model_class).where(model_class.id == created_id)
        result = await self.session.execute(stmt)
        typed_account = result.scalars().first()
        
        return typed_account

    async def update_typed_account(
        self,
        account_id: int,
        account_type: str,
        data: Dict,
        account_type_registry=None,
    ) -> Optional[Account]:
        """
        Update an account of the specified type.

        Args:
            account_id (int): Account ID
            account_type (str): Account type
            data (Dict): Update data
            account_type_registry: Optional registry to get model class

        Returns:
            Optional[Account]: Updated account or None if not found

        Raises:
            ValueError: If account type is invalid

        Note:
            Feature flag validation is now handled by the FeatureFlagRepositoryProxy layer.
        """

        # Get the account using polymorphic loading to ensure correct type
        poly_account = with_polymorphic(Account, "*")
        result = await self.session.execute(
            select(poly_account).where(poly_account.id == account_id)
        )
        account = result.scalars().first()
        
        if not account:
            return None

        # Verify account_type matches expected type
        if account.account_type != account_type:
            raise ValueError(
                f"Account ID {account_id} is of type {account.account_type}, not {account_type}"
            )


        # Ensure account_type is preserved
        filtered_data = data.copy()
        filtered_data["account_type"] = account_type
        
        # Get model class for validation (if registry is provided)
        model_class = None
        if account_type_registry:
            model_class = account_type_registry.get_model_class(account_type)
        
        # Use global registry if none provided
        if model_class is None and account_type_registry is None:
            from src.registry.account_types import account_type_registry as global_registry
            model_class = global_registry.get_model_class(account_type)
        
        # Get required fields that should not be set to NULL
        required_fields = {}
        if model_class and hasattr(model_class, "__table__"):
            for column in model_class.__table__.columns:
                if not column.nullable:
                    required_fields[column.key] = True
                    
            # Also check parent classes for required fields
            parent_class = model_class.__bases__[0]
            while hasattr(parent_class, "__table__") and parent_class != object:
                for column in parent_class.__table__.columns:
                    if not column.nullable:
                        required_fields[column.key] = True
                parent_class = parent_class.__bases__[0]
        
        # Log debug info
        print(f"DEBUG: Account before update: {account!r}")
        print(f"DEBUG: Filtered data: {filtered_data}")
        print(f"DEBUG: Required fields that cannot be NULL: {list(required_fields.keys())}")
        
        # Update entity fields, preserving required fields if NULL value provided
        updated_fields = []
        for key, value in filtered_data.items():
            if hasattr(account, key):
                before_value = getattr(account, key)
                
                # Special handling for required fields
                if key in required_fields and value is None:
                    # Skip setting required fields to NULL
                    print(f"DEBUG: Skipping NULL update for required field: {key}, keeping value: {before_value}")
                    continue
                    
                # Handle special default values (like account_format="local")
                if key == "account_format" and value is None and hasattr(account, "account_format"):
                    # This field has a database default, preserve it
                    print(f"DEBUG: Preserving account_format default: {before_value}")
                    continue
                
                setattr(account, key, value)
                after_value = getattr(account, key)
                updated_fields.append(f"{key}: {before_value} -> {after_value}")
                
        print(f"DEBUG: Updated fields: {updated_fields}")

        # Save changes
        self.session.add(account)
        await self.session.flush()
        await self.session.refresh(account)

        return account
