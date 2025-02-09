from decimal import Decimal
from datetime import date
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.bills import Bill
from src.models.bill_splits import BillSplit

class BillSplitService:
    def __init__(self, db: AsyncSession):
        self.db = db
    
    async def create_split(self, bill_id: int, account_id: int, amount: Decimal) -> BillSplit:
        """Create a new bill split."""
        split = BillSplit(
            bill_id=bill_id,
            account_id=account_id,
            amount=amount,
            created_at=date.today(),
            updated_at=date.today()
        )
        self.db.add(split)
        await self.db.flush()
        return split
    
    async def validate_splits(self, bill_id: int) -> bool:
        """Validate that the sum of all splits equals the bill amount."""
        return await validate_bill_splits(self.db, bill_id)
    
    async def get_total_splits(self, bill_id: int) -> Decimal:
        """Get the total amount of all splits for a bill."""
        return await calculate_split_totals(self.db, bill_id)

    async def delete_bill_splits(self, bill_id: int) -> None:
        """Delete all splits for a bill."""
        from sqlalchemy import delete
        await self.db.execute(
            delete(BillSplit).where(BillSplit.bill_id == bill_id)
        )
        await self.db.commit()

async def calculate_split_totals(db: AsyncSession, bill_id: int) -> Decimal:
    """Calculate the total amount of all splits for a given bill."""
    result = await db.execute(
        select(BillSplit).where(BillSplit.bill_id == bill_id)
    )
    splits = result.scalars().all()
    return sum(split.amount for split in splits)

async def validate_bill_splits(db: AsyncSession, bill_id: int) -> bool:
    """
    Validate that the sum of all splits equals the bill amount.
    Returns True if valid, False otherwise.
    """
    # Get the bill
    result = await db.execute(
        select(Bill).where(Bill.id == bill_id)
    )
    bill = result.scalar_one()
    
    # Calculate total of splits
    total_splits = await calculate_split_totals(db, bill_id)
    
    # Compare with bill amount
    return total_splits == bill.amount
