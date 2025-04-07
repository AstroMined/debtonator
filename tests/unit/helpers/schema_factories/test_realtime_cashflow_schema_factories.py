"""
Unit tests for realtime cashflow schema factory functions.

Tests ensure that realtime cashflow schema factories produce valid schema instances
that pass validation.
"""

# pylint: disable=no-member

from datetime import datetime, timedelta, timezone
from decimal import Decimal

import pytest

from src.schemas.realtime_cashflow import (
    AccountBalance,
    AccountType,
    RealtimeCashflow,
    RealtimeCashflowResponse,
)
from tests.helpers.schema_factories.realtime_cashflow import (
    create_account_balance_schema,
    create_realtime_cashflow_schema,
    create_realtime_cashflow_response_schema,
)


def test_create_account_balance_schema_checking():
    """Test creating an AccountBalance schema for a checking account."""
    schema = create_account_balance_schema(
        account_id=1,
        name="Main Checking",
        type=AccountType.CHECKING
    )
    
    assert isinstance(schema, AccountBalance)
    assert schema.account_id == 1
    assert schema.name == "Main Checking"
    assert schema.type == AccountType.CHECKING
    assert schema.current_balance == Decimal("1000.00")
    assert schema.available_credit is None
    assert schema.total_limit is None


def test_create_account_balance_schema_credit():
    """Test creating an AccountBalance schema for a credit account."""
    schema = create_account_balance_schema(
        account_id=2,
        name="Credit Card",
        type=AccountType.CREDIT
    )
    
    assert isinstance(schema, AccountBalance)
    assert schema.account_id == 2
    assert schema.name == "Credit Card"
    assert schema.type == AccountType.CREDIT
    assert schema.current_balance == Decimal("-500.00")
    assert schema.available_credit == Decimal("4500.00")
    assert schema.total_limit == Decimal("5000.00")


def test_create_account_balance_schema_with_custom_values():
    """Test creating an AccountBalance schema with custom values."""
    schema = create_account_balance_schema(
        account_id=3,
        name="Custom Account",
        type=AccountType.SAVINGS,
        current_balance=Decimal("2500.00")
    )
    
    assert isinstance(schema, AccountBalance)
    assert schema.account_id == 3
    assert schema.name == "Custom Account"
    assert schema.type == AccountType.SAVINGS
    assert schema.current_balance == Decimal("2500.00")
    assert schema.available_credit is None
    assert schema.total_limit is None


def test_create_account_balance_schema_credit_with_custom_values():
    """Test creating an AccountBalance schema for a credit account with custom values."""
    schema = create_account_balance_schema(
        account_id=4,
        name="Custom Credit Card",
        type=AccountType.CREDIT,
        current_balance=Decimal("-1000.00"),
        available_credit=Decimal("9000.00"),
        total_limit=Decimal("10000.00")
    )
    
    assert isinstance(schema, AccountBalance)
    assert schema.account_id == 4
    assert schema.name == "Custom Credit Card"
    assert schema.type == AccountType.CREDIT
    assert schema.current_balance == Decimal("-1000.00")
    assert schema.available_credit == Decimal("9000.00")
    assert schema.total_limit == Decimal("10000.00")


def test_create_realtime_cashflow_schema():
    """Test creating a RealtimeCashflow schema with default values."""
    schema = create_realtime_cashflow_schema()
    
    assert isinstance(schema, RealtimeCashflow)
    assert isinstance(schema.timestamp, datetime)
    assert schema.timestamp.tzinfo == timezone.utc
    assert isinstance(schema.account_balances, list)
    assert len(schema.account_balances) == 2
    assert schema.total_available_funds == Decimal("1000.00")
    assert schema.total_available_credit == Decimal("4500.00")
    assert schema.total_liabilities_due == Decimal("500.00")
    assert schema.net_position == Decimal("500.00")
    assert schema.minimum_balance_required == Decimal("200.00")
    assert schema.next_bill_due is None
    assert schema.days_until_next_bill is None
    assert schema.projected_deficit is None


