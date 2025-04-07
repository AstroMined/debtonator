"""
Unit tests for liability schema factory functions.

Tests ensure that liability schema factories produce valid schema instances
that pass validation.
"""

# pylint: disable=no-member

from datetime import datetime
from decimal import Decimal

import pytest

from src.schemas.liabilities import (
    AutoPaySettings,
    AutoPayUpdate,
    LiabilityCreate,
    LiabilityDateRange,
    LiabilityInDB,
    LiabilityResponse,
    LiabilityUpdate,
)
from src.utils.datetime_utils import utc_datetime, utc_now
from tests.helpers.schema_factories.liabilities import (
    create_liability_schema,
    create_auto_pay_settings_schema,
    create_auto_pay_update_schema,
    create_liability_in_db_schema,
    create_liability_response_schema,
    create_liability_date_range_schema,
    create_liability_update_schema,
)


def test_create_liability_schema():
    """Test creating a LiabilityCreate schema with default values."""
    schema = create_liability_schema(primary_account_id=1)
    
    assert isinstance(schema, LiabilityCreate)
    assert schema.name == "Test Liability"
    assert schema.amount == Decimal("100.00")
    assert schema.primary_account_id == 1
    assert isinstance(schema.due_date, datetime)
    assert schema.paid is False
    assert schema.category_id is not None  # Uses DEFAULT_CATEGORY_ID 


def test_create_liability_schema_with_custom_values():
    """Test creating a LiabilityCreate schema with custom values."""
    due_date = utc_datetime(2023, 5, 15)
    
    schema = create_liability_schema(
        name="Mortgage Payment",
        amount=Decimal("1250.75"),
        due_date=due_date,
        paid=True,
        category_id=5,
        primary_account_id=2
    )
    
    assert isinstance(schema, LiabilityCreate)
    assert schema.name == "Mortgage Payment"
    assert schema.amount == Decimal("1250.75")
    assert schema.due_date == due_date
    assert schema.paid is True
    assert schema.category_id == 5
    assert schema.primary_account_id == 2


def test_create_auto_pay_settings_schema():
    """Test creating an AutoPaySettings schema with default values."""
    schema = create_auto_pay_settings_schema()
    
    assert isinstance(schema, AutoPaySettings)
    assert schema.payment_method == "ACH Transfer"
    assert schema.days_before_due == 5
    assert schema.preferred_pay_date is None
    assert schema.retry_on_failure is True
    assert schema.notification_email is None
    assert schema.minimum_balance_required is None


def test_create_auto_pay_settings_schema_with_custom_values():
    """Test creating an AutoPaySettings schema with custom values."""
    schema = create_auto_pay_settings_schema(
        payment_method="Credit Card",
        preferred_pay_date=10,
        minimum_balance_required=Decimal("500.00"),
        retry_on_failure=False,
        notification_email="test@example.com"
    )
    
    assert isinstance(schema, AutoPaySettings)
    assert schema.payment_method == "Credit Card"
    assert schema.preferred_pay_date == 10
    assert schema.days_before_due is None  # Can't set both preferred_pay_date and days_before_due
    assert schema.minimum_balance_required == Decimal("500.00")
    assert schema.retry_on_failure is False
    assert schema.notification_email == "test@example.com"


def test_create_auto_pay_update_schema():
    """Test creating an AutoPayUpdate schema with default values."""
    schema = create_auto_pay_update_schema()
    
    assert isinstance(schema, AutoPayUpdate)
    assert schema.enabled is True
    assert isinstance(schema.settings, AutoPaySettings)
    assert schema.settings.payment_method == "ACH Transfer"


def test_create_auto_pay_update_schema_disabled():
    """Test creating an AutoPayUpdate schema for disabling auto-pay."""
    schema = create_auto_pay_update_schema(enabled=False)
    
    assert isinstance(schema, AutoPayUpdate)
    assert schema.enabled is False
    assert schema.settings is None


def test_create_auto_pay_update_schema_with_custom_settings():
    """Test creating an AutoPayUpdate schema with custom settings."""
    custom_settings = create_auto_pay_settings_schema(
        payment_method="Bank Transfer",
        days_before_due=3
    )
    
    schema = create_auto_pay_update_schema(
        enabled=True,
        settings=custom_settings
    )
    
    assert isinstance(schema, AutoPayUpdate)
    assert schema.enabled is True
    assert schema.settings.payment_method == "Bank Transfer"
    assert schema.settings.days_before_due == 3


