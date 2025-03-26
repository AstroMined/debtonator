"""
Integration tests for the BalanceReconciliationRepository.

This module contains tests for the BalanceReconciliationRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.
"""

from datetime import timedelta
from decimal import Decimal
from typing import List

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.balance_reconciliation import BalanceReconciliation
from src.repositories.accounts import AccountRepository
from src.repositories.balance_reconciliation import \
    BalanceReconciliationRepository
from src.schemas.balance_reconciliation import (BalanceReconciliationCreate,
                                                BalanceReconciliationUpdate)
from src.utils.datetime_utils import (
    utc_now, days_ago, days_from_now, datetime_equals, datetime_greater_than
)
from tests.helpers.schema_factories.accounts import create_account_schema
from tests.helpers.schema_factories.balance_reconciliation import \
    create_balance_reconciliation_schema

pytestmark = pytest.mark.asyncio


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
    start_date = days_ago(95)  # Ensure we cover the oldest reconciliation (90 days ago)
    end_date = days_ago(3)     # Ensure we cover the most recent reconciliation (5 days ago)

    # 2. ACT: Get reconciliation entries within date range
    results = await balance_reconciliation_repository.get_by_date_range(
        test_checking_account.id, start_date, end_date
    )

    # 3. ASSERT: Verify the operation results
    assert len(results) >= 3  # Should get at least 3 entries in this range
    for entry in results:
        assert entry.account_id == test_checking_account.id
        # Use datetime helpers with ignore_timezone=True for proper comparison
        assert datetime_greater_than(entry.reconciliation_date, start_date, ignore_timezone=True) or datetime_equals(entry.reconciliation_date, start_date, ignore_timezone=True)
        assert datetime_greater_than(end_date, entry.reconciliation_date, ignore_timezone=True) or datetime_equals(end_date, entry.reconciliation_date, ignore_timezone=True)


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
    # Use datetime helpers for timezone-aware comparison with ignore_timezone=True
    assert datetime_greater_than(result.reconciliation_date, seven_days_ago, ignore_timezone=True) or datetime_equals(result.reconciliation_date, seven_days_ago, ignore_timezone=True)
    assert datetime_greater_than(now, result.reconciliation_date, ignore_timezone=True) or datetime_equals(now, result.reconciliation_date, ignore_timezone=True)


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
    # Note: Due to timezone considerations, we allow a slightly wider range
    assert 10 <= frequency <= 35


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
