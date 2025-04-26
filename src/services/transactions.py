"""
Transaction service implementation.

This module provides services for managing transaction history operations including
creating, updating, and querying transactions across accounts. It properly implements
the repository pattern according to ADR-014 Repository Layer Compliance.

Uses ADR-011 compliant datetime handling with utilities from datetime_utils.
"""

from datetime import datetime
from typing import List, Optional

from src.models.transaction_history import TransactionHistory, TransactionType
from src.repositories.accounts import AccountRepository
from src.repositories.transaction_history import TransactionHistoryRepository
from src.schemas.transaction_history import (
    TransactionHistoryCreate as TransactionCreate,
)
from src.schemas.transaction_history import (
    TransactionHistoryUpdate as TransactionUpdate,
)
from src.services.base import BaseService


class TransactionService(BaseService):
    """
    Service for handling transaction operations.

    This service manages transaction history operations including creating,
    retrieving, updating, and deleting transactions. It also provides specialized
    queries for transaction analysis and reporting.

    Follows ADR-014 Repository Layer Compliance by using the BaseService pattern.
    """

    # The service inherits all initialization behavior from BaseService
    # No need to override __init__ as it would add no new functionality

    async def create_transaction(
        self, account_id: int, transaction_data: TransactionCreate
    ) -> TransactionHistory:
        """
        Create a new transaction and update account balance.

        Args:
            account_id: ID of the account for the transaction
            transaction_data: Transaction data to create

        Returns:
            TransactionHistory: Created transaction

        Raises:
            ValueError: If account doesn't exist
        """
        # Get repositories using BaseService pattern
        account_repo = await self._get_repository(AccountRepository)
        transaction_repo = await self._get_repository(TransactionHistoryRepository)

        # Get the account
        account = await account_repo.get(account_id)
        if not account:
            raise ValueError(f"Account with id {account_id} not found")

        # Prepare transaction data
        transaction_dict = {
            "account_id": account_id,
            "amount": transaction_data.amount,
            "transaction_type": transaction_data.transaction_type,
            "description": transaction_data.description,
            "transaction_date": transaction_data.transaction_date,
        }

        # Update account balance based on transaction type
        if transaction_data.transaction_type == TransactionType.CREDIT:
            account.available_balance += transaction_data.amount
        else:  # DEBIT
            account.available_balance -= transaction_data.amount

        # Update the account
        await account_repo.update(
            account_id, {"available_balance": account.available_balance}
        )

        # Create transaction using repository
        transaction = await transaction_repo.create(transaction_dict)

        return transaction

    async def get_transaction(
        self, transaction_id: int
    ) -> Optional[TransactionHistory]:
        """
        Get a transaction by ID with account relationship loaded.

        Args:
            transaction_id: ID of the transaction to retrieve

        Returns:
            Optional[TransactionHistory]: Transaction with account or None if not found
        """
        # Get repository using BaseService pattern
        transaction_repo = await self._get_repository(TransactionHistoryRepository)
        return await transaction_repo.get_with_account(transaction_id)

    async def get_account_transactions(
        self,
        account_id: int,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> tuple[List[TransactionHistory], int]:
        """
        Get transactions for an account with optional date filtering and pagination.

        Args:
            account_id: ID of the account to get transactions for
            skip: Number of records to skip for pagination
            limit: Maximum number of records to return
            start_date: Optional start date for filtering
            end_date: Optional end date for filtering

        Returns:
            Tuple containing transactions list and total count
        """
        # Get repository using BaseService pattern
        transaction_repo = await self._get_repository(TransactionHistoryRepository)

        # Get transactions within date range if specified
        if start_date and end_date:
            transactions = await transaction_repo.get_by_date_range(
                account_id, start_date, end_date
            )
            total = len(transactions)

            # Apply pagination
            paginated_transactions = transactions[skip : skip + limit]
            return paginated_transactions, total

        # Get all transactions for the account with pagination
        transactions = await transaction_repo.get_by_account_ordered(
            account_id, order_by_desc=True, limit=limit
        )

        # Get total count for pagination
        all_transactions = await transaction_repo.get_by_account(account_id)
        total = len(all_transactions)

        return transactions, total

    async def update_transaction(
        self, transaction_id: int, transaction_data: TransactionUpdate
    ) -> Optional[TransactionHistory]:
        """
        Update a transaction and adjust account balance if amount changes.

        Args:
            transaction_id: ID of the transaction to update
            transaction_data: Transaction data for update

        Returns:
            Optional[TransactionHistory]: Updated transaction or None if not found
        """
        # Get repositories using BaseService pattern
        transaction_repo = await self._get_repository(TransactionHistoryRepository)

        # Get existing transaction with account
        transaction = await transaction_repo.get_with_account(transaction_id)
        if not transaction:
            return None

        # Calculate balance adjustment if amount or type changes
        old_impact = (
            transaction.amount
            if transaction.transaction_type == TransactionType.CREDIT
            else -transaction.amount
        )

        # Update transaction fields
        update_data = transaction_data.model_dump(exclude_unset=True)

        # Calculate new balance impact
        new_type = update_data.get("transaction_type", transaction.transaction_type)
        new_amount = update_data.get("amount", transaction.amount)

        new_impact = new_amount if new_type == TransactionType.CREDIT else -new_amount

        # Adjust account balance if impact changes
        if old_impact != new_impact:
            balance_adjustment = new_impact - old_impact
            new_balance = transaction.account.available_balance + balance_adjustment

            # Update account balance
            account_repo = await self._get_repository(AccountRepository)
            await account_repo.update(
                transaction.account.id, {"available_balance": new_balance}
            )

        # Update the transaction
        updated_transaction = await transaction_repo.update(transaction_id, update_data)
        return updated_transaction

    async def delete_transaction(self, transaction_id: int) -> bool:
        """
        Delete a transaction and reverse its impact on account balance.

        This method ensures that when a transaction is deleted, its effect
        on the account balance is properly reversed to maintain consistency.

        Args:
            transaction_id: ID of the transaction to delete

        Returns:
            bool: True if successful, False if transaction not found
        """
        # Get repositories using BaseService pattern
        transaction_repo = await self._get_repository(TransactionHistoryRepository)

        # Get transaction with account
        transaction = await transaction_repo.get_with_account(transaction_id)
        if not transaction:
            return False

        # Reverse the transaction's impact on account balance
        if transaction.transaction_type == TransactionType.CREDIT:
            adjustment = -transaction.amount
        else:  # DEBIT
            adjustment = transaction.amount

        # Update account balance
        account_repo = await self._get_repository(AccountRepository)
        new_balance = transaction.account.available_balance + adjustment
        await account_repo.update(
            transaction.account.id, {"available_balance": new_balance}
        )

        # Delete the transaction
        await transaction_repo.delete(transaction_id)
        return True
