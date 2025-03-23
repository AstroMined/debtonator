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
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.liabilities import Liability
from src.models.payments import Payment, PaymentSource
from src.repositories.accounts import AccountRepository
from src.repositories.liabilities import LiabilityRepository
from src.repositories.payments import PaymentRepository
from src.schemas.payments import (PaymentCreate, PaymentDateRange,
                                  PaymentSourceCreate, PaymentUpdate)
from tests.helpers.datetime_utils import utc_now
from tests.helpers.schema_factories.accounts import create_account_schema
from tests.helpers.schema_factories.liabilities import create_liability_schema
from tests.helpers.schema_factories.payment_sources import \
    create_payment_source_schema
from tests.helpers.schema_factories.payments import (
    create_payment_date_range_schema, create_payment_schema)


@pytest_asyncio.fixture
async def payment_repository(db_session: AsyncSession) -> PaymentRepository:
    """Fixture for PaymentRepository with test database session."""
    return PaymentRepository(db_session)


@pytest_asyncio.fixture
async def account_repository(db_session: AsyncSession) -> AccountRepository:
    """Fixture for AccountRepository with test database session."""
    return AccountRepository(db_session)


@pytest_asyncio.fixture
async def liability_repository(db_session: AsyncSession) -> LiabilityRepository:
    """Fixture for LiabilityRepository with test database session."""
    return LiabilityRepository(db_session)


@pytest_asyncio.fixture
async def test_account(account_repository: AccountRepository) -> Account:
    """Create a test account for use in tests."""
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
    """Create a second test account for use in split payment tests."""
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
async def test_liability(
    liability_repository: LiabilityRepository, test_account: Account
) -> Liability:
    """Create a test liability for use in tests."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. SCHEMA: Create and validate through Pydantic schema
    due_date = utc_now() + timedelta(days=15)
    liability_schema = create_liability_schema(
        name="Test Bill",
        amount=Decimal("150.00"),
        due_date=due_date,
        category_id=1,  # Assuming category ID 1 exists
        primary_account_id=test_account.id,
    )

    # Convert validated schema to dict for repository
    validated_data = liability_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    return await liability_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_payment(
    payment_repository: PaymentRepository,
    test_account: Account,
    test_liability: Liability,
) -> Payment:
    """Create a test payment for use in tests."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. SCHEMA: Create and validate through Pydantic schema
    payment_schema = create_payment_schema(
        amount=Decimal("50.00"),
        payment_date=utc_now(),
        category="Utilities",
        description="Test payment for utilities",
        liability_id=test_liability.id,
        sources=[
            {
                "account_id": test_account.id,
                "amount": Decimal("50.00"),
            }
        ],
    )

    # Convert validated schema to dict for repository
    validated_data = payment_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    return await payment_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_multiple_payments(
    payment_repository: PaymentRepository,
    test_account: Account,
    test_second_account: Account,
    test_liability: Liability,
) -> List[Payment]:
    """Create multiple test payments with different dates and categories."""
    # 1. ARRANGE: Setup payment dates and categories
    now = utc_now()
    payment_data = [
        # Recent utility payment
        {
            "amount": Decimal("75.00"),
            "payment_date": now - timedelta(days=5),
            "category": "Utilities",
            "liability_id": test_liability.id,
            "sources": [{"account_id": test_account.id, "amount": Decimal("75.00")}],
        },
        # Older rent payment
        {
            "amount": Decimal("800.00"),
            "payment_date": now - timedelta(days=25),
            "category": "Rent",
            "sources": [{"account_id": test_account.id, "amount": Decimal("800.00")}],
        },
        # Split payment for insurance
        {
            "amount": Decimal("120.00"),
            "payment_date": now - timedelta(days=10),
            "category": "Insurance",
            "sources": [
                {"account_id": test_account.id, "amount": Decimal("60.00")},
                {"account_id": test_second_account.id, "amount": Decimal("60.00")},
            ],
        },
        # Future payment (scheduled)
        {
            "amount": Decimal("45.00"),
            "payment_date": now + timedelta(days=5),
            "category": "Subscription",
            "sources": [{"account_id": test_account.id, "amount": Decimal("45.00")}],
        },
    ]

    payments = []
    for data in payment_data:
        # 2. SCHEMA: Create and validate through Pydantic schema
        payment_schema = create_payment_schema(**data)

        # Convert validated schema to dict for repository
        validated_data = payment_schema.model_dump()

        # 3. ACT: Pass validated data to repository
        payment = await payment_repository.create(validated_data)
        payments.append(payment)

    return payments