def test_create_liability_in_db_schema():
    """Test creating a LiabilityInDB schema with default values."""
    schema = create_liability_in_db_schema(id=1)
    
    assert isinstance(schema, LiabilityInDB)
    assert schema.id == 1
    assert schema.name == "Test Liability"
    assert schema.amount == Decimal("100.00")
    assert isinstance(schema.due_date, datetime)
    assert schema.paid is False
    assert schema.recurring is False
    assert schema.auto_pay is False
    assert schema.auto_pay_enabled is False
    assert schema.category_id == 1
    assert schema.primary_account_id == 1
    assert isinstance(schema.created_at, datetime)
    assert isinstance(schema.updated_at, datetime)


def test_create_liability_in_db_schema_with_auto_pay():
    """Test creating a LiabilityInDB schema with auto-pay enabled."""
    schema = create_liability_in_db_schema(
        id=2,
        auto_pay=True,
        auto_pay_enabled=True
    )
    
    assert isinstance(schema, LiabilityInDB)
    assert schema.id == 2
    assert schema.auto_pay is True
    assert schema.auto_pay_enabled is True
    assert isinstance(schema.auto_pay_settings, AutoPaySettings)
    assert schema.auto_pay_settings.payment_method == "ACH Transfer"


def test_create_liability_in_db_schema_with_custom_values():
    """Test creating a LiabilityInDB schema with custom values."""
    due_date = utc_datetime(2023, 6, 15)
    created_at = utc_datetime(2023, 6, 1) 
    updated_at = utc_datetime(2023, 6, 5)
    auto_pay_settings = create_auto_pay_settings_schema(
        payment_method="Direct Debit",
        days_before_due=7
    )
    
    schema = create_liability_in_db_schema(
        id=3,
        name="Car Payment",
        amount=Decimal("350.50"),
        due_date=due_date,
        category_id=4,
        primary_account_id=2,
        paid=True,
        recurring=True,
        auto_pay=True,
        auto_pay_enabled=True,
        auto_pay_settings=auto_pay_settings,
        recurring_bill_id=5,
        created_at=created_at,
        updated_at=updated_at
    )
    
    assert isinstance(schema, LiabilityInDB)
    assert schema.id == 3
    assert schema.name == "Car Payment"
    assert schema.amount == Decimal("350.50")
    assert schema.due_date == due_date
    assert schema.category_id == 4
    assert schema.primary_account_id == 2
    assert schema.paid is True
    assert schema.recurring is True
    assert schema.auto_pay is True
    assert schema.auto_pay_enabled is True
    assert schema.auto_pay_settings.payment_method == "Direct Debit"
    assert schema.auto_pay_settings.days_before_due == 7
    assert schema.recurring_bill_id == 5
    assert schema.created_at == created_at
    assert schema.updated_at == updated_at


def test_create_liability_response_schema():
    """Test creating a LiabilityResponse schema with default values."""
    schema = create_liability_response_schema(id=4)
    
    assert isinstance(schema, LiabilityResponse)
    assert schema.id == 4
    assert schema.name == "Test Liability"
    assert schema.amount == Decimal("100.00")
    assert isinstance(schema.due_date, datetime)
    # Other fields would be the same as LiabilityInDB


def test_create_liability_date_range_schema():
    """Test creating a LiabilityDateRange schema with default values."""
    schema = create_liability_date_range_schema()
    
    assert isinstance(schema, LiabilityDateRange)
    assert isinstance(schema.start_date, datetime)
    assert isinstance(schema.end_date, datetime)
    assert schema.end_date > schema.start_date


def test_create_liability_date_range_schema_with_custom_values():
    """Test creating a LiabilityDateRange schema with custom values."""
    start_date = utc_datetime(2023, 1, 1)
    end_date = utc_datetime(2023, 12, 31)
    
    schema = create_liability_date_range_schema(
        start_date=start_date,
        end_date=end_date
    )
    
    assert isinstance(schema, LiabilityDateRange)
    assert schema.start_date == start_date
    assert schema.end_date == end_date


def test_create_liability_update_schema():
    """Test creating a LiabilityUpdate schema with default values."""
    schema = create_liability_update_schema(id=5)
    
    assert isinstance(schema, LiabilityUpdate)
    # The fields exist but are set to None
    assert schema.name is None
    assert schema.amount is None 
    assert schema.due_date is None
    # paid field isn't in LiabilityUpdate schema


def test_create_liability_update_schema_with_values():
    """Test creating a LiabilityUpdate schema with specified values."""
    due_date = utc_datetime(2023, 8, 15)
    
    schema = create_liability_update_schema(
        id=6,
        name="Updated Liability",
        amount=Decimal("200.00"),
        due_date=due_date
        # paid field isn't in LiabilityUpdate schema
    )
    
    assert isinstance(schema, LiabilityUpdate)
    assert schema.name == "Updated Liability"
    assert schema.amount == Decimal("200.00") 
    assert schema.due_date == due_date