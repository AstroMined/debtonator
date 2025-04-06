"""
Unit tests for recurring income schema factory functions.

Tests ensure that recurring income schema factories produce valid schema instances
that pass validation.
"""

# pylint: disable=no-member

from decimal import Decimal
from datetime import datetime

import pytest

from src.schemas.recurring_income import (
    RecurringIncomeCreate,
    RecurringIncomeInDB,
    RecurringIncomeResponse,
    RecurringIncomeUpdate,
)
from src.utils.datetime_utils import utc_now, utc_datetime
from tests.helpers.schema_factories.base import MEDIUM_AMOUNT
from tests.helpers.schema_factories.recurring_income import (
    create_recurring_income_schema,
    create_recurring_income_update_schema,
    create_recurring_income_in_db_schema,
    create_recurring_income_response_schema,
)


def test_create_recurring_income_schema_default():
    """Test creating a RecurringIncomeCreate schema with default values."""
    schema = create_recurring_income_schema()
    
    assert isinstance(schema, RecurringIncomeCreate)
    assert schema.source == "Monthly Salary"
    assert schema.amount == MEDIUM_AMOUNT * Decimal("10")  # 1000.00
    assert schema.day_of_month == 15
    assert schema.account_id == 1
    assert schema.category_id is None
    assert schema.auto_deposit is False
    # Note: active field is in factory but not in schema


def test_create_recurring_income_schema_custom():
    """Test creating a RecurringIncomeCreate schema with custom values."""
    schema = create_recurring_income_schema(
        source="Consulting Income",
        amount=Decimal("2500.00"),
        day_of_month=5,
        account_id=3,
        category_id=10,
        auto_deposit=True,
        active=True  # Passed to factory but not in schema
    )
    
    assert isinstance(schema, RecurringIncomeCreate)
    assert schema.source == "Consulting Income"
    assert schema.amount == Decimal("2500.00")
    assert schema.day_of_month == 5
    assert schema.account_id == 3
    assert schema.category_id == 10
    assert schema.auto_deposit is True
    # Note: active field is in factory but not in schema


def test_create_recurring_income_update_schema_empty():
    """Test creating an empty RecurringIncomeUpdate schema."""
    schema = create_recurring_income_update_schema()
    
    assert isinstance(schema, RecurringIncomeUpdate)
    assert schema.source is None
    assert schema.amount is None
    assert schema.day_of_month is None
    assert schema.account_id is None
    assert schema.category_id is None
    assert schema.auto_deposit is None
    assert schema.active is None


def test_create_recurring_income_update_schema_partial():
    """Test creating a RecurringIncomeUpdate schema with partial fields."""
    schema = create_recurring_income_update_schema(
        amount=Decimal("1800.00"),
        active=False
    )
    
    assert isinstance(schema, RecurringIncomeUpdate)
    assert schema.source is None
    assert schema.amount == Decimal("1800.00")
    assert schema.day_of_month is None
    assert schema.account_id is None
    assert schema.category_id is None
    assert schema.auto_deposit is None
    assert schema.active is False


def test_create_recurring_income_update_schema_full():
    """Test creating a RecurringIncomeUpdate schema with all fields."""
    schema = create_recurring_income_update_schema(
        source="Updated Income",
        amount=Decimal("2200.00"),
        day_of_month=20,
        account_id=2,
        category_id=5,
        auto_deposit=True,
        active=True
    )
    
    assert isinstance(schema, RecurringIncomeUpdate)
    assert schema.source == "Updated Income"
    assert schema.amount == Decimal("2200.00")
    assert schema.day_of_month == 20
    assert schema.account_id == 2
    assert schema.category_id == 5
    assert schema.auto_deposit is True
    assert schema.active is True


def test_create_recurring_income_in_db_schema_default():
    """Test creating a RecurringIncomeInDB schema with default values."""
    # Schema needs UTC datetime
    schema = create_recurring_income_in_db_schema()
    
    assert isinstance(schema, RecurringIncomeInDB)
    assert schema.id == 1
    assert schema.source == "Monthly Salary"
    assert schema.amount == MEDIUM_AMOUNT * Decimal("10")  # 1000.00
    assert schema.day_of_month == 15
    assert schema.account_id == 1
    assert schema.category_id is None
    assert schema.auto_deposit is False
    assert schema.active is True
    assert schema.created_at is not None
    assert schema.updated_at is not None
    # Verify datetime has timezone info
    assert schema.created_at.tzinfo is not None
    assert schema.updated_at.tzinfo is not None


