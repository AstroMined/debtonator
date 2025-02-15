from datetime import date
from typing import List, Optional, Tuple
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from src.models.deposit_schedules import DepositSchedule
from src.models.income import Income
from src.models.accounts import Account
from src.schemas.deposit_schedules import DepositScheduleCreate, DepositScheduleUpdate

class DepositScheduleService:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def create_deposit_schedule(
        self, schedule: DepositScheduleCreate
    ) -> Tuple[bool, Optional[str], Optional[DepositSchedule]]:
        """Create a new deposit schedule"""
        try:
            # Verify income exists
            income = await self.session.get(Income, schedule.income_id)
            if not income:
                return False, "Income not found", None

            # Verify account exists
            account = await self.session.get(Account, schedule.account_id)
            if not account:
                return False, "Account not found", None

            # Verify amount doesn't exceed income amount
            if schedule.amount > income.amount:
                return False, "Schedule amount cannot exceed income amount", None

            # Create deposit schedule
            db_schedule = DepositSchedule(
                income_id=schedule.income_id,
                account_id=schedule.account_id,
                schedule_date=schedule.schedule_date,
                amount=schedule.amount,
                recurring=schedule.recurring,
                recurrence_pattern=schedule.recurrence_pattern,
                status=schedule.status
            )
            self.session.add(db_schedule)
            await self.session.commit()
            await self.session.refresh(db_schedule)
            return True, None, db_schedule
        except Exception as e:
            await self.session.rollback()
            return False, str(e), None

    async def get_deposit_schedule(self, schedule_id: int) -> Optional[DepositSchedule]:
        """Get a deposit schedule by ID"""
        query = select(DepositSchedule).where(DepositSchedule.id == schedule_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_deposit_schedule(
        self, schedule_id: int, schedule_update: DepositScheduleUpdate
    ) -> Tuple[bool, Optional[str], Optional[DepositSchedule]]:
        """Update a deposit schedule"""
        try:
            db_schedule = await self.get_deposit_schedule(schedule_id)
            if not db_schedule:
                return False, "Deposit schedule not found", None

            # Update fields if provided
            for field, value in schedule_update.model_dump(exclude_unset=True).items():
                setattr(db_schedule, field, value)

            # If amount is updated, verify it doesn't exceed income amount
            if schedule_update.amount is not None:
                income = await self.session.get(Income, db_schedule.income_id)
                if schedule_update.amount > income.amount:
                    return False, "Schedule amount cannot exceed income amount", None

            await self.session.commit()
            await self.session.refresh(db_schedule)
            return True, None, db_schedule
        except Exception as e:
            await self.session.rollback()
            return False, str(e), None

    async def delete_deposit_schedule(self, schedule_id: int) -> Tuple[bool, Optional[str]]:
        """Delete a deposit schedule"""
        try:
            db_schedule = await self.get_deposit_schedule(schedule_id)
            if not db_schedule:
                return False, "Deposit schedule not found"

            await self.session.delete(db_schedule)
            await self.session.commit()
            return True, None
        except Exception as e:
            await self.session.rollback()
            return False, str(e)

    async def list_deposit_schedules(
        self,
        income_id: Optional[int] = None,
        account_id: Optional[int] = None,
        status: Optional[str] = None,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None
    ) -> List[DepositSchedule]:
        """List deposit schedules with optional filters"""
        query = select(DepositSchedule)

        if income_id is not None:
            query = query.where(DepositSchedule.income_id == income_id)
        if account_id is not None:
            query = query.where(DepositSchedule.account_id == account_id)
        if status is not None:
            query = query.where(DepositSchedule.status == status)
        if from_date is not None:
            query = query.where(DepositSchedule.schedule_date >= from_date)
        if to_date is not None:
            query = query.where(DepositSchedule.schedule_date <= to_date)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_pending_deposits(
        self, account_id: Optional[int] = None
    ) -> List[DepositSchedule]:
        """Get all pending deposits, optionally filtered by account"""
        query = select(DepositSchedule).where(DepositSchedule.status == "pending")
        
        if account_id is not None:
            query = query.where(DepositSchedule.account_id == account_id)
            
        query = query.order_by(DepositSchedule.schedule_date)
        result = await self.session.execute(query)
        return list(result.scalars().all())
