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
    SavingsAccountUpdate,
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
    # Test valid interest rate
    savings = SavingsAccountCreate(
        name="Valid Interest",
        account_type="savings",
        current_balance=Decimal("5000.00"),
        available_balance=Decimal("5000.00"),
        interest_rate=Decimal("0.0250"),  # 2.5%
    )
    assert savings.interest_rate == Decimal("0.0250")

    # Test interest rate at upper boundary (1.0)
    savings = SavingsAccountCreate(
        name="Max Interest",
        account_type="savings",
        current_balance=Decimal("5000.00"),
        available_balance=Decimal("5000.00"),
        interest_rate=Decimal("1.0"),  # 100% (max allowed)
    )
    assert savings.interest_rate == Decimal("1.0")

    # Test money validation for interest rate (should be between 0 and 1 for decimal percentage)
    with pytest.raises(
        ValidationError, match="Input should be less than or equal to 1"
    ):
        SavingsAccountCreate(
            name="Invalid Interest",
            account_type="savings",
            current_balance=Decimal("5000.00"),
            available_balance=Decimal("5000.00"),
            interest_rate=Decimal(
                "1.5"
            ),  # Should be between 0-1 (e.g., 0.015 for 1.5%)
        )

    # Test high interest rate - now allowed since reasonableness validation moved to service layer
    # This previously raised an error when we had the validator in the schema
    savings = SavingsAccountCreate(
        name="High Interest",
        account_type="savings",
        current_balance=Decimal("5000.00"),
        available_balance=Decimal("5000.00"),
        interest_rate=Decimal("0.25"),  # 25% - now allowed
    )
    assert savings.interest_rate == Decimal("0.25")

    # Test negative minimum balance
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        SavingsAccountCreate(
            name="Invalid Minimum",
            account_type="savings",
            current_balance=Decimal("5000.00"),
            available_balance=Decimal("5000.00"),
            minimum_balance=Decimal("-500.00"),  # Negative value not allowed
        )

    # Test valid minimum balance
    savings = SavingsAccountCreate(
        name="Valid Minimum",
        account_type="savings",
        current_balance=Decimal("5000.00"),
        available_balance=Decimal("5000.00"),
        minimum_balance=Decimal("500.00"),
    )
    assert savings.minimum_balance == Decimal("500.00")

    # Test zero minimum balance
    savings = SavingsAccountCreate(
        name="Zero Minimum",
        account_type="savings",
        current_balance=Decimal("5000.00"),
        available_balance=Decimal("5000.00"),
        minimum_balance=Decimal("0.00"),
    )
    assert savings.minimum_balance == Decimal("0.00")

    # Test negative withdrawal limit
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        SavingsAccountCreate(
            name="Invalid Withdrawal Limit",
            account_type="savings",
            current_balance=Decimal("5000.00"),
            available_balance=Decimal("5000.00"),
            withdrawal_limit=-1,  # Negative value not allowed
        )

    # Test zero withdrawal limit
    savings = SavingsAccountCreate(
        name="Zero Withdrawal Limit",
        account_type="savings",
        current_balance=Decimal("5000.00"),
        available_balance=Decimal("5000.00"),
        withdrawal_limit=0,  # Zero is valid - means no withdrawals allowed
    )
    assert savings.withdrawal_limit == 0

    # Test positive withdrawal limit
    savings = SavingsAccountCreate(
        name="Valid Withdrawal Limit",
        account_type="savings",
        current_balance=Decimal("5000.00"),
        available_balance=Decimal("5000.00"),
        withdrawal_limit=6,
    )
    assert savings.withdrawal_limit == 6


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
    with pytest.raises(ValidationError, match="Compound frequency must be one of:"):
        SavingsAccountCreate(
            name="Invalid Frequency",
            account_type="savings",
            current_balance=Decimal("5000.00"),
            available_balance=Decimal("5000.00"),
            compound_frequency="weekly",  # Not in allowed values
        )

    # Test empty string (not in valid values)
    with pytest.raises(ValidationError, match="Compound frequency must be one of:"):
        SavingsAccountCreate(
            name="Empty Frequency",
            account_type="savings",
            current_balance=Decimal("5000.00"),
            available_balance=Decimal("5000.00"),
            compound_frequency="",  # Empty string is not valid
        )

    # Test None value (valid as it's the default)
    savings = SavingsAccountCreate(
        name="No Frequency",
        account_type="savings",
        current_balance=Decimal("5000.00"),
        available_balance=Decimal("5000.00"),
        compound_frequency=None,
    )
    assert savings.compound_frequency is None


