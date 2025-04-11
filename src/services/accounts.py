"""
Account service implementation.

This module provides service methods for account management, including account creation,
update, deletion, and specialized operations like statement balance and credit limit updates.
"""

from datetime import date
from decimal import Decimal
from typing import Any, Callable, Dict, List, Optional, Tuple

from src.models.accounts import Account as AccountModel
from src.registry.account_types import account_type_registry
from src.repositories.accounts import AccountRepository
from src.repositories.credit_limit_history import CreditLimitHistoryRepository
from src.repositories.statement_history import StatementHistoryRepository
from src.repositories.transaction_history import TransactionHistoryRepository
from src.schemas.account_types import AccountCreateUnion, AccountResponseUnion
from src.schemas.accounts import (
    AccountInDB,
    AccountStatementHistoryResponse,
    AccountUpdate,
    AvailableCreditResponse,
    StatementBalanceHistory,
)
from src.schemas.credit_limit_history import (
    AccountCreditLimitHistoryResponse,
    CreditLimitHistoryCreate,
    CreditLimitHistoryUpdate,
)
from src.schemas.statement_history import StatementHistoryCreate
from src.services.feature_flags import FeatureFlagService
from src.utils.decimal_precision import DecimalPrecision


class AccountService:
    """
    Service for account management operations.

    This service handles business logic for account operations including validation,
    creation, updates, and specialized operations like statement and credit limit management.

    Supports dynamic loading of type-specific service modules for different account types.
    """

    def __init__(
        self,
        account_repo: AccountRepository,
        statement_repo: StatementHistoryRepository,
        credit_limit_repo: CreditLimitHistoryRepository,
        transaction_repo: TransactionHistoryRepository,
        feature_flag_service: Optional[FeatureFlagService] = None,
    ):
        """
        Initialize service with required repositories.

        Args:
            account_repo: Repository for account operations
            statement_repo: Repository for statement history operations
            credit_limit_repo: Repository for credit limit history operations
            transaction_repo: Repository for transaction history operations
            feature_flag_service: Optional service for feature flag functionality
        """
        self.account_repo = account_repo
        self.statement_repo = statement_repo
        self.credit_limit_repo = credit_limit_repo
        self.transaction_repo = transaction_repo
        self.feature_flag_service = feature_flag_service

        # Storage for dynamically loaded type-specific functions
        self._type_specific_functions: Dict[str, Callable] = {}

    async def validate_account_balance(
        self, account: AccountModel, amount: Decimal
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate if an account has sufficient balance for a transaction

        Args:
            account: The account to validate
            amount: The transaction amount

        Returns:
            Tuple of (is_valid, error_message)
        """
        if account.account_type == "credit":
            # For credit accounts, check against available credit
            if account.total_limit is None:
                return False, "Credit account has no limit set"

            available_credit = await self.calculate_available_credit(account.id)
            if not available_credit:
                return False, "Failed to calculate available credit"

            # Compare with proper precision
            amount_calc = DecimalPrecision.round_for_calculation(amount)
            credit_calc = DecimalPrecision.round_for_calculation(
                available_credit.available_credit
            )

            if amount_calc > credit_calc:
                # Format for display in error message
                amount_display = DecimalPrecision.round_for_display(amount)
                credit_display = DecimalPrecision.round_for_display(
                    available_credit.available_credit
                )
                return (
                    False,
                    f"Transaction amount {amount_display} exceeds available credit {credit_display}",
                )

            return True, None

        else:
            # For checking/savings accounts, check against available balance
            # Compare with proper precision
            amount_calc = DecimalPrecision.round_for_calculation(amount)
            balance_calc = DecimalPrecision.round_for_calculation(
                account.available_balance
            )

            if amount_calc > balance_calc:
                # Format for display in error message
                amount_display = DecimalPrecision.round_for_display(amount)
                balance_display = DecimalPrecision.round_for_display(
                    account.available_balance
                )
                return (
                    False,
                    f"Transaction amount {amount_display} exceeds available balance {balance_display}",
                )

            return True, None

    async def validate_credit_limit_history_update(
        self, account: AccountModel, new_limit: Decimal
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a credit limit update

        Args:
            account: The account to validate
            new_limit: The new credit limit

        Returns:
            Tuple of (is_valid, error_message)
        """
        if account.account_type != "credit":
            return False, "Credit limit can only be set for credit accounts"

        if new_limit <= Decimal(0):
            return False, "Credit limit must be greater than zero"

        if account.available_balance and abs(account.available_balance) > new_limit:
            return (
                False,
                f"New credit limit {new_limit} is less than current balance {abs(account.available_balance)}",
            )

        return True, None

    async def validate_credit_limit_history(
        self, account_id: int
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate that an account can have credit limit history entries

        This replaces the SQLAlchemy event listener that was on the CreditLimitHistory model.
        Ensures credit limit history can only be created for credit accounts.

        Args:
            account_id: ID of the account to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Get the account using the repository
        account = await self.account_repo.get(account_id)

        # Check if account exists
        if not account:
            return False, f"Account with ID {account_id} not found"

        # Check if account is a credit account
        if account.account_type != "credit":
            return False, "Credit limit history can only be created for credit accounts"

        return True, None

    async def validate_transaction(
        self, account: AccountModel, transaction_data: Dict[str, Any]
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate a transaction against account constraints

        Args:
            account: The account to validate
            transaction_data: Transaction details including amount and type

        Returns:
            Tuple of (is_valid, error_message)
        """
        amount = transaction_data.get("amount")
        if not amount:
            return False, "Transaction amount is required"

        if not isinstance(amount, Decimal):
            try:
                amount = Decimal(str(amount))
            except (TypeError, ValueError):
                return False, "Invalid transaction amount"

        if amount <= Decimal(0):
            return False, "Transaction amount must be greater than zero"

        transaction_type = transaction_data.get("transaction_type")
        if transaction_type not in ["debit", "credit"]:
            return False, "Invalid transaction type"

        # For debit transactions, validate balance
        if transaction_type == "debit":
            return await self.validate_account_balance(account, amount)

        return True, None

    def _update_available_credit(self, account: AccountModel) -> None:
        """Update available credit based on total limit and current balance"""
        if account.account_type == "credit" and account.total_limit is not None:
            # Use 4 decimal places for internal calculation
            balance_abs = DecimalPrecision.round_for_calculation(
                abs(account.available_balance)
            )
            available = DecimalPrecision.round_for_calculation(
                account.total_limit - balance_abs
            )

            # Round to 2 decimal places for storage
            account.available_credit = DecimalPrecision.round_for_display(available)

    async def create_account(
        self, account_data: AccountCreateUnion
    ) -> AccountResponseUnion:
        """
        Create a new account of the appropriate type

        Args:
            account_data: Type-specific account creation data (discriminated union)

        Returns:
            Created account with appropriate type

        Raises:
            ValueError: If validation fails
            FeatureDisabledError: If the account type feature is disabled
                                 (enforced by ServiceProxy)
        """
        # Get the account type from the discriminated union
        account_type = account_data.account_type

        # Validate account type against registry
        # This replaces the validation that was previously in the schema
        if not account_type_registry.is_valid_account_type(
            account_type, self.feature_flag_service
        ):
            valid_types = account_type_registry.get_all_types(self.feature_flag_service)
            valid_type_ids = [t["id"] for t in valid_types]
            valid_types_str = ", ".join(valid_type_ids)
            raise ValueError(
                f"Invalid account type '{account_type}'. Must be one of: {valid_types_str}"
            )

        # NOTE: Feature flag checks have been moved to the ServiceProxy layer
        # The proxy will intercept this method call and check if the account type is enabled

        # Apply type-specific validation if available
        await self._apply_type_specific_validation(
            account_type, "validate_create", account_data
        )

        # Initialize account dict
        account_dict = account_data.model_dump()

        # For credit accounts, validate and calculate credit-specific fields
        if account_type == "credit":
            # Add special validation for credit cards
            if (
                not hasattr(account_data, "total_limit")
                or account_data.total_limit is None
            ):
                raise ValueError("Credit accounts must have a total limit")

            # Validate initial credit limit using a mock model
            mock_account = AccountModel(
                type="credit",
                available_balance=Decimal(0),
                total_limit=account_data.total_limit,
            )
            is_valid, error_message = await self.validate_credit_limit_history_update(
                mock_account,
                account_data.total_limit,
            )
            if not is_valid:
                raise ValueError(error_message)

            # Calculate available credit before database insertion
            # Use a properly constructed model instance
            account_obj = AccountModel(**account_dict)
            self._update_available_credit(account_obj)
            account_dict["available_credit"] = account_obj.available_credit

        # Use repository to create account
        db_account = await self.account_repo.create(account_dict)

        # Convert to appropriate response type based on account type
        # This will work with a discriminated union because all the response types
        # are derived from AccountInDB which is derived from AccountBase
        return AccountInDB.model_validate(db_account)

    async def get_account(self, account_id: int) -> Optional[AccountInDB]:
        """
        Get an account by ID

        Args:
            account_id: ID of the account to retrieve

        Returns:
            Account data or None if not found
        """
        db_account = await self.account_repo.get(account_id)
        return AccountInDB.model_validate(db_account) if db_account else None

    async def update_account(
        self, account_id: int, account_data: AccountUpdate
    ) -> Optional[AccountInDB]:
        """
        Update an account and handle credit-related calculations

        Args:
            account_id: ID of the account to update
            account_data: Account update data

        Returns:
            Updated account or None if not found

        Raises:
            ValueError: If validation fails
        """
        db_account = await self.account_repo.get(account_id)
        if not db_account:
            return None

        update_data = account_data.model_dump(exclude_unset=True)

        # Validate type change
        if "type" in update_data and update_data["type"] != db_account.type:
            if db_account.type == "credit" and db_account.available_balance != Decimal(
                0
            ):
                raise ValueError(
                    "Cannot change type of credit account with non-zero balance"
                )
            if update_data["type"] == "credit" and "total_limit" not in update_data:
                raise ValueError("Credit accounts must have a total limit")

        # Validate credit limit changes
        if "total_limit" in update_data:
            is_valid, error_message = await self.validate_credit_limit_history_update(
                db_account, update_data["total_limit"]
            )
            if not is_valid:
                raise ValueError(error_message)

        # Update fields directly in model object for available_credit calculation
        for field, value in update_data.items():
            setattr(db_account, field, value)

        # Calculate available_credit if this is a credit account
        if db_account.type == "credit":
            self._update_available_credit(db_account)
            update_data["available_credit"] = db_account.available_credit

        # Use repository to update account
        updated_account = await self.account_repo.update(account_id, update_data)
        return AccountInDB.model_validate(updated_account) if updated_account else None

    async def validate_account_deletion(
        self, account: AccountModel
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate if an account can be deleted

        Args:
            account: The account to validate

        Returns:
            Tuple of (is_valid, error_message)
        """
        # Check for non-zero balance
        # Use EPSILON for comparing decimal equality
        balance = DecimalPrecision.round_for_calculation(account.available_balance)
        if abs(balance) > DecimalPrecision.EPSILON:
            balance_display = DecimalPrecision.round_for_display(
                account.available_balance
            )
            return (
                False,
                f"Cannot delete account with non-zero balance: {balance_display}",
            )

        # Check for pending transactions
        pending_debits = await self._get_pending_transactions(account.id)
        pending_credits = await self._get_pending_payments(account.id)

        if pending_debits > Decimal(0) or pending_credits > Decimal(0):
            return False, "Cannot delete account with pending transactions"

        # For credit accounts, check statement balance
        if (
            account.account_type == "credit"
            and account.last_statement_balance
            and account.last_statement_balance != Decimal(0)
        ):
            return (
                False,
                f"Cannot delete credit account with outstanding statement balance: {account.last_statement_balance}",
            )

        return True, None

    async def delete_account(self, account_id: int) -> bool:
        """
        Delete an account

        Args:
            account_id: ID of the account to delete

        Returns:
            True if deleted, False if not found

        Raises:
            ValueError: If validation fails
        """
        db_account = await self.account_repo.get(account_id)
        if not db_account:
            return False

        # Validate account deletion
        is_valid, error_message = await self.validate_account_deletion(db_account)
        if not is_valid:
            raise ValueError(error_message)

        # Use repository to delete account
        return await self.account_repo.delete(account_id)

    async def list_accounts(self) -> List[AccountInDB]:
        """
        List all accounts

        Returns:
            List of all accounts
        """
        accounts = await self.account_repo.get_active_accounts()
        return [AccountInDB.model_validate(account) for account in accounts]

    async def validate_statement_update(
        self,
        account: AccountModel,
        statement_balance: Decimal,
        statement_date: date,
        minimum_payment: Optional[Decimal] = None,
        due_date: Optional[date] = None,
    ) -> Tuple[bool, Optional[str]]:
        """
        Validate statement balance update

        Args:
            account: The account to validate
            statement_balance: New statement balance
            statement_date: Statement date
            minimum_payment: Optional minimum payment
            due_date: Optional due date

        Returns:
            Tuple of (is_valid, error_message)
        """
        if statement_balance < Decimal(0):
            return False, "Statement balance cannot be negative"

        if minimum_payment is not None:
            if minimum_payment < Decimal(0):
                return False, "Minimum payment cannot be negative"
            if minimum_payment > statement_balance:
                return False, "Minimum payment cannot exceed statement balance"

        if due_date is not None and statement_date > due_date:
            return False, "Due date cannot be before statement date"

        # For credit accounts, validate against credit limit
        if account.account_type == "credit":
            if account.total_limit is None:
                return False, "Credit account has no limit set"
            if statement_balance > account.total_limit:
                return (
                    False,
                    f"Statement balance {statement_balance} exceeds credit limit {account.total_limit}",
                )

        return True, None

    async def update_statement_balance(
        self,
        account_id: int,
        statement_balance: Decimal,
        statement_date: date,
        minimum_payment: Optional[Decimal] = None,
        due_date: Optional[date] = None,
    ) -> Optional[AccountInDB]:
        """
        Update an account's statement balance and related information

        Args:
            account_id: ID of the account to update
            statement_balance: New statement balance
            statement_date: Statement date
            minimum_payment: Optional minimum payment
            due_date: Optional due date

        Returns:
            Updated account or None if not found

        Raises:
            ValueError: If validation fails
        """
        db_account = await self.account_repo.get(account_id)
        if not db_account:
            return None

        # Validate statement update
        is_valid, error_message = await self.validate_statement_update(
            db_account, statement_balance, statement_date, minimum_payment, due_date
        )
        if not is_valid:
            raise ValueError(error_message)

        # Update current statement info using the account repository
        account_update = {
            "last_statement_balance": statement_balance,
            "last_statement_date": statement_date,
        }
        updated_account = await self.account_repo.update(account_id, account_update)

        # Create statement history entry using the statement repository
        statement_data = StatementHistoryCreate(
            account_id=account_id,
            statement_date=statement_date,
            statement_balance=statement_balance,
            minimum_payment=minimum_payment,
            due_date=due_date,
        )
        await self.statement_repo.create(statement_data.model_dump())

        return AccountInDB.model_validate(updated_account) if updated_account else None

    async def update_credit_limit(
        self, account_id: int, credit_limit_data: CreditLimitHistoryUpdate
    ) -> Optional[AccountInDB]:
        """
        Update an account's credit limit and record in history

        Args:
            account_id: ID of the account to update
            credit_limit_data: New credit limit data including limit, date, and reason

        Returns:
            Updated account or None if not found

        Raises:
            ValueError: If validation fails
        """
        db_account = await self.account_repo.get(account_id)
        if not db_account:
            return None

        # Validate credit limit update
        is_valid, error_message = await self.validate_credit_limit_history_update(
            db_account, credit_limit_data.credit_limit
        )
        if not is_valid:
            raise ValueError(error_message)

        # Validate credit limit history creation
        is_valid, error_message = await self.validate_credit_limit_history(account_id)
        if not is_valid:
            raise ValueError(error_message)

        # Update account's total limit and recalculate available credit
        db_account.total_limit = credit_limit_data.credit_limit
        self._update_available_credit(db_account)

        # Use account repository to update the account
        account_update = {
            "total_limit": credit_limit_data.credit_limit,
            "available_credit": db_account.available_credit,
        }
        updated_account = await self.account_repo.update(account_id, account_update)

        # Create credit limit history entry using the credit limit repository
        history_data = CreditLimitHistoryCreate(
            account_id=account_id,
            credit_limit=credit_limit_data.credit_limit,
            effective_date=credit_limit_data.effective_date,
            reason=credit_limit_data.reason,
        )
        await self.credit_limit_repo.create(history_data.model_dump())

        return AccountInDB.model_validate(updated_account) if updated_account else None

    async def get_credit_limit_history(
        self, account_id: int
    ) -> Optional[AccountCreditLimitHistoryResponse]:
        """
        Get credit limit history for an account

        Args:
            account_id: ID of the account to get history for

        Returns:
            Credit limit history or None if account not found

        Raises:
            ValueError: If account is not a credit account
        """
        db_account = await self.account_repo.get(account_id)
        if not db_account:
            return None

        if db_account.type != "credit":
            raise ValueError("Credit limit history only available for credit accounts")

        # Get credit limit history ordered by effective date descending
        history_records = await self.credit_limit_repo.get_by_account_ordered(
            account_id, order_by_desc=True
        )

        return AccountCreditLimitHistoryResponse(
            account_id=db_account.id,
            account_name=db_account.name,
            current_credit_limit=db_account.total_limit or Decimal(0),
            credit_limit_history=history_records,
        )

    async def calculate_available_credit(
        self, account_id: int
    ) -> Optional[AvailableCreditResponse]:
        """
        Calculate real-time available credit for a credit account

        Args:
            account_id: ID of the account to calculate credit for

        Returns:
            Available credit information or None if account not found

        Raises:
            ValueError: If account is not a credit account
        """
        db_account = await self.account_repo.get(account_id)
        if not db_account:
            return None

        if db_account.type != "credit":
            raise ValueError(
                "Available credit calculation only available for credit accounts"
            )

        # Get pending payments and transactions using transaction repository
        pending_debits = await self._get_pending_transactions(account_id)
        pending_credits = await self._get_pending_payments(account_id)

        # Calculate real-time available credit with proper precision
        current_balance = db_account.available_balance

        # Use 4 decimal places for internal calculations
        pending_debits_calc = DecimalPrecision.round_for_calculation(pending_debits)
        pending_credits_calc = DecimalPrecision.round_for_calculation(pending_credits)
        current_balance_calc = DecimalPrecision.round_for_calculation(current_balance)

        # Calculate with 4 decimal precision
        total_pending = DecimalPrecision.round_for_calculation(
            pending_debits_calc - pending_credits_calc
        )
        adjusted_balance = DecimalPrecision.round_for_calculation(
            current_balance_calc + total_pending
        )

        # Round the result to 2 decimal places for API boundary
        total_pending = DecimalPrecision.round_for_display(total_pending)
        adjusted_balance = DecimalPrecision.round_for_display(adjusted_balance)

        # Calculate available credit with proper precision
        if db_account.total_limit:
            abs_adjusted = DecimalPrecision.round_for_calculation(abs(adjusted_balance))
            limit_calc = DecimalPrecision.round_for_calculation(db_account.total_limit)
            available_credit = DecimalPrecision.round_for_display(
                limit_calc - abs_adjusted
            )
        else:
            available_credit = Decimal(0)

        return AvailableCreditResponse(
            account_id=db_account.id,
            account_name=db_account.name,
            total_limit=db_account.total_limit or Decimal(0),
            current_balance=current_balance,
            pending_transactions=total_pending,
            adjusted_balance=adjusted_balance,
            available_credit=available_credit,
        )
        
    async def get_available_credit_amount(self, credit_account: AccountModel) -> Decimal:
        """
        Calculate and return just the available credit amount for a CreditAccount.
        
        Use this method to access credit availability without requiring a database lookup,
        when you already have the account instance (follows ADR-012).
        
        Args:
            credit_account: Credit account to calculate available credit for
            
        Returns:
            Decimal: Available credit amount
            
        Raises:
            ValueError: If account is not a credit account
        """
        if credit_account.account_type != "credit":
            raise ValueError("Available credit calculation only available for credit accounts")
            
        if not hasattr(credit_account, "credit_limit") or credit_account.credit_limit is None:
            return Decimal("0")
            
        if credit_account.available_balance >= 0:
            # If balance is positive (credit), all credit is available
            return credit_account.credit_limit
            
        # If balance is negative (debit), subtract from limit  
        return credit_account.credit_limit - abs(credit_account.available_balance)

    async def _get_pending_transactions(self, account_id: int) -> Decimal:
        """
        Get sum of pending debit transactions

        Args:
            account_id: ID of the account to get transactions for

        Returns:
            Sum of pending debit transactions
        """
        transactions = await self.transaction_repo.get_debit_sum_for_account(account_id)
        return transactions or Decimal(0)

    async def _get_pending_payments(self, account_id: int) -> Decimal:
        """
        Get sum of pending credit transactions

        Args:
            account_id: ID of the account to get transactions for

        Returns:
            Sum of pending credit transactions
        """
        payments = await self.transaction_repo.get_credit_sum_for_account(account_id)
        return payments or Decimal(0)

    async def get_statement_history(
        self, account_id: int
    ) -> Optional[AccountStatementHistoryResponse]:
        """
        Get statement balance history for an account

        Args:
            account_id: ID of the account to get history for

        Returns:
            Statement history or None if account not found
        """
        # Get account using repository
        db_account = await self.account_repo.get(account_id)
        if not db_account:
            return None

        # Get statement history ordered by date descending
        history_records = await self.statement_repo.get_by_account_ordered(
            account_id, order_by_desc=True
        )

        # Convert to schema response format
        statement_history = [
            StatementBalanceHistory(
                statement_date=record.statement_date,
                statement_balance=record.statement_balance,
                minimum_payment=record.minimum_payment,
                due_date=record.due_date,
            )
            for record in history_records
        ]

        return AccountStatementHistoryResponse(
            account_id=db_account.id,
            account_name=db_account.name,
            statement_history=statement_history,
        )

    # Dynamic service module loading methods

    async def _apply_type_specific_validation(
        self,
        account_type: str,
        validation_type: str,
        data: Any,
        existing_obj: Any = None,
    ) -> None:
        """
        Apply type-specific validation using dynamically loaded validation functions.

        Args:
            account_type: Account type for which to load validation
            validation_type: Type of validation to perform (e.g., 'validate_create', 'validate_update')
            data: Data to validate
            existing_obj: Optional existing object for update validations

        Raises:
            ValueError: If validation fails
        """
        # The feature flag check has been moved to the ServiceProxy layer

        # Use the ServiceFactory to dynamically bind service modules
        from src.services.factory import ServiceFactory

        # Try to load and bind the service module
        success = ServiceFactory.bind_account_type_service(
            self, account_type, self.account_repo._session
        )
        if not success:
            return

        # Check if we have a type-specific validator function
        function_key = f"{account_type}.{validation_type}"
        if function_key in self._type_specific_functions:
            validator_func = self._type_specific_functions[function_key]

            # Call the validator function with appropriate arguments
            if existing_obj:
                await validator_func(data, existing_obj)
            else:
                await validator_func(data)

    async def _apply_type_specific_function(
        self, account_type: str, function_name: str, *args, **kwargs
    ) -> Any:
        """
        Apply type-specific function using dynamically loaded functions.

        Args:
            account_type: Account type for which to load function
            function_name: Name of function to call
            *args: Positional arguments to pass to the function
            **kwargs: Keyword arguments to pass to the function

        Returns:
            Result of the function call, or None if function not found
            
        Note:
            Feature flag checks are handled by the ServiceProxy layer
        """
        # The feature flag check has been moved to the ServiceProxy layer

        # Use the ServiceFactory to dynamically bind service modules
        from src.services.factory import ServiceFactory

        # Try to load and bind the service module
        success = ServiceFactory.bind_account_type_service(
            self, account_type, self.account_repo._session
        )
        if not success:
            return None

        # Check if we have a type-specific function
        function_key = f"{account_type}.{function_name}"
        if function_key in self._type_specific_functions:
            func = self._type_specific_functions[function_key]

            # Call the function with the provided arguments
            return await func(*args, **kwargs)

        return None

    async def get_banking_overview(self, user_id: int) -> Dict[str, Any]:
        """
        Get comprehensive overview of all banking accounts for a user.

        Args:
            user_id: User ID to get overview for

        Returns:
            Dictionary with banking overview information
        """
        # Get all accounts for the user
        accounts = await self.account_repo.get_by_user(user_id)

        # Initialize overview with zero values
        overview = {
            "total_cash": Decimal("0.00"),
            "checking_balance": Decimal("0.00"),
            "savings_balance": Decimal("0.00"),
            "payment_app_balance": Decimal("0.00"),
            "credit_used": Decimal("0.00"),
            "credit_limit": Decimal("0.00"),
            "credit_available": Decimal("0.00"),
            "credit_utilization": Decimal("0.00"),
            "bnpl_balance": Decimal("0.00"),
            "ewa_balance": Decimal("0.00"),
            "total_debt": Decimal("0.00"),
        }

        # Process each account, updating the overview
        for account in accounts:
            if account.is_closed:
                continue

            # Apply type-specific overview update function if available
            type_specific_update = await self._apply_type_specific_function(
                account.account_type, "update_overview", account, overview
            )

            # If there was a type-specific handler, continue to next account
            if type_specific_update is not None:
                continue

            # Apply basic categorization if no type-specific function was found
            if account.account_type == "checking":
                overview["checking_balance"] += account.available_balance
                overview["total_cash"] += account.available_balance
            elif account.account_type == "savings":
                overview["savings_balance"] += account.available_balance
                overview["total_cash"] += account.available_balance
            elif account.account_type == "payment_app":
                overview["payment_app_balance"] += account.available_balance
                overview["total_cash"] += account.available_balance
            elif account.account_type == "credit":
                overview["credit_used"] += abs(account.current_balance)
                if account.total_limit:
                    overview["credit_limit"] += account.total_limit
                    overview["total_debt"] += abs(account.current_balance)
            elif account.account_type == "bnpl":
                overview["bnpl_balance"] += abs(account.current_balance)
                overview["total_debt"] += abs(account.current_balance)
            elif account.account_type == "ewa":
                overview["ewa_balance"] += abs(account.current_balance)
                overview["total_debt"] += abs(account.current_balance)

        # Calculate derived metrics
        if overview["credit_limit"] > 0:
            overview["credit_available"] = (
                overview["credit_limit"] - overview["credit_used"]
            )
            overview["credit_utilization"] = (
                overview["credit_used"] / overview["credit_limit"]
            ) * 100

        return overview

    async def get_upcoming_payments(
        self, user_id: int, days: int = 14
    ) -> List[Dict[str, Any]]:
        """
        Get all upcoming payments for a user across account types.

        Args:
            user_id: User ID to get payments for
            days: Number of days to look ahead

        Returns:
            List of upcoming payments with due dates and amounts
        """
        upcoming_payments = []

        # Get accounts for the user
        accounts = await self.account_repo.get_by_user(user_id)

        # Process each account type
        for account in accounts:
            if account.is_closed:
                continue

            # Get upcoming payments for this account type if supported
            account_payments = await self._apply_type_specific_function(
                account.account_type, "get_upcoming_payments", account.id, days
            )

            # Add to the list if we got payments
            if account_payments:
                upcoming_payments.extend(account_payments)

        # Sort by due date
        return sorted(upcoming_payments, key=lambda x: x["due_date"])

    async def get_account_by_user_and_type(
        self, user_id: int, account_type: str
    ) -> List[AccountInDB]:
        """
        Get all accounts of a specific type for a user.

        Args:
            user_id: User ID to get accounts for
            account_type: Type of accounts to get

        Returns:
            List of accounts of the specified type
        """
        accounts = await self.account_repo.get_by_user_and_type(user_id, account_type)
        return [AccountInDB.model_validate(account) for account in accounts]
