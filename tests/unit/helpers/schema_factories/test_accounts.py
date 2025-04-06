"""
Unit tests for base account schema factory functions.

Tests ensure that base account schema factories produce valid schema instances
that pass validation. Account type-specific tests are in their respective modules.
"""

# pylint: disable=no-member

from datetime import datetime
from decimal import Decimal

import pytest

from src.schemas.accounts import (
    AccountUpdate,
    AccountStatementHistoryResponse,
    AvailableCreditResponse,
)
from src.utils.datetime_utils import utc_now
from tests.helpers.schema_factories.accounts import (
    create_account_update_schema,
    create_account_statement_history_response_schema,
    create_available_credit_response_schema,
)


def test_create_account_update_schema():
    """Test creating an account update schema with basic fields."""
    schema = create_account_update_schema(
        name="Updated Name",
        available_balance=Decimal("999.99"),
    )
    
    assert isinstance(schema, AccountUpdate)
    assert schema.name == "Updated Name"
    assert schema.available_balance == Decimal("999.99")
    assert schema.account_type is None  # Optional fields should be None by default


def test_create_account_update_schema_minimal():
    """Test creating an account update schema with no fields."""
    schema = create_account_update_schema()
    
    assert isinstance(schema, AccountUpdate)
    assert schema.name is None
    assert schema.available_balance is None
    assert schema.account_type is None


def test_create_account_update_schema_credit_fields():
    """Test creating an account update schema with credit-specific fields."""
    schema = create_account_update_schema(
        account_type="credit",
        total_limit=Decimal("10000.00"),
        available_credit=Decimal("5000.00"),
    )
    
    assert isinstance(schema, AccountUpdate)
    assert schema.account_type == "credit"
    assert schema.total_limit == Decimal("10000.00")
    assert schema.available_credit == Decimal("5000.00")


def test_create_account_update_schema_credit_validation():
    """Test that credit fields are only allowed for credit accounts."""
    with pytest.raises(ValueError, match="Total Limit can only be set for credit accounts"):
        create_account_update_schema(
            account_type="checking",
            total_limit=Decimal("5000.00"),
        )


def test_create_account_statement_history_response_schema():
    """Test creating an account statement history response schema."""
    now = utc_now()
    schema = create_account_statement_history_response_schema(
        account_id=123,
        account_name="Test Account",
    )
    
    assert isinstance(schema, AccountStatementHistoryResponse)
    assert schema.account_id == 123
    assert schema.account_name == "Test Account"
    assert len(schema.statement_history) == 3  # Default creates 3 months
    
    # Verify statement history is in descending order
    assert schema.statement_history[0].statement_balance > schema.statement_history[1].statement_balance
    assert schema.statement_history[1].statement_balance > schema.statement_history[2].statement_balance


def test_create_account_statement_history_response_schema_custom():
    """Test creating an account statement history response with custom history."""
    now = utc_now()
    custom_history = [
        {
            "statement_date": datetime(now.year, now.month, 1, tzinfo=now.tzinfo),
            "statement_balance": Decimal("1000.00"),
            "minimum_payment": Decimal("100.00"),
            "due_date": datetime(now.year, now.month, 25, tzinfo=now.tzinfo),
        }
    ]
    
    schema = create_account_statement_history_response_schema(
        account_id=123,
        account_name="Test Account",
        statement_history=custom_history,
    )
    
    assert len(schema.statement_history) == 1
    assert schema.statement_history[0].statement_balance == Decimal("1000.00")
    assert schema.statement_history[0].minimum_payment == Decimal("100.00")


def test_create_available_credit_response_schema():
    """Test creating an available credit response schema."""
    schema = create_available_credit_response_schema(
        account_id=123,
        account_name="Test Credit Card",
        total_limit=Decimal("5000.00"),
        current_balance=Decimal("-1500.00"),
        pending_transactions=Decimal("200.00"),
    )
    
    assert isinstance(schema, AvailableCreditResponse)
    assert schema.account_id == 123
    assert schema.account_name == "Test Credit Card"
    assert schema.total_limit == Decimal("5000.00")
    assert schema.current_balance == Decimal("-1500.00")
    assert schema.pending_transactions == Decimal("200.00")
    assert schema.adjusted_balance == Decimal("-1700.00")  # -1500 - 200
    assert schema.available_credit == Decimal("3300.00")  # 5000 + (-1700)


def test_create_available_credit_response_schema_defaults():
    """Test creating an available credit response schema with defaults."""
    schema = create_available_credit_response_schema(
        account_id=123,
        account_name="Test Credit Card",
    )
    
    assert isinstance(schema, AvailableCreditResponse)
    assert schema.total_limit == Decimal("5000.00")  # Default
    assert schema.current_balance == Decimal("-1500.00")  # Default
    assert schema.pending_transactions == Decimal("200.00")  # Default
    assert schema.adjusted_balance == Decimal("-1700.00")  # Calculated
    assert schema.available_credit == Decimal("3300.00")  # Calculated
