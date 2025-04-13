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
    CheckingAccountUpdate,
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
    assert checking.available_balance == Decimal("1000.00")

    # Test with all fields
    checking = CheckingAccountCreate(
        name="Full Checking",
        account_type="checking",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("980.00"),
        institution="Test Bank",
        currency="USD",
        account_number="12345678",
        routing_number="123456789",
        has_checks=True,
        has_debit_card=True,
        card_last_four="5678",
        has_overdraft_protection=True,
        overdraft_limit=Decimal("500.00"),
        monthly_fee=Decimal("12.95"),
        interest_rate=Decimal("0.0025"),
        iban="DE89370400440532013000",
        swift_bic="COBADEFFXXX",
        sort_code="12-34-56",
        branch_code="001",
        account_format="local",
    )
    assert checking.institution == "Test Bank"
    assert checking.routing_number == "123456789"
    assert checking.has_overdraft_protection is True
    assert checking.overdraft_limit == Decimal("500.00")
    assert checking.interest_rate == Decimal("0.0025")

    # Test validation of incorrect account type
    with pytest.raises(ValidationError, match="Input should be 'checking'"):
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

    # Test with minimum required fields
    checking_response = CheckingAccountResponse(
        id=1,
        name="Checking Response",
        account_type="checking",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
        created_at=now,
        updated_at=now,
    )
    assert checking_response.id == 1
    assert checking_response.name == "Checking Response"
    assert checking_response.account_type == "checking"
    assert checking_response.created_at == now
    assert checking_response.updated_at == now

    # Test with all fields
    checking_response = CheckingAccountResponse(
        id=2,
        name="Full Checking Response",
        account_type="checking",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("980.00"),
        institution="Test Bank",
        currency="USD",
        account_number="12345678",
        routing_number="123456789",
        has_checks=True,
        has_debit_card=True,
        card_last_four="5678",
        has_overdraft_protection=True,
        overdraft_limit=Decimal("500.00"),
        monthly_fee=Decimal("12.95"),
        interest_rate=Decimal("0.0025"),
        iban="DE89370400440532013000",
        swift_bic="COBADEFFXXX",
        sort_code="12-34-56",
        branch_code="001",
        account_format="local",
        created_at=now,
        updated_at=now,
    )
    assert checking_response.institution == "Test Bank"
    assert checking_response.routing_number == "123456789"
    assert checking_response.has_overdraft_protection is True
    assert checking_response.overdraft_limit == Decimal("500.00")

    # Test validation of incorrect account type
    with pytest.raises(ValidationError, match="Input should be 'checking'"):
        CheckingAccountResponse(
            id=1,
            name="Invalid Type",
            account_type="savings",  # Wrong type
            current_balance=Decimal("1000.00"),
            available_balance=Decimal("1000.00"),
            created_at=now,
            updated_at=now,
        )


def test_checking_account_overdraft_validation():
    """Test overdraft protection validation in checking account schemas."""
    # Test with overdraft protection enabled and limit set
    checking = CheckingAccountCreate(
        name="Overdraft Protected",
        account_type="checking",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
        has_overdraft_protection=True,
        overdraft_limit=Decimal("500.00"),
    )
    assert checking.has_overdraft_protection is True
    assert checking.overdraft_limit == Decimal("500.00")

    # Test with overdraft protection disabled and no limit
    checking = CheckingAccountCreate(
        name="No Overdraft",
        account_type="checking",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
        has_overdraft_protection=False,
    )
    assert checking.has_overdraft_protection is False
    assert checking.overdraft_limit is None

    # Test with overdraft protection enabled but no limit
    # This should trigger the validation error
    with pytest.raises(ValidationError, match="Overdraft limit is required when overdraft protection is enabled"):
        CheckingAccountCreate(
            name="Overdraft Without Limit",
            account_type="checking",
            current_balance=Decimal("1000.00"),
            available_balance=Decimal("1000.00"),
            has_overdraft_protection=True,  # Enabled but no limit set
            overdraft_limit=None,  # Explicitly set to None
        )

    # Test with overdraft protection disabled but limit set
    with pytest.raises(
        ValidationError,
        match="Overdraft limit cannot be set when overdraft protection is disabled",
    ):
        CheckingAccountCreate(
            name="No Overdraft With Limit",
            account_type="checking",
            current_balance=Decimal("1000.00"),
            available_balance=Decimal("1000.00"),
            has_overdraft_protection=False,
            overdraft_limit=Decimal("500.00"),  # Disabled but limit set
        )


