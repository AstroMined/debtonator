from datetime import date
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..models.liabilities import Liability
from ..models.payments import Payment
from ..schemas.liabilities import LiabilityCreate, LiabilityUpdate

class LiabilityService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_liabilities(self, skip: int = 0, limit: int = 100) -> List[Liability]:
        stmt = (
            select(Liability)
            .options(joinedload(Liability.payments))
            .offset(skip)
            .limit(limit)
            .order_by(Liability.due_date.desc())
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def get_liability(self, liability_id: int) -> Optional[Liability]:
        stmt = (
            select(Liability)
            .options(joinedload(Liability.payments))
            .filter(Liability.id == liability_id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def get_liabilities_by_date_range(
        self, start_date: date, end_date: date
    ) -> List[Liability]:
        stmt = (
            select(Liability)
            .options(joinedload(Liability.payments))
            .filter(Liability.due_date.between(start_date, end_date))
            .order_by(Liability.due_date.desc())
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def get_unpaid_liabilities(self) -> List[Liability]:
        stmt = (
            select(Liability)
            .options(joinedload(Liability.payments))
            .filter(~Liability.payments.any())  # No associated payments
            .order_by(Liability.due_date.desc())
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def create_liability(self, liability_create: LiabilityCreate) -> Liability:
        db_liability = Liability(
            name=liability_create.name,
            amount=liability_create.amount,
            due_date=liability_create.due_date,
            description=liability_create.description,
            category=liability_create.category,
            recurring=liability_create.recurring,
            recurrence_pattern=liability_create.recurrence_pattern
        )
        
        self.db.add(db_liability)
        await self.db.commit()
        await self.db.refresh(db_liability)
        
        return db_liability

    async def update_liability(
        self, liability_id: int, liability_update: LiabilityUpdate
    ) -> Optional[Liability]:
        db_liability = await self.get_liability(liability_id)
        if not db_liability:
            return None

        # Update fields
        update_data = liability_update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(db_liability, key, value)

        await self.db.commit()
        await self.db.refresh(db_liability)
        return db_liability

    async def delete_liability(self, liability_id: int) -> bool:
        db_liability = await self.get_liability(liability_id)
        if not db_liability:
            return False
        
        # The cascade will handle deleting associated payments and payment sources
        await self.db.delete(db_liability)
        await self.db.commit()
        return True

    async def is_paid(self, liability_id: int) -> bool:
        """Check if a liability has any associated payments"""
        stmt = (
            select(Payment)
            .filter(Payment.bill_id == liability_id)
        )
        result = await self.db.execute(stmt)
        return result.first() is not None
