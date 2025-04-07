"""
Unit tests for checking account schema factories.

Tests ensure that schema factories produce valid schema instances
that pass validation.
"""

# pylint: disable=no-member

import pytest
from decimal import Decimal

from src.utils.datetime_utils import utc_now, utc_datetime
from src.schemas.account_types.banking.checking import (
    CheckingAccountCreate,
    CheckingAccountResponse,
)

from tests.helpers.schema_factories.account_types.banking.checking import (
    create_checking_account_schema,
    create_checking_account_response_schema,
)


def test_create_checking_account_schema():
    """Test creating a CheckingAccountCreate schema."""
    schema = create_checking_account_schema()
    assert isinstance(schema, CheckingAccountCreate)
    assert schema.account_type == "checking"
    assert schema.name == "Test Checking Account"
    assert schema.institution == "Test Bank"
    assert schema.routing_number == "123456789"
    assert schema.has_overdraft_protection is False
    assert schema.account_format == "local"


def test_create_checking_account_schema_with_overdraft():
    """Test creating a CheckingAccountCreate schema with overdraft protection."""
    schema = create_checking_account_schema(
        has_overdraft_protection=True,
        overdraft_limit=Decimal("200.00"),
    )
    assert schema.has_overdraft_protection is True
    assert schema.overdraft_limit == Decimal("200.00")


def test_create_checking_account_schema_with_international():
    """Test creating a CheckingAccountCreate schema with international fields."""
    schema = create_checking_account_schema(
        iban="DE89370400440532013000",
        swift_bic="DEUTDEFF",
        sort_code="123456",
        branch_code="12345",
        account_format="iban",
    )
    assert schema.iban == "DE89370400440532013000"
    assert schema.swift_bic == "DEUTDEFF"
    assert schema.sort_code == "123456"
    assert schema.branch_code == "12345"
    assert schema.account_format == "iban"


def test_create_checking_account_response_schema():
    """Test creating a CheckingAccountResponse schema."""
    now = utc_now()
    schema = create_checking_account_response_schema(
        id=123,
        created_at=now,
        updated_at=now,
    )
    assert isinstance(schema, CheckingAccountResponse)
    assert schema.id == 123
    assert schema.account_type == "checking"
    assert schema.created_at == now
    assert schema.updated_at == now
