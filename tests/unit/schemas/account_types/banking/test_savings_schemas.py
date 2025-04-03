"""
Unit tests for SavingsAccount schemas.

Tests the savings account schema validation and serialization
as part of ADR-016 Account Type Expansion and ADR-019 Banking Account Types Expansion.
"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.schemas.account_types.banking.savings import (
    SavingsAccountCreate,
    SavingsAccountResponse,
)
from src.utils.datetime_utils import utc_now


def test_savings_account_create_schema():
    """Test the savings account create schema."""
    # Test with minimum required fields
    savings = SavingsAccountCreate(
        name="Basic Savings",
        account_type="savings",
        current_balance=Decimal("5000.00"),
        available_balance=Decimal("5000.00"),
    )
    assert savings.name == "Basic Savings"
    assert savings.account_type == "savings"
    assert savings.current_balance == Decimal("5000.00")

    # Test with all fields
    savings = SavingsAccountCreate(
        name="Full Savings",
        account_type="savings",
        current_balance=Decimal("5000.00"),
        available_balance=Decimal("5000.00"),
        institution="Test Bank",
        currency="USD",
        account_number="9876543210",
        interest_rate=Decimal("0.0250"),  # 2.5%
        compound_frequency="daily",
        interest_earned_ytd=Decimal("25.50"),
        withdrawal_limit=6,
        minimum_balance=Decimal("500.00"),
    )
    assert savings.interest_rate == Decimal("0.0250")
    assert savings.compound_frequency == "daily"
    assert savings.interest_earned_ytd == Decimal("25.50")
    assert savings.withdrawal_limit == 6
    assert savings.minimum_balance == Decimal("500.00")

    # Test validation of incorrect account type
    with pytest.raises(ValidationError, match="Value error at account_type"):
        SavingsAccountCreate(
            name="Invalid Type",
            account_type="checking",  # Wrong type
            current_balance=Decimal("5000.00"),
            available_balance=Decimal("5000.00"),
        )


def test_savings_account_response_schema():
    """Test the savings account response schema."""
    now = utc_now()

    # Test with minimum required fields
    savings_response = SavingsAccountResponse(
        id=1,
        name="Savings Response",
        account_type="savings",
        current_balance=Decimal("5000.00"),
        available_balance=Decimal("5000.00"),
        created_at=now,
        updated_at=now,
    )
    assert savings_response.id == 1
    assert savings_response.name == "Savings Response"
    assert savings_response.account_type == "savings"
    assert savings_response.created_at == now
    assert savings_response.updated_at == now

    # Test with all fields
    savings_response = SavingsAccountResponse(
        id=2,
        name="Full Savings Response",
        account_type="savings",
        current_balance=Decimal("5000.00"),
        available_balance=Decimal("5000.00"),
        institution="Test Bank",
        currency="USD",
        account_number="9876543210",
        interest_rate=Decimal("0.0250"),  # 2.5%
        compound_frequency="daily",
        interest_earned_ytd=Decimal("25.50"),
        withdrawal_limit=6,
        minimum_balance=Decimal("500.00"),
        created_at=now,
        updated_at=now,
    )
    assert savings_response.interest_rate == Decimal("0.0250")
    assert savings_response.compound_frequency == "daily"
    assert savings_response.interest_earned_ytd == Decimal("25.50")

    # Test validation of incorrect account type
    with pytest.raises(ValidationError, match="Value error at account_type"):
        SavingsAccountResponse(
            id=1,
            name="Invalid Type",
            account_type="checking",  # Wrong type
            current_balance=Decimal("5000.00"),
            available_balance=Decimal("5000.00"),
            created_at=now,
            updated_at=now,
        )


def test_savings_account_money_validation():
    """Test money validation in savings account schemas."""
    # Test money validation for interest rate (should be between 0 and 1 for decimal percentage)
    with pytest.raises(
        ValidationError, match="ensure this value is less than or equal to"
    ):
        SavingsAccountCreate(
            name="Invalid Interest Rate",
            account_type="savings",
            current_balance=Decimal("5000.00"),
            available_balance=Decimal("5000.00"),
            interest_rate=Decimal(
                "1.5"
            ),  # Should be between 0-1 (e.g., 0.025 for 2.5%)
        )

    # Test negative minimum balance
    with pytest.raises(ValidationError, match="greater than or equal to 0"):
        SavingsAccountCreate(
            name="Invalid Min Balance",
            account_type="savings",
            current_balance=Decimal("5000.00"),
            available_balance=Decimal("5000.00"),
            minimum_balance=Decimal("-500.00"),  # Negative value not allowed
        )


def test_savings_account_compound_frequency_validation():
    """Test compound frequency validation in savings account schemas."""
    # Test valid compound frequencies
    valid_frequencies = ["daily", "monthly", "quarterly", "annually"]

    for frequency in valid_frequencies:
        savings = SavingsAccountCreate(
            name="Frequency Test",
            account_type="savings",
            current_balance=Decimal("5000.00"),
            available_balance=Decimal("5000.00"),
            compound_frequency=frequency,
        )
        assert savings.compound_frequency == frequency

    # Test invalid compound frequency
    with pytest.raises(
        ValidationError, match="value is not a valid enumeration member"
    ):
        SavingsAccountCreate(
            name="Invalid Frequency",
            account_type="savings",
            current_balance=Decimal("5000.00"),
            available_balance=Decimal("5000.00"),
            compound_frequency="weekly",  # Not in the allowed values
        )
