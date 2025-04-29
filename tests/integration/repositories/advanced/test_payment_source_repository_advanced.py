"""
Integration tests for the PaymentSourceRepository.

This module contains tests for the PaymentSourceRepository using a real
test database to verify CRUD operations and specialized methods.
These tests follow the Arrange-Schema-Act-Assert pattern for repository testing.
"""

from decimal import Decimal

import pytest

from src.models.accounts import Account
from src.models.payments import Payment, PaymentSource
from src.repositories.payment_sources import PaymentSourceRepository
from src.repositories.payments import PaymentRepository
from src.utils.datetime_utils import utc_now
from tests.helpers.schema_factories.payments_schema_factories import (
    create_payment_schema,
)

pytestmark = pytest.mark.asyncio


async def test_get_with_relationships(
    payment_source_repository: PaymentSourceRepository,
    test_payment_source: PaymentSource,
):
    """Test getting a payment source with relationships loaded."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get the payment source with relationships
    result = await payment_source_repository.get_with_relationships(
        test_payment_source.id, include_payment=True, include_account=True
    )

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_payment_source.id

    # Check that relationships are properly loaded
    assert hasattr(result, "payment")
    assert result.payment is not None
    assert result.payment.id == test_payment_source.payment_id

    assert hasattr(result, "account")
    assert result.account is not None
    assert result.account.id == test_payment_source.account_id


async def test_get_sources_for_payment(
    payment_source_repository: PaymentSourceRepository,
    test_payment_with_multiple_sources: Payment,
):
    """Test getting sources for a specific payment."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get sources for the payment
    results = await payment_source_repository.get_sources_for_payment(
        test_payment_with_multiple_sources.id
    )

    # 3. ASSERT: Verify the operation results
    assert results is not None
    assert len(results) == 2  # The test payment has 2 sources

    # Check that all sources belong to the correct payment
    for source in results:
        assert source.payment_id == test_payment_with_multiple_sources.id


async def test_get_sources_for_account(
    payment_source_repository: PaymentSourceRepository,
    test_checking_account: Account,
    test_payment: Payment,
    test_payment_with_multiple_sources: Payment,
):
    """Test getting sources for a specific account."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get sources for the account
    results = await payment_source_repository.get_sources_for_account(
        test_checking_account.id
    )

    # 3. ASSERT: Verify the operation results
    assert results is not None
    assert len(results) >= 2  # At least 2 sources use this account

    # Check that all sources belong to the correct account
    for source in results:
        assert source.account_id == test_checking_account.id


async def test_payment_with_multiple_sources(
    payment_repository: PaymentRepository,
    test_checking_account: Account,
    test_second_checking_account: Account,
):
    """
    Test creating a payment with multiple sources.

    This test aligns with the ADR-017 design where payment sources can only be created
    as part of a parent payment, never standalone.
    """
    # 1. ARRANGE: Setup is already done with fixtures
    total_amount = Decimal("70.00")
    source1_amount = Decimal("30.00")
    source2_amount = Decimal("40.00")

    # 2. SCHEMA: Create and validate through Pydantic schema
    payment_schema = create_payment_schema(
        amount=total_amount,
        payment_date=utc_now(),
        category="Test Multiple Sources",
        description="Test payment with multiple sources creation through ADR-017 pattern",
        sources=[
            {
                "account_id": test_checking_account.id,
                "amount": source1_amount,
            },
            {
                "account_id": test_second_checking_account.id,
                "amount": source2_amount,
            },
        ],
    )

    # Convert validated schema to dict for repository
    validated_data = payment_schema.model_dump()

    # 3. ACT: Pass validated data to repository to create payment with sources
    result = await payment_repository.create(validated_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id is not None
    assert result.amount == total_amount

    # Verify sources were created as part of the payment
    assert hasattr(result, "sources")
    assert len(result.sources) == 2

    # Find sources by account
    source1 = next(
        s for s in result.sources if s.account_id == test_checking_account.id
    )
    source2 = next(
        s for s in result.sources if s.account_id == test_second_checking_account.id
    )

    # Verify first source
    assert source1.payment_id == result.id
    assert source1.amount == source1_amount

    # Verify second source
    assert source2.payment_id == result.id
    assert source2.amount == source2_amount


async def test_get_total_amount_by_account(
    payment_source_repository: PaymentSourceRepository,
    test_checking_account: Account,
    test_payment: Payment,
    test_payment_with_multiple_sources: Payment,
    test_payment_source: PaymentSource,
):
    """Test getting total payment amount from a specific account."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get total amount for the account
    total = await payment_source_repository.get_total_amount_by_account(
        test_checking_account.id
    )

    # 3. ASSERT: Verify the operation results
    # We have 3 sources using this account:
    # - One from test_payment (50.00)
    # - One from test_payment_with_multiple_sources (100.00)
    # - One from test_payment_source (75.00)
    expected_total = Decimal("225.00")
    assert total == expected_total


async def test_delete_sources_for_payment(
    payment_source_repository: PaymentSourceRepository,
    test_payment_with_multiple_sources: Payment,
):
    """Test deleting all sources for a specific payment."""
    # 1. ARRANGE: Setup is already done with fixtures

    # First verify we have the expected sources
    initial_sources = await payment_source_repository.get_sources_for_payment(
        test_payment_with_multiple_sources.id
    )
    assert len(initial_sources) == 2

    # 2. ACT: Delete all sources for the payment
    count = await payment_source_repository.delete_sources_for_payment(
        test_payment_with_multiple_sources.id
    )

    # 3. ASSERT: Verify the operation results
    assert count == 2  # Should have deleted 2 sources

    # Verify the sources are actually deleted
    remaining_sources = await payment_source_repository.get_sources_for_payment(
        test_payment_with_multiple_sources.id
    )
    assert len(remaining_sources) == 0


async def test_validation_error_handling():
    """Test that schema validation catches invalid data."""
    # Import the schema factory
    from tests.helpers.schema_factories.payment_sources_schema_factories import (
        create_payment_source_schema,
    )

    # Try creating a schema with invalid data
    try:
        # Using PaymentSourceCreate since it doesn't require payment_id
        invalid_schema = create_payment_source_schema(
            account_id=-1,  # Invalid negative ID
            amount=Decimal("-50.00"),  # Invalid negative amount
        )
        assert False, "Schema should have raised a validation error"
    except ValueError as e:
        # This is expected - schema validation should catch the error
        error_str = str(e).lower()
        assert "account_id" in error_str or "amount" in error_str
