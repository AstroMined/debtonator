from decimal import Decimal
from datetime import date
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.liabilities import Liability
from src.models.bill_splits import BillSplit
from src.schemas.bill_splits import BillSplitCreate, BillSplitUpdate

class BillSplitService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def get_bill_splits(self, liability_id: int) -> List[BillSplit]:
        """Get all splits for a specific liability."""
        result = await self.db.execute(
            select(BillSplit).where(BillSplit.liability_id == liability_id)
        )
        return result.scalars().all()

    async def get_account_splits(self, account_id: int) -> List[BillSplit]:
        """Get all splits for a specific account."""
        result = await self.db.execute(
            select(BillSplit).where(BillSplit.account_id == account_id)
        )
        return result.scalars().all()

    async def create_split(self, liability_id: int, account_id: int, amount: Decimal) -> BillSplit:
        """Create a new bill split (internal use)."""
        split = BillSplit(
            liability_id=liability_id,
            account_id=account_id,
            amount=amount,
            created_at=date.today(),
            updated_at=date.today()
        )
        self.db.add(split)
        await self.db.flush()
        return split

    async def create_bill_split(self, split: BillSplitCreate) -> BillSplit:
        """Create a new bill split (API use)."""
        # Verify liability exists
        liability_result = await self.db.execute(
            select(Liability).where(Liability.id == split.liability_id)
        )
        if not liability_result.scalar_one_or_none():
            raise ValueError(f"Liability with id {split.liability_id} not found")

        return await self.create_split(
            liability_id=split.liability_id,
            account_id=split.account_id,
            amount=split.amount
        )

    async def update_bill_split(self, split_id: int, split: BillSplitUpdate) -> Optional[BillSplit]:
        """Update an existing bill split."""
        result = await self.db.execute(
            select(BillSplit).where(BillSplit.id == split_id)
        )
        db_split = result.scalar_one_or_none()
        if not db_split:
            return None

        if split.amount is not None:
            db_split.amount = split.amount
        db_split.updated_at = date.today()
        
        await self.db.flush()
        return db_split

    async def delete_bill_split(self, split_id: int) -> bool:
        """Delete a specific bill split. Returns True if successful."""
        result = await self.db.execute(
            delete(BillSplit).where(BillSplit.id == split_id)
        )
        return result.rowcount > 0

    async def delete_bill_splits(self, liability_id: int) -> None:
        """Delete all splits for a liability."""
        await self.db.execute(
            delete(BillSplit).where(BillSplit.liability_id == liability_id)
        )
        await self.db.commit()

async def calculate_split_totals(db: AsyncSession, liability_id: int) -> Decimal:
    """Calculate the total amount of all splits for a given liability."""
    result = await db.execute(
        select(BillSplit).where(BillSplit.liability_id == liability_id)
    )
    splits = result.scalars().all()
    return sum(split.amount for split in splits)

async def validate_bill_splits(db: AsyncSession, liability_id: int) -> bool:
    """
    Validate that the sum of all splits equals the liability amount.
    Returns True if valid, False otherwise.
    """
    # Get the liability
    result = await db.execute(
        select(Liability).where(Liability.id == liability_id)
    )
    liability = result.scalar_one()
    
    # Calculate total of splits
    total_splits = await calculate_split_totals(db, liability_id)
    
    # Compare with liability amount
    return total_splits == liability.amount
