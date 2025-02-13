from datetime import date, datetime
from typing import List, Optional, Dict
from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..models.liabilities import Liability
from ..models.payments import Payment
from ..schemas.liabilities import (
    LiabilityCreate, 
    LiabilityUpdate, 
    AutoPayUpdate,
    AutoPaySettings
)

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
            category_id=liability_create.category_id,
            recurring=liability_create.recurring,
            recurrence_pattern=liability_create.recurrence_pattern,
            primary_account_id=liability_create.primary_account_id
        )
        
        self.db.add(db_liability)
        await self.db.commit()

        # Fetch fresh copy with relationships
        stmt = (
            select(Liability)
            .options(joinedload(Liability.payments))
            .filter(Liability.id == db_liability.id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one()

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

        # Fetch fresh copy with relationships
        stmt = (
            select(Liability)
            .options(joinedload(Liability.payments))
            .filter(Liability.id == liability_id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one()

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
            .options(
                joinedload(Payment.sources),
                joinedload(Payment.liability)
            )
            .filter(Payment.liability_id == liability_id)
        )
        result = await self.db.execute(stmt)
        return result.unique().first() is not None

    async def update_auto_pay(self, liability_id: int, auto_pay_update: AutoPayUpdate) -> Optional[Liability]:
        """Update auto-pay settings for a liability"""
        db_liability = await self.get_liability(liability_id)
        if not db_liability:
            return None

        # Update auto-pay state
        db_liability.auto_pay = True
        db_liability.auto_pay_enabled = auto_pay_update.enabled
        
        if auto_pay_update.settings:
            # FastAPI will handle validation before this point
            settings_dict = auto_pay_update.settings.model_dump(mode='json', exclude_none=True)
            db_liability.auto_pay_settings = settings_dict
        elif not auto_pay_update.enabled:
            # Clear settings when disabling auto-pay
            db_liability.auto_pay_settings = None

        await self.db.commit()
        await self.db.refresh(db_liability)  # Ensure we have latest data
        return db_liability

    async def get_auto_pay_candidates(self, days_ahead: int = 7) -> List[Liability]:
        """Get liabilities that are candidates for auto-pay processing"""
        from datetime import timedelta
        end_date = date.today() + timedelta(days=days_ahead)
        
        stmt = (
            select(Liability)
            .options(joinedload(Liability.payments))
            .filter(
                and_(
                    Liability.auto_pay == True,
                    Liability.auto_pay_enabled == True,
                    Liability.paid == False,
                    Liability.due_date <= end_date
                )
            )
            .order_by(Liability.due_date.asc())
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def process_auto_pay(self, liability_id: int) -> bool:
        """Process auto-pay for a specific liability"""
        db_liability = await self.get_liability(liability_id)
        if not db_liability or not db_liability.auto_pay_enabled:
            return False

        try:
            # Update last attempt timestamp
            db_liability.last_auto_pay_attempt = datetime.utcnow()
            
            # TODO: Implement actual payment processing logic here
            # This would involve:
            # 1. Checking account balances
            # 2. Creating payment record
            # 3. Processing payment through payment service
            # 4. Updating liability status
            
            await self.db.commit()
            return True
        except Exception:
            await self.db.rollback()
            return False

    async def disable_auto_pay(self, liability_id: int) -> Optional[Liability]:
        """Disable auto-pay for a liability"""
        db_liability = await self.get_liability(liability_id)
        if not db_liability:
            return None

        db_liability.auto_pay = False
        db_liability.auto_pay_enabled = False
        db_liability.auto_pay_settings = None
        
        await self.db.commit()
        await self.db.refresh(db_liability)  # Ensure we have latest data
        return db_liability

    async def get_auto_pay_status(self, liability_id: int) -> Optional[Dict]:
        """Get auto-pay status and settings for a liability"""
        db_liability = await self.get_liability(liability_id)
        if not db_liability:
            return None

        return {
            "auto_pay": db_liability.auto_pay,
            "enabled": db_liability.auto_pay_enabled,
            "settings": db_liability.auto_pay_settings,
            "last_attempt": db_liability.last_auto_pay_attempt
        }
