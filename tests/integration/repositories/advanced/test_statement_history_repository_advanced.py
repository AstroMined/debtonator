"""
Integration tests for the StatementHistoryRepository.

This module contains tests for the StatementHistoryRepository using the
standard 4-step pattern (Arrange-Schema-Act-Assert) to properly simulate
the validation flow from services to repositories.
"""

from datetime import timedelta
from decimal import Decimal
from typing import List, Tuple

import pytest

from src.models.accounts import Account
from src.models.statement_history import StatementHistory
from src.repositories.statement_history import StatementHistoryRepository
from src.schemas.statement_history import StatementHistoryCreate
from src.utils.datetime_utils import (
    datetime_equals,
    datetime_greater_than,
    days_ago,
    days_from_now,
    utc_now,
)
from tests.helpers.schema_factories.statement_history_schema_factories import (
    create_statement_history_schema,
)

pytestmark = pytest.mark.asyncio


async def test_get_by_account(
    statement_history_repository: StatementHistoryRepository,
    test_multiple_statements: List[StatementHistory],
    test_credit_account: Account,
):
    """Test retrieving statement history records for an account."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get statements by account ID
    results = await statement_history_repository.get_by_account(test_credit_account.id)

    # 3. ASSERT: Verify the operation results
    assert len(results) >= 3  # At least the 3 statements we created
    for statement in results:
        assert statement.account_id == test_credit_account.id

    # Test with limit
    limited_results = await statement_history_repository.get_by_account(
        test_credit_account.id, limit=2
    )
    assert len(limited_results) == 2


async def test_get_latest_statement(
    statement_history_repository: StatementHistoryRepository,
    test_multiple_statements: List[StatementHistory],
    test_credit_account: Account,
):
    """Test retrieving the latest statement for an account."""
    # 1. ARRANGE: Setup is already done with fixtures
    latest_statement = test_multiple_statements[-1]  # Last in list (most recent)

    # 2. ACT: Get latest statement
    result = await statement_history_repository.get_latest_statement(
        test_credit_account.id
    )

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == latest_statement.id
    assert result.statement_date == latest_statement.statement_date
    assert result.statement_balance == latest_statement.statement_balance
    assert result.minimum_payment == latest_statement.minimum_payment
    assert result.due_date == latest_statement.due_date


async def test_get_with_account(
    statement_history_repository: StatementHistoryRepository,
    test_statement_history: StatementHistory,
    test_credit_account: Account,
):
    """Test retrieving a statement with its associated account."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get statement with account
    result = await statement_history_repository.get_with_account(
        test_statement_history.id
    )

    # 3. ASSERT: Verify the operation results
    assert result is not None
    assert result.id == test_statement_history.id
    assert result.account is not None
    assert result.account.id == test_credit_account.id
    assert result.account.name == test_credit_account.name
    assert result.account.type == test_credit_account.type


async def test_get_by_date_range(
    statement_history_repository: StatementHistoryRepository,
    test_multiple_statements: List[StatementHistory],
    test_credit_account: Account,
):
    """Test retrieving statements within a date range."""
    # 1. ARRANGE: Setup date range parameters
    now = utc_now()
    start_date = now - timedelta(days=70)
    end_date = now - timedelta(days=20)

    # 2. ACT: Get statements within date range
    results = await statement_history_repository.get_by_date_range(
        test_credit_account.id, start_date, end_date
    )

    # 3. ASSERT: Verify the operation results
    assert len(results) >= 1  # Should include at least the 60-day-old statement

    # Check that statements are within range
    for statement in results:
        assert statement.account_id == test_credit_account.id
        # Use proper timezone-aware comparison
        assert datetime_greater_than(
            statement.statement_date, start_date, ignore_timezone=True
        ) or datetime_equals(statement.statement_date, start_date, ignore_timezone=True)
        assert datetime_greater_than(
            end_date, statement.statement_date, ignore_timezone=True
        ) or datetime_equals(end_date, statement.statement_date, ignore_timezone=True)


async def test_get_statements_with_due_dates(
    statement_history_repository: StatementHistoryRepository,
    test_multiple_accounts_with_statements: Tuple[
        List[Account], List[StatementHistory]
    ],
):
    """Test retrieving statements with due dates in a specified range."""
    # 1. ARRANGE: Setup date range for due dates
    now = utc_now()
    start_date = now
    end_date = now + timedelta(days=30)

    # 2. ACT: Get statements with due dates in range
    results = await statement_history_repository.get_statements_with_due_dates(
        start_date, end_date
    )

    # 3. ASSERT: Verify the operation results
    assert len(results) > 0  # Should find at least one statement

    # Check that due dates are within range
    for statement in results:
        assert statement.due_date is not None
        assert datetime_greater_than(
            statement.due_date, start_date, ignore_timezone=True
        ) or datetime_equals(statement.due_date, start_date, ignore_timezone=True)
        assert datetime_greater_than(
            end_date, statement.due_date, ignore_timezone=True
        ) or datetime_equals(end_date, statement.due_date, ignore_timezone=True)


async def test_get_upcoming_statements_with_accounts(
    statement_history_repository: StatementHistoryRepository,
    test_multiple_accounts_with_statements: Tuple[
        List[Account], List[StatementHistory]
    ],
):
    """Test retrieving upcoming statements with their accounts."""
    # 1. ARRANGE: Setup is already done with fixtures
    now = utc_now()

    # 2. ACT: Get upcoming statements with accounts (default 30 days)
    results = await statement_history_repository.get_upcoming_statements_with_accounts()

    # Test with custom days parameter
    results_custom = (
        await statement_history_repository.get_upcoming_statements_with_accounts(
            days=10
        )
    )

    # 3. ASSERT: Verify the operation results
    assert len(results) > 0  # Should find at least one statement

    # Check that results contain both statements and accounts
    for statement, account in results:
        assert statement.account_id == account.id
        assert statement.due_date is not None
        # Use proper timezone-aware comparison
        assert datetime_greater_than(statement.due_date, now) or datetime_equals(
            statement.due_date, now
        )
        assert datetime_greater_than(
            days_from_now(30), statement.due_date
        ) or datetime_equals(days_from_now(30), statement.due_date)

    # Check custom days parameter
    for statement, account in results_custom:
        assert datetime_greater_than(
            days_from_now(10), statement.due_date
        ) or datetime_equals(days_from_now(10), statement.due_date)


