"""
Unit tests for CreditAccount schemas.

Tests the credit account schema validation and serialization
as part of ADR-016 Account Type Expansion and ADR-019 Banking Account Types Expansion.
"""

from decimal import Decimal
from datetime import datetime, timedelta

import pytest
from pydantic import ValidationError

from src.schemas.account_types.banking.credit import (
    CreditAccountCreate,
    CreditAccountResponse,
    CreditAccountUpdate,
)
from src.utils.datetime_utils import utc_now


def test_credit_account_create_schema():
    """Test the credit account create schema."""
    # Test with minimum required fields
    credit = CreditAccountCreate(
        name="Basic Credit Card",
        account_type="credit",
        current_balance=Decimal("500.00"),
        available_balance=Decimal("500.00"),
        credit_limit=Decimal("2000.00"),
    )
    assert credit.name == "Basic Credit Card"
    assert credit.account_type == "credit"
    assert credit.credit_limit == Decimal("2000.00")

    # Test with all fields
    statement_date = utc_now()
    credit = CreditAccountCreate(
        name="Full Credit Card",
        account_type="credit",
        current_balance=Decimal("500.00"),
        available_balance=Decimal("500.00"),
        institution="Test Bank",
        currency="USD",
        account_number="5432-1098-7654-3210",
        credit_limit=Decimal("3000.00"),
        statement_balance=Decimal("750.00"),
        statement_due_date=statement_date,
        minimum_payment=Decimal("35.00"),
        apr=Decimal("0.1999"),  # 19.99%
        annual_fee=Decimal("95.00"),
        rewards_program="Cash Back Plus",
        autopay_status="minimum",
        last_statement_date=statement_date,
    )
    assert credit.credit_limit == Decimal("3000.00")
    assert credit.statement_balance == Decimal("750.00")
    assert credit.minimum_payment == Decimal("35.00")
    assert credit.apr == Decimal("0.1999")
    assert credit.annual_fee == Decimal("95.00")
    assert credit.rewards_program == "Cash Back Plus"

    # Test validation of incorrect account type
    with pytest.raises(ValidationError, match="Input should be 'credit'"):
        CreditAccountCreate(
            name="Invalid Type",
            account_type="checking",  # Wrong type
            current_balance=Decimal("500.00"),
            available_balance=Decimal("500.00"),
            credit_limit=Decimal("2000.00"),
        )

    # Test validation of credit-specific field
    with pytest.raises(ValidationError, match="credit_limit"):
        CreditAccountCreate(
            name="Invalid Credit Limit",
            account_type="credit",
            current_balance=Decimal("500.00"),
            available_balance=Decimal("500.00"),
            # Missing required credit_limit
        )


def test_credit_account_response_schema():
    """Test the credit account response schema."""
    now = utc_now()

    # Test with minimum required fields
    credit_response = CreditAccountResponse(
        id=1,
        name="Credit Response",
        account_type="credit",
        current_balance=Decimal("500.00"),
        available_balance=Decimal("500.00"),
        credit_limit=Decimal("2000.00"),
        created_at=now,
        updated_at=now,
    )
    assert credit_response.id == 1
    assert credit_response.name == "Credit Response"
    assert credit_response.account_type == "credit"
    assert credit_response.credit_limit == Decimal("2000.00")
    assert credit_response.created_at == now
    assert credit_response.updated_at == now

    # Test with all fields
    credit_response = CreditAccountResponse(
        id=2,
        name="Full Credit Response",
        account_type="credit",
        current_balance=Decimal("750.00"),
        available_balance=Decimal("750.00"),
        institution="Test Bank",
        currency="USD",
        account_number="5432-1098-7654-3210",
        credit_limit=Decimal("3000.00"),
        statement_balance=Decimal("750.00"),
        statement_due_date=now,
        minimum_payment=Decimal("35.00"),
        apr=Decimal("0.1999"),  # 19.99%
        annual_fee=Decimal("95.00"),
        rewards_program="Cash Back Plus",
        autopay_status="minimum",
        last_statement_date=now,
        created_at=now,
        updated_at=now,
    )
    assert credit_response.statement_balance == Decimal("750.00")
    assert credit_response.minimum_payment == Decimal("35.00")
    assert credit_response.apr == Decimal("0.1999")

    # Test validation of incorrect account type
    with pytest.raises(ValidationError, match="Input should be 'credit'"):
        CreditAccountResponse(
            id=1,
            name="Invalid Type",
            account_type="checking",  # Wrong type
            current_balance=Decimal("500.00"),
            available_balance=Decimal("500.00"),
            credit_limit=Decimal("2000.00"),
            created_at=now,
            updated_at=now,
        )


