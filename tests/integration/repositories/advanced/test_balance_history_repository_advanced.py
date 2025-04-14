# pylint: disable=no-member
"""
Integration tests for the BalanceHistoryRepository.

This module contains tests for the BalanceHistoryRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.
"""

from datetime import timedelta
from decimal import Decimal
from typing import List

import pytest

from src.models.accounts import Account
from src.models.balance_history import BalanceHistory
from src.repositories.balance_history import BalanceHistoryRepository
from src.utils.datetime_utils import datetime_equals, datetime_greater_than, utc_now
from tests.helpers.schema_factories.balance_history_schema_factories import (
    create_balance_history_schema,
)

pytestmark = pytest.mark.asyncio


async def test_get_by_account(
    balance_history_repository: BalanceHistoryRepository,
    test_multiple_balances: List[BalanceHistory],
    test_checking_account: Account,
):
    """
    Test retrieving balance history records for an account.

    Args:
        balance_history_repository: Repository fixture for balance history
        test_multiple_balances: Test balance history records fixture
        test_checking_account: Test checking account fixture
    """
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get balances by account ID
    results = await balance_history_repository.get_by_account(test_checking_account.id)

    # 3. ASSERT: Verify the operation results
    assert len(results) >= 3  # At least the 3 balances we created
    for balance in results:
        assert balance.account_id == test_checking_account.id

    # Test with limit
    limited_results = await balance_history_repository.get_by_account(
        test_checking_account.id, limit=2
    )
    assert len(limited_results) == 2

    # Should be ordered by timestamp descending (most recent first)
    assert limited_results[0].balance == Decimal("2000.00")
    assert limited_results[1].balance == Decimal("1500.00")


async def test_get_latest_balance(
    balance_history_repository: BalanceHistoryRepository,
    test_multiple_balances: List[BalanceHistory],
    test_checking_account: Account,
):
    """
    Test retrieving the latest balance for an account.

    Args:
        balance_history_repository: Repository fixture for balance history
        test_multiple_balances: Test balance history records fixture
        test_checking_account: Test checking account fixture
    """
    # 1. ARRANGE: Setup is already done with fixtures
    latest_balance = test_multiple_balances[-1]  # Last in list (most recent)

    # 2. ACT: Get latest balance
    result = await balance_history_repository.get_latest_balance(
        test_checking_account.id
    )

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == latest_balance.id
    assert result.timestamp == latest_balance.timestamp
    assert result.balance == latest_balance.balance


async def test_get_with_account(
    balance_history_repository: BalanceHistoryRepository,
    test_balance_history: BalanceHistory,
    test_checking_account: Account,
):
    """
    Test retrieving a balance history with its associated account.

    Args:
        balance_history_repository: Repository fixture for balance history
        test_balance_history: Test balance history record fixture
        test_checking_account: Test checking account fixture
    """
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get balance with account
    result = await balance_history_repository.get_with_account(test_balance_history.id)

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_balance_history.id
    assert result.account is not None
    assert result.account.id == test_checking_account.id
    assert result.account.name == test_checking_account.name
    assert result.account.account_type == test_checking_account.account_type


async def test_get_by_date_range(
    balance_history_repository: BalanceHistoryRepository,
    test_multiple_balances: List[BalanceHistory],
    test_checking_account: Account,
):
    """
    Test retrieving balance history within a date range.

    Args:
        balance_history_repository: Repository fixture for balance history
        test_multiple_balances: Test balance history records fixture
        test_checking_account: Test checking account fixture
    """
    # 1. ARRANGE: Setup date range parameters
    now = utc_now()
    start_date = now - timedelta(days=15)
    end_date = now - timedelta(days=5)

    # 2. ACT: Get balances within date range
    results = await balance_history_repository.get_by_date_range(
        test_checking_account.id, start_date, end_date
    )

    # 3. ASSERT: Verify the operation results
    assert len(results) >= 1  # Should include at least the 10-day-old balance

    # Check that balances are within range
    for balance in results:
        assert balance.account_id == test_checking_account.id
        # Use proper timezone-aware comparison
        assert datetime_greater_than(
            balance.timestamp, start_date, ignore_timezone=True
        ) or datetime_equals(balance.timestamp, start_date, ignore_timezone=True)
        assert datetime_greater_than(
            end_date, balance.timestamp, ignore_timezone=True
        ) or datetime_equals(end_date, balance.timestamp, ignore_timezone=True)


