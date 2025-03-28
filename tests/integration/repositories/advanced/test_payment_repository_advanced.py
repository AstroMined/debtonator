"""
Integration tests for the PaymentRepository.

This module contains tests for the PaymentRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List, Optional

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.liabilities import Liability
from src.models.payments import Payment, PaymentSource
from src.repositories.payments import PaymentRepository
from src.schemas.payments import (
    PaymentCreate,
    PaymentDateRange,
    PaymentSourceCreate,
    PaymentUpdate,
)
from src.utils.datetime_utils import datetime_equals, datetime_greater_than, utc_now
from tests.helpers.schema_factories.payments import (
    create_payment_date_range_schema,
    create_payment_schema,
)

pytestmark = pytest.mark.asyncio


async def test_create_split_payment(
    payment_repository: PaymentRepository,
    test_checking_account: Account,
    test_second_account: Account,
):
    """Test creating a payment split across multiple accounts."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. SCHEMA: Create and validate through Pydantic schema
    payment_schema = create_payment_schema(
        amount=Decimal("150.00"),
        payment_date=utc_now(),
        category="Insurance",
        description="Insurance payment split across accounts",
        sources=[
            {
                "account_id": test_checking_account.id,
                "amount": Decimal("100.00"),
            },
            {
                "account_id": test_second_account.id,
                "amount": Decimal("50.00"),
            },
        ],
    )

    # Convert validated schema to dict for repository
    validated_data = payment_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await payment_repository.create(validated_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id is not None
    assert result.amount == Decimal("150.00")

    # Verify sources were created
    assert hasattr(result, "sources")
    assert len(result.sources) == 2

    # Find sources by account
    source1 = next(
        s for s in result.sources if s.account_id == test_checking_account.id
    )
    source2 = next(s for s in result.sources if s.account_id == test_second_account.id)

    assert source1.amount == Decimal("100.00")
    assert source2.amount == Decimal("50.00")


async def test_get_with_sources(
    payment_repository: PaymentRepository,
    test_payment: Payment,
):
    """Test getting a payment with its sources loaded."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get the payment with sources
    result = await payment_repository.get_with_sources(test_payment.id)

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_payment.id
    assert hasattr(result, "sources")
    assert len(result.sources) >= 1

    # Check that sources are loaded correctly
    source = result.sources[0]
    assert source.payment_id == test_payment.id
    assert source.amount == Decimal("50.00")  # From test_payment fixture


async def test_get_with_relationships(
    payment_repository: PaymentRepository,
    test_payment: Payment,
):
    """Test getting a payment with multiple relationships loaded."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get the payment with relationships
    result = await payment_repository.get_with_relationships(
        payment_id=test_payment.id,
        include_sources=True,
        include_liability=True,
    )

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_payment.id
    assert hasattr(result, "sources")
    assert hasattr(result, "liability")

    # Check that relationships are loaded correctly
    assert len(result.sources) >= 1
    assert result.liability is not None
    assert result.liability.id == test_payment.liability_id


async def test_get_payments_for_bill(
    payment_repository: PaymentRepository,
    test_payment: Payment,
    test_liability: Liability,
):
    """Test getting payments for a specific bill."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get payments for bill
    results = await payment_repository.get_payments_for_bill(test_liability.id)

    # 3. ASSERT: Verify the operation results
    assert len(results) >= 1

    # Check that our test payment is in the results
    payment_ids = [p.id for p in results]
    assert test_payment.id in payment_ids

    # Verify all returned payments are for the correct liability
    for payment in results:
        assert payment.liability_id == test_liability.id


async def test_get_payments_for_account(
    payment_repository: PaymentRepository,
    test_payment: Payment,
    test_checking_account: Account,
):
    """Test getting payments for a specific account."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get payments for account
    results = await payment_repository.get_payments_for_account(
        test_checking_account.id
    )

    # 3. ASSERT: Verify the operation results
    assert len(results) >= 1

    # Check that our test payment is in the results
    payment_ids = [p.id for p in results]
    assert test_payment.id in payment_ids


async def test_get_payments_in_date_range(
    payment_repository: PaymentRepository,
    test_multiple_payments: List[Payment],
):
    """Test getting payments within a date range."""
    # 1. ARRANGE: Setup is already done with fixtures
    now = utc_now()
    start_date = now - timedelta(days=20)
    end_date = now

    # 2. SCHEMA: Create and validate through Pydantic schema
    date_range_schema = create_payment_date_range_schema(
        start_date=start_date,
        end_date=end_date,
    )

    # 3. ACT: Get payments in date range
    results = await payment_repository.get_payments_in_date_range(
        date_range_schema.start_date, date_range_schema.end_date
    )

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 2  # Should find at least 2 payments in this range

    # Verify all returned payments are within the date range
    for payment in results:
        assert datetime_greater_than(
            payment.payment_date, start_date, ignore_timezone=True
        ) or datetime_equals(payment.payment_date, start_date, ignore_timezone=True)
        assert datetime_greater_than(
            end_date, payment.payment_date, ignore_timezone=True
        ) or datetime_equals(end_date, payment.payment_date, ignore_timezone=True)


async def test_get_payments_by_category(
    payment_repository: PaymentRepository,
    test_multiple_payments: List[Payment],
):
    """Test getting payments by category."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get payments by category (Utilities)
    results = await payment_repository.get_payments_by_category("Utilities")

    # 3. ASSERT: Verify the operation results
    assert len(results) >= 1

    # Verify all returned payments have the correct category
    for payment in results:
        assert payment.category == "Utilities"


async def test_get_total_amount_in_range(
    payment_repository: PaymentRepository,
    test_multiple_payments: List[Payment],
):
    """Test getting total payment amount in a date range."""
    # 1. ARRANGE: Setup is already done with fixtures
    now = utc_now()
    start_date = now - timedelta(days=30)
    end_date = now

    # 2. ACT: Get total amount in range
    total = await payment_repository.get_total_amount_in_range(start_date, end_date)

    # 3. ASSERT: Verify the operation results
    assert total >= Decimal(
        "995.00"
    )  # Sum of all payments in test_multiple_payments within range


async def test_get_total_amount_by_category(
    payment_repository: PaymentRepository,
    test_multiple_payments: List[Payment],
):
    """Test getting total payment amount by category in a date range."""
    # 1. ARRANGE: Setup is already done with fixtures
    now = utc_now()
    start_date = now - timedelta(days=30)
    end_date = now

    # 2. ACT: Get total amount for Utilities category
    total = await payment_repository.get_total_amount_in_range(
        start_date, end_date, category="Utilities"
    )

    # 3. ASSERT: Verify the operation results
    assert total >= Decimal("75.00")  # From utilities payment in test_multiple_payments


async def test_get_recent_payments(
    payment_repository: PaymentRepository,
    test_multiple_payments: List[Payment],
):
    """Test getting recent payments."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get recent payments (within last 10 days)
    results = await payment_repository.get_recent_payments(days=10)

    # 3. ASSERT: Verify the operation results
    assert len(results) >= 2  # Should find at least 2 payments in this range

    # Verify all returned payments are within the last 10 days
    now = utc_now()
    cutoff_date = now - timedelta(days=10)
    for payment in results:
        assert datetime_greater_than(
            payment.payment_date, cutoff_date, ignore_timezone=True
        ) or datetime_equals(payment.payment_date, cutoff_date, ignore_timezone=True)


async def test_validation_error_handling():
    """Test handling of validation errors that would be caught by the Pydantic schema."""
    # Try creating a schema with invalid data
    try:
        # Sources don't add up to total amount
        invalid_schema = PaymentCreate(
            amount=Decimal("100.00"),
            payment_date=utc_now(),
            category="Utilities",
            sources=[
                PaymentSourceCreate(
                    account_id=1,
                    amount=Decimal("50.00"),  # Only 50 of 100 total
                )
            ],
        )
        assert False, "Schema should have raised a validation error"
    except ValueError as e:
        # This is expected - schema validation should catch the error
        error_str = str(e).lower()
        assert "sources" in error_str or "sum" in error_str

    # Try another invalid case
    try:
        # Negative amount
        invalid_schema = PaymentCreate(
            amount=Decimal("-50.00"),
            payment_date=utc_now(),
            category="Utilities",
            sources=[
                PaymentSourceCreate(
                    account_id=1,
                    amount=Decimal("-50.00"),
                )
            ],
        )
        assert False, "Schema should have raised a validation error"
    except ValueError as e:
        # This is expected - schema validation should catch the error
        error_str = str(e).lower()
        assert "amount" in error_str