def test_checking_account_routing_number_validation():
    """Test routing number validation in checking account schemas."""
    # Test with valid routing number
    checking = CheckingAccountCreate(
        name="Valid Routing",
        account_type="checking",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
        routing_number="123456789",
    )
    assert checking.routing_number == "123456789"

    # Test with minimum length routing number
    checking = CheckingAccountCreate(
        name="Min Length Routing",
        account_type="checking",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
        routing_number="12345678",  # Exactly 8 digits
    )
    assert checking.routing_number == "12345678"

    # Test with empty string (should be allowed)
    checking = CheckingAccountCreate(
        name="Empty Routing",
        account_type="checking",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
        routing_number="",
    )
    assert checking.routing_number == ""

    # Test with None (should be allowed as it's the default)
    checking = CheckingAccountCreate(
        name="No Routing",
        account_type="checking",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
        routing_number=None,
    )
    assert checking.routing_number is None

    # Test with non-digit characters
    with pytest.raises(ValidationError, match="Routing number must be at least 8 digits"):
        CheckingAccountCreate(
            name="Invalid Routing",
            account_type="checking",
            current_balance=Decimal("1000.00"),
            available_balance=Decimal("1000.00"),
            routing_number="123-456-78",  # Contains non-digit characters
        )

    # Test with too short routing number
    with pytest.raises(ValidationError, match="Routing number must be at least 8 digits"):
        CheckingAccountCreate(
            name="Short Routing",
            account_type="checking",
            current_balance=Decimal("1000.00"),
            available_balance=Decimal("1000.00"),
            routing_number="1234567",  # Only 7 digits
        )


def test_checking_account_account_format_validation():
    """Test account format validation in checking account schemas."""
    # Test with each valid format
    valid_formats = ["local", "iban", "swift", "sort_code", "branch_code"]
    
    for format_value in valid_formats:
        checking = CheckingAccountCreate(
            name=f"{format_value.capitalize()} Format",
            account_type="checking",
            current_balance=Decimal("1000.00"),
            available_balance=Decimal("1000.00"),
            account_format=format_value,
        )
        assert checking.account_format == format_value

    # Test with invalid format
    with pytest.raises(ValidationError, match="Account format must be one of:"):
        CheckingAccountCreate(
            name="Invalid Format",
            account_type="checking",
            current_balance=Decimal("1000.00"),
            available_balance=Decimal("1000.00"),
            account_format="invalid_format",
        )

    # Test default value
    checking = CheckingAccountCreate(
        name="Default Format",
        account_type="checking",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
    )
    assert checking.account_format == "local"  # Default should be "local"


def test_checking_account_update_schema():
    """Test the checking account update schema."""
    # Test with no fields (all optional in update)
    update = CheckingAccountUpdate()
    assert update.account_type is None
    assert update.name is None
    assert update.current_balance is None
    assert update.available_balance is None

    # Test with some fields
    update = CheckingAccountUpdate(
        name="Updated Checking",
        current_balance=Decimal("1500.00"),
        available_balance=Decimal("1450.00"),
    )
    assert update.name == "Updated Checking"
    assert update.current_balance == Decimal("1500.00")
    assert update.available_balance == Decimal("1450.00")
    assert update.account_type is None

    # Test with explicit account type
    update = CheckingAccountUpdate(
        account_type="checking",
        name="Updated Checking",
    )
    assert update.account_type == "checking"
    assert update.name == "Updated Checking"

    # Test with wrong account type
    with pytest.raises(ValidationError, match="Input should be 'checking'"):
        CheckingAccountUpdate(
            account_type="savings",  # Wrong type
            name="Wrong Type Update",
        )


