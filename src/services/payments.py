from datetime import date
from decimal import Decimal
from typing import List, Optional, Tuple

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.models.accounts import Account
from src.models.income import Income
from src.models.liabilities import Liability
from src.models.payments import Payment, PaymentSource
from src.schemas.payments import PaymentCreate, PaymentUpdate
from src.utils.decimal_precision import DecimalPrecision


class PaymentService:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def validate_account_availability(
        self, sources: List[dict]
    ) -> Tuple[bool, Optional[str]]:
        """Validates accounts exist and have sufficient funds/credit."""
        for source in sources:
            account_result = await self.db.execute(
                select(Account).filter(Account.id == source["account_id"])
            )
            account = account_result.scalar_one_or_none()
            if not account:
                return False, f"Account {source['account_id']} not found"

            # Validate account has sufficient funds/credit
            source_amount = Decimal(str(source["amount"]))
            # Round for internal calculation to ensure consistency
            source_amount = DecimalPrecision.round_for_calculation(source_amount)

            if account.type == "credit":
                available_credit = DecimalPrecision.round_for_calculation(
                    account.available_credit
                )
                if available_credit < source_amount:
                    return False, f"Insufficient credit in account {account.name}"
            else:
                available_balance = DecimalPrecision.round_for_calculation(
                    account.available_balance
                )
                if available_balance < source_amount:
                    return False, f"Insufficient funds in account {account.name}"

        return True, None

    async def validate_references(
        self, liability_id: Optional[int], income_id: Optional[int]
    ) -> Tuple[bool, Optional[str]]:
        """Validates optional liability and income references exist."""
        if liability_id:
            liability_result = await self.db.execute(
                select(Liability).filter(Liability.id == liability_id)
            )
            if not liability_result.scalar_one_or_none():
                return False, f"Liability {liability_id} not found"

        if income_id:
            income_result = await self.db.execute(
                select(Income).filter(Income.id == income_id)
            )
            if not income_result.scalar_one_or_none():
                return False, f"Income {income_id} not found"

        return True, None

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
        # Validate account availability
        valid, error = await self.validate_account_availability(
            [source.model_dump() for source in payment_create.sources]
        )
        if not valid:
            raise ValueError(error)

        # Validate references
        valid, error = await self.validate_references(
            payment_create.liability_id, payment_create.income_id
        )
        if not valid:
            raise ValueError(error)

        # Create payment
        # Use calculation precision for internal storage, but this will display as 2 decimal places in API responses
        amount = DecimalPrecision.round_for_calculation(payment_create.amount)
        db_payment = Payment(
            liability_id=payment_create.liability_id,
            income_id=payment_create.income_id,
            amount=amount,
            payment_date=payment_create.payment_date,
            description=payment_create.description,
            category=payment_create.category,
        )
        self.db.add(db_payment)
        await self.db.flush()

        # Create payment sources
        for source in payment_create.sources:
            source_amount = DecimalPrecision.round_for_calculation(source.amount)
            db_source = PaymentSource(
                payment_id=db_payment.id,
                account_id=source.account_id,
                amount=source_amount,
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

        # Prepare update data
        update_data = payment_update.model_dump(exclude_unset=True, exclude={"sources"})

        # Update payment fields
        for key, value in update_data.items():
            setattr(db_payment, key, value)

        # If sources are being updated, validate account availability
        if payment_update.sources is not None:
            # Validate account availability
            valid, error = await self.validate_account_availability(
                [source.model_dump() for source in payment_update.sources]
            )
            if not valid:
                raise ValueError(error)

            # Clear existing sources and set new ones
            db_payment.sources = [
                PaymentSource(
                    payment_id=payment_id,
                    account_id=source.account_id,
                    amount=source.amount,
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