class TestPaymentRepository:
    """
    Tests for the PaymentRepository.

    These tests follow the standard 4-step pattern (Arrange-Schema-Act-Assert)
    for repository testing, simulating proper service-to-repository validation flow.
    """

    @pytest.mark.asyncio
    async def test_create_payment(
        self,
        payment_repository: PaymentRepository,
        test_account: Account,
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
                    "account_id": test_account.id,
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
        assert result.sources[0].account_id == test_account.id
        assert result.sources[0].amount == Decimal("100.00")

    @pytest.mark.asyncio
    async def test_create_split_payment(
        self,
        payment_repository: PaymentRepository,
        test_account: Account,
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
                    "account_id": test_account.id,
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
        source1 = next(s for s in result.sources if s.account_id == test_account.id)
        source2 = next(
            s for s in result.sources if s.account_id == test_second_account.id
        )

        assert source1.amount == Decimal("100.00")
        assert source2.amount == Decimal("50.00")

    @pytest.mark.asyncio
    async def test_get_payment(
        self,
        payment_repository: PaymentRepository,
        test_payment: Payment,
    ):
        """Test retrieving a payment by ID."""
        # 1. ARRANGE: Setup is already done with fixtures

        # 2. ACT: Get the payment by ID
        result = await payment_repository.get(test_payment.id)

        # 3. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_payment.id
        assert result.amount == test_payment.amount
        assert result.payment_date == test_payment.payment_date
        assert result.category == test_payment.category
        assert result.description == test_payment.description
        assert result.liability_id == test_payment.liability_id

    @pytest.mark.asyncio
    async def test_update_payment(
        self,
        payment_repository: PaymentRepository,
        test_payment: Payment,
    ):
        """Test updating a payment with proper validation flow."""
        # 1. ARRANGE: Setup is already done with fixtures

        # 2. SCHEMA: Create and validate update data through Pydantic schema
        update_schema = PaymentUpdate(
            id=test_payment.id,
            amount=Decimal("75.00"),
            category="Updated Category",
            description="Updated payment description",
        )

        # Convert validated schema to dict for repository
        update_data = update_schema.model_dump(exclude={"id"})

        # 3. ACT: Pass validated data to repository
        result = await payment_repository.update(test_payment.id, update_data)

        # 4. ASSERT: Verify the operation results
        assert result is not None
        assert result.id == test_payment.id
        assert result.amount == Decimal("75.00")
        assert result.category == "Updated Category"
        assert result.description == "Updated payment description"
        # Fields not in update_data should remain unchanged
        assert result.payment_date == test_payment.payment_date
        assert result.liability_id == test_payment.liability_id
        assert result.updated_at > test_payment.updated_at

    @pytest.mark.asyncio
    async def test_delete_payment(
        self,
        payment_repository: PaymentRepository,
        test_payment: Payment,
    ):
        """Test deleting a payment."""
        # 1. ARRANGE: Setup is already done with fixtures

        # 2. ACT: Delete the payment
        result = await payment_repository.delete(test_payment.id)

        # 3. ASSERT: Verify the operation results
        assert result is True

        # Verify the payment is actually deleted
        deleted_check = await payment_repository.get(test_payment.id)
        assert deleted_check is None

    @pytest.mark.asyncio
    async def test_get_with_sources(
        self,
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

    @pytest.mark.asyncio
    async def test_get_with_relationships(
        self,
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

    @pytest.mark.asyncio
    async def test_get_payments_for_bill(
        self,
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

    @pytest.mark.asyncio
    async def test_get_payments_for_account(
        self,
        payment_repository: PaymentRepository,
        test_payment: Payment,
        test_account: Account,
    ):
        """Test getting payments for a specific account."""
        # 1. ARRANGE: Setup is already done with fixtures

        # 2. ACT: Get payments for account
        results = await payment_repository.get_payments_for_account(test_account.id)

        # 3. ASSERT: Verify the operation results
        assert len(results) >= 1

        # Check that our test payment is in the results
        payment_ids = [p.id for p in results]
        assert test_payment.id in payment_ids

    @pytest.mark.asyncio
    async def test_get_payments_in_date_range(
        self,
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
            assert payment.payment_date >= start_date
            assert payment.payment_date <= end_date

    @pytest.mark.asyncio
    async def test_get_payments_by_category(
        self,
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

    @pytest.mark.asyncio
    async def test_get_total_amount_in_range(
        self,
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

    @pytest.mark.asyncio
    async def test_get_total_amount_by_category(
        self,
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
        assert total >= Decimal(
            "75.00"
        )  # From utilities payment in test_multiple_payments

    @pytest.mark.asyncio
    async def test_get_recent_payments(
        self,
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
            assert payment.payment_date >= cutoff_date

    @pytest.mark.asyncio
    async def test_validation_error_handling(self):
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
