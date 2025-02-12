from datetime import date
from typing import List, Optional
from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from ..models.payments import Payment, PaymentSource
from ..models.accounts import Account
from ..schemas.payments import PaymentCreate, PaymentUpdate

class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_payments(self, skip: int = 0, limit: int = 100) -> List[Payment]:
        stmt = (
            select(Payment)
            .options(joinedload(Payment.sources))
            .offset(skip)
            .limit(limit)
            .order_by(Payment.payment_date.desc())
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def get_payment(self, payment_id: int) -> Optional[Payment]:
        stmt = (
            select(Payment)
            .options(joinedload(Payment.sources))
            .filter(Payment.id == payment_id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one_or_none()

    async def create_payment(self, payment_create: PaymentCreate) -> Payment:
        # Validate payment sources
        payment_create.validate_sources()
        
        # Validate accounts exist
        for source in payment_create.sources:
            account_result = await self.db.execute(
                select(Account).filter(Account.id == source.account_id)
            )
            if not account_result.scalar_one_or_none():
                raise ValueError(f"Account {source.account_id} not found")

        # Create payment
        db_payment = Payment(
            liability_id=payment_create.liability_id,
            income_id=payment_create.income_id,
            amount=payment_create.amount,
            payment_date=payment_create.payment_date,
            description=payment_create.description,
            category=payment_create.category
        )
        self.db.add(db_payment)
        await self.db.flush()

        # Create payment sources
        for source in payment_create.sources:
            db_source = PaymentSource(
                payment_id=db_payment.id,
                account_id=source.account_id,
                amount=source.amount
            )
            self.db.add(db_source)

        await self.db.commit()
        
        # Fetch the complete payment with sources
        stmt = (
            select(Payment)
            .options(joinedload(Payment.sources))
            .filter(Payment.id == db_payment.id)
        )
        result = await self.db.execute(stmt)
        return result.unique().scalar_one()

    async def update_payment(
        self, payment_id: int, payment_update: PaymentUpdate
    ) -> Optional[Payment]:
        # Get existing payment with sources
        db_payment = await self.get_payment(payment_id)
        if not db_payment:
            return None

        # Update payment fields first
        update_data = payment_update.model_dump(exclude_unset=True, exclude={'sources'})
        for key, value in update_data.items():
            setattr(db_payment, key, value)

        # If sources are being updated, validate them with the new payment amount
        if payment_update.sources is not None:
            # Use the new payment amount if it was updated, otherwise use existing amount
            current_amount = payment_update.amount if payment_update.amount is not None else db_payment.amount
            payment_update.validate_sources(current_amount)
            
            # Clear existing sources and set new ones
            db_payment.sources = [
                PaymentSource(
                    payment_id=payment_id,
                    account_id=source.account_id,
                    amount=source.amount
                )
                for source in payment_update.sources
            ]
            
            await self.db.commit()
            return await self.get_payment(payment_id)
        else:
            await self.db.commit()
            return await self.get_payment(payment_id)

    async def delete_payment(self, payment_id: int) -> bool:
        db_payment = await self.get_payment(payment_id)
        if not db_payment:
            return False
        
        await self.db.delete(db_payment)
        await self.db.commit()
        return True

    async def get_payments_by_date_range(
        self, start_date: date, end_date: date
    ) -> List[Payment]:
        stmt = (
            select(Payment)
            .options(joinedload(Payment.sources))
            .filter(Payment.payment_date.between(start_date, end_date))
            .order_by(Payment.payment_date.desc())
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def get_payments_for_liability(self, liability_id: int) -> List[Payment]:
        stmt = (
            select(Payment)
            .options(joinedload(Payment.sources))
            .filter(Payment.liability_id == liability_id)
            .order_by(Payment.payment_date.desc())
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def get_payments_for_account(self, account_id: int) -> List[Payment]:
        stmt = (
            select(Payment)
            .options(joinedload(Payment.sources))
            .join(PaymentSource)
            .filter(PaymentSource.account_id == account_id)
            .order_by(Payment.payment_date.desc())
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()
