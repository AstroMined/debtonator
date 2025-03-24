"""
Integration tests for the BalanceReconciliationRepository.

This module contains tests for the BalanceReconciliationRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.
"""

from datetime import datetime, timedelta
from decimal import Decimal
from typing import List

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.balance_reconciliation import BalanceReconciliation
from src.repositories.accounts import AccountRepository
from src.repositories.balance_reconciliation import BalanceReconciliationRepository
from src.schemas.balance_reconciliation import (
    BalanceReconciliationCreate,
    BalanceReconciliationUpdate,
)
from tests.helpers.datetime_utils import utc_now
from tests.helpers.schema_factories.accounts import create_account_schema
from tests.helpers.schema_factories.balance_reconciliation import (
    create_balance_reconciliation_schema,
)

pytestmark = pytest.mark.asyncio


@pytest_asyncio.fixture
async def balance_reconciliation_repository(
    db_session: AsyncSession,
) -> BalanceReconciliationRepository:
    """Fixture for BalanceReconciliationRepository with test database session."""
    return BalanceReconciliationRepository(db_session)


@pytest_asyncio.fixture
async def test_checking_account(account_repository: AccountRepository) -> Account:
    """Create a test account for use in tests."""
    # Create and validate through Pydantic schema
    account_schema = create_account_schema(
        name="Test Checking Account",
        account_type="checking",
        available_balance=Decimal("1000.00"),
    )

    # Convert validated schema to dict for repository
    validated_data = account_schema.model_dump()

    # Create account through repository
    return await account_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_balance_reconciliation(
    balance_reconciliation_repository: BalanceReconciliationRepository,
    test_checking_account: Account,
) -> BalanceReconciliation:
    """Create a test balance reconciliation entry for use in tests."""
    # Create and validate through Pydantic schema
    reconciliation_schema = create_balance_reconciliation_schema(
        account_id=test_checking_account.id,
        previous_balance=Decimal("1000.00"),
        new_balance=Decimal("1025.50"),
        reason="Initial reconciliation after transaction verification",
    )

    # Convert validated schema to dict for repository
    validated_data = reconciliation_schema.model_dump()

    # Create reconciliation entry through repository
    return await balance_reconciliation_repository.create(validated_data)


@pytest_asyncio.fixture
async def test_multiple_reconciliations(
    balance_reconciliation_repository: BalanceReconciliationRepository,
    test_checking_account: Account,
) -> List[BalanceReconciliation]:
    """Create multiple balance reconciliation entries for testing."""
    now = utc_now()

    # Create multiple reconciliation entries with different dates
    entries = []

    for i, days_ago in enumerate([90, 60, 30, 15, 5]):
        schema = create_balance_reconciliation_schema(
            account_id=test_checking_account.id,
            previous_balance=Decimal(f"{1000 + (i * 50)}.00"),
            new_balance=Decimal(f"{1000 + ((i + 1) * 50)}.00"),
            reason=f"Reconciliation #{i + 1}",
            reconciliation_date=now - timedelta(days=days_ago),
        )

        entry = await balance_reconciliation_repository.create(schema.model_dump())
        entries.append(entry)

    return entries


async def test_create_balance_reconciliation(
    balance_reconciliation_repository: BalanceReconciliationRepository,
    test_checking_account: Account,
):
    """Test creating a balance reconciliation entry with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. SCHEMA: Create and validate through Pydantic schema
    reconciliation_schema = create_balance_reconciliation_schema(
        account_id=test_checking_account.id,
        previous_balance=Decimal("1000.00"),
        new_balance=Decimal("1050.00"),
        reason="Monthly balance verification",
    )

    # Convert validated schema to dict for repository
    validated_data = reconciliation_schema.model_dump()

    # 3. ACT: Pass validated data to repository
    result = await balance_reconciliation_repository.create(validated_data)

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id is not None
    assert result.account_id == test_checking_account.id
    assert result.previous_balance == Decimal("1000.00")
    assert result.new_balance == Decimal("1050.00")
    assert result.adjustment_amount == Decimal("50.00")
    assert result.reason == "Monthly balance verification"
    assert result.reconciliation_date is not None


async def test_get_balance_reconciliation(
    balance_reconciliation_repository: BalanceReconciliationRepository,
    test_balance_reconciliation: BalanceReconciliation,
):
    """Test retrieving a balance reconciliation entry by ID."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get the reconciliation entry
    result = await balance_reconciliation_repository.get(test_balance_reconciliation.id)

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_balance_reconciliation.id
    assert result.account_id == test_balance_reconciliation.account_id
    assert result.previous_balance == test_balance_reconciliation.previous_balance
    assert result.new_balance == test_balance_reconciliation.new_balance
    assert result.adjustment_amount == test_balance_reconciliation.adjustment_amount
    assert result.reason == test_balance_reconciliation.reason


