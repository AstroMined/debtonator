from datetime import date
from typing import List, Optional
from sqlalchemy import select
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
            bill_id=payment_create.bill_id,
            income_id=payment_create.income_id,
            amount=payment_create.amount,
            payment_date=payment_create.payment_date,
            description=payment_create.description,
            category=payment_create.category
        )
        self.db.add(db_payment)
        await self.db.flush()  # Get payment ID without committing

        # Create payment sources
        for source in payment_create.sources:
            db_source = PaymentSource(
                payment_id=db_payment.id,
                account_id=source.account_id,
                amount=source.amount
            )
            self.db.add(db_source)

        await self.db.commit()
        await self.db.refresh(db_payment)
        return db_payment

    async def update_payment(
        self, payment_id: int, payment_update: PaymentUpdate
    ) -> Optional[Payment]:
        db_payment = await self.get_payment(payment_id)
        if not db_payment:
            return None

        # If sources are being updated, validate them
        if payment_update.sources is not None:
            payment_update.validate_sources(
                payment_update.amount or db_payment.amount
            )
            
            # Delete existing sources
            await self.db.execute(
                select(PaymentSource)
                .filter(PaymentSource.payment_id == payment_id)
                .delete()
            )
            
            # Create new sources
            for source in payment_update.sources:
                db_source = PaymentSource(
                    payment_id=payment_id,
                    account_id=source.account_id,
                    amount=source.amount
                )
                self.db.add(db_source)

        # Update payment fields
        update_data = payment_update.model_dump(exclude_unset=True, exclude={'sources'})
        for key, value in update_data.items():
            setattr(db_payment, key, value)

        await self.db.commit()
        await self.db.refresh(db_payment)
        return db_payment

    async def delete_payment(self, payment_id: int) -> bool:
        db_payment = await self.get_payment(payment_id)
        if not db_payment:
            return False
        
        # The cascade will handle deleting associated payment sources
        await self.db.delete(db_payment)
        await self.db.commit()
        return True

    async def get_payments_for_liability(self, liability_id: int) -> List[Payment]:
        """Get all payments associated with a liability"""
        stmt = (
            select(Payment)
            .options(joinedload(Payment.sources))
            .filter(Payment.bill_id == liability_id)
            .order_by(Payment.payment_date.desc())
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()

    async def get_payments_for_account(self, account_id: int) -> List[Payment]:
        """Get all payments that have sources from a specific account"""
        stmt = (
            select(Payment)
            .options(joinedload(Payment.sources))
            .join(PaymentSource)
            .filter(PaymentSource.account_id == account_id)
            .order_by(Payment.payment_date.desc())
        )
        result = await self.db.execute(stmt)
        return result.unique().scalars().all()
