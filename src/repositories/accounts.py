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
        self, account_type: str, feature_flag_service=None
    ) -> List[Account]:
        """
        Get accounts by type.

        Args:
            account_type (str): Account type to filter by
            feature_flag_service: Optional feature flag service for feature validation

        Returns:
            List[Account]: List of accounts matching the specified type

        Raises:
            ValueError: If the account type is unavailable due to disabled feature flags
        """
        # Check if this type is available based on feature flags
        if feature_flag_service and account_type in ["payment_app", "bnpl", "ewa"]:
            if not feature_flag_service.is_enabled("BANKING_ACCOUNT_TYPES_ENABLED"):
                raise ValueError(
                    f"Account type {account_type} is not currently enabled"
                )

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
        self, currency: str, include_closed: bool = False, feature_flag_service=None
    ) -> List[Account]:
        """
        Get accounts with a specific currency.

        Args:
            currency (str): ISO 4217 currency code (e.g., USD, EUR)
            include_closed (bool): Whether to include closed accounts
            feature_flag_service: Optional feature flag service for feature validation

        Returns:
            List[Account]: Accounts with the specified currency

        Note:
            This method respects the MULTI_CURRENCY_SUPPORT_ENABLED feature flag if provided.
        """
        # Check if multi-currency support is enabled
        if feature_flag_service and currency != "USD":
            if not feature_flag_service.is_enabled("MULTI_CURRENCY_SUPPORT_ENABLED"):
                # If multi-currency is disabled, only return USD accounts
                currency = "USD"

        query = select(Account).where(Account.currency == currency)

        if not include_closed:
            query = query.where(Account.is_closed == False)  # noqa: E712

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_accounts_with_international_fields(
        self, include_closed: bool = False, feature_flag_service=None
    ) -> List[Account]:
        """
        Get accounts that have international banking fields set.

        Args:
            include_closed (bool): Whether to include closed accounts
            feature_flag_service: Optional feature flag service for feature validation

        Returns:
            List[Account]: Accounts with international banking fields

        Note:
            This method respects the INTERNATIONAL_ACCOUNT_SUPPORT_ENABLED feature flag
            if provided.
        """
        # Check if international account support is enabled
        if feature_flag_service:
            if not feature_flag_service.is_enabled(
                "INTERNATIONAL_ACCOUNT_SUPPORT_ENABLED"
            ):
                return []

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

    async def create_typed_account(
        self,
        account_type: str,
        data: Dict,
        feature_flag_service=None,
        account_type_registry=None,
    ) -> Account:
        """
        Create a new account of the specified type.

        Args:
            account_type (str): Account type to create
            data (Dict): Account data dictionary
            feature_flag_service: Optional feature flag service for feature validation
            account_type_registry: Optional registry to get model class

        Returns:
            Account: Created account

        Raises:
            ValueError: If account type is invalid or unavailable due to feature flags
        """
        # Check if this account type is available based on feature flags
        if feature_flag_service and account_type_registry:
            type_info = account_type_registry._registry.get(account_type, {})
            feature_flag = type_info.get("feature_flag")
            if feature_flag and not feature_flag_service.is_enabled(feature_flag):
                raise ValueError(
                    f"Account type {account_type} is not currently enabled"
                )

        # Get model class if registry is provided
        model_class = None
        if account_type_registry:
            model_class = account_type_registry.get_model_class(account_type)
            if not model_class:
                raise ValueError(f"Unknown account type: {account_type}")
        
        # If no model class found, fall back to base Account
        if not model_class:
            model_class = Account
            
        # Ensure account_type is set correctly
        if "account_type" not in data:
            data["account_type"] = account_type
        
        # Filter data to only include fields valid for this model class
        filtered_data = {}
        
        # Get all valid columns for this model class and its parent classes
        valid_columns = set()
        current_class = model_class
        
        # Walk up the inheritance hierarchy to collect all valid columns
        while current_class is not object:
            if hasattr(current_class, "__table__"):
                valid_columns.update(column.key for column in current_class.__table__.columns)
            
            # Move to the parent class
            current_class = current_class.__base__
            
            # Stop if we've reached the base SQLAlchemy model
            if current_class.__name__ == "Base":
                break
        
        # If we couldn't determine columns, use a more direct approach
        if not valid_columns and hasattr(model_class, "__mapper__"):
            valid_columns = set(model_class.__mapper__.column_attrs.keys())
        
        # Include only valid columns in filtered data
        if valid_columns:
            for key, value in data.items():
                if key in valid_columns:
                    filtered_data[key] = value
                
            # Ensure account_type is set
            filtered_data["account_type"] = account_type
        else:
            # If we still can't determine columns, use the original data
            filtered_data = data.copy()
            filtered_data["account_type"] = account_type

        # Create the account using the appropriate model class
        db_obj = model_class(**filtered_data)
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def update_typed_account(
        self,
        account_id: int,
        account_type: str,
        data: Dict,
        feature_flag_service=None,
        account_type_registry=None,
    ) -> Optional[Account]:
        """
        Update an account of the specified type.

        Args:
            account_id (int): Account ID
            account_type (str): Account type
            data (Dict): Update data
            feature_flag_service: Optional feature flag service for feature validation
            account_type_registry: Optional registry to get model class

        Returns:
            Optional[Account]: Updated account or None if not found

        Raises:
            ValueError: If account type is invalid or unavailable due to feature flags
        """
        # Check if this account type is available based on feature flags
        if feature_flag_service and account_type_registry:
            type_info = account_type_registry._registry.get(account_type, {})
            feature_flag = type_info.get("feature_flag")
            if feature_flag and not feature_flag_service.is_enabled(feature_flag):
                raise ValueError(
                    f"Account type {account_type} is not currently enabled"
                )

        # Get the account
        account = await self.get(account_id)
        if not account:
            return None

        # Check if updating international fields and if they're allowed
        if feature_flag_service:
            international_fields = [
                "iban",
                "swift_bic",
                "sort_code",
                "branch_code",
                "account_format",
            ]
            has_international_fields = any(
                field in data for field in international_fields
            )

            if has_international_fields and not feature_flag_service.is_enabled(
                "INTERNATIONAL_ACCOUNT_SUPPORT_ENABLED"
            ):
                # Remove international fields from update data
                for field in international_fields:
                    if field in data:
                        del data[field]

        # Check if updating currency and if it's allowed
        if feature_flag_service and "currency" in data and data["currency"] != "USD":
            if not feature_flag_service.is_enabled("MULTI_CURRENCY_SUPPORT_ENABLED"):
                # Force USD if multi-currency is disabled
                data["currency"] = "USD"
        
        # Filter data to only include fields valid for this account type
        filtered_data = data.copy()
        
        # Remove account_type if it's None to preserve the existing value
        if "account_type" in filtered_data and filtered_data["account_type"] is None:
            del filtered_data["account_type"]
        
        # Get model class if registry is provided
        model_class = None
        if account_type_registry:
            model_class = account_type_registry.get_model_class(account_type)
        
        # Filter fields if we have a model class
        if model_class:
            # Get all valid columns for this model class and its parent classes
            valid_columns = set()
            current_class = model_class
            
            # Walk up the inheritance hierarchy to collect all valid columns
            while current_class is not object:
                if hasattr(current_class, "__table__"):
                    valid_columns.update(column.key for column in current_class.__table__.columns)
                
                # Move to the parent class
                current_class = current_class.__base__
                
                # Stop if we've reached the base SQLAlchemy model
                if current_class.__name__ == "Base":
                    break
            
            # If we couldn't determine columns, use a more direct approach
            if not valid_columns and hasattr(model_class, "__mapper__"):
                valid_columns = set(model_class.__mapper__.column_attrs.keys())
            
            # Filter data to only include valid columns
            if valid_columns:
                keys_to_remove = []
                for key in filtered_data:
                    if key not in valid_columns:
                        keys_to_remove.append(key)
                
                for key in keys_to_remove:
                    del filtered_data[key]

        # Update the entity
        updated_account = await self.update(account_id, filtered_data)
        return updated_account
