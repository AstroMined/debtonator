from decimal import Decimal
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.bill_splits import BillSplit
from ..models.accounts import Account
from ..schemas.bill_splits import BillSplitCreate, BillSplitUpdate

class BillSplitService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_bill_split(self, split_data: BillSplitCreate) -> BillSplit:
        """Create a new bill split"""
        split = BillSplit(
            bill_id=split_data.bill_id,
            account_id=split_data.account_id,
            amount=split_data.amount
        )
        self.session.add(split)
        await self.session.flush()
        return split

    async def get_bill_splits(self, bill_id: int) -> List[BillSplit]:
        """Get all splits for a specific bill"""
        result = await self.session.execute(
            select(BillSplit).where(BillSplit.bill_id == bill_id)
        )
        return list(result.scalars().all())

    async def get_account_splits(self, account_id: int) -> List[BillSplit]:
        """Get all splits for a specific account"""
        result = await self.session.execute(
            select(BillSplit).where(BillSplit.account_id == account_id)
        )
        return list(result.scalars().all())

    async def update_bill_split(
        self, split_id: int, split_data: BillSplitUpdate
    ) -> Optional[BillSplit]:
        """Update an existing bill split"""
        result = await self.session.execute(
            select(BillSplit).where(BillSplit.id == split_id)
        )
        split = result.scalar_one_or_none()
        
        if split:
            split.amount = split_data.amount
            await self.session.flush()
        
        return split

    async def delete_bill_split(self, split_id: int) -> bool:
        """Delete a bill split"""
        result = await self.session.execute(
            select(BillSplit).where(BillSplit.id == split_id)
        )
        split = result.scalar_one_or_none()
        
        if split:
            await self.session.delete(split)
            await self.session.flush()
            return True
        
        return False

    async def delete_bill_splits(self, bill_id: int) -> bool:
        """Delete all splits for a specific bill"""
        result = await self.session.execute(
            select(BillSplit).where(BillSplit.bill_id == bill_id)
        )
        splits = result.scalars().all()
        
        for split in splits:
            await self.session.delete(split)
        
        await self.session.flush()
        return True

    async def validate_split_total(self, bill_id: int, total_amount: Decimal) -> bool:
        """Validate that the sum of splits equals the total bill amount"""
        splits = await self.get_bill_splits(bill_id)
        split_sum = sum(split.amount for split in splits)
        return split_sum == total_amount
