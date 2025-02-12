from datetime import date
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..models.recurring_bills import RecurringBill
from ..models.liabilities import Liability
from ..schemas.recurring_bills import RecurringBillCreate, RecurringBillUpdate

class RecurringBillService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_recurring_bills(
        self, skip: int = 0, limit: int = 100, active_only: bool = True
    ) -> List[RecurringBill]:
        """Get all recurring bills"""
        stmt = (
            select(RecurringBill)
            .options(
                joinedload(RecurringBill.account),
                joinedload(RecurringBill.liabilities)
            )
        )
        
        if active_only:
            stmt = stmt.filter(RecurringBill.active == True)
            
        stmt = stmt.offset(skip).limit(limit).order_by(RecurringBill.bill_name)
        
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def get_recurring_bill(self, recurring_bill_id: int) -> Optional[RecurringBill]:
        """Get a specific recurring bill by ID"""
        stmt = (
            select(RecurringBill)
            .options(
                joinedload(RecurringBill.account),
                joinedload(RecurringBill.liabilities)
            )
            .filter(RecurringBill.id == recurring_bill_id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def create_recurring_bill(
        self, recurring_bill_create: RecurringBillCreate
    ) -> RecurringBill:
        """Create a new recurring bill"""
        db_recurring_bill = RecurringBill(
            bill_name=recurring_bill_create.bill_name,
            amount=recurring_bill_create.amount,
            day_of_month=recurring_bill_create.day_of_month,
            account_id=recurring_bill_create.account_id,
            auto_pay=recurring_bill_create.auto_pay
        )
        
        self.db.add(db_recurring_bill)
        await self.db.commit()
        await self.db.refresh(db_recurring_bill)
        
        return db_recurring_bill

    async def update_recurring_bill(
        self, recurring_bill_id: int, recurring_bill_update: RecurringBillUpdate
    ) -> Optional[RecurringBill]:
        """Update a recurring bill"""
        db_recurring_bill = await self.get_recurring_bill(recurring_bill_id)
        if not db_recurring_bill:
            return None

        update_data = recurring_bill_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_recurring_bill, key, value)

        await self.db.commit()
        await self.db.refresh(db_recurring_bill)
        
        return db_recurring_bill

    async def delete_recurring_bill(self, recurring_bill_id: int) -> bool:
        """Delete a recurring bill and its generated liabilities"""
        db_recurring_bill = await self.get_recurring_bill(recurring_bill_id)
        if not db_recurring_bill:
            return False

        await self.db.delete(db_recurring_bill)
        await self.db.commit()
        return True

    async def generate_bills(
        self, recurring_bill_id: int, month: int, year: int
    ) -> List[Liability]:
        """Generate liabilities for a recurring bill pattern"""
        db_recurring_bill = await self.get_recurring_bill(recurring_bill_id)
        if not db_recurring_bill or not db_recurring_bill.active:
            return []

        # Check if bills already exist for this month/year
        stmt = (
            select(Liability)
            .filter(
                Liability.recurring_bill_id == recurring_bill_id,
                Liability.due_date == date(year, month, db_recurring_bill.day_of_month)
            )
        )
        result = await self.db.execute(stmt)
        if result.first():
            return []  # Bills already exist for this period

        # Create new liability
        liability = db_recurring_bill.create_liability(str(month), year)
        self.db.add(liability)
        await self.db.commit()
        await self.db.refresh(liability)

        return [liability]

    async def generate_bills_for_month(
        self, month: int, year: int, active_only: bool = True
    ) -> List[Liability]:
        """Generate liabilities for all recurring bills for a specific month"""
        recurring_bills = await self.get_recurring_bills(active_only=active_only)
        generated_bills = []

        for recurring_bill in recurring_bills:
            bills = await self.generate_bills(recurring_bill.id, month, year)
            generated_bills.extend(bills)

        return generated_bills
