from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.transaction_history import TransactionHistory, TransactionType
from src.models.accounts import Account
from src.schemas.transactions import TransactionCreate, TransactionUpdate

class TransactionService:
    """Service for handling transaction operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_transaction(
        self, account_id: int, transaction_data: TransactionCreate
    ) -> TransactionHistory:
        """Create a new transaction and update account balance"""
        # Get the account
        account = await self.session.get(Account, account_id)
        if not account:
            raise ValueError(f"Account with id {account_id} not found")

        # Create transaction
        transaction = TransactionHistory(
            account_id=account_id,
            amount=transaction_data.amount,
            transaction_type=transaction_data.transaction_type,
            description=transaction_data.description,
            transaction_date=transaction_data.transaction_date
        )

        # Update account balance based on transaction type
        if transaction_data.transaction_type == TransactionType.CREDIT:
            account.available_balance += transaction_data.amount
        else:  # DEBIT
            account.available_balance -= transaction_data.amount

        # Save transaction and updated account
        self.session.add(transaction)
        await self.session.commit()
        await self.session.refresh(transaction)

        return transaction

    async def get_transaction(self, transaction_id: int) -> Optional[TransactionHistory]:
        """Get a transaction by ID"""
        query = select(TransactionHistory).where(
            TransactionHistory.id == transaction_id
        ).options(selectinload(TransactionHistory.account))
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_account_transactions(
        self,
        account_id: int,
        skip: int = 0,
        limit: int = 100,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> tuple[List[TransactionHistory], int]:
        """Get transactions for an account with optional date filtering"""
        query = select(TransactionHistory).where(
            TransactionHistory.account_id == account_id
        )

        if start_date:
            query = query.where(TransactionHistory.transaction_date >= start_date)
        if end_date:
            query = query.where(TransactionHistory.transaction_date <= end_date)

        # Get total count
        count_query = select(func.count()).select_from(query.subquery())
        total = await self.session.scalar(count_query)

        # Get paginated results
        query = query.order_by(TransactionHistory.transaction_date.desc())
        query = query.offset(skip).limit(limit)
        result = await self.session.execute(query)
        
        return list(result.scalars().all()), total

    async def update_transaction(
        self,
        transaction_id: int,
        transaction_data: TransactionUpdate
    ) -> Optional[TransactionHistory]:
        """Update a transaction and adjust account balance if amount changes"""
        transaction = await self.get_transaction(transaction_id)
        if not transaction:
            return None

        # Calculate balance adjustment if amount or type changes
        old_impact = (
            transaction.amount 
            if transaction.transaction_type == TransactionType.CREDIT 
            else -transaction.amount
        )
        
        # Update transaction fields
        for field, value in transaction_data.model_dump(exclude_unset=True).items():
            setattr(transaction, field, value)

        # Calculate new balance impact
        new_impact = (
            transaction.amount 
            if transaction.transaction_type == TransactionType.CREDIT 
            else -transaction.amount
        )

        # Adjust account balance
        if old_impact != new_impact:
            balance_adjustment = new_impact - old_impact
            transaction.account.available_balance += balance_adjustment

        await self.session.commit()
        await self.session.refresh(transaction)
        return transaction

    async def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction and reverse its impact on account balance"""
        transaction = await self.get_transaction(transaction_id)
        if not transaction:
            return False

        # Reverse the transaction's impact on account balance
        if transaction.transaction_type == TransactionType.CREDIT:
            transaction.account.available_balance -= transaction.amount
        else:  # DEBIT
            transaction.account.available_balance += transaction.amount

        await self.session.delete(transaction)
        await self.session.commit()
        return True
