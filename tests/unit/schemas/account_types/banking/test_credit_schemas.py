"""
Unit tests for CreditAccount schemas.

Tests the credit account schema validation and serialization
as part of ADR-016 Account Type Expansion and ADR-019 Banking Account Types Expansion.
"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.schemas.account_types.banking.credit import (
    CreditAccountCreate,
    CreditAccountResponse,
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
    with pytest.raises(ValidationError, match="Input should be greater than or equal to 0"):
        CreditAccountCreate(
            name="Invalid Fee",
            account_type="credit",
            current_balance=Decimal("500.00"),
            available_balance=Decimal("500.00"),
            credit_limit=Decimal("2000.00"),
            annual_fee=Decimal("-95.00"),  # Negative value not allowed
        )