def test_credit_account_money_validation():
    """Test money validation in credit account schemas."""
    # Test valid APR (should be between 0 and 1 for decimal percentage)
    # Note: In current implementation, the APR validation is not enforcing upper limit of 1
    credit = CreditAccountCreate(
        name="Valid APR",
        account_type="credit",
        current_balance=Decimal("500.00"),
        available_balance=Decimal("500.00"),
        credit_limit=Decimal("2000.00"),
        apr=Decimal("0.25"),  # 25%
    )
    assert credit.apr == Decimal("0.25")

    # Test valid APR above 1.0 (which is now allowed)
    credit = CreditAccountCreate(
        name="High APR",
        account_type="credit",
        current_balance=Decimal("500.00"),
        available_balance=Decimal("500.00"),
        credit_limit=Decimal("2000.00"),
        apr=Decimal("1.5"),  # 150% (predatory, but valid in the schema)
    )
    assert credit.apr == Decimal("1.5")

    # Test negative annual fee
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        CreditAccountCreate(
            name="Invalid Fee",
            account_type="credit",
            current_balance=Decimal("500.00"),
            available_balance=Decimal("500.00"),
            credit_limit=Decimal("2000.00"),
            annual_fee=Decimal("-95.00"),  # Negative value not allowed
        )


def test_credit_account_update_schema():
    """Test the credit account update schema."""
    # Test with no fields (all optional in update)
    update = CreditAccountUpdate()
    assert update.account_type is None
    assert update.name is None
    assert update.current_balance is None
    assert update.available_balance is None
    assert update.credit_limit is None

    # Test with some fields
    update = CreditAccountUpdate(
        name="Updated Credit Card",
        credit_limit=Decimal("5000.00"),
        apr=Decimal("0.1799"),
    )
    assert update.name == "Updated Credit Card"
    assert update.credit_limit == Decimal("5000.00")
    assert update.apr == Decimal("0.1799")
    assert update.account_type is None

    # Test with explicit account type
    update = CreditAccountUpdate(
        account_type="credit",
        name="Updated Credit Card Type",
    )
    assert update.account_type == "credit"
    assert update.name == "Updated Credit Card Type"

    # Test with wrong account type
    with pytest.raises(ValidationError, match="Input should be 'credit'"):
        CreditAccountUpdate(
            account_type="checking",  # Wrong type
            name="Wrong Type Update",
        )


def test_minimum_payment_validation():
    """Test minimum payment validation in credit account schemas."""
    # Test valid: minimum payment less than statement balance
    credit = CreditAccountCreate(
        name="Valid Minimum Payment",
        account_type="credit",
        current_balance=Decimal("500.00"),
        available_balance=Decimal("500.00"),
        credit_limit=Decimal("2000.00"),
        statement_balance=Decimal("500.00"),
        minimum_payment=Decimal("25.00"),
    )
    assert credit.statement_balance == Decimal("500.00")
    assert credit.minimum_payment == Decimal("25.00")

    # Test valid: minimum payment equal to statement balance
    credit = CreditAccountCreate(
        name="Equal Minimum Payment",
        account_type="credit",
        current_balance=Decimal("500.00"),
        available_balance=Decimal("500.00"),
        credit_limit=Decimal("2000.00"),
        statement_balance=Decimal("500.00"),
        minimum_payment=Decimal("500.00"),
    )
    assert credit.statement_balance == Decimal("500.00")
    assert credit.minimum_payment == Decimal("500.00")

    # Test invalid: minimum payment greater than statement balance
    with pytest.raises(ValidationError, match="Minimum payment cannot exceed statement balance"):
        CreditAccountCreate(
            name="Invalid Minimum Payment",
            account_type="credit",
            current_balance=Decimal("500.00"),
            available_balance=Decimal("500.00"),
            credit_limit=Decimal("2000.00"),
            statement_balance=Decimal("500.00"),
            minimum_payment=Decimal("550.00"),  # Exceeds statement balance
        )

    # Test valid: minimum payment provided but no statement balance
    # This should be valid as validation only applies when both are provided
    credit = CreditAccountCreate(
        name="Minimum Payment Without Statement",
        account_type="credit",
        current_balance=Decimal("500.00"),
        available_balance=Decimal("500.00"),
        credit_limit=Decimal("2000.00"),
        minimum_payment=Decimal("25.00"),
    )
    assert credit.minimum_payment == Decimal("25.00")
    assert credit.statement_balance is None

    # Test valid: statement balance provided but no minimum payment
    credit = CreditAccountCreate(
        name="Statement Without Minimum",
        account_type="credit",
        current_balance=Decimal("500.00"),
        available_balance=Decimal("500.00"),
        credit_limit=Decimal("2000.00"),
        statement_balance=Decimal("500.00"),
    )
    assert credit.statement_balance == Decimal("500.00")
    assert credit.minimum_payment is None

    # Test update: changing only minimum payment
    update = CreditAccountUpdate(
        minimum_payment=Decimal("30.00"),
    )
    assert update.minimum_payment == Decimal("30.00")
    assert update.statement_balance is None

    # Test update: changing only statement balance
    update = CreditAccountUpdate(
        statement_balance=Decimal("600.00"),
    )
    assert update.statement_balance == Decimal("600.00")
    assert update.minimum_payment is None

    # Test update: changing both to valid values
    update = CreditAccountUpdate(
        statement_balance=Decimal("600.00"),
        minimum_payment=Decimal("30.00"),
    )
    assert update.statement_balance == Decimal("600.00")
    assert update.minimum_payment == Decimal("30.00")

    # Test update: invalid minimum payment
    with pytest.raises(ValidationError, match="Minimum payment cannot exceed statement balance"):
        CreditAccountUpdate(
            statement_balance=Decimal("600.00"),
            minimum_payment=Decimal("650.00"),  # Exceeds statement balance
        )