async def test_get_statements_with_minimum_payment(
    statement_history_repository: StatementHistoryRepository,
    test_credit_account: Account,
):
    """Test retrieving statements with minimum payment information."""
    # 1. ARRANGE: Create statements with and without minimum payments
    # Create statement with minimum payment
    with_payment_schema = create_statement_history_schema(
        account_id=test_credit_account.id,
        statement_date=days_ago(30),
        statement_balance=Decimal("400.00"),
        minimum_payment=Decimal("20.00"),
    )
    with_payment = await statement_history_repository.create(
        with_payment_schema.model_dump()
    )

    # Create statement without minimum payment
    without_payment_schema = create_statement_history_schema(
        account_id=test_credit_account.id,
        statement_date=days_ago(15),
        statement_balance=Decimal("350.00"),
        minimum_payment=None,  # Explicitly None
    )
    without_payment = await statement_history_repository.create(
        without_payment_schema.model_dump()
    )

    # 2. ACT: Get statements with minimum payment
    results = await statement_history_repository.get_statements_with_minimum_payment(
        test_credit_account.id
    )

    # 3. ASSERT: Verify the operation results
    assert len(results) >= 1  # At least the one we created
    assert any(stmt.id == with_payment.id for stmt in results)
    assert not any(stmt.id == without_payment.id for stmt in results)

    # Check that all results have minimum payment
    for statement in results:
        assert statement.minimum_payment is not None


async def test_get_average_statement_balance(
    statement_history_repository: StatementHistoryRepository,
    test_multiple_statements: List[StatementHistory],
    test_credit_account: Account,
):
    """Test calculating average statement balance."""
    # 1. ARRANGE: Setup is already done with fixtures
    # Our test_multiple_statements has three statements with balances: 400, 600, 800
    expected_average = Decimal("600.00")  # (400 + 600 + 800) / 3

    # 2. ACT: Get average statement balance
    result = await statement_history_repository.get_average_statement_balance(
        test_credit_account.id
    )

    # 3. ASSERT: Verify the operation results
    assert result == expected_average

    # Test with custom months parameter (last 1 month)
    result_1month = await statement_history_repository.get_average_statement_balance(
        test_credit_account.id, months=1
    )
    assert result_1month == Decimal("800.00")  # Only the most recent statement


async def test_get_statement_trend(
    statement_history_repository: StatementHistoryRepository,
    test_multiple_statements: List[StatementHistory],
    test_credit_account: Account,
):
    """Test retrieving statement balance trend."""
    # 1. ARRANGE: Setup is already done with fixtures

    # 2. ACT: Get statement trend
    trend = await statement_history_repository.get_statement_trend(
        test_credit_account.id
    )

    # 3. ASSERT: Verify the operation results
    assert len(trend) >= 3  # At least our 3 statements

    # Check that trend contains date and balance pairs
    dates = [date for date, _ in trend]
    balances = [balance for _, balance in trend]

    # Verify our statement dates and balances are in the trend
    for statement in test_multiple_statements:
        assert statement.statement_date in dates
        assert statement.statement_balance in balances


async def test_get_total_minimum_payments_due(
    statement_history_repository: StatementHistoryRepository,
    test_multiple_accounts_with_statements: Tuple[
        List[Account], List[StatementHistory]
    ],
):
    """Test calculating total minimum payments due."""
    # 1. ARRANGE: Setup date range for due dates
    now = utc_now()
    start_date = now
    end_date = days_from_now(30)

    # Create fresh statements with due dates in the target range
    accounts, _ = test_multiple_accounts_with_statements
    statements_in_range = []

    # Create statements for each account with due dates in range
    for i, account in enumerate(accounts):
        stmt_schema = create_statement_history_schema(
            account_id=account.id,
            statement_date=days_ago(10),
            statement_balance=Decimal(f"{(i+1)*300}.00"),
            minimum_payment=Decimal(f"{(i+1)*25}.00"),
            due_date=days_from_now(10),  # Within range
        )
        stmt = await statement_history_repository.create(stmt_schema.model_dump())
        statements_in_range.append(stmt)

    # Expected total (25 + 50) = 75
    expected_total = sum(stmt.minimum_payment for stmt in statements_in_range)

    # 2. ACT: Get total minimum payments due
    result = await statement_history_repository.get_total_minimum_payments_due(
        start_date, end_date
    )

    # 3. ASSERT: Verify the operation results
    assert result >= expected_total  # May include other statements


async def test_validation_error_handling():
    """Test handling of validation errors that would be caught by the Pydantic schema."""
    # Try creating a schema with invalid data
    try:
        invalid_schema = create_statement_history_schema(
            account_id=-1,  # Invalid negative ID
            statement_date=utc_now(),
            statement_balance=Decimal(
                "-100.00"
            ),  # May or may not be valid depending on schema
            minimum_payment=Decimal("-10.00"),  # Invalid negative payment
        )
        assert False, "Schema should have raised a validation error"
    except ValueError as e:
        # This is expected - schema validation should catch the error
        error_str = str(e).lower()
        assert "account_id" in error_str or "minimum_payment" in error_str
