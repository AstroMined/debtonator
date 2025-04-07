"""
Unit tests for account schema factory functions.

Tests ensure that account schema factories produce valid schema instances
that pass validation and maintain ADR-011 compliance for datetime handling.
"""

# pylint: disable=no-member

from datetime import datetime, timedelta, timezone
from decimal import Decimal
from typing import Dict, List

import pytest

from src.schemas.accounts import (
    AccountInDB,
    AccountResponse,
    AccountStatementHistoryResponse,
    AccountUpdate,
    AvailableCreditResponse,
    StatementBalanceHistory,
)
from src.schemas.account_types import AccountCreateUnion
from src.schemas.account_types.banking import (
    CheckingAccountCreate,
    SavingsAccountCreate,
    CreditAccountCreate,
    PaymentAppAccountCreate,
    BNPLAccountCreate,
    EWAAccountCreate,
)
from src.utils.datetime_utils import datetime_equals, utc_now
from tests.helpers.schema_factories.accounts import (
    create_account_schema,
    create_account_in_db_schema,
    create_account_response_schema,
    create_account_update_schema,
    create_account_statement_history_response_schema,
    create_available_credit_response_schema,
    create_statement_balance_history_schema,
)


def test_create_account_schema_checking():
    """Test creating a checking account schema."""
    schema = create_account_schema(
        name="My Checking",
        account_type="checking",
        available_balance=Decimal("1500.00"),
    )
    
    assert isinstance(schema, CheckingAccountCreate)
    assert schema.name == "My Checking"
    assert schema.available_balance == Decimal("1500.00")
    assert schema.account_type == "checking"


def test_create_account_schema_savings():
    """Test creating a savings account schema."""
    schema = create_account_schema(
        name="My Savings",
        account_type="savings",
        available_balance=Decimal("5000.00"),
    )
    
    assert isinstance(schema, SavingsAccountCreate)
    assert schema.name == "My Savings"
    assert schema.available_balance == Decimal("5000.00")
    assert schema.account_type == "savings"


def test_create_account_schema_credit():
    """Test creating a credit account schema."""
    schema = create_account_schema(
        name="My Credit Card",
        account_type="credit",
        available_balance=Decimal("-1200.00"),
        total_limit=Decimal("5000.00"),
    )
    
    assert isinstance(schema, CreditAccountCreate)
    assert schema.name == "My Credit Card"
    assert schema.available_balance == Decimal("-1200.00")
    assert schema.account_type == "credit"
    assert schema.credit_limit == Decimal("5000.00")


def test_create_account_schema_payment_app():
    """Test creating a payment app account schema."""
    schema = create_account_schema(
        name="My Payment App",
        account_type="payment_app",
        available_balance=Decimal("750.00"),
    )
    
    assert isinstance(schema, PaymentAppAccountCreate)
    assert schema.name == "My Payment App"
    assert schema.available_balance == Decimal("750.00")
    assert schema.account_type == "payment_app"


def test_create_account_schema_bnpl():
    """Test creating a BNPL account schema."""
    schema = create_account_schema(
        name="My BNPL Account",
        account_type="bnpl",
        available_balance=Decimal("-400.00"),
    )
    
    assert isinstance(schema, BNPLAccountCreate)
    assert schema.name == "My BNPL Account"
    assert schema.available_balance == Decimal("-400.00")
    assert schema.account_type == "bnpl"


def test_create_account_schema_ewa():
    """Test creating an EWA account schema."""
    schema = create_account_schema(
        name="My EWA Account",
        account_type="ewa",
        available_balance=Decimal("-150.00"),
    )
    
    assert isinstance(schema, EWAAccountCreate)
    assert schema.name == "My EWA Account"
    assert schema.available_balance == Decimal("-150.00")
    assert schema.account_type == "ewa"


def test_create_account_schema_unsupported_type():
    """Test that creating an account with unsupported type raises error."""
    with pytest.raises(ValueError, match="Unsupported account type"):
        create_account_schema(
            name="Invalid Account",
            account_type="unsupported",
        )


def test_create_account_in_db_schema():
    """Test creating an AccountInDB schema with default values."""
    schema = create_account_in_db_schema(id=1)
    
    assert isinstance(schema, AccountInDB)
    assert schema.id == 1
    assert schema.name == "Test Account"
    assert schema.account_type == "checking"
    assert schema.available_balance == Decimal("1000.00")
    
    # Verify datetime fields are timezone-aware and in UTC per ADR-011
    assert schema.created_at.tzinfo is not None
    assert schema.created_at.tzinfo == timezone.utc
    assert schema.updated_at.tzinfo is not None
    assert schema.updated_at.tzinfo == timezone.utc