def test_statement_balance_validation():
    """Test statement balance validation in credit account schemas."""
    # Test valid: statement balance less than credit limit
    credit = CreditAccountCreate(
        name="Valid Statement Balance",
        account_type="credit",
        current_balance=Decimal("1500.00"),
        available_balance=Decimal("1500.00"),
        credit_limit=Decimal("2000.00"),
        statement_balance=Decimal("1500.00"),
    )
    assert credit.credit_limit == Decimal("2000.00")
    assert credit.statement_balance == Decimal("1500.00")

    # Test valid: statement balance equal to credit limit
    credit = CreditAccountCreate(
        name="Equal Statement Balance",
        account_type="credit",
        current_balance=Decimal("2000.00"),
        available_balance=Decimal("2000.00"),
        credit_limit=Decimal("2000.00"),
        statement_balance=Decimal("2000.00"),
    )
    assert credit.credit_limit == Decimal("2000.00")
    assert credit.statement_balance == Decimal("2000.00")

    # Test invalid: statement balance greater than credit limit
    with pytest.raises(ValidationError, match="Statement balance cannot exceed credit limit"):
        CreditAccountCreate(
            name="Invalid Statement Balance",
            account_type="credit",
            current_balance=Decimal("2500.00"),
            available_balance=Decimal("2500.00"),
            credit_limit=Decimal("2000.00"),
            statement_balance=Decimal("2500.00"),  # Exceeds credit limit
        )

    # Test valid: no statement balance provided
    credit = CreditAccountCreate(
        name="No Statement Balance",
        account_type="credit",
        current_balance=Decimal("500.00"),
        available_balance=Decimal("500.00"),
        credit_limit=Decimal("2000.00"),
    )
    assert credit.credit_limit == Decimal("2000.00")
    assert credit.statement_balance is None

    # Test update: changing only statement balance
    update = CreditAccountUpdate(
        statement_balance=Decimal("1500.00"),
    )
    assert update.statement_balance == Decimal("1500.00")
    assert update.credit_limit is None

    # Test update: changing only credit limit
    update = CreditAccountUpdate(
        credit_limit=Decimal("5000.00"),
    )
    assert update.credit_limit == Decimal("5000.00")
    assert update.statement_balance is None

    # Test update: changing both to valid values
    update = CreditAccountUpdate(
        credit_limit=Decimal("5000.00"),
        statement_balance=Decimal("3000.00"),
    )
    assert update.credit_limit == Decimal("5000.00")
    assert update.statement_balance == Decimal("3000.00")

    # Test update: invalid statement balance
    with pytest.raises(ValidationError, match="Statement balance cannot exceed credit limit"):
        CreditAccountUpdate(
            credit_limit=Decimal("5000.00"),
            statement_balance=Decimal("6000.00"),  # Exceeds credit limit
        )


