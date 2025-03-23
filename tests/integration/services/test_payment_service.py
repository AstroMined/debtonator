from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest

from src.models.accounts import Account
from src.models.income import Income
from src.models.liabilities import Liability
from src.models.payments import Payment, PaymentSource
from src.schemas.payments import (PaymentCreate, PaymentSourceCreate,
                                  PaymentUpdate)
from src.services.payments import PaymentService


@pytest.mark.asyncio
class TestPaymentService:
    async def test_validate_account_availability_valid(self, db_session):
        # Setup
        service = PaymentService(db_session)
        account = Account(
            name="Test Account", type="checking", available_balance=Decimal("1000.00")
        )
        db_session.add(account)
        await db_session.flush()

        sources = [{"account_id": account.id, "amount": Decimal("100.00")}]

        valid, error = await service.validate_account_availability(sources)
        assert valid is True
        assert error is None

    async def test_validate_account_availability_account_not_found(self, db_session):
        service = PaymentService(db_session)
        sources = [{"account_id": 999, "amount": Decimal("100.00")}]

        valid, error = await service.validate_account_availability(sources)
        assert valid is False
        assert "not found" in error

    async def test_validate_account_availability_insufficient_funds(self, db_session):
        # Setup
        service = PaymentService(db_session)
        account = Account(
            name="Test Account", type="checking", available_balance=Decimal("50.00")
        )
        db_session.add(account)
        await db_session.flush()

        sources = [{"account_id": account.id, "amount": Decimal("100.00")}]

        valid, error = await service.validate_account_availability(sources)
        assert valid is False
        assert "insufficient funds" in error.lower()

    async def test_validate_account_availability_insufficient_credit(self, db_session):
        # Setup
        service = PaymentService(db_session)
        account = Account(
            name="Test Credit Card",
            type="credit",
            available_balance=Decimal("-900.00"),
            total_limit=Decimal("1000.00"),
        )
        db_session.add(account)
        await db_session.flush()

        sources = [{"account_id": account.id, "amount": Decimal("200.00")}]

        valid, error = await service.validate_account_availability(sources)
        assert valid is False
        assert "insufficient credit" in error.lower()

    async def test_validate_references_valid(self, db_session):
        # Setup
        service = PaymentService(db_session)
        liability = Liability(name="Test Bill", amount=Decimal("100.00"))
        income = Income(
            date=datetime.now(ZoneInfo("UTC")),
            source="Test Income",
            amount=Decimal("1000.00"),
        )
        db_session.add_all([liability, income])
        await db_session.flush()

        valid, error = await service.validate_references(liability.id, income.id)
        assert valid is True
        assert error is None

    async def test_validate_references_invalid_liability(self, db_session):
        service = PaymentService(db_session)
        valid, error = await service.validate_references(999, None)
        assert valid is False
        assert "Liability" in error

    async def test_validate_references_invalid_income(self, db_session):
        service = PaymentService(db_session)
        valid, error = await service.validate_references(None, 999)
        assert valid is False
        assert "Income" in error

    async def test_create_payment_success(self, db_session):
        # Setup
        service = PaymentService(db_session)
        account = Account(
            name="Test Account", type="checking", available_balance=Decimal("1000.00")
        )
        liability = Liability(name="Test Bill", amount=Decimal("100.00"))
        db_session.add_all([account, liability])
        await db_session.flush()

        payment_create = PaymentCreate(
            liability_id=liability.id,
            amount=Decimal("100.00"),
            payment_date=datetime.now(ZoneInfo("UTC")),
            category="Test",
            sources=[
                PaymentSourceCreate(account_id=account.id, amount=Decimal("100.00"))
            ],
        )

        # Execute
        payment = await service.create_payment(payment_create)

        # Assert
        assert payment.amount == Decimal("100.00")
        assert payment.liability_id == liability.id
        assert len(payment.sources) == 1
        assert payment.sources[0].account_id == account.id
        assert payment.sources[0].amount == Decimal("100.00")

    async def test_create_payment_insufficient_funds(self, db_session):
        # Setup
        service = PaymentService(db_session)
        account = Account(
            name="Test Account", type="checking", available_balance=Decimal("50.00")
        )
        liability = Liability(name="Test Bill", amount=Decimal("100.00"))
        db_session.add_all([account, liability])
        await db_session.flush()

        payment_create = PaymentCreate(
            liability_id=liability.id,
            amount=Decimal("100.00"),
            payment_date=datetime.now(ZoneInfo("UTC")),
            category="Test",
            sources=[
                PaymentSourceCreate(account_id=account.id, amount=Decimal("100.00"))
            ],
        )

        # Execute and Assert
        with pytest.raises(ValueError, match="insufficient funds"):
            await service.create_payment(payment_create)

    async def test_update_payment_success(self, db_session):
        # Setup
        service = PaymentService(db_session)
        account = Account(
            name="Test Account", type="checking", available_balance=Decimal("1000.00")
        )
        liability = Liability(name="Test Bill", amount=Decimal("100.00"))
        db_session.add_all([account, liability])
        await db_session.flush()

        # Create initial payment
        payment = Payment(
            liability_id=liability.id,
            amount=Decimal("100.00"),
            payment_date=datetime.now(ZoneInfo("UTC")),
            category="Test",
        )
        source = PaymentSource(account_id=account.id, amount=Decimal("100.00"))
        payment.sources = [source]
        db_session.add(payment)
        await db_session.flush()

        # Update payment
        payment_update = PaymentUpdate(
            amount=Decimal("150.00"),
            sources=[
                PaymentSourceCreate(account_id=account.id, amount=Decimal("150.00"))
            ],
        )

        # Execute
        updated_payment = await service.update_payment(payment.id, payment_update)

        # Assert
        assert updated_payment is not None
        assert updated_payment.amount == Decimal("150.00")
        assert len(updated_payment.sources) == 1
        assert updated_payment.sources[0].amount == Decimal("150.00")

    async def test_update_payment_insufficient_funds(self, db_session):
        # Setup
        service = PaymentService(db_session)
        account = Account(
            name="Test Account", type="checking", available_balance=Decimal("100.00")
        )
        liability = Liability(name="Test Bill", amount=Decimal("100.00"))
        db_session.add_all([account, liability])
        await db_session.flush()

        # Create initial payment
        payment = Payment(
            liability_id=liability.id,
            amount=Decimal("50.00"),
            payment_date=datetime.now(ZoneInfo("UTC")),
            category="Test",
        )
        source = PaymentSource(account_id=account.id, amount=Decimal("50.00"))
        payment.sources = [source]
        db_session.add(payment)
        await db_session.flush()

        # Update payment
        payment_update = PaymentUpdate(
            amount=Decimal("200.00"),
            sources=[
                PaymentSourceCreate(account_id=account.id, amount=Decimal("200.00"))
            ],
        )

        # Execute and Assert
        with pytest.raises(ValueError, match="insufficient funds"):
            await service.update_payment(payment.id, payment_update)

    async def test_delete_payment_success(self, db_session):
        # Setup
        service = PaymentService(db_session)
        account = Account(
            name="Test Account", type="checking", available_balance=Decimal("1000.00")
        )
        payment = Payment(
            amount=Decimal("100.00"),
            payment_date=datetime.now(ZoneInfo("UTC")),
            category="Test",
        )
        source = PaymentSource(account_id=account.id, amount=Decimal("100.00"))
        payment.sources = [source]
        db_session.add_all([account, payment])
        await db_session.flush()

        # Execute
        result = await service.delete_payment(payment.id)

        # Assert
        assert result is True
        deleted_payment = await service.get_payment(payment.id)
        assert deleted_payment is None
