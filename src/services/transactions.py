from datetime import datetime
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from src.models.transaction_history import TransactionHistory, TransactionType
from src.repositories.accounts import AccountRepository
from src.repositories.factory import RepositoryFactory
from src.repositories.transaction_history import TransactionHistoryRepository
from src.schemas.transaction_history import (
    TransactionHistoryCreate as TransactionCreate,
)
from src.schemas.transaction_history import (
    TransactionHistoryUpdate as TransactionUpdate,
)


class TransactionService:
    """Service for handling transaction operations"""

    def __init__(self, session: AsyncSession):
        self.session = session
        self._transaction_repo = None
        self._account_repo = None

    @property
    async def transaction_repo(self) -> TransactionHistoryRepository:
        """
        Get the transaction history repository instance.
        
        Returns:
            TransactionHistoryRepository: Transaction history repository
        """
        if self._transaction_repo is None:
            self._transaction_repo = await RepositoryFactory.create_transaction_history_repository(
                self.session
            )
        return self._transaction_repo

    @property
    async def account_repo(self) -> AccountRepository:
        """
        Get the account repository instance.
        
        Returns:
            AccountRepository: Account repository
        """
        if self._account_repo is None:
            self._account_repo = await RepositoryFactory.create_account_repository(
                self.session
            )
        return self._account_repo

    async def create_transaction(
        self, account_id: int, transaction_data: TransactionCreate
    ) -> TransactionHistory:
        """Create a new transaction and update account balance"""
        # Get the account using repository
        account_repo = await self.account_repo
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
        await account_repo.update(account_id, {"available_balance": account.available_balance})

        # Create transaction using repository
        transaction_repo = await self.transaction_repo
        transaction = await transaction_repo.create(transaction_dict)

        return transaction

    async def get_transaction(
        self, transaction_id: int
    ) -> Optional[TransactionHistory]:
        """Get a transaction by ID"""
        transaction_repo = await self.transaction_repo
        return await transaction_repo.get_with_account(transaction_id)

    async def get_account_transactions(
        self,
        account_id: int,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> tuple[List[TransactionHistory], int]:
        """Get transactions for an account with optional date filtering"""
        transaction_repo = await self.transaction_repo
        
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
        # We're using the repository directly since it has the count functionality
        all_transactions = await transaction_repo.get_by_account(account_id)
        total = len(all_transactions)
        
        return transactions, total

    async def update_transaction(
        self, transaction_id: int, transaction_data: TransactionUpdate
    ) -> Optional[TransactionHistory]:
        """Update a transaction and adjust account balance if amount changes"""
        # Get existing transaction with account
        transaction_repo = await self.transaction_repo
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
        
        new_impact = (
            new_amount
            if new_type == TransactionType.CREDIT
            else -new_amount
        )

        # Adjust account balance if impact changes
        if old_impact != new_impact:
            balance_adjustment = new_impact - old_impact
            new_balance = transaction.account.available_balance + balance_adjustment
            
            # Update account balance
            account_repo = await self.account_repo
            await account_repo.update(
                transaction.account.id, {"available_balance": new_balance}
            )

        # Update the transaction
        updated_transaction = await transaction_repo.update(transaction_id, update_data)
        return updated_transaction

    async def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction and reverse its impact on account balance"""
        # Get transaction with account
        transaction_repo = await self.transaction_repo
        transaction = await transaction_repo.get_with_account(transaction_id)
        if not transaction:
            return False

        # Reverse the transaction's impact on account balance
        if transaction.transaction_type == TransactionType.CREDIT:
            adjustment = -transaction.amount
        else:  # DEBIT
            adjustment = transaction.amount
        
        # Update account balance
        account_repo = await self.account_repo
        new_balance = transaction.account.available_balance + adjustment
        await account_repo.update(
            transaction.account.id, {"available_balance": new_balance}
        )

        # Delete the transaction
        await transaction_repo.delete(transaction_id)
        return True
