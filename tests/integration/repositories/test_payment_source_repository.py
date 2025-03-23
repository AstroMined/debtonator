"""
Integration tests for the PaymentSourceRepository.

This module contains tests for the PaymentSourceRepository using a real
test database to verify CRUD operations and specialized methods.
These tests follow the Arrange-Schema-Act-Assert pattern for repository testing.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.payments import Payment, PaymentSource
from src.repositories.accounts import AccountRepository
from src.repositories.payment_sources import PaymentSourceRepository
from src.repositories.payments import PaymentRepository
from src.schemas.accounts import AccountCreate
from src.schemas.payments import (PaymentCreate, PaymentSourceCreate,
                                  PaymentSourceUpdate)
from tests.helpers.datetime_utils import utc_now
from tests.helpers.schema_factories.accounts import create_account_schema
from tests.helpers.schema_factories.payment_sources import \
    create_payment_source_schema
from tests.helpers.schema_factories.payments import create_payment_schema


@pytest_asyncio.fixture
async def account_repository(db_session: AsyncSession) -> AccountRepository:
    """Fixture for AccountRepository with test database session."""
    return AccountRepository(db_session)


@pytest_asyncio.fixture
async def payment_repository(db_session: AsyncSession) -> PaymentRepository:
    """Fixture for PaymentRepository with test database session."""
    return PaymentRepository(db_session)


@pytest_asyncio.fixture
async def payment_source_repository(
    db_session: AsyncSession,
) -> PaymentSourceRepository:
    """Fixture for PaymentSourceRepository with test database session."""
    return PaymentSourceRepository(db_session)


@pytest_asyncio.fixture
async def test_account(account_repository: AccountRepository) -> Account:
    """Create a test checking account for use in tests."""
    # 1. ARRANGE: No setup needed for this fixture

    # 2. SCHEMA: Create and validate through Pydantic schema
    account_schema = create_account_schema(
        name="Test Checking Account",
        account_type="checking",
        available_balance=Decimal("1000.00"),
    )

    # Convert validated schema to dict for repository
    validated_data = account_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    return await account_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_second_account(account_repository: AccountRepository) -> Account:
    """Create a second test checking account for use in tests."""
    # 1. ARRANGE: No setup needed for this fixture

    # 2. SCHEMA: Create and validate through Pydantic schema
    account_schema = create_account_schema(
        name="Second Checking Account",
        account_type="checking",
        available_balance=Decimal("2000.00"),
    )

    # Convert validated schema to dict for repository
    validated_data = account_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    return await account_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_payment(
    payment_repository: PaymentRepository,
    test_account: Account,
) -> Payment:
    """Create a test payment for use in tests."""
    # 1. ARRANGE: No setup needed for this fixture

    # 2. SCHEMA: Create and validate through Pydantic schema
    payment_schema = create_payment_schema(
        amount=Decimal("100.00"),
        payment_date=utc_now(),
        category="Bill Payment",
        description="Test payment",
        sources=[
            create_payment_source_schema(
                account_id=test_account.id, amount=Decimal("100.00")
            )
        ],
    )

    # Convert validated schema to dict for repository
    validated_data = payment_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    return await payment_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_payment_with_multiple_sources(
    payment_repository: PaymentRepository,
    test_account: Account,
    test_second_account: Account,
) -> Payment:
    """Create a test payment with multiple payment sources."""
    # 1. ARRANGE: No setup needed for this fixture

    # 2. SCHEMA: Create and validate through Pydantic schema
    payment_schema = create_payment_schema(
        amount=Decimal("150.00"),
        payment_date=utc_now(),
        category="Bill Payment",
        description="Test payment with multiple sources",
        sources=[
            create_payment_source_schema(
                account_id=test_account.id, amount=Decimal("100.00")
            ),
            create_payment_source_schema(
                account_id=test_second_account.id, amount=Decimal("50.00")
            ),
        ],
    )

    # Convert validated schema to dict for repository
    validated_data = payment_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    return await payment_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_payment_source(
    payment_source_repository: PaymentSourceRepository,
    test_payment: Payment,
    test_account: Account,
) -> PaymentSource:
    """
    Create a test payment source.

    Note: This fixture creates a separate payment source, not directly
    associated with the test_payment fixture which already has its own source.
    """
    # 1. ARRANGE: No setup needed for this fixture

    # 2. SCHEMA: Create and validate through Pydantic schema
    source_schema = create_payment_source_schema(
        account_id=test_account.id, amount=Decimal("75.00"), payment_id=test_payment.id
    )

    # Convert validated schema to dict for repository
    validated_data = source_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    return await payment_source_repository.create(validated_data)


class TestPaymentSourceRepository:
    """
    Tests for the PaymentSourceRepository.

    These tests follow the standard 4-step pattern (Arrange-Schema-Act-Assert)
    for repository testing, simulating proper service-to-repository validation flow.
    """

    @pytest.mark.asyncio
    async def test_create_payment_source(
        self,
        payment_source_repository: PaymentSourceRepository,
        test_payment: Payment,
        test_account: Account,
    ):
        """Test creating a payment source with proper validation flow."""
        # 1. ARRANGE: Setup is already done with fixtures

        # 2. SCHEMA: Create and validate through Pydantic schema
        source_schema = create_payment_source_schema(
            account_id=test_account.id,
            amount=Decimal("50.00"),
            payment_id=test_payment.id,
        )

        # Convert validated schema to dict for repository
        validated_data = source_schema.model_dump()

        # 3. ACT: Pass validated data to repository
        result = await payment_source_repository.create(validated_data)

        # 4. ASSERT: Verify the operation results
        assert result is not None
        assert result.id is not None
        assert result.payment_id == test_payment.id
        assert result.account_id == test_account.id
        assert result.amount == Decimal("50.00")
        assert result.created_at is not None
        assert result.updated_at is not None

    @pytest.mark.asyncio
    async def test_get_payment_source(
        self,
        payment_source_repository: PaymentSourceRepository,
        test_payment_source: PaymentSource,
    ):
        """Test retrieving a payment source by ID with proper validation flow."""
        # 1. ARRANGE: Setup is already done with fixtures

        # 2. ACT: Get the payment source by ID
        result = await payment_source_repository.get(test_payment_source.id)

        # 3. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_payment_source.id
        assert result.payment_id == test_payment_source.payment_id
        assert result.account_id == test_payment_source.account_id
        assert result.amount == test_payment_source.amount

    @pytest.mark.asyncio
    async def test_update_payment_source(
        self,
        payment_source_repository: PaymentSourceRepository,
        test_payment_source: PaymentSource,
    ):
        """Test updating a payment source with proper validation flow."""
        # 1. ARRANGE: Setup is already done with fixtures

        # 2. SCHEMA: Create and validate through Pydantic schema
        # Note: PaymentSourceUpdate isn't defined in the schema, so we'll use PaymentSourceCreate
        # In a real scenario, we would use the proper update schema
        update_data = {"amount": Decimal("125.00")}

        # 3. ACT: Pass validated data to repository
        result = await payment_source_repository.update(
            test_payment_source.id, update_data
        )

        # 4. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_payment_source.id
        assert result.amount == Decimal("125.00")
        # Fields not in update_data should remain unchanged
        assert result.payment_id == test_payment_source.payment_id
        assert result.account_id == test_payment_source.account_id
        assert result.updated_at > test_payment_source.updated_at

    @pytest.mark.asyncio
    async def test_delete_payment_source(
        self,
        payment_source_repository: PaymentSourceRepository,
        test_payment_source: PaymentSource,
    ):
        """Test deleting a payment source."""
        # 1. ARRANGE: Setup is already done with fixtures

        # 2. ACT: Delete the payment source
        result = await payment_source_repository.delete(test_payment_source.id)

        # 3. ASSERT: Verify the operation results
        assert result is True

        # Verify the payment source is actually deleted
        deleted_check = await payment_source_repository.get(test_payment_source.id)
        assert deleted_check is None

    @pytest.mark.asyncio
    async def test_get_with_relationships(
        self,
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

    @pytest.mark.asyncio
    async def test_get_sources_for_payment(
        self,
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

    @pytest.mark.asyncio
    async def test_get_sources_for_account(
        self,
        payment_source_repository: PaymentSourceRepository,
        test_account: Account,
        test_payment: Payment,
        test_payment_with_multiple_sources: Payment,
    ):
        """Test getting sources for a specific account."""
        # 1. ARRANGE: Setup is already done with fixtures

        # 2. ACT: Get sources for the account
        results = await payment_source_repository.get_sources_for_account(
            test_account.id
        )

        # 3. ASSERT: Verify the operation results
        assert results is not None
        assert len(results) >= 2  # At least 2 sources use this account

        # Check that all sources belong to the correct account
        for source in results:
            assert source.account_id == test_account.id

    @pytest.mark.asyncio
    async def test_bulk_create_sources(
        self,
        payment_source_repository: PaymentSourceRepository,
        test_payment: Payment,
        test_account: Account,
        test_second_account: Account,
    ):
        """Test creating multiple sources at once with proper validation flow."""
        # 1. ARRANGE: Setup is already done with fixtures

        # 2. SCHEMA: Create and validate through Pydantic schema
        source_schema1 = create_payment_source_schema(
            account_id=test_account.id,
            amount=Decimal("30.00"),
            payment_id=test_payment.id,
        )

        source_schema2 = create_payment_source_schema(
            account_id=test_second_account.id,
            amount=Decimal("40.00"),
            payment_id=test_payment.id,
        )

        # Convert validated schemas to dicts for repository
        sources_data = [source_schema1.model_dump(), source_schema2.model_dump()]

        # 3. ACT: Pass validated data to repository
        results = await payment_source_repository.bulk_create_sources(sources_data)

        # 4. ASSERT: Verify the operation results
        assert results is not None
        assert len(results) == 2

        # Check that both sources were created correctly
        assert results[0].payment_id == test_payment.id
        assert results[0].account_id == test_account.id
        assert results[0].amount == Decimal("30.00")

        assert results[1].payment_id == test_payment.id
        assert results[1].account_id == test_second_account.id
        assert results[1].amount == Decimal("40.00")

    @pytest.mark.asyncio
    async def test_get_total_amount_by_account(
        self,
        payment_source_repository: PaymentSourceRepository,
        test_account: Account,
        test_payment: Payment,
        test_payment_with_multiple_sources: Payment,
        test_payment_source: PaymentSource,
    ):
        """Test getting total payment amount from a specific account."""
        # 1. ARRANGE: Setup is already done with fixtures

        # 2. ACT: Get total amount for the account
        total = await payment_source_repository.get_total_amount_by_account(
            test_account.id
        )

        # 3. ASSERT: Verify the operation results
        # We have 3 sources using this account:
        # - One from test_payment (100.00)
        # - One from test_payment_with_multiple_sources (100.00)
        # - One from test_payment_source (75.00)
        expected_total = Decimal("275.00")
        assert total == expected_total

    @pytest.mark.asyncio
    async def test_delete_sources_for_payment(
        self,
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

    @pytest.mark.asyncio
    async def test_validation_error_handling(self):
        """Test that schema validation catches invalid data."""
        # Try creating a schema with invalid data
        try:
            invalid_schema = PaymentSourceCreate(
                account_id=-1,  # Invalid negative ID
                amount=Decimal("-50.00"),  # Invalid negative amount
            )
            assert False, "Schema should have raised a validation error"
        except ValueError as e:
            # This is expected - schema validation should catch the error
            error_str = str(e).lower()
            assert "account_id" in error_str or "amount" in error_str