def test_create_account_in_db_schema_custom_values():
    """Test creating an AccountInDB schema with custom values."""
    created_at = utc_now() - timedelta(days=30)
    updated_at = utc_now()
    
    schema = create_account_in_db_schema(
        id=2,
        name="Custom Account",
        account_type="savings",
        available_balance=Decimal("5000.00"),
        created_at=created_at,
        updated_at=updated_at,
    )
    
    assert isinstance(schema, AccountInDB)
    assert schema.id == 2
    assert schema.name == "Custom Account"
    assert schema.account_type == "savings"
    assert schema.available_balance == Decimal("5000.00")
    
    # Verify datetime fields using datetime_equals for proper ADR-011 comparison
    assert datetime_equals(schema.created_at, created_at)
    assert datetime_equals(schema.updated_at, updated_at)


def test_create_account_in_db_schema_credit():
    """Test creating a credit AccountInDB schema."""
    schema = create_account_in_db_schema(
        id=3,
        name="Credit Card",
        account_type="credit",
        available_balance=Decimal("-1500.00"),
        total_limit=Decimal("10000.00"),
        last_statement_balance=Decimal("-1200.00"),
        last_statement_date=utc_now() - timedelta(days=15),
    )
    
    assert isinstance(schema, AccountInDB)
    assert schema.id == 3
    assert schema.name == "Credit Card"
    assert schema.account_type == "credit"
    assert schema.available_balance == Decimal("-1500.00")
    assert schema.total_limit == Decimal("10000.00")
    assert schema.available_credit == Decimal("8500.00")  # 10000 + (-1500)
    assert schema.last_statement_balance == Decimal("-1200.00")
    
    # Verify last_statement_date is timezone-aware and in UTC per ADR-011
    assert schema.last_statement_date.tzinfo is not None
    assert schema.last_statement_date.tzinfo == timezone.utc


def test_create_account_response_schema():
    """Test creating an AccountResponse schema with default values."""
    schema = create_account_response_schema(id=1)
    
    assert isinstance(schema, AccountResponse)
    assert schema.id == 1
    assert schema.name == "Test Account"
    assert schema.account_type == "checking"
    assert schema.available_balance == Decimal("1000.00")
    
    # Verify datetime fields are timezone-aware and in UTC per ADR-011
    assert schema.created_at.tzinfo is not None
    assert schema.created_at.tzinfo == timezone.utc
    assert schema.updated_at.tzinfo is not None
    assert schema.updated_at.tzinfo == timezone.utc


def test_create_account_response_schema_credit():
    """Test creating a credit AccountResponse schema."""
    schema = create_account_response_schema(
        id=3,
        name="Credit Card",
        account_type="credit",
        available_balance=Decimal("-1500.00"),
        total_limit=Decimal("10000.00"),
    )
    
    assert isinstance(schema, AccountResponse)
    assert schema.id == 3
    assert schema.name == "Credit Card"
    assert schema.account_type == "credit"
    assert schema.available_balance == Decimal("-1500.00")
    assert schema.total_limit == Decimal("10000.00")
    assert schema.available_credit == Decimal("8500.00")  # 10000 + (-1500)


def test_create_statement_balance_history_schema():
    """Test creating a StatementBalanceHistory schema with default values."""
    schema = create_statement_balance_history_schema()
    
    assert isinstance(schema, StatementBalanceHistory)
    assert schema.statement_balance == Decimal("500.00")
    assert schema.minimum_payment == Decimal("50.00")  # 10% of 500
    
    # Verify datetime fields are timezone-aware and in UTC per ADR-011
    assert schema.statement_date.tzinfo is not None
    assert schema.statement_date.tzinfo == timezone.utc
    assert schema.due_date.tzinfo is not None
    assert schema.due_date.tzinfo == timezone.utc
    
    # Verify due_date is approximately 25 days after statement_date
    delta = schema.due_date - schema.statement_date
    assert 20 <= delta.days <= 28  # Account for month transitions


def test_create_statement_balance_history_schema_custom_values():
    """Test creating a StatementBalanceHistory schema with custom values."""
    statement_date = utc_now().replace(day=5)
    due_date = statement_date + timedelta(days=20)
    
    schema = create_statement_balance_history_schema(
        statement_date=statement_date,
        statement_balance=Decimal("1200.00"),
        minimum_payment=Decimal("100.00"),
        due_date=due_date,
    )
    
    assert isinstance(schema, StatementBalanceHistory)
    
    # Verify datetime fields using datetime_equals for proper ADR-011 comparison
    assert datetime_equals(schema.statement_date, statement_date)
    assert datetime_equals(schema.due_date, due_date)
    
    assert schema.statement_balance == Decimal("1200.00")
    assert schema.minimum_payment == Decimal("100.00")