async def test_get_reconciled_balances(
    balance_history_repository: BalanceHistoryRepository,
    test_multiple_balances: List[BalanceHistory],
    test_checking_account: Account,
):
    """
    Test retrieving reconciled balance records.

    Args:
        balance_history_repository: Repository fixture for balance history
        test_multiple_balances: Test balance history records fixture
        test_checking_account: Test checking account fixture
    """
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get reconciled balances
    results = await balance_history_repository.get_reconciled_balances(
        test_checking_account.id
    )

    # 3. ASSERT: Verify the operation results
    assert len(results) >= 1  # Should find at least the one reconciled balance

    # Check that all results are reconciled
    for balance in results:
        assert balance.account_id == test_checking_account.id
        assert balance.is_reconciled is True


async def test_get_min_max_balance(
    balance_history_repository: BalanceHistoryRepository,
    test_multiple_balances: List[BalanceHistory],
    test_checking_account: Account,
):
    """
    Test retrieving minimum and maximum balance records.

    Args:
        balance_history_repository: Repository fixture for balance history
        test_multiple_balances: Test balance history records fixture
        test_checking_account: Test checking account fixture
    """
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get min and max balances
    min_balance, max_balance = await balance_history_repository.get_min_max_balance(
        test_checking_account.id
    )

    # 3. ASSERT: Verify the operation results
    assert min_balance is not None
    assert max_balance is not None
    assert min_balance.balance == Decimal("1000.00")
    assert max_balance.balance == Decimal("2000.00")


async def test_get_balance_trend(
    balance_history_repository: BalanceHistoryRepository,
    test_multiple_balances: List[BalanceHistory],
    test_checking_account: Account,
):
    """
    Test retrieving balance trend data.

    Args:
        balance_history_repository: Repository fixture for balance history
        test_multiple_balances: Test balance history records fixture
        test_checking_account: Test checking account fixture
    """
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get balance trend
    trend = await balance_history_repository.get_balance_trend(test_checking_account.id)

    # 3. ASSERT: Verify the operation results
    assert len(trend) >= 3  # At least our 3 balances

    # Check that trend contains timestamp and balance pairs
    trend_timestamps = [timestamp for timestamp, _ in trend]
    balances = [balance for _, balance in trend]

    # Verify our balance timestamps and amounts are in the trend
    for balance in test_multiple_balances:
        assert balance.timestamp in trend_timestamps
        assert balance.balance in balances


async def test_get_average_balance(
    balance_history_repository: BalanceHistoryRepository,
    test_multiple_balances: List[BalanceHistory],
    test_checking_account: Account,
):
    """
    Test calculating average balance.

    Args:
        balance_history_repository: Repository fixture for balance history
        test_multiple_balances: Test balance history records fixture
        test_checking_account: Test checking account fixture
    """
    # 1. ARRANGE: Setup is already done with fixtures
    # Our test_multiple_balances has balances of 1000, 1500, and 2000
    expected_average = Decimal("1500.00")  # (1000 + 1500 + 2000) / 3

    # 2. ACT: Get average balance
    result = await balance_history_repository.get_average_balance(
        test_checking_account.id
    )

    # 3. ASSERT: Verify the operation results
    assert result == expected_average

    # Test with custom days parameter (last 15 days)
    # This should only include the last two balances: 1500 and 2000
    result_15days = await balance_history_repository.get_average_balance(
        test_checking_account.id, days=15
    )
    assert result_15days == Decimal("1750.00")  # (1500 + 2000) / 2


async def test_get_balance_history_with_notes(
    balance_history_repository: BalanceHistoryRepository,
    test_checking_account: Account,
):
    """
    Test retrieving balance history records with notes.

    Args:
        balance_history_repository: Repository fixture for balance history
        test_checking_account: Test checking account fixture
    """
    # 1. ARRANGE: Create balances with different note configurations
    now = utc_now()

    # Create schemas with and without notes
    with_note1_schema = create_balance_history_schema(
        account_id=test_checking_account.id,
        balance=Decimal("1100.00"),
        notes="First note entry",
        timestamp=now - timedelta(days=3),
    )

    no_note_schema = create_balance_history_schema(
        account_id=test_checking_account.id,
        balance=Decimal("1200.00"),
        notes=None,  # Explicitly None
        timestamp=now - timedelta(days=2),
    )

    empty_note_schema = create_balance_history_schema(
        account_id=test_checking_account.id,
        balance=Decimal("1300.00"),
        notes="",  # Empty string
        timestamp=now - timedelta(days=1),
    )

    with_note2_schema = create_balance_history_schema(
        account_id=test_checking_account.id,
        balance=Decimal("1400.00"),
        notes="Second note entry",
        timestamp=now,
    )

    # 2. SCHEMA: Convert schemas to dictionaries
    with_note1_data = with_note1_schema.model_dump()
    no_note_data = no_note_schema.model_dump()
    empty_note_data = empty_note_schema.model_dump()
    with_note2_data = with_note2_schema.model_dump()

    # 3. ACT: Create balance entries
    with_note1 = await balance_history_repository.create(with_note1_data)
    no_note = await balance_history_repository.create(no_note_data)
    empty_note = await balance_history_repository.create(empty_note_data)
    with_note2 = await balance_history_repository.create(with_note2_data)

    # Get balances with notes
    results = await balance_history_repository.get_balance_history_with_notes(
        test_checking_account.id
    )

    # 4. ASSERT: Verify the operation results
    assert len(results) >= 2  # At least the two with notes
    assert any(bal.id == with_note1.id for bal in results)
    assert any(bal.id == with_note2.id for bal in results)
    assert not any(bal.id == no_note.id for bal in results)
    assert not any(bal.id == empty_note.id for bal in results)

    # Check that all results have non-empty notes
    for balance in results:
        assert balance.notes is not None
        assert balance.notes != ""


async def test_mark_as_reconciled(
    balance_history_repository: BalanceHistoryRepository,
    test_balance_history: BalanceHistory,
):
    """
    Test marking a balance record as reconciled.

    Args:
        balance_history_repository: Repository fixture for balance history
        test_balance_history: Test balance history record fixture
    """
    # 1. ARRANGE: Setup is already done with fixtures
    # Make sure it's not already reconciled
    assert test_balance_history.is_reconciled is False

    # 2. ACT: Mark as reconciled
    result = await balance_history_repository.mark_as_reconciled(
        test_balance_history.id
    )

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_balance_history.id
    assert result.is_reconciled is True

    # 4. ACT AGAIN: Unmark as reconciled
    result = await balance_history_repository.mark_as_reconciled(
        test_balance_history.id, reconciled=False
    )

    # 5. ASSERT AGAIN: Verify it's now not reconciled
    assert result.is_reconciled is False


async def test_add_balance_note(
    balance_history_repository: BalanceHistoryRepository,
    test_balance_history: BalanceHistory,
):
    """
    Test adding a note to a balance record.

    Args:
        balance_history_repository: Repository fixture for balance history
        test_balance_history: Test balance history record fixture
    """
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Add note to balance record
    new_note = "Updated balance after account review"
    result = await balance_history_repository.add_balance_note(
        test_balance_history.id, new_note
    )

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_balance_history.id
    assert result.notes == new_note

    # 4. ACT AGAIN: Update the note
    updated_note = "Final corrected balance"
    result = await balance_history_repository.add_balance_note(
        test_balance_history.id, updated_note
    )

    # 5. ASSERT AGAIN: Verify the note was updated
    assert result.notes == updated_note


