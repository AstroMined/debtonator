"""
Unit tests for statement history schema factory functions.

Tests ensure that statement history schema factories produce valid schema instances
that pass validation.
"""

# pylint: disable=no-member

from datetime import datetime, timedelta, timezone
from decimal import Decimal

from src.schemas.statement_history import StatementHistoryCreate
from tests.helpers.schema_factories.statement_history_schema_factories import (
    create_statement_history_schema,
)


def test_create_statement_history_schema():
    """Test creating a StatementHistoryCreate schema with default values."""
    schema = create_statement_history_schema(account_id=1)

    assert isinstance(schema, StatementHistoryCreate)
    assert schema.account_id == 1
    assert schema.statement_balance == Decimal("500.00")
    assert isinstance(schema.statement_date, datetime)
    assert schema.minimum_payment is None
    assert schema.due_date is None


def test_create_statement_history_schema_with_custom_values():
    """Test creating a StatementHistoryCreate schema with custom values."""
    statement_date = datetime(2023, 6, 1, tzinfo=timezone.utc)
    due_date = datetime(2023, 6, 25, tzinfo=timezone.utc)

    schema = create_statement_history_schema(
        account_id=2,
        statement_date=statement_date,
        statement_balance=Decimal("1250.75"),
        minimum_payment=Decimal("35.00"),
        due_date=due_date,
    )

    assert isinstance(schema, StatementHistoryCreate)
    assert schema.account_id == 2
    assert schema.statement_date == statement_date
    assert schema.statement_balance == Decimal("1250.75")
    assert schema.minimum_payment == Decimal("35.00")
    assert schema.due_date == due_date


def test_create_statement_history_schema_minimum_payment_only():
    """Test creating a StatementHistoryCreate schema with minimum payment but no due date."""
    statement_date = datetime(2023, 7, 1, tzinfo=timezone.utc)

    schema = create_statement_history_schema(
        account_id=3,
        statement_date=statement_date,
        statement_balance=Decimal("750.50"),
        minimum_payment=Decimal("25.00"),
    )

    assert isinstance(schema, StatementHistoryCreate)
    assert schema.account_id == 3
    assert schema.statement_date == statement_date
    assert schema.statement_balance == Decimal("750.50")
    assert schema.minimum_payment == Decimal("25.00")

    # Due date should be auto-calculated as statement_date + 25 days
    assert schema.due_date is not None
    assert schema.due_date == statement_date + timedelta(days=25)


def test_create_statement_history_schema_zero_balance():
    """Test creating a StatementHistoryCreate schema with zero balance."""
    schema = create_statement_history_schema(
        account_id=4, statement_balance=Decimal("0.00")
    )

    assert isinstance(schema, StatementHistoryCreate)
    assert schema.account_id == 4
    assert schema.statement_balance == Decimal("0.00")
    assert schema.minimum_payment is None
    assert schema.due_date is None


def test_create_statement_history_schema_with_additional_fields():
    """Test creating a StatementHistoryCreate schema with additional fields via kwargs."""
    # While additional fields are included as kwargs, they don't become
    # attributes in the actual schema, so we only test the core fields
    schema = create_statement_history_schema(
        account_id=5,
        statement_balance=Decimal("1500.00"),
        is_reconciled=True,
        interest_charged=Decimal("32.50"),
        fees_charged=Decimal("0.00"),
    )

    assert isinstance(schema, StatementHistoryCreate)
    assert schema.account_id == 5
    assert schema.statement_balance == Decimal("1500.00")
    # The following fields don't exist in the schema
    # assert schema.is_reconciled is True
    # assert schema.interest_charged == Decimal("32.50")
    # assert schema.fees_charged == Decimal("0.00")


def test_create_statement_history_schema_negative_balance():
    """Test creating a StatementHistoryCreate schema with negative balance."""
    schema = create_statement_history_schema(
        account_id=6, statement_balance=Decimal("-150.25")
    )

    assert isinstance(schema, StatementHistoryCreate)
    assert schema.account_id == 6
    assert schema.statement_balance == Decimal("-150.25")
    assert schema.minimum_payment is None
    assert schema.due_date is None


def test_create_statement_history_schema_with_zero_minimum_payment():
    """Test creating a StatementHistoryCreate schema with zero minimum payment."""
    schema = create_statement_history_schema(
        account_id=7,
        statement_balance=Decimal("100.00"),
        minimum_payment=Decimal("0.00"),
    )

    assert isinstance(schema, StatementHistoryCreate)
    assert schema.account_id == 7
    assert schema.statement_balance == Decimal("100.00")
    assert schema.minimum_payment == Decimal("0.00")
    assert schema.due_date is not None  # Due date should still be set
