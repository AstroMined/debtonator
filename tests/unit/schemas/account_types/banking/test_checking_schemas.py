"""
Unit tests for CheckingAccount schemas.

Tests the checking account schema validation and serialization
as part of ADR-016 Account Type Expansion and ADR-019 Banking Account Types Expansion.
"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.schemas.account_types.banking.checking import (
    CheckingAccountCreate,
    CheckingAccountResponse,
)
from src.utils.datetime_utils import utc_now


def test_checking_account_create_schema():
    """Test the checking account create schema."""
    # Test with minimum required fields
    checking = CheckingAccountCreate(
        name="Basic Checking",
        account_type="checking",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
    )
    assert checking.name == "Basic Checking"
    assert checking.account_type == "checking"
    assert checking.current_balance == Decimal("1000.00")

    # Test with all fields
    checking = CheckingAccountCreate(
        name="Full Checking",
        account_type="checking",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
        institution="Test Bank",
        currency="USD",
        account_number="1234567890",
        routing_number="987654321",
        has_overdraft_protection=True,
        overdraft_limit=Decimal("500.00"),
        monthly_fee=Decimal("5.00"),
        interest_rate=Decimal("0.0025"),  # 0.25%
        iban="DE89370400440532013000",
        swift_bic="COBADEFFXXX",
        sort_code="12-34-56",
        branch_code="001",
        account_format="local",
    )
    assert checking.routing_number == "987654321"
    assert checking.has_overdraft_protection is True
    assert checking.overdraft_limit == Decimal("500.00")
    assert checking.monthly_fee == Decimal("5.00")
    assert checking.interest_rate == Decimal("0.0025")

    # Test validation of incorrect account type
    with pytest.raises(ValidationError, match="Value error at account_type"):
        CheckingAccountCreate(
            name="Invalid Type",
            account_type="savings",  # Wrong type
            current_balance=Decimal("1000.00"),
            available_balance=Decimal("1000.00"),
        )

    # Test validation of money decimals
    with pytest.raises(ValidationError):
        CheckingAccountCreate(
            name="Invalid Decimal",
            account_type="checking",
            current_balance=Decimal("1000.12345"),  # Too many decimal places
            available_balance=Decimal("1000.00"),
        )


def test_checking_account_response_schema():
    """Test the checking account response schema."""
    now = utc_now()

    # Test with required fields
    checking_response = CheckingAccountResponse(
        id=1,
        name="Checking Response",
        account_type="checking",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
        routing_number="123456789",
        has_overdraft_protection=True,
        overdraft_limit=Decimal("500.00"),
        created_at=now,
        updated_at=now,
    )
    assert checking_response.id == 1
    assert checking_response.name == "Checking Response"
    assert checking_response.account_type == "checking"
    assert checking_response.routing_number == "123456789"
    assert checking_response.has_overdraft_protection is True
    assert checking_response.created_at == now

    # Test validation of incorrect account type
    with pytest.raises(ValidationError, match="Value error at account_type"):
        CheckingAccountResponse(
            id=1,
            name="Invalid Type",
            account_type="savings",  # Wrong type
            current_balance=Decimal("1000.00"),
            available_balance=Decimal("1000.00"),
            routing_number="123456789",
            has_overdraft_protection=True,
            created_at=now,
            updated_at=now,
        )