def test_savings_account_update_schema():
    """Test the savings account update schema."""
    # Test with no fields (all optional in update)
    update = SavingsAccountUpdate()
    assert update.account_type is None
    assert update.name is None
    assert update.current_balance is None
    assert update.available_balance is None
    assert update.interest_rate is None
    assert update.compound_frequency is None

    # Test with some fields
    update = SavingsAccountUpdate(
        name="Updated Savings",
        interest_rate=Decimal("0.0175"),  # 1.75%
        minimum_balance=Decimal("1000.00"),
    )
    assert update.name == "Updated Savings"
    assert update.interest_rate == Decimal("0.0175")
    assert update.minimum_balance == Decimal("1000.00")
    assert update.account_type is None

    # Test with explicit account type
    update = SavingsAccountUpdate(
        account_type="savings",
        name="Updated Savings Type",
    )
    assert update.account_type == "savings"
    assert update.name == "Updated Savings Type"

    # Test with wrong account type
    with pytest.raises(ValidationError, match="Input should be 'savings'"):
        SavingsAccountUpdate(
            account_type="checking",  # Wrong type
            name="Wrong Type Update",
        )


def test_savings_account_update_money_validation():
    """Test money validation in savings account update schema."""
    # Test valid interest rate update
    update = SavingsAccountUpdate(
        interest_rate=Decimal("0.0199"),  # 1.99%
    )
    assert update.interest_rate == Decimal("0.0199")

    # Test interest rate at upper boundary (1.0)
    update = SavingsAccountUpdate(
        interest_rate=Decimal("1.0"),  # 100% (max allowed)
    )
    assert update.interest_rate == Decimal("1.0")

    # Test exceeding max interest rate
    with pytest.raises(
        ValidationError, match="Input should be less than or equal to 1"
    ):
        SavingsAccountUpdate(
            interest_rate=Decimal("1.25"),  # Exceeds max of 1.0
        )

    # Test high interest rate - now allowed since reasonableness validation moved to service layer
    # This previously raised an error when we had the validator in the schema
    update = SavingsAccountUpdate(
        interest_rate=Decimal("0.35"),  # 35% - now allowed
    )
    assert update.interest_rate == Decimal("0.35")

    # Test negative minimum balance
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        SavingsAccountUpdate(
            minimum_balance=Decimal("-10.00"),  # Negative value not allowed
        )

    # Test negative interest earned
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        SavingsAccountUpdate(
            interest_earned_ytd=Decimal("-5.00"),  # Negative value not allowed
        )

    # Test None values (don't update)
    update = SavingsAccountUpdate(
        interest_rate=None,
        minimum_balance=None,
        interest_earned_ytd=None,
    )
    assert update.interest_rate is None
    assert update.minimum_balance is None
    assert update.interest_earned_ytd is None


def test_savings_account_update_compound_frequency():
    """Test compound frequency in savings account update schema."""
    # Test valid frequencies
    valid_frequencies = ["daily", "monthly", "quarterly", "annually"]

    for frequency in valid_frequencies:
        update = SavingsAccountUpdate(
            compound_frequency=frequency,
        )
        assert update.compound_frequency == frequency

    # Test invalid frequency
    with pytest.raises(ValidationError, match="Compound frequency must be one of:"):
        SavingsAccountUpdate(
            compound_frequency="bi-weekly",  # Not in allowed values
        )

    # Test None value (don't update)
    update = SavingsAccountUpdate(
        compound_frequency=None,
    )
    assert update.compound_frequency is None
