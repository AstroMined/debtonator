from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.bills import Bill
from src.schemas.bills import BillCreate, BillUpdate

class BillService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_bills(self, skip: int = 0, limit: int = 100) -> List[Bill]:
        result = await self.db.execute(select(Bill).offset(skip).limit(limit))
        return result.scalars().all()

    async def get_bill(self, bill_id: int) -> Optional[Bill]:
        result = await self.db.execute(select(Bill).filter(Bill.id == bill_id))
        return result.scalar_one_or_none()

    async def get_bills_by_date_range(self, start_date: date, end_date: date) -> List[Bill]:
        result = await self.db.execute(
            select(Bill).filter(Bill.due_date.between(start_date, end_date))
        )
        return result.scalars().all()

    async def get_unpaid_bills(self) -> List[Bill]:
        result = await self.db.execute(select(Bill).filter(Bill.paid == False))
        return result.scalars().all()

    async def create_bill(self, bill_create: BillCreate) -> Bill:
        # Calculate due date
        due_date = datetime.strptime(f"{bill_create.month}/{bill_create.day_of_month}/2025", "%m/%d/%Y").date()
        
        # Create bill instance
        db_bill = Bill(
            month=bill_create.month,
            day_of_month=bill_create.day_of_month,
            due_date=due_date,
            bill_name=bill_create.bill_name,
            amount=bill_create.amount,
            account=bill_create.account,
            auto_pay=bill_create.auto_pay,
            up_to_date=True,  # New bills are up to date by default
            paid=False
        )
        
        # Set account-specific amounts
        if bill_create.account == "AMEX":
            db_bill.amex_amount = bill_create.amount
        elif bill_create.account == "UNLIMITED":
            db_bill.unlimited_amount = bill_create.amount
        elif bill_create.account == "UFCU":
            db_bill.ufcu_amount = bill_create.amount

        self.db.add(db_bill)
        await self.db.commit()
        await self.db.refresh(db_bill)
        return db_bill

    async def update_bill(self, bill_id: int, bill_update: BillUpdate) -> Optional[Bill]:
        db_bill = await self.get_bill(bill_id)
        if not db_bill:
            return None

        update_data = bill_update.model_dump(exclude_unset=True)
        
        # If paid status is being updated to True, set paid_date
        if update_data.get("paid") is True and not db_bill.paid:
            update_data["paid_date"] = date.today()
        
        # Update account-specific amounts if account or amount changes
        if "amount" in update_data or "account" in update_data:
            new_amount = update_data.get("amount", db_bill.amount)
            new_account = update_data.get("account", db_bill.account)
            
            # Reset all account amounts
            update_data["amex_amount"] = None
            update_data["unlimited_amount"] = None
            update_data["ufcu_amount"] = None
            
            # Set new account amount
            if new_account == "AMEX":
                update_data["amex_amount"] = new_amount
            elif new_account == "UNLIMITED":
                update_data["unlimited_amount"] = new_amount
            elif new_account == "UFCU":
                update_data["ufcu_amount"] = new_amount

        for key, value in update_data.items():
            setattr(db_bill, key, value)

        await self.db.commit()
        await self.db.refresh(db_bill)
        return db_bill

    async def delete_bill(self, bill_id: int) -> bool:
        db_bill = await self.get_bill(bill_id)
        if not db_bill:
            return False
            
        await self.db.delete(db_bill)
        await self.db.commit()
        return True

    async def mark_bill_paid(self, bill_id: int) -> Optional[Bill]:
        db_bill = await self.get_bill(bill_id)
        if not db_bill:
            return None
            
        db_bill.paid = True
        db_bill.paid_date = date.today()
        
        await self.db.commit()
        await self.db.refresh(db_bill)
        return db_bill