def test_create_recurring_income_in_db_schema_custom():
    """Test creating a RecurringIncomeInDB schema with custom values."""
    # Need to use timezone-aware datetimes
    created_at = utc_datetime(2023, 1, 1)
    updated_at = utc_datetime(2023, 2, 1)
    
    schema = create_recurring_income_in_db_schema(
        id=5,
        source="Freelance Income",
        amount=Decimal("3000.00"),
        day_of_month=25,
        account_id=4,
        category_id=7,
        auto_deposit=True,
        active=False,
        created_at=created_at,
        updated_at=updated_at
    )
    
    assert isinstance(schema, RecurringIncomeInDB)
    assert schema.id == 5
    assert schema.source == "Freelance Income"
    assert schema.amount == Decimal("3000.00")
    assert schema.day_of_month == 25
    assert schema.account_id == 4
    assert schema.category_id == 7
    assert schema.auto_deposit is True
    assert schema.active is False
    assert schema.created_at == created_at
    assert schema.updated_at == updated_at
    # Verify datetime has timezone info
    assert schema.created_at.tzinfo is not None
    assert schema.updated_at.tzinfo is not None


def test_create_recurring_income_response_schema_default():
    """Test creating a RecurringIncomeResponse schema with default values."""
    schema = create_recurring_income_response_schema()
    
    assert isinstance(schema, RecurringIncomeResponse)
    assert schema.id == 1
    assert schema.source == "Monthly Salary"
    assert schema.amount == MEDIUM_AMOUNT * Decimal("10")  # 1000.00
    assert schema.day_of_month == 15
    assert schema.account_id == 1
    assert schema.category_id is None
    assert schema.auto_deposit is False
    assert schema.active is True
    assert schema.created_at is not None
    assert schema.updated_at is not None
    # Verify datetime has timezone info
    assert schema.created_at.tzinfo is not None
    assert schema.updated_at.tzinfo is not None
    
    # Note: account and category fields are passed to factory but not in schema


def test_create_recurring_income_response_schema_with_category():
    """Test creating a RecurringIncomeResponse schema with category."""
    schema = create_recurring_income_response_schema(
        category_id=5
    )
    
    assert isinstance(schema, RecurringIncomeResponse)
    assert schema.category_id == 5
    # Note: category field is passed to factory but not in schema
    # Verify datetime has timezone info
    assert schema.created_at.tzinfo is not None
    assert schema.updated_at.tzinfo is not None


def test_create_recurring_income_response_schema_custom():
    """Test creating a RecurringIncomeResponse schema with custom values and overrides."""
    # Need to use timezone-aware datetimes
    created_at = utc_datetime(2023, 1, 1)
    updated_at = utc_datetime(2023, 2, 1)
    
    custom_account = {
        "id": 10,
        "name": "Custom Account",
        "account_type": "savings",
        "active": True,
    }
    
    custom_category = {
        "id": 20,
        "name": "Custom Category",
    }
    
    schema = create_recurring_income_response_schema(
        id=15,
        source="Custom Income",
        amount=Decimal("4500.00"),
        day_of_month=10,
        account_id=10,
        category_id=20,
        auto_deposit=True,
        active=True,
        created_at=created_at,
        updated_at=updated_at,
        account=custom_account,  # Passed to factory but not in schema
        category=custom_category  # Passed to factory but not in schema
    )
    
    assert isinstance(schema, RecurringIncomeResponse)
    assert schema.id == 15
    assert schema.source == "Custom Income"
    assert schema.amount == Decimal("4500.00")
    assert schema.day_of_month == 10
    assert schema.account_id == 10
    assert schema.category_id == 20
    assert schema.created_at == created_at
    assert schema.updated_at == updated_at
    
    # Note: account and category fields are passed to factory but not in schema
