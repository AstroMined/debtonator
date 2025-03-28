"""
Account service implementation.

This module provides service methods for account management, including account creation,
update, deletion, and specialized operations like statement balance and credit limit updates.
"""

from datetime import date
from decimal import Decimal
from typing import Any, Dict, List, Optional, Tuple

from src.core.decimal_precision import DecimalPrecision
from src.models.accounts import Account as AccountModel
from src.repositories.accounts import AccountRepository
from src.repositories.credit_limit_history import CreditLimitHistoryRepository
from src.repositories.statement_history import StatementHistoryRepository
from src.repositories.transaction_history import TransactionHistoryRepository
from src.schemas.accounts import (
    AccountCreate,
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


class AccountService:
    """
    Service for account management operations.

    This service handles business logic for account operations including validation,
    creation, updates, and specialized operations like statement and credit limit management.
    """

    def __init__(
        self,
        account_repo: AccountRepository,
        statement_repo: StatementHistoryRepository,
        credit_limit_repo: CreditLimitHistoryRepository,
        transaction_repo: TransactionHistoryRepository,
    ):
        """
        Initialize service with required repositories.

        Args:
            account_repo (AccountRepository): Repository for account operations
            statement_repo (StatementHistoryRepository): Repository for statement history operations
            credit_limit_repo (CreditLimitHistoryRepository): Repository for credit limit history operations
            transaction_repo (TransactionHistoryRepository): Repository for transaction history operations
        """
        self.account_repo = account_repo
        self.statement_repo = statement_repo
        self.credit_limit_repo = credit_limit_repo
        self.transaction_repo = transaction_repo

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
        if account.type == "credit":
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
        if account.type != "credit":
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
        if account.type != "credit":
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
        if account.type == "credit" and account.total_limit is not None:
            # Use 4 decimal places for internal calculation
            balance_abs = DecimalPrecision.round_for_calculation(
                abs(account.available_balance)
            )
            available = DecimalPrecision.round_for_calculation(
                account.total_limit - balance_abs
            )

            # Round to 2 decimal places for storage
            account.available_credit = DecimalPrecision.round_for_display(available)

    async def create_account(self, account_data: AccountCreate) -> AccountInDB:
        """
        Create a new account and initialize credit-related fields if applicable

        Args:
            account_data: Account creation data

        Returns:
            Created account

        Raises:
            ValueError: If validation fails
        """
        # Validate credit-related fields for credit accounts
        if account_data.type == "credit":
            if account_data.total_limit is None:
                raise ValueError("Credit accounts must have a total limit")

            # Validate initial credit limit
            is_valid, error_message = await self.validate_credit_limit_history_update(
                AccountModel(type="credit", available_balance=Decimal(0)),
                account_data.total_limit,
            )
            if not is_valid:
                raise ValueError(error_message)

        # Initialize available_credit for credit accounts
        account_dict = account_data.model_dump()
        account_obj = AccountModel(**account_dict)

        # Calculate available_credit before database insertion
        if account_obj.type == "credit" and account_obj.total_limit is not None:
            self._update_available_credit(account_obj)
            account_dict["available_credit"] = account_obj.available_credit

        # Use repository to create account
        db_account = await self.account_repo.create(account_dict)
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
            account.type == "credit"
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
        if account.type == "credit":
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