def test_autopay_status_validation():
    """Test autopay status validation in credit account schemas."""
    # Test all valid autopay statuses
    valid_statuses = ["none", "minimum", "full_balance", "fixed_amount"]
    
    for status in valid_statuses:
        credit = CreditAccountCreate(
            name=f"{status.capitalize()} Autopay",
            account_type="credit",
            current_balance=Decimal("500.00"),
            available_balance=Decimal("500.00"),
            credit_limit=Decimal("2000.00"),
            autopay_status=status,
        )
        assert credit.autopay_status == status

    # Test invalid autopay status
    with pytest.raises(ValidationError, match="Autopay status must be one of:"):
        CreditAccountCreate(
            name="Invalid Autopay",
            account_type="credit",
            current_balance=Decimal("500.00"),
            available_balance=Decimal("500.00"),
            credit_limit=Decimal("2000.00"),
            autopay_status="partial",  # Invalid status
        )

    # Test empty string (not in valid values)
    with pytest.raises(ValidationError, match="Autopay status must be one of:"):
        CreditAccountCreate(
            name="Empty Autopay",
            account_type="credit",
            current_balance=Decimal("500.00"),
            available_balance=Decimal("500.00"),
            credit_limit=Decimal("2000.00"),
            autopay_status="",  # Empty string is not valid
        )

    # Test None (default value)
    credit = CreditAccountCreate(
        name="No Autopay",
        account_type="credit",
        current_balance=Decimal("500.00"),
        available_balance=Decimal("500.00"),
        credit_limit=Decimal("2000.00"),
    )
    assert credit.autopay_status is None

    # Test update with valid status
    update = CreditAccountUpdate(
        autopay_status="full_balance",
    )
    assert update.autopay_status == "full_balance"

    # Test update with invalid status
    with pytest.raises(ValidationError, match="Autopay status must be one of:"):
        CreditAccountUpdate(
            autopay_status="automatic",  # Invalid status
        )

    # Test update with None (don't update)
    update = CreditAccountUpdate(
        autopay_status=None,
    )
    assert update.autopay_status is None


def test_apr_validation():
    """Test APR validation in credit account schemas."""
    # Test valid APR (low)
    credit = CreditAccountCreate(
        name="Low APR",
        account_type="credit",
        current_balance=Decimal("500.00"),
        available_balance=Decimal("500.00"),
        credit_limit=Decimal("2000.00"),
        apr=Decimal("0.0999"),  # 9.99%
    )
    assert credit.apr == Decimal("0.0999")

    # Test valid APR (standard)
    credit = CreditAccountCreate(
        name="Standard APR",
        account_type="credit",
        current_balance=Decimal("500.00"),
        available_balance=Decimal("500.00"),
        credit_limit=Decimal("2000.00"),
        apr=Decimal("0.2499"),  # 24.99%
    )
    assert credit.apr == Decimal("0.2499")

    # Test high APR - now allowed since reasonableness validation moved to service layer
    # This previously raised an error when we had the validator in the schema
    credit = CreditAccountCreate(
        name="High APR",
        account_type="credit",
        current_balance=Decimal("500.00"),
        available_balance=Decimal("500.00"),
        credit_limit=Decimal("2000.00"),
        apr=Decimal("0.4999"),  # 49.99%
    )
    assert credit.apr == Decimal("0.4999")
    
    # Test extremely high APR - still allowed, enforcement moved to service layer
    credit = CreditAccountCreate(
        name="Extremely High APR",
        account_type="credit",
        current_balance=Decimal("500.00"),
        available_balance=Decimal("500.00"),
        credit_limit=Decimal("2000.00"),
        apr=Decimal("0.9999"),  # 99.99%
    )
    assert credit.apr == Decimal("0.9999")

    # Test update with valid APR
    update = CreditAccountUpdate(
        apr=Decimal("0.1499"),  # 14.99%
    )
    assert update.apr == Decimal("0.1499")

    # Test update with high APR - now allowed
    update = CreditAccountUpdate(
        apr=Decimal("0.6000"),  # 60.00%
    )
    assert update.apr == Decimal("0.6000")

    # Test update with None (don't update)
    update = CreditAccountUpdate(
        apr=None,
    )
    assert update.apr is None


def test_dates_in_credit_account():
    """Test date fields in credit account schemas."""
    now = utc_now()
    due_date = now + timedelta(days=25)
    statement_date = now - timedelta(days=5)
    
    # Test valid dates
    credit = CreditAccountCreate(
        name="Credit With Dates",
        account_type="credit",
        current_balance=Decimal("500.00"),
        available_balance=Decimal("500.00"),
        credit_limit=Decimal("2000.00"),
        statement_due_date=due_date,
        last_statement_date=statement_date,
    )
    assert credit.statement_due_date == due_date
    assert credit.last_statement_date == statement_date

    # Test update with date fields
    new_due_date = now + timedelta(days=30)
    update = CreditAccountUpdate(
        statement_due_date=new_due_date,
    )
    assert update.statement_due_date == new_due_date
    assert update.last_statement_date is None
