from datetime import datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.accounts import Account
from src.models.balance_reconciliation import BalanceReconciliation
from src.schemas.balance_reconciliation import BalanceReconciliationCreate, BalanceReconciliationUpdate

class BalanceReconciliationService:
    """Service for handling balance reconciliation operations"""

    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_reconciliation(
        self, reconciliation_data: BalanceReconciliationCreate
    ) -> BalanceReconciliation:
        """Create a new balance reconciliation record and update account balance"""
        
        # Get the account
        account = await self.session.get(Account, reconciliation_data.account_id)
        if not account:
            raise ValueError(f"Account with id {reconciliation_data.account_id} not found")

        # Calculate adjustment amount
        adjustment_amount = reconciliation_data.new_balance - reconciliation_data.previous_balance

        # Create reconciliation record
        reconciliation = BalanceReconciliation(
            account_id=account.id,
            previous_balance=reconciliation_data.previous_balance,
            new_balance=reconciliation_data.new_balance,
            adjustment_amount=adjustment_amount,
            reason=reconciliation_data.reason,
            reconciliation_date=datetime.utcnow()
        )

        # Update account balance
        account.available_balance = reconciliation_data.new_balance

        # Save changes
        self.session.add(reconciliation)
        await self.session.commit()
        await self.session.refresh(reconciliation)

        return reconciliation

    async def get_reconciliation(self, reconciliation_id: int) -> Optional[BalanceReconciliation]:
        """Get a specific reconciliation record"""
        query = select(BalanceReconciliation).where(
            BalanceReconciliation.id == reconciliation_id
        ).options(selectinload(BalanceReconciliation.account))
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_account_reconciliations(
        self, account_id: int, limit: int = 100, offset: int = 0
    ) -> List[BalanceReconciliation]:
        """Get reconciliation history for an account"""
        query = select(BalanceReconciliation).where(
            BalanceReconciliation.account_id == account_id
        ).order_by(
            BalanceReconciliation.reconciliation_date.desc()
        ).limit(limit).offset(offset)
        
        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def update_reconciliation(
        self, reconciliation_id: int, update_data: BalanceReconciliationUpdate
    ) -> Optional[BalanceReconciliation]:
        """Update a reconciliation record (only reason can be updated)"""
        reconciliation = await self.get_reconciliation(reconciliation_id)
        if not reconciliation:
            return None

        # Update allowed fields
        if update_data.reason is not None:
            reconciliation.reason = update_data.reason
            reconciliation.updated_at = datetime.utcnow()

        await self.session.commit()
        await self.session.refresh(reconciliation)
        return reconciliation

    async def delete_reconciliation(self, reconciliation_id: int) -> bool:
        """Delete a reconciliation record"""
        reconciliation = await self.get_reconciliation(reconciliation_id)
        if not reconciliation:
            return False

        await self.session.delete(reconciliation)
        await self.session.commit()
        return True

    async def get_latest_reconciliation(self, account_id: int) -> Optional[BalanceReconciliation]:
        """Get the most recent reconciliation for an account"""
        query = select(BalanceReconciliation).where(
            BalanceReconciliation.account_id == account_id
        ).order_by(
            BalanceReconciliation.reconciliation_date.desc()
        ).limit(1)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