async def test_update_balance_reconciliation(
    balance_reconciliation_repository: BalanceReconciliationRepository,
    test_balance_reconciliation: BalanceReconciliation,
):
    """Test updating a balance reconciliation entry with proper validation flow."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. SCHEMA: Create and validate update data through Pydantic schema
    update_schema = BalanceReconciliationUpdate(
        id=test_balance_reconciliation.id,
        new_balance=Decimal("1075.25"),
        reason="Updated reconciliation with corrected balance",
    )

    # Calculate new adjustment amount
    adjustment_amount = (
        Decimal("1075.25") - test_balance_reconciliation.previous_balance
    )

    # Convert validated schema to dict for repository
    update_data = update_schema.model_dump(exclude={"id"})
    update_data["adjustment_amount"] = adjustment_amount

    # 3. ACT: Pass validated data to repository
    result = await balance_reconciliation_repository.update(
        test_balance_reconciliation.id, update_data
    )

    # 4. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_balance_reconciliation.id
    assert result.new_balance == Decimal("1075.25")
    assert result.adjustment_amount == adjustment_amount
    assert result.reason == "Updated reconciliation with corrected balance"
    assert result.updated_at > test_balance_reconciliation.updated_at


async def test_get_by_account(
    balance_reconciliation_repository: BalanceReconciliationRepository,
    test_checking_account: Account,
    test_multiple_reconciliations: List[BalanceReconciliation],
):
    """Test getting balance reconciliation entries for an account."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get reconciliation entries for the account
    results = await balance_reconciliation_repository.get_by_account(
        test_checking_account.id
    )

    # 3. ASSERT: Verify the operation results
    assert len(results) >= 5  # At least 5 entries from fixture
    for entry in results:
        assert entry.account_id == test_checking_account.id


async def test_get_with_account(
    balance_reconciliation_repository: BalanceReconciliationRepository,
    test_balance_reconciliation: BalanceReconciliation,
):
    """Test getting a balance reconciliation entry with account relationship loaded."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get the reconciliation entry with account
    result = await balance_reconciliation_repository.get_with_account(
        test_balance_reconciliation.id
    )

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_balance_reconciliation.id
    assert result.account is not None
    assert result.account.id == test_balance_reconciliation.account_id


async def test_get_by_date_range(
    balance_reconciliation_repository: BalanceReconciliationRepository,
    test_checking_account: Account,
    test_multiple_reconciliations: List[BalanceReconciliation],
):
    """Test getting balance reconciliation entries within a date range."""
    # 1. ARRANGE: Setup is already done with fixtures
    now = utc_now()
    start_date = now - timedelta(days=70)
    end_date = now - timedelta(days=10)

    # 2. ACT: Get reconciliation entries within date range
    results = await balance_reconciliation_repository.get_by_date_range(
        test_checking_account.id, start_date, end_date
    )

    # 3. ASSERT: Verify the operation results
    assert len(results) >= 3  # Should get at least 3 entries in this range
    for entry in results:
        assert entry.account_id == test_checking_account.id
        assert entry.reconciliation_date >= start_date
        assert entry.reconciliation_date <= end_date


async def test_get_most_recent(
    balance_reconciliation_repository: BalanceReconciliationRepository,
    test_checking_account: Account,
    test_multiple_reconciliations: List[BalanceReconciliation],
):
    """Test getting the most recent balance reconciliation for an account."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get most recent reconciliation
    result = await balance_reconciliation_repository.get_most_recent(
        test_checking_account.id
    )

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.account_id == test_checking_account.id

    # Should be the most recent one (5 days ago)
    now = utc_now()
    five_days_ago = now - timedelta(days=5)
    seven_days_ago = now - timedelta(days=7)
    assert result.reconciliation_date >= seven_days_ago
    assert result.reconciliation_date <= now


