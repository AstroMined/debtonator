"""
Unit tests for credit limit history schema factory functions.

Tests ensure that credit limit history schema factories produce valid schema instances
that pass validation.
"""

# pylint: disable=no-member

from datetime import datetime, timezone
from decimal import Decimal

import pytest

from src.schemas.credit_limit_history import (
    AccountCreditLimitHistoryResponse,
    CreditLimitHistoryCreate,
    CreditLimitHistoryInDB,
    CreditLimitHistoryUpdate,
)
from tests.helpers.schema_factories.credit_limit_history import (
    create_credit_limit_history_schema,
    create_credit_limit_history_in_db_schema,
    create_credit_limit_history_update_schema,
    create_account_credit_limit_history_response_schema,
)


def test_create_credit_limit_history_schema():
    """Test creating a CreditLimitHistoryCreate schema with default values."""
    schema = create_credit_limit_history_schema(account_id=1)
    
    assert isinstance(schema, CreditLimitHistoryCreate)
    assert schema.account_id == 1
    assert schema.credit_limit == Decimal("5000.00")
    assert isinstance(schema.effective_date, datetime)
    assert schema.reason is None


def test_create_credit_limit_history_schema_with_custom_values():
    """Test creating a CreditLimitHistoryCreate schema with custom values."""
    effective_date = datetime(2023, 5, 15, tzinfo=timezone.utc)
    
    schema = create_credit_limit_history_schema(
        account_id=2,
        credit_limit=Decimal("7500.00"),
        effective_date=effective_date,
        reason="Credit score increase"
    )
    
    assert isinstance(schema, CreditLimitHistoryCreate)
    assert schema.account_id == 2
    assert schema.credit_limit == Decimal("7500.00")
    assert schema.effective_date == effective_date
    assert schema.reason == "Credit score increase"


def test_create_credit_limit_history_in_db_schema():
    """Test creating a CreditLimitHistoryInDB schema with default values."""
    schema = create_credit_limit_history_in_db_schema(id=1, account_id=1)
    
    assert isinstance(schema, CreditLimitHistoryInDB)
    assert schema.id == 1
    assert schema.account_id == 1
    assert schema.credit_limit == Decimal("5000.00")
    assert isinstance(schema.effective_date, datetime)
    assert isinstance(schema.created_at, datetime)
    assert schema.reason is None


def test_create_credit_limit_history_in_db_schema_with_custom_values():
    """Test creating a CreditLimitHistoryInDB schema with custom values."""
    effective_date = datetime(2023, 5, 15, tzinfo=timezone.utc)
    created_at = datetime(2023, 5, 16, tzinfo=timezone.utc)
    
    schema = create_credit_limit_history_in_db_schema(
        id=2,
        account_id=3,
        credit_limit=Decimal("8000.00"),
        effective_date=effective_date,
        created_at=created_at,
        reason="Annual review increase"
    )
    
    assert isinstance(schema, CreditLimitHistoryInDB)
    assert schema.id == 2
    assert schema.account_id == 3
    assert schema.credit_limit == Decimal("8000.00")
    assert schema.effective_date == effective_date
    assert schema.created_at == created_at
    assert schema.reason == "Annual review increase"


def test_create_account_credit_limit_history_response_schema():
    """Test creating an AccountCreditLimitHistoryResponse schema with default values."""
    schema = create_account_credit_limit_history_response_schema(account_id=4)
    
    assert isinstance(schema, AccountCreditLimitHistoryResponse)
    assert schema.account_id == 4
    assert schema.account_name == "Test Credit Card"
    assert schema.current_credit_limit == Decimal("5000.00")
    assert len(schema.credit_limit_history) == 3
    
    # Check history entries are in the expected order (newest first)
    assert schema.credit_limit_history[0].credit_limit == Decimal("5000.00")
    assert schema.credit_limit_history[1].credit_limit == Decimal("4000.00")
    assert schema.credit_limit_history[2].credit_limit == Decimal("3000.00")
    
    # Check that reasons are set as expected
    assert schema.credit_limit_history[0].reason == "Current limit"
    assert "increase" in schema.credit_limit_history[1].reason.lower()
    assert "initial" in schema.credit_limit_history[2].reason.lower()


def test_create_account_credit_limit_history_response_schema_with_custom_values():
    """Test creating an AccountCreditLimitHistoryResponse schema with custom values."""
    # Create custom history entries
    custom_history = [
        create_credit_limit_history_in_db_schema(
            id=5,
            account_id=5,
            credit_limit=Decimal("10000.00"),
            effective_date=datetime(2024, 2, 1, tzinfo=timezone.utc),
            reason="Latest limit"
        ),
        create_credit_limit_history_in_db_schema(
            id=6,
            account_id=5,
            credit_limit=Decimal("7500.00"),
            effective_date=datetime(2023, 7, 1, tzinfo=timezone.utc),
            reason="Increase after account review"
        ),
    ]
    
    schema = create_account_credit_limit_history_response_schema(
        account_id=5,
        account_name="Premium Credit Card",
        current_credit_limit=Decimal("10000.00"),
        credit_limit_history=custom_history
    )
    
    assert isinstance(schema, AccountCreditLimitHistoryResponse)
    assert schema.account_id == 5
    assert schema.account_name == "Premium Credit Card"
    assert schema.current_credit_limit == Decimal("10000.00")
    assert len(schema.credit_limit_history) == 2
    
    # Check that our custom history entries are used
    assert schema.credit_limit_history[0].id == 5
    assert schema.credit_limit_history[0].credit_limit == Decimal("10000.00")
    assert schema.credit_limit_history[0].reason == "Latest limit"
    
    assert schema.credit_limit_history[1].id == 6
    assert schema.credit_limit_history[1].credit_limit == Decimal("7500.00")
    assert schema.credit_limit_history[1].reason == "Increase after account review"


def test_create_credit_limit_history_update_schema():
    """Test creating a CreditLimitHistoryUpdate schema with default values."""
    schema = create_credit_limit_history_update_schema(id=7)
    
    assert isinstance(schema, CreditLimitHistoryUpdate)
    assert schema.id == 7
    assert isinstance(schema.effective_date, datetime)
    assert schema.credit_limit is None
    assert schema.reason is None


def test_create_credit_limit_history_update_schema_with_custom_values():
    """Test creating a CreditLimitHistoryUpdate schema with custom values."""
    effective_date = datetime(2023, 8, 1, tzinfo=timezone.utc)
    
    schema = create_credit_limit_history_update_schema(
        id=8,
        effective_date=effective_date,
        credit_limit=Decimal("12000.00"),
        reason="Customer loyalty bonus"
    )
    
    assert isinstance(schema, CreditLimitHistoryUpdate)
    assert schema.id == 8
    assert schema.effective_date == effective_date
    assert schema.credit_limit == Decimal("12000.00")
    assert schema.reason == "Customer loyalty bonus"


def test_create_credit_limit_history_update_schema_partial_update():
    """Test creating a CreditLimitHistoryUpdate schema with partial field updates."""
    schema = create_credit_limit_history_update_schema(
        id=9,
        reason="Updated reason only"
    )
    
    assert isinstance(schema, CreditLimitHistoryUpdate)
    assert schema.id == 9
    assert isinstance(schema.effective_date, datetime)
    assert schema.credit_limit is None
    assert schema.reason == "Updated reason only"
