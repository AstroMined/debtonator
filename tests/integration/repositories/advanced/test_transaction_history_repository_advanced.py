"""
Integration tests for the TransactionHistoryRepository.

This module contains tests for the TransactionHistoryRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.

Implements ADR-011 compliant datetime handling with utilities from datetime_utils.
"""

from decimal import Decimal
from typing import List

import pytest

from src.models.accounts import Account
from src.models.transaction_history import TransactionHistory, TransactionType
from src.repositories.transaction_history import TransactionHistoryRepository
from src.schemas.transaction_history import TransactionHistoryCreate
from src.utils.datetime_utils import (
    datetime_equals,
    datetime_greater_than,
    days_ago,
    end_of_day,
    start_of_day,
    utc_now,
)
from tests.helpers.schema_factories.transaction_history_schema_factories import (
    create_transaction_history_schema,
)

pytestmark = pytest.mark.asyncio


async def test_get_by_account(
    transaction_history_repository: TransactionHistoryRepository,
    test_checking_account: Account,
    test_multiple_transactions: List[TransactionHistory],
):
    """Test getting transaction history entries for an account."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get transaction entries for the account
    results = await transaction_history_repository.get_by_account(
        test_checking_account.id
    )

    # 3. ASSERT: Verify the operation results
    assert len(results) >= 7  # At least 7 entries from fixture
    for entry in results:
        assert entry.account_id == test_checking_account.id


async def test_get_with_account(
    transaction_history_repository: TransactionHistoryRepository,
    test_transaction_history: TransactionHistory,
):
    """Test getting a transaction history entry with account relationship loaded."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get the transaction entry with account
    result = await transaction_history_repository.get_with_account(
        test_transaction_history.id
    )

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_transaction_history.id
    assert result.account is not None
    assert result.account.id == test_transaction_history.account_id


async def test_get_by_date_range(
    transaction_history_repository: TransactionHistoryRepository,
    test_checking_account: Account,
    test_date_range_transactions: List[TransactionHistory],
):
    """Test getting transaction history entries within a date range.

    Uses ADR-011 compliant datetime handling with utilities.
    Uses test_date_range_transactions fixture with known date patterns.
    """
    # 1. ARRANGE: Use specific date range with transactions at known dates
    # Our fixture creates transactions at days 5, 10, 15, 20, 25, 30, 45, 60 ago

    # Use a date range that should capture 4 transactions (days 10-25 ago)
    start_date = start_of_day(days_ago(25))
    end_date = end_of_day(days_ago(10))

    # 2. ACT: Get transaction entries within date range
    results = await transaction_history_repository.get_by_date_range(
        test_checking_account.id, start_date, end_date
    )

    # 3. ASSERT: Verify the operation results
    # We expect exactly 4 transactions in this range (days 10, 15, 20, 25 ago)
    assert len(results) == 4

    for entry in results:
        assert entry.account_id == test_checking_account.id

        # Use ADR-011 compliant date comparison utilities
        # Database-agnostic date comparison
        assert datetime_greater_than(
            entry.transaction_date, start_date, ignore_timezone=True
        ) or datetime_equals(entry.transaction_date, start_date, ignore_timezone=True)
        assert datetime_greater_than(
            end_date, entry.transaction_date, ignore_timezone=True
        ) or datetime_equals(entry.transaction_date, end_date, ignore_timezone=True)


async def test_get_by_type(
    transaction_history_repository: TransactionHistoryRepository,
    test_checking_account: Account,
    test_multiple_transactions: List[TransactionHistory],
):
    """Test getting transaction history entries by type."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get credit transactions
    credit_results = await transaction_history_repository.get_by_type(
        test_checking_account.id, TransactionType.CREDIT
    )

    # Get debit transactions
    debit_results = await transaction_history_repository.get_by_type(
        test_checking_account.id, TransactionType.DEBIT
    )

    # 3. ASSERT: Verify the operation results
    assert len(credit_results) >= 3  # At least 3 credit transactions in fixture
    for entry in credit_results:
        assert entry.account_id == test_checking_account.id
        assert entry.transaction_type == TransactionType.CREDIT

    assert len(debit_results) >= 4  # At least 4 debit transactions in fixture
    for entry in debit_results:
        assert entry.account_id == test_checking_account.id
        assert entry.transaction_type == TransactionType.DEBIT


async def test_search_by_description(
    transaction_history_repository: TransactionHistoryRepository,
    test_checking_account: Account,
    test_multiple_transactions: List[TransactionHistory],
):
    """Test searching transaction history entries by description."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Search for transactions with 'deposit' in description
    results = await transaction_history_repository.search_by_description(
        test_checking_account.id, "deposit"
    )

    # 3. ASSERT: Verify the operation results
    assert len(results) >= 1  # At least 1 transaction has 'deposit' in description
    for entry in results:
        assert entry.account_id == test_checking_account.id
        assert "deposit" in entry.description.lower()