def test_checking_account_update_overdraft_validation():
    """Test overdraft protection validation in checking account update schema."""
    # Test setting both has_overdraft_protection and overdraft_limit
    update = CheckingAccountUpdate(
        has_overdraft_protection=True,
        overdraft_limit=Decimal("750.00"),
    )
    assert update.has_overdraft_protection is True
    assert update.overdraft_limit == Decimal("750.00")

    # Test setting neither (should be valid for update)
    update = CheckingAccountUpdate(
        name="Update Without Overdraft Changes",
    )
    assert update.has_overdraft_protection is None
    assert update.overdraft_limit is None

    # Test disabling protection and clearing limit
    update = CheckingAccountUpdate(
        has_overdraft_protection=False,
        overdraft_limit=None,
    )
    assert update.has_overdraft_protection is False
    assert update.overdraft_limit is None

    # Test enabling protection but no limit
    # In update schema, we can't validate this if the overdraft_limit is None
    # since None means "don't update" rather than "set to None"
    update = CheckingAccountUpdate(
        has_overdraft_protection=True,
        overdraft_limit=None,
    )
    assert update.has_overdraft_protection is True
    assert update.overdraft_limit is None

    # Test conflict: disabling protection but setting limit
    with pytest.raises(ValidationError, match="Overdraft limit cannot be set when overdraft protection is disabled"):
        CheckingAccountUpdate(
            has_overdraft_protection=False,
            overdraft_limit=Decimal("500.00"),
        )

    # Test updating only the limit (without changing protection status)
    update = CheckingAccountUpdate(
        overdraft_limit=Decimal("1000.00"),
    )
    assert update.has_overdraft_protection is None
    assert update.overdraft_limit == Decimal("1000.00")


def test_checking_account_update_routing_number_validation():
    """Test routing number validation in checking account update schema."""
    # Test valid routing number
    update = CheckingAccountUpdate(
        routing_number="987654321",
    )
    assert update.routing_number == "987654321"

    # Test with None (don't update)
    update = CheckingAccountUpdate(
        routing_number=None,
    )
    assert update.routing_number is None

    # Test with empty string
    update = CheckingAccountUpdate(
        routing_number="",
    )
    assert update.routing_number == ""

    # Test with invalid format
    with pytest.raises(ValidationError, match="Routing number must be at least 8 digits"):
        CheckingAccountUpdate(
            routing_number="123abc",
        )

    # Test with too short
    with pytest.raises(ValidationError, match="Routing number must be at least 8 digits"):
        CheckingAccountUpdate(
            routing_number="1234567",  # 7 digits, need at least 8
        )


def test_checking_account_update_account_format_validation():
    """Test account format validation in checking account update schema."""
    # Test each valid format
    valid_formats = ["local", "iban", "swift", "sort_code", "branch_code"]
    
    for format_value in valid_formats:
        update = CheckingAccountUpdate(
            account_format=format_value,
        )
        assert update.account_format == format_value

    # Test with None (don't update)
    update = CheckingAccountUpdate(
        account_format=None,
    )
    assert update.account_format is None

    # Test with invalid format
    with pytest.raises(ValidationError, match="Account format must be one of:"):
        CheckingAccountUpdate(
            account_format="unknown_format",
        )


def test_international_banking_fields():
    """Test international banking fields in checking account schemas."""
    # Test with all international fields
    checking = CheckingAccountCreate(
        name="International Account",
        account_type="checking",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
        iban="DE89370400440532013000",
        swift_bic="COBADEFFXXX",
        sort_code="12-34-56",
        branch_code="001",
        account_format="iban",
    )
    assert checking.iban == "DE89370400440532013000"
    assert checking.swift_bic == "COBADEFFXXX"
    assert checking.sort_code == "12-34-56"
    assert checking.branch_code == "001"
    assert checking.account_format == "iban"

    # Test update of international fields
    update = CheckingAccountUpdate(
        iban="FR1420041010050500013M02606",
        swift_bic="SOGEFRPP",
        sort_code="",  # Clear the field
        branch_code=None,  # Don't update
        account_format="swift",
    )
    assert update.iban == "FR1420041010050500013M02606"
    assert update.swift_bic == "SOGEFRPP"
    assert update.sort_code == ""
    assert update.branch_code is None
    assert update.account_format == "swift"
