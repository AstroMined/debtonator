from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.bills import Bill
from ..models.accounts import Account
from ..schemas.bills import BillCreate, BillUpdate
from .bill_splits import BillSplitService
from ..schemas.bill_splits import BillSplitCreate

class BillService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.split_service = BillSplitService(db)

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
        
        # Get account name for denormalized field
        account_result = await self.db.execute(
            select(Account).filter(Account.id == bill_create.account_id)
        )
        account = account_result.scalar_one()
        
        # Create bill instance
        db_bill = Bill(
            month=bill_create.month,
            day_of_month=bill_create.day_of_month,
            due_date=due_date,
            bill_name=bill_create.bill_name,
            amount=bill_create.amount,
            account_id=bill_create.account_id,
            account_name=account.name,  # Denormalized field
            auto_pay=bill_create.auto_pay,
            up_to_date=True,  # New bills are up to date by default
            paid=False
        )
        
        self.db.add(db_bill)
        await self.db.flush()  # Get the bill ID without committing

        # Handle bill splits if provided
        if bill_create.splits:
            total_split_amount = Decimal('0')
            for split_input in bill_create.splits:
                split_create = BillSplitCreate(
                    bill_id=db_bill.id,
                    account_id=split_input.account_id,
                    amount=split_input.amount
                )
                await self.split_service.create_bill_split(split_create)
                total_split_amount += split_input.amount

            # Calculate primary account amount (total - splits)
            primary_amount = bill_create.amount - total_split_amount
            
            # Create split for primary account
            primary_split = BillSplitCreate(
                bill_id=db_bill.id,
                account_id=bill_create.account_id,
                amount=primary_amount
            )
            await self.split_service.create_bill_split(primary_split)

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
        
        # If account_id is being updated, update account_name
        if "account_id" in update_data:
            account_result = await self.db.execute(
                select(Account).filter(Account.id == update_data["account_id"])
            )
            account = account_result.scalar_one()
            update_data["account_name"] = account.name

        # Handle bill splits update
        if "splits" in update_data:
            # Delete existing splits
            await self.split_service.delete_bill_splits(bill_id)
            
            # Create new splits if provided
            splits = update_data.pop("splits")  # Remove splits from update_data
            if splits:
                total_split_amount = Decimal('0')
                for split_input in splits:
                    split_create = BillSplitCreate(
                        bill_id=bill_id,
                        account_id=split_input.account_id,
                        amount=split_input.amount
                    )
                    await self.split_service.create_bill_split(split_create)
                    total_split_amount += split_input.amount

                # Calculate primary account amount (total - splits)
                bill_amount = update_data.get("amount", db_bill.amount)
                primary_amount = bill_amount - total_split_amount
                
                # Create split for primary account
                primary_split = BillSplitCreate(
                    bill_id=bill_id,
                    account_id=update_data.get("account_id", db_bill.account_id),
                    amount=primary_amount
                )
                await self.split_service.create_bill_split(primary_split)

        # Update bill fields
        for key, value in update_data.items():
            setattr(db_bill, key, value)

        await self.db.commit()
        await self.db.refresh(db_bill)
        return db_bill

    async def delete_bill(self, bill_id: int) -> bool:
        db_bill = await self.get_bill(bill_id)
        if not db_bill:
            return False
        
        # Delete associated splits first
        await self.split_service.delete_bill_splits(bill_id)
            
        # Then delete the bill
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