def test_create_realtime_cashflow_schema_with_custom_values():
    """Test creating a RealtimeCashflow schema with custom values."""
    timestamp = datetime(2023, 6, 15, tzinfo=timezone.utc)
    next_bill_due = datetime(2023, 6, 20, tzinfo=timezone.utc)
    
    account_balances = [
        create_account_balance_schema(
            account_id=1,
            name="Checking Account",
            type=AccountType.CHECKING,
            current_balance=Decimal("2000.00")
        ).model_dump(),
        create_account_balance_schema(
            account_id=2,
            name="Credit Card",
            type=AccountType.CREDIT,
            current_balance=Decimal("-800.00"),
            available_credit=Decimal("4200.00"),
            total_limit=Decimal("5000.00")
        ).model_dump()
    ]
    
    schema = create_realtime_cashflow_schema(
        timestamp=timestamp,
        account_balances=account_balances,
        total_available_funds=Decimal("2000.00"),
        total_available_credit=Decimal("4200.00"),
        total_liabilities_due=Decimal("800.00"),
        net_position=Decimal("1200.00"),
        next_bill_due=next_bill_due,
        days_until_next_bill=5,
        minimum_balance_required=Decimal("500.00"),
        projected_deficit=Decimal("100.00")
    )
    
    assert isinstance(schema, RealtimeCashflow)
    assert schema.timestamp == timestamp
    assert len(schema.account_balances) == 2
    assert schema.account_balances[0].account_id == 1
    assert schema.account_balances[0].current_balance == Decimal("2000.00")
    assert schema.account_balances[1].account_id == 2
    assert schema.account_balances[1].available_credit == Decimal("4200.00")
    assert schema.total_available_funds == Decimal("2000.00")
    assert schema.total_available_credit == Decimal("4200.00")
    assert schema.total_liabilities_due == Decimal("800.00")
    assert schema.net_position == Decimal("1200.00")
    assert schema.next_bill_due == next_bill_due
    assert schema.days_until_next_bill == 5
    assert schema.minimum_balance_required == Decimal("500.00")
    assert schema.projected_deficit == Decimal("100.00")


def test_create_realtime_cashflow_schema_with_next_bill_date_only():
    """Test creating a RealtimeCashflow schema with only next bill date set."""
    timestamp = datetime(2023, 6, 15, tzinfo=timezone.utc)
    next_bill_due = datetime(2023, 6, 20, tzinfo=timezone.utc)
    
    schema = create_realtime_cashflow_schema(
        timestamp=timestamp,
        next_bill_due=next_bill_due
    )
    
    assert isinstance(schema, RealtimeCashflow)
    assert schema.next_bill_due == next_bill_due
    assert schema.days_until_next_bill == 5  # Calculated automatically


def test_create_realtime_cashflow_schema_with_days_until_next_bill_only():
    """Test creating a RealtimeCashflow schema with only days until next bill set."""
    timestamp = datetime(2023, 6, 15, tzinfo=timezone.utc)
    
    schema = create_realtime_cashflow_schema(
        timestamp=timestamp,
        days_until_next_bill=7
    )
    
    assert isinstance(schema, RealtimeCashflow)
    assert schema.days_until_next_bill == 7
    assert schema.next_bill_due == timestamp + timedelta(days=7)


def test_create_realtime_cashflow_response_schema():
    """Test creating a RealtimeCashflowResponse schema with default values."""
    schema = create_realtime_cashflow_response_schema()
    
    assert isinstance(schema, RealtimeCashflowResponse)
    assert isinstance(schema.data, RealtimeCashflow)
    assert isinstance(schema.last_updated, datetime)
    assert schema.last_updated.tzinfo == timezone.utc
    
    # Check that data contains expected default values
    assert schema.data.total_available_funds == Decimal("1000.00")
    assert schema.data.total_available_credit == Decimal("4500.00")
    assert schema.data.total_liabilities_due == Decimal("500.00")
    assert schema.data.net_position == Decimal("500.00")


def test_create_realtime_cashflow_response_schema_with_custom_values():
    """Test creating a RealtimeCashflowResponse schema with custom values."""
    timestamp = datetime(2023, 6, 15, tzinfo=timezone.utc)
    last_updated = datetime(2023, 6, 15, hour=12, tzinfo=timezone.utc)
    
    custom_data = create_realtime_cashflow_schema(
        timestamp=timestamp,
        total_available_funds=Decimal("3000.00"),
        total_available_credit=Decimal("6000.00"),
        total_liabilities_due=Decimal("1000.00"),
        net_position=Decimal("2000.00")
    ).model_dump()
    
    schema = create_realtime_cashflow_response_schema(
        data=custom_data,
        last_updated=last_updated
    )
    
    assert isinstance(schema, RealtimeCashflowResponse)
    assert schema.last_updated == last_updated
    assert schema.data.timestamp == timestamp
    assert schema.data.total_available_funds == Decimal("3000.00")
    assert schema.data.total_available_credit == Decimal("6000.00")
    assert schema.data.total_liabilities_due == Decimal("1000.00")
    assert schema.data.net_position == Decimal("2000.00")


def test_realtime_cashflow_validates_net_position():
    """Test that RealtimeCashflow validates net position calculation."""
    # This should pass because net_position = total_available_funds - total_liabilities_due
    valid_schema = create_realtime_cashflow_schema(
        total_available_funds=Decimal("1000.00"),
        total_liabilities_due=Decimal("300.00"),
        net_position=Decimal("700.00")
    )
    
    assert valid_schema.net_position == Decimal("700.00")
    
    # This should fail because net_position != total_available_funds - total_liabilities_due
    with pytest.raises(ValueError):
        create_realtime_cashflow_schema(
            total_available_funds=Decimal("1000.00"),
            total_liabilities_due=Decimal("300.00"),
            net_position=Decimal("500.00")  # Incorrect: should be 700.00
        )
