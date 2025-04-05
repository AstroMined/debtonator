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
    assert savings.available_balance == Decimal("5000.00")

    # Test with all fields
    savings = SavingsAccountCreate(
        name="Full Savings",
        account_type="savings",
        current_balance=Decimal("5000.00"),
        available_balance=Decimal("4800.00"),
        institution="Test Bank",
        currency="USD",
        account_number="12345678",
        routing_number="123456789",
        interest_rate=Decimal("0.0150"),  # 1.50%
        compound_frequency="daily",
        interest_earned_ytd=Decimal("25.50"),
        withdrawal_limit=6,
        minimum_balance=Decimal("500.00"),
    )
    assert savings.institution == "Test Bank"
    assert savings.routing_number == "123456789"
    assert savings.interest_rate == Decimal("0.0150")
    assert savings.compound_frequency == "daily"
    assert savings.interest_earned_ytd == Decimal("25.50")

    # Test validation of incorrect account type
    with pytest.raises(ValidationError, match="Input should be 'savings'"):
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
        available_balance=Decimal("4800.00"),
        institution="Test Bank",
        currency="USD",
        account_number="12345678",
        routing_number="123456789",
        interest_rate=Decimal("0.0150"),  # 1.50%
        compound_frequency="daily",
        interest_earned_ytd=Decimal("25.50"),
        withdrawal_limit=6,
        minimum_balance=Decimal("500.00"),
        created_at=now,
        updated_at=now,
    )
    assert savings_response.institution == "Test Bank"
    assert savings_response.interest_rate == Decimal("0.0150")
    assert savings_response.compound_frequency == "daily"

    # Test validation of incorrect account type
    with pytest.raises(ValidationError, match="Input should be 'savings'"):
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
    with pytest.raises(ValidationError, match="Input should be less than or equal to 1"):
        SavingsAccountCreate(
            name="Invalid Interest",
            account_type="savings",
            current_balance=Decimal("5000.00"),
            available_balance=Decimal("5000.00"),
            interest_rate=Decimal("1.5"),  # Should be between 0-1 (e.g., 0.015 for 1.5%)
        )

    # Test negative minimum balance
    with pytest.raises(ValidationError, match="Input should be greater than or equal to 0"):
        SavingsAccountCreate(
            name="Invalid Minimum",
            account_type="savings",
            current_balance=Decimal("5000.00"),
            available_balance=Decimal("5000.00"),
            minimum_balance=Decimal("-500.00"),  # Negative value not allowed
        )


def test_savings_account_compound_frequency_validation():
    """Test compound frequency validation in savings account schemas."""
    # Test valid frequencies
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

    # Test invalid frequency
    with pytest.raises(
        ValidationError, match="Compound frequency must be one of:"
    ):
        SavingsAccountCreate(
            name="Invalid Frequency",
            account_type="savings",
            current_balance=Decimal("5000.00"),
            available_balance=Decimal("5000.00"),
            compound_frequency="weekly",  # Not in allowed values
        )