async def test_get_missing_days(
    balance_history_repository: BalanceHistoryRepository,
    test_balance_history_with_gaps: List[BalanceHistory],
    test_checking_account: Account,
):
    """
    Test finding days with no balance records using fixed test data.

    Args:
        balance_history_repository: Repository fixture for balance history
        test_balance_history_with_gaps: Test balance history records with gaps fixture
        test_checking_account: Test checking account fixture
    """
    # 1. ARRANGE: Setup is done with fixture
    # Get the actual dates from our test fixture
    entry_dates = [entry.timestamp.date() for entry in test_balance_history_with_gaps]

    # Get today's date from the most recent entry
    most_recent = max(test_balance_history_with_gaps, key=lambda x: x.timestamp)
    today = most_recent.timestamp.replace(hour=0, minute=0, second=0, microsecond=0)

    # 2. ACT: Get missing days
    missing_days = await balance_history_repository.get_missing_days(
        test_checking_account.id, days=10
    )

    # 3. ASSERT: Verify there are exactly 8 missing days
    # Should find days 1-4 and 6-9 as missing (8 total)
    assert len(missing_days) == 8

    # Check specific days that should be missing
    day_minus_1 = (today - timedelta(days=1)).date()
    day_minus_6 = (today - timedelta(days=6)).date()
    day_minus_9 = (today - timedelta(days=9)).date()

    assert day_minus_1 in missing_days
    assert day_minus_6 in missing_days
    assert day_minus_9 in missing_days

    # Check days that should not be missing
    day_minus_0 = today.date()
    day_minus_5 = (today - timedelta(days=5)).date()
    day_minus_10 = (today - timedelta(days=10)).date()

    assert day_minus_0 not in missing_days
    assert day_minus_5 not in missing_days
    assert day_minus_10 not in missing_days


async def test_get_available_credit_trend(
    balance_history_repository: BalanceHistoryRepository,
    test_credit_account: Account,
):
    """
    Test retrieving available credit trend for a credit account.

    Args:
        balance_history_repository: Repository fixture for balance history
        test_credit_account: Test credit account fixture
    """
    # 1. ARRANGE: Create balance history records with available credit
    ten_days_ago = utc_now() - timedelta(days=10)
    five_days_ago = utc_now() - timedelta(days=5)
    now = utc_now()

    # 2. SCHEMA: Create schemas with available credit
    day1_schema = create_balance_history_schema(
        account_id=test_credit_account.id,
        balance=Decimal("-500.00"),
        available_credit=Decimal("1500.00"),
        timestamp=ten_days_ago,
    )

    day2_schema = create_balance_history_schema(
        account_id=test_credit_account.id,
        balance=Decimal("-700.00"),
        available_credit=Decimal("1300.00"),
        timestamp=five_days_ago,
    )

    day3_schema = create_balance_history_schema(
        account_id=test_credit_account.id,
        balance=Decimal("-900.00"),
        available_credit=Decimal("1100.00"),
        timestamp=now,
    )

    # Convert schemas to dictionaries
    day1_data = day1_schema.model_dump()
    day2_data = day2_schema.model_dump()
    day3_data = day3_schema.model_dump()

    # 3. ACT: Create balance records and get available credit trend
    await balance_history_repository.create(day1_data)
    await balance_history_repository.create(day2_data)
    await balance_history_repository.create(day3_data)

    trend = await balance_history_repository.get_available_credit_trend(
        test_credit_account.id
    )

    # 4. ASSERT: Verify the operation results
    assert len(trend) >= 3

    # Check that the trend contains timestamp and credit pairs
    trend_timestamps = [timestamp for timestamp, _ in trend]
    trend_credits = [credit for _, credit in trend]

    # Verify the expected trend_timestamps are in the trend
    assert ten_days_ago in trend_timestamps
    assert five_days_ago in trend_timestamps
    assert now in trend_timestamps
    assert ten_days_ago < five_days_ago < now

    # Verify the expected credit values are in the trend
    assert Decimal("1500.00") in trend_credits
    assert Decimal("1300.00") in trend_credits
    assert Decimal("1100.00") in trend_credits


async def test_validation_error_handling():
    """
    Test handling of validation errors that would be caught by the Pydantic schema.
    """
    # 1. ARRANGE & ACT & ASSERT: Try creating a schema with invalid data
    try:
        # Use schema factory with invalid data
        create_balance_history_schema(
            account_id=0,  # Invalid account ID
            balance=Decimal("-100.00"),  # Valid but negative
            is_reconciled="not_a_boolean",  # Invalid type for boolean field
        )
        assert False, "Schema should have raised a validation error"
    except ValueError as e:
        # This is expected - schema validation should catch the error
        error_str = str(e).lower()
        assert "account_id" in error_str or "is_reconciled" in error_str
