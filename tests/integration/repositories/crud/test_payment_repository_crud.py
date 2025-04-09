"""
Integration tests for the PaymentRepository.

This module contains tests for the PaymentRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.
"""

from decimal import Decimal

import pytest

from src.models.accounts import Account
from src.models.liabilities import Liability
from src.models.payments import Payment
from src.repositories.payments import PaymentRepository
from src.utils.datetime_utils import datetime_equals, utc_now
from tests.helpers.schema_factories.payments_schema_factories import (
    create_payment_schema,
    create_payment_update_schema,
)

pytestmark = pytest.mark.asyncio


async def test_create_payment(
    payment_repository: PaymentRepository,
    test_checking_account: Account,
    test_liability: Liability,
):
    """Test creating a payment with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. SCHEMA: Create and validate through Pydantic schema
    payment_schema = create_payment_schema(
        amount=Decimal("100.00"),
        payment_date=utc_now(),
        category="Utilities",
        description="Monthly utility payment",
        liability_id=test_liability.id,
        sources=[
            {
                "account_id": test_checking_account.id,
                "amount": Decimal("100.00"),
            }
        ],
    )

    # Convert validated schema to dict for repository
    validated_data = payment_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await payment_repository.create(validated_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id is not None
    assert result.amount == Decimal("100.00")
    assert result.category == "Utilities"
    assert result.description == "Monthly utility payment"
    assert result.liability_id == test_liability.id

    # Verify sources were created
    assert hasattr(result, "sources")
    assert len(result.sources) == 1
    assert result.sources[0].account_id == test_checking_account.id
    assert result.sources[0].amount == Decimal("100.00")


async def test_get_payment(
    payment_repository: PaymentRepository,
    test_payment: Payment,
):
    """Test retrieving a payment by ID."""
    # 1. ARRANGE: Setup is already done with fixtures
    # Ensure test_payment is a SQLAlchemy model instance with an id
    payment_id = test_payment.id

    # 2. ACT: Get the payment by ID
    result = await payment_repository.get(payment_id)

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == payment_id
    assert result.amount == test_payment.amount
    assert datetime_equals(
        result.payment_date, test_payment.payment_date, ignore_timezone=True
    )
    assert result.category == test_payment.category
    assert result.description == test_payment.description
    assert result.liability_id == test_payment.liability_id


async def test_update_payment(
    payment_repository: PaymentRepository,
    test_payment: Payment,
):
    """Test updating a payment with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures
    payment_id = test_payment.id
    initial_payment_date = test_payment.payment_date
    initial_liability_id = test_payment.liability_id

    # Store original timestamp before update
    original_updated_at = test_payment.updated_at

    # 2. SCHEMA: Create and validate update data through Pydantic schema
    # Note: We're not updating sources in this test, so we don't include it
    update_schema = create_payment_update_schema(
        id=payment_id,
        amount=Decimal("75.00"),
        category="Updated Category",
        description="Updated payment description",
    )

    # Convert validated schema to dict for repository and explicitly remove 'sources'
    # to simulate a partial update of just these fields
    update_data = update_schema.model_dump(exclude={"id", "sources"})

    # 3. ACT: Pass validated data to repository
    result = await payment_repository.update(payment_id, update_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == payment_id
    assert result.amount == Decimal("75.00")
    assert result.category == "Updated Category"
    assert result.description == "Updated payment description"
    # Fields not in update_data should remain unchanged
    assert datetime_equals(
        result.payment_date, initial_payment_date, ignore_timezone=True
    )
    assert result.liability_id == initial_liability_id
    assert result.updated_at > original_updated_at


async def test_delete_payment(
    payment_repository: PaymentRepository,
    test_payment: Payment,
):
    """Test deleting a payment."""
    # 1. ARRANGE: Setup is already done with fixtures
    payment_id = test_payment.id

    # 2. ACT: Delete the payment
    result = await payment_repository.delete(payment_id)

    # 3. ASSERT: Verify the operation results
    assert result is True

    # Verify the payment is actually deleted
    deleted_check = await payment_repository.get(payment_id)
    assert deleted_check is None