async def test_get_largest_adjustments(
    balance_reconciliation_repository: BalanceReconciliationRepository,
    test_checking_account: Account,
    test_multiple_reconciliations: List[BalanceReconciliation],
):
    """Test getting largest balance adjustments by absolute value."""
    # 1. ARRANGE: Setup is already done with fixtures

    # Create a large negative adjustment
    negative_schema = create_balance_reconciliation_schema(
        account_id=test_checking_account.id,
        previous_balance=Decimal("1000.00"),
        new_balance=Decimal("850.00"),
        reason="Large negative adjustment",
    )
    await balance_reconciliation_repository.create(negative_schema.model_dump())

    # Create a large positive adjustment
    positive_schema = create_balance_reconciliation_schema(
        account_id=test_checking_account.id,
        previous_balance=Decimal("1000.00"),
        new_balance=Decimal("1200.00"),
        reason="Large positive adjustment",
    )
    await balance_reconciliation_repository.create(positive_schema.model_dump())

    # 2. ACT: Get largest adjustments
    results = await balance_reconciliation_repository.get_largest_adjustments(
        account_id=test_checking_account.id, limit=2
    )

    # 3. ASSERT: Verify the operation results
    assert len(results) == 2
    for entry in results:
        assert entry.account_id == test_checking_account.id
        # Either the -150 or +200 adjustment should be in top 2
        assert abs(entry.adjustment_amount) >= Decimal("50")


async def test_get_total_adjustment_amount(
    balance_reconciliation_repository: BalanceReconciliationRepository,
    test_checking_account: Account,
    test_multiple_reconciliations: List[BalanceReconciliation],
):
    """Test calculating total adjustment amount for an account."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get total adjustment amount
    total = await balance_reconciliation_repository.get_total_adjustment_amount(
        test_checking_account.id
    )

    # 3. ASSERT: Verify the operation results
    assert total is not None
    # In the fixture, we have 5 adjustments of 50 each
    assert total >= Decimal("200")


async def test_get_adjustment_count_by_reason(
    balance_reconciliation_repository: BalanceReconciliationRepository,
    test_checking_account: Account,
    test_multiple_reconciliations: List[BalanceReconciliation],
):
    """Test counting adjustments grouped by reason."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get counts by reason
    result = await balance_reconciliation_repository.get_adjustment_count_by_reason(
        test_checking_account.id
    )

    # 3. ASSERT: Verify the operation results
    assert len(result) >= 5  # Should have at least 5 distinct reasons

    # Check that the reasons from our fixtures are in the results
    for i in range(1, 6):
        reason = f"Reconciliation #{i}"
        assert reason in result
        assert result[reason] == 1


async def test_get_reconciliation_frequency(
    balance_reconciliation_repository: BalanceReconciliationRepository,
    test_checking_account: Account,
    test_multiple_reconciliations: List[BalanceReconciliation],
):
    """Test calculating average days between reconciliations."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get reconciliation frequency
    frequency = await balance_reconciliation_repository.get_reconciliation_frequency(
        test_checking_account.id
    )

    # 3. ASSERT: Verify the operation results
    assert frequency > 0
    # In the fixture, we have reconciliations at 90, 60, 30, 15, and 5 days ago
    # So the average gap should be around 21-22 days
    assert 15 <= frequency <= 30


async def test_validation_error_handling():
    """Test handling of validation errors that would be caught by the Pydantic schema."""
    # Try creating a schema with invalid data
    try:
        invalid_schema = BalanceReconciliationCreate(
            account_id=999,
            previous_balance=Decimal("1000.00"),
            new_balance=Decimal(
                "1000.00"
            ),  # Same as previous, so adjustment would be 0
            adjustment_amount=Decimal("100.00"),  # Inconsistent with balance difference
            reason="",  # Empty reason
            reconciliation_date=utc_now(),
        )
        assert False, "Schema should have raised a validation error"
    except ValueError as e:
        # This is expected - schema validation should catch the error
        error_str = str(e).lower()
        assert "reason" in error_str or "adjustment" in error_str
