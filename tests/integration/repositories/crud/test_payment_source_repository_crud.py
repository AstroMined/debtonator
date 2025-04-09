"""
Integration tests for the PaymentSourceRepository.

This module contains tests for the PaymentSourceRepository using a real
test database to verify CRUD operations and specialized methods.
These tests follow the Arrange-Schema-Act-Assert pattern for repository testing.
"""

from decimal import Decimal

import pytest

from src.models.accounts import Account
from src.models.payments import PaymentSource
from src.repositories.payment_sources import PaymentSourceRepository
from src.repositories.payments import PaymentRepository
from src.utils.datetime_utils import utc_now
from tests.helpers.schema_factories.payment_sources_schema_factories import (
    create_payment_source_update_schema,
)
from tests.helpers.schema_factories.payments_schema_factories import (
    create_payment_schema,
)

pytestmark = pytest.mark.asyncio


async def test_create_payment_with_source(
    payment_repository: PaymentRepository,
    test_checking_account: Account,
):
    """
    Test creating a payment with a source.

    This test aligns with the ADR-017 design where payment sources
    are only created through a parent payment.
    """
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. SCHEMA: Create and validate through Pydantic schema
    # Create a payment with a single source
    payment_schema = create_payment_schema(
        amount=Decimal("50.00"),
        payment_date=utc_now(),
        category="Test Payment",
        description="Test payment creation through ADR-017 pattern",
        sources=[
            {
                "account_id": test_checking_account.id,
                "amount": Decimal("50.00"),
            }
        ],
    )

    # Convert validated schema to dict for repository
    validated_data = payment_schema.model_dump()

    # 3. ACT: Pass validated data to repository to create payment with source
    result = await payment_repository.create(validated_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id is not None
    assert result.amount == Decimal("50.00")

    # Verify source was created as part of the payment
    assert hasattr(result, "sources")
    assert len(result.sources) == 1

    source = result.sources[0]
    assert source.payment_id == result.id
    assert source.account_id == test_checking_account.id
    assert source.amount == Decimal("50.00")
    assert source.created_at is not None
    assert source.updated_at is not None


async def test_get_payment_source(
    payment_source_repository: PaymentSourceRepository,
    test_payment_source: PaymentSource,
):
    """Test retrieving a payment source by ID with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures
    # Ensure test_payment_source is treated as a SQLAlchemy model instance
    payment_source_id = test_payment_source.id

    # 2. ACT: Get the payment source by ID
    result = await payment_source_repository.get(payment_source_id)

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == payment_source_id
    assert result.payment_id == test_payment_source.payment_id
    assert result.account_id == test_payment_source.account_id
    assert result.amount == test_payment_source.amount


async def test_update_payment_source(
    payment_source_repository: PaymentSourceRepository,
    test_payment_source: PaymentSource,
):
    """Test updating a payment source with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures
    payment_source_id = test_payment_source.id
    initial_payment_id = test_payment_source.payment_id
    initial_account_id = test_payment_source.account_id
    initial_updated_at = test_payment_source.updated_at

    # 2. SCHEMA: Create and validate through Pydantic schema
    # Create a validated schema using the factory, explicitly including the payment_id to preserve it
    update_schema = create_payment_source_update_schema(
        id=payment_source_id,
        amount=Decimal("125.00"),
        payment_id=initial_payment_id,  # Keep the existing payment_id
        account_id=initial_account_id,  # Keep the existing account_id
    )

    # Convert validated schema to dict for repository, excluding id
    update_data = update_schema.model_dump(exclude={"id"})

    # 3. ACT: Pass validated data to repository
    result = await payment_source_repository.update(payment_source_id, update_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == payment_source_id
    assert result.amount == Decimal("125.00")
    # Fields not in update_data should remain unchanged
    assert result.payment_id == initial_payment_id
    assert result.account_id == initial_account_id
    assert result.updated_at > initial_updated_at


async def test_delete_payment_source(
    payment_source_repository: PaymentSourceRepository,
    test_payment_source: PaymentSource,
):
    """Test deleting a payment source."""
    # 1. ARRANGE: Setup is already done with fixtures
    payment_source_id = test_payment_source.id

    # 2. ACT: Delete the payment source
    result = await payment_source_repository.delete(payment_source_id)

    # 3. ASSERT: Verify the operation results
    assert result is True

    # Verify the payment source is actually deleted
    deleted_check = await payment_source_repository.get(payment_source_id)
    assert deleted_check is None