def test_create_account_statement_history_response_schema():
    """Test creating an AccountStatementHistoryResponse schema with default values."""
    schema = create_account_statement_history_response_schema(
        account_id=123,
        account_name="Test Account",
    )
    
    assert isinstance(schema, AccountStatementHistoryResponse)
    assert schema.account_id == 123
    assert schema.account_name == "Test Account"
    assert len(schema.statement_history) == 3  # Default creates 3 months
    
    # Verify statement history is in descending order (most recent first)
    assert schema.statement_history[0].statement_balance > schema.statement_history[1].statement_balance
    assert schema.statement_history[1].statement_balance > schema.statement_history[2].statement_balance
    
    # Verify all dates are timezone-aware and in UTC per ADR-011
    for statement in schema.statement_history:
        assert statement.statement_date.tzinfo is not None
        assert statement.statement_date.tzinfo == timezone.utc
        assert statement.due_date.tzinfo is not None
        assert statement.due_date.tzinfo == timezone.utc


def test_create_account_statement_history_response_schema_custom():
    """Test creating an AccountStatementHistoryResponse with custom history."""
    now = utc_now()
    custom_history = [
        create_statement_balance_history_schema(
            statement_date=datetime(now.year, now.month, 1, tzinfo=now.tzinfo),
            statement_balance=Decimal("1000.00"),
            minimum_payment=Decimal("100.00"),
        ),
        create_statement_balance_history_schema(
            statement_date=datetime(now.year, now.month-1, 1, tzinfo=now.tzinfo),
            statement_balance=Decimal("900.00"),
            minimum_payment=Decimal("90.00"),
        ),
    ]
    
    schema = create_account_statement_history_response_schema(
        account_id=123,
        account_name="Test Account",
        statement_history=custom_history,
    )
    
    assert isinstance(schema, AccountStatementHistoryResponse)
    assert len(schema.statement_history) == 2
    assert schema.statement_history[0].statement_balance == Decimal("1000.00")
    assert schema.statement_history[1].statement_balance == Decimal("900.00")


def test_create_available_credit_response_schema():
    """Test creating an AvailableCreditResponse schema with default values."""
    schema = create_available_credit_response_schema(
        account_id=123,
        account_name="Test Credit Card",
    )
    
    assert isinstance(schema, AvailableCreditResponse)
    assert schema.account_id == 123
    assert schema.account_name == "Test Credit Card"
    assert schema.total_limit == Decimal("5000.00")  # Default
    assert schema.current_balance == Decimal("-1500.00")  # Default
    assert schema.pending_transactions == Decimal("200.00")  # Default
    assert schema.adjusted_balance == Decimal("-1700.00")  # Calculated (current - pending)
    assert schema.available_credit == Decimal("3300.00")  # Calculated (limit + adjusted)


def test_create_available_credit_response_schema_custom_values():
    """Test creating an AvailableCreditResponse schema with custom values."""
    schema = create_available_credit_response_schema(
        account_id=123,
        account_name="Test Credit Card",
        total_limit=Decimal("10000.00"),
        current_balance=Decimal("-2500.00"),
        pending_transactions=Decimal("500.00"),
    )
    
    assert isinstance(schema, AvailableCreditResponse)
    assert schema.total_limit == Decimal("10000.00")
    assert schema.current_balance == Decimal("-2500.00")
    assert schema.pending_transactions == Decimal("500.00")
    assert schema.adjusted_balance == Decimal("-3000.00")  # Calculated
    assert schema.available_credit == Decimal("7000.00")  # Calculated


def test_create_available_credit_response_schema_manual_calculation():
    """Test creating an AvailableCreditResponse schema with manually provided calculations."""
    schema = create_available_credit_response_schema(
        account_id=123,
        account_name="Test Credit Card",
        total_limit=Decimal("10000.00"),
        current_balance=Decimal("-2500.00"),
        pending_transactions=Decimal("500.00"),
        adjusted_balance=Decimal("-3000.00"),
        available_credit=Decimal("7000.00"),
    )
    
    assert isinstance(schema, AvailableCreditResponse)
    assert schema.adjusted_balance == Decimal("-3000.00")
    assert schema.available_credit == Decimal("7000.00")


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