async def test_get_total_by_type(
    transaction_history_repository: TransactionHistoryRepository,
    test_checking_account: Account,
    test_multiple_transactions: List[TransactionHistory],
):
    """Test calculating total amount for transactions of a specific type."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get total credit amount
    credit_total = await transaction_history_repository.get_total_by_type(
        test_checking_account.id, TransactionType.CREDIT
    )

    # Get total debit amount
    debit_total = await transaction_history_repository.get_total_by_type(
        test_checking_account.id, TransactionType.DEBIT
    )

    # 3. ASSERT: Verify the operation results
    assert credit_total >= Decimal("950.00")  # Sum of credit transactions in fixture
    assert debit_total >= Decimal("280.50")  # Sum of debit transactions in fixture


async def test_get_transaction_count(
    transaction_history_repository: TransactionHistoryRepository,
    test_checking_account: Account,
    test_multiple_transactions: List[TransactionHistory],
):
    """Test counting transactions by type."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get transaction counts by type
    counts = await transaction_history_repository.get_transaction_count(
        test_checking_account.id
    )

    # 3. ASSERT: Verify the operation results
    assert TransactionType.CREDIT.value in counts
    assert TransactionType.DEBIT.value in counts
    assert (
        counts[TransactionType.CREDIT.value] >= 3
    )  # At least 3 credit transactions in fixture
    assert (
        counts[TransactionType.DEBIT.value] >= 4
    )  # At least 4 debit transactions in fixture


async def test_get_net_change(
    transaction_history_repository: TransactionHistoryRepository,
    test_checking_account: Account,
    test_multiple_transactions: List[TransactionHistory],
):
    """Test calculating net change in account balance from transactions."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get net change
    net_change = await transaction_history_repository.get_net_change(
        test_checking_account.id
    )

    # 3. ASSERT: Verify the operation results
    # Net change should be credits - debits (950.00 - 280.50 = 669.50)
    assert net_change >= Decimal("650.00")


async def test_get_monthly_totals(
    transaction_history_repository: TransactionHistoryRepository,
    test_checking_account: Account,
    test_multiple_transactions: List[TransactionHistory],
):
    """Test getting monthly transaction totals."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get monthly totals
    monthly_totals = await transaction_history_repository.get_monthly_totals(
        test_checking_account.id, months=2
    )

    # 3. ASSERT: Verify the operation results
    assert len(monthly_totals) >= 1  # At least 1 month of data

    for month_data in monthly_totals:
        assert "month" in month_data
        assert "credits" in month_data
        assert "debits" in month_data
        assert "net" in month_data
        assert month_data["net"] == month_data["credits"] - month_data["debits"]


async def test_get_transaction_patterns(
    transaction_history_repository: TransactionHistoryRepository,
    test_checking_account: Account,
    test_recurring_transaction_patterns: List[TransactionHistory],
):
    """Test identifying recurring transaction patterns.

    Uses ADR-011 compliant datetime handling with utilities.
    Uses test_recurring_transaction_patterns fixture that creates:
    - 4 weekly grocery transactions (Weekly Grocery Shopping)
    - 2 monthly bill payments (Monthly Internet Bill)
    """
    # 1. ARRANGE: Setup is already done with the fixture

    # 2. ACT: Analyze transaction patterns
    patterns = await transaction_history_repository.get_transaction_patterns(
        test_checking_account.id
    )

    # 3. ASSERT: Verify the operation results
    assert len(patterns) >= 2  # At least 2 patterns (grocery and internet)

    has_grocery_pattern = False
    has_bill_pattern = False

    for pattern in patterns:
        if "grocery" in pattern["description"].lower():
            has_grocery_pattern = True
            assert pattern["count"] >= 4
            if "pattern_type" in pattern:
                assert "weekly" in pattern["pattern_type"].lower()

        if "internet" in pattern["description"].lower():
            has_bill_pattern = True
            assert pattern["count"] >= 2
            if "pattern_type" in pattern:
                assert "month" in pattern["pattern_type"].lower()

    assert has_grocery_pattern
    assert has_bill_pattern


async def test_bulk_create_transactions(
    transaction_history_repository: TransactionHistoryRepository,
    test_checking_account: Account,
):
    """Test creating multiple transactions in bulk.

    Uses ADR-011 compliant datetime handling with utilities.
    """
    # 1. ARRANGE: Prepare multiple transaction schemas using ADR-011 utilities

    transaction_schemas = [
        create_transaction_history_schema(
            account_id=test_checking_account.id,
            amount=Decimal("25.00"),
            transaction_type=TransactionType.DEBIT,
            description="Coffee shop",
            transaction_date=days_ago(1),
        ),
        create_transaction_history_schema(
            account_id=test_checking_account.id,
            amount=Decimal("45.00"),
            transaction_type=TransactionType.DEBIT,
            description="Restaurant",
            transaction_date=days_ago(2),
        ),
        create_transaction_history_schema(
            account_id=test_checking_account.id,
            amount=Decimal("60.00"),
            transaction_type=TransactionType.DEBIT,
            description="Gas station",
            transaction_date=days_ago(3),
        ),
    ]

    # Convert schemas to dicts
    transaction_data = [schema.model_dump() for schema in transaction_schemas]

    # 2. ACT: Bulk create transactions
    results = await transaction_history_repository.bulk_create_transactions(
        test_checking_account.id, transaction_data
    )

    # 3. ASSERT: Verify the operation results
    assert len(results) == 3
    assert all(tx.account_id == test_checking_account.id for tx in results)
    assert any(tx.description == "Coffee shop" for tx in results)
    assert any(tx.description == "Restaurant" for tx in results)
    assert any(tx.description == "Gas station" for tx in results)


async def test_validation_error_handling():
    """Test handling of validation errors that would be caught by the Pydantic schema.

    Uses ADR-011 compliant datetime handling with utilities.
    """
    # Try creating a schema with invalid data
    try:
        invalid_schema = TransactionHistoryCreate(
            account_id=999,
            amount=Decimal("-10.00"),  # Negative amount
            transaction_type=TransactionType.CREDIT,
            transaction_date=utc_now(),  # Use ADR-011 compliant utility
        )
        assert False, "Schema should have raised a validation error for negative amount"
    except ValueError as e:
        # This is expected - schema validation should catch the error
        assert "amount" in str(e).lower()
