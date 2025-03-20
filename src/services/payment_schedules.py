from datetime import date, datetime
from decimal import Decimal
from typing import List, Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models.accounts import Account
from src.models.liabilities import Liability
from src.models.payment_schedules import PaymentSchedule
from src.schemas.payment_schedules import PaymentScheduleCreate
from src.schemas.payments import PaymentCreate, PaymentSourceCreate
from src.services.payments import PaymentService


class PaymentScheduleService:
    def __init__(self, session: AsyncSession):
        self.session = session
        self.payment_service = PaymentService(session)

    async def create_schedule(
        self, schedule_data: PaymentScheduleCreate
    ) -> PaymentSchedule:
        """Create a new payment schedule"""
        # Verify liability exists and is not paid
        liability = await self.session.get(Liability, schedule_data.liability_id)
        if not liability:
            raise ValueError("Liability not found")
        if liability.paid:
            raise ValueError("Cannot schedule payment for already paid liability")

        # Verify account exists
        account = await self.session.get(Account, schedule_data.account_id)
        if not account:
            raise ValueError("Account not found")

        # Create schedule
        schedule = PaymentSchedule(
            liability_id=schedule_data.liability_id,
            account_id=schedule_data.account_id,
            scheduled_date=schedule_data.scheduled_date,
            amount=Decimal(str(schedule_data.amount)),
            description=schedule_data.description,
            auto_process=schedule_data.auto_process,
        )

        self.session.add(schedule)
        await self.session.commit()
        await self.session.refresh(schedule)
        return schedule

    async def get_schedule(self, schedule_id: int) -> Optional[PaymentSchedule]:
        """Get a payment schedule by ID"""
        query = select(PaymentSchedule).where(PaymentSchedule.id == schedule_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def get_schedules_by_date_range(
        self, start_date: date, end_date: date, include_processed: bool = False
    ) -> List[PaymentSchedule]:
        """Get payment schedules within a date range"""
        query = select(PaymentSchedule).where(
            PaymentSchedule.scheduled_date.between(start_date, end_date)
        )

        if not include_processed:
            query = query.where(PaymentSchedule.processed == False)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def get_schedules_by_liability(
        self, liability_id: int, include_processed: bool = False
    ) -> List[PaymentSchedule]:
        """Get payment schedules for a specific liability"""
        query = select(PaymentSchedule).where(
            PaymentSchedule.liability_id == liability_id
        )

        if not include_processed:
            query = query.where(PaymentSchedule.processed == False)

        result = await self.session.execute(query)
        return list(result.scalars().all())

    async def process_schedule(self, schedule_id: int) -> PaymentSchedule:
        """Process a payment schedule, creating the actual payment"""
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            raise ValueError("Schedule not found")

        if schedule.processed:
            raise ValueError("Schedule already processed")

        # Create the payment using PaymentCreate schema
        payment_data = PaymentCreate(
            liability_id=schedule.liability_id,
            amount=schedule.amount,
            payment_date=schedule.scheduled_date,
            description=schedule.description or "Scheduled payment",
            category="Scheduled Payment",  # Default category for scheduled payments
            sources=[
                PaymentSourceCreate(
                    account_id=schedule.account_id, amount=schedule.amount
                )
            ],
        )
        await self.payment_service.create_payment(payment_data)

        # Mark schedule as processed
        schedule.processed = True
        schedule.processed_date = datetime.utcnow()
        await self.session.commit()
        await self.session.refresh(schedule)

        return schedule

    async def delete_schedule(self, schedule_id: int) -> bool:
        """Delete a payment schedule"""
        schedule = await self.get_schedule(schedule_id)
        if not schedule:
            return False

        if schedule.processed:
            raise ValueError("Cannot delete processed schedule")

        await self.session.delete(schedule)
        await self.session.commit()
        return True

    async def process_due_schedules(self) -> List[PaymentSchedule]:
        """Process all auto-process schedules that are due"""
        today = date.today()
        due_schedules = await self.get_schedules_by_date_range(
            start_date=today, end_date=today, include_processed=False
        )

        processed_schedules = []
        for schedule in due_schedules:
            if schedule.auto_process:
                try:
                    processed_schedule = await self.process_schedule(schedule.id)
                    processed_schedules.append(processed_schedule)
                except Exception as e:
                    # Log error but continue processing other schedules
                    print(f"Error processing schedule {schedule.id}: {str(e)}")

        return processed_schedules
