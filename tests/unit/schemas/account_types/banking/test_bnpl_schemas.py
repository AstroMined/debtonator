"""
Unit tests for BNPLAccount schemas.

Tests the Buy Now Pay Later (BNPL) account schema validation and serialization
as part of ADR-016 Account Type Expansion and ADR-019 Banking Account Types Expansion.
"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.schemas.account_types.banking.bnpl import (
    BNPLAccountCreate,
    BNPLAccountResponse,
)
from src.utils.datetime_utils import utc_now


def test_bnpl_account_create_schema():
    """Test the BNPL account create schema."""
    # Test with minimum required fields
    bnpl = BNPLAccountCreate(
        name="Basic BNPL",
        account_type="bnpl",
        current_balance=Decimal("300.00"),
        available_balance=Decimal("300.00"),
        original_amount=Decimal("400.00"),
        installment_count=4,
        installments_paid=1,
        installment_amount=Decimal("100.00"),
        payment_frequency="monthly",
        bnpl_provider="Affirm",
    )
    assert bnpl.name == "Basic BNPL"
    assert bnpl.account_type == "bnpl"
    assert bnpl.original_amount == Decimal("400.00")
    assert bnpl.installment_count == 4
    assert bnpl.installments_paid == 1
    assert bnpl.payment_frequency == "monthly"
    assert bnpl.bnpl_provider == "Affirm"

    # Test with all fields including dates
    next_payment_date = utc_now()
    bnpl = BNPLAccountCreate(
        name="Full BNPL",
        account_type="bnpl",
        current_balance=Decimal("450.00"),
        available_balance=Decimal("450.00"),
        institution="Affirm, Inc.",
        currency="USD",
        account_number="BNPL-12345",
        original_amount=Decimal("600.00"),
        installment_count=6,
        installments_paid=1,
        installment_amount=Decimal("100.00"),
        payment_frequency="monthly",
        next_payment_date=next_payment_date,
        promotion_info="0% interest if paid within 6 months",
        late_fee=Decimal("25.00"),
        bnpl_provider="Affirm",
    )
    assert bnpl.original_amount == Decimal("600.00")
    assert bnpl.installment_count == 6
    assert bnpl.next_payment_date == next_payment_date
    assert bnpl.promotion_info == "0% interest if paid within 6 months"
    assert bnpl.late_fee == Decimal("25.00")

    # Test validation of incorrect account type
    with pytest.raises(ValidationError, match="Value error at account_type"):
        BNPLAccountCreate(
            name="Invalid Type",
            account_type="checking",  # Wrong type
            current_balance=Decimal("300.00"),
            available_balance=Decimal("300.00"),
            original_amount=Decimal("400.00"),
            installment_count=4,
            installments_paid=1,
            installment_amount=Decimal("100.00"),
            payment_frequency="monthly",
            bnpl_provider="Affirm",
        )

    # Test validation of BNPL-specific field
    with pytest.raises(ValidationError, match="bnpl_provider"):
        BNPLAccountCreate(
            name="Invalid Provider",
            account_type="bnpl",
            current_balance=Decimal("300.00"),
            available_balance=Decimal("300.00"),
            original_amount=Decimal("400.00"),
            installment_count=4,
            installments_paid=1,
            installment_amount=Decimal("100.00"),
            payment_frequency="monthly",
            # Missing required bnpl_provider
        )


def test_bnpl_account_response_schema():
    """Test the BNPL account response schema."""
    now = utc_now()

    # Test with minimum required fields
    bnpl_response = BNPLAccountResponse(
        id=1,
        name="BNPL Response",
        account_type="bnpl",
        current_balance=Decimal("300.00"),
        available_balance=Decimal("300.00"),
        original_amount=Decimal("400.00"),
        installment_count=4,
        installments_paid=1,
        installment_amount=Decimal("100.00"),
        payment_frequency="monthly",
        bnpl_provider="Affirm",
        created_at=now,
        updated_at=now,
    )
    assert bnpl_response.id == 1
    assert bnpl_response.name == "BNPL Response"
    assert bnpl_response.account_type == "bnpl"
    assert bnpl_response.original_amount == Decimal("400.00")
    assert bnpl_response.installment_count == 4
    assert bnpl_response.created_at == now
    assert bnpl_response.updated_at == now

    # Test with all fields
    bnpl_response = BNPLAccountResponse(
        id=2,
        name="Full BNPL Response",
        account_type="bnpl",
        current_balance=Decimal("450.00"),
        available_balance=Decimal("450.00"),
        institution="Affirm, Inc.",
        currency="USD",
        account_number="BNPL-12345",
        original_amount=Decimal("600.00"),
        installment_count=6,
        installments_paid=1,
        installment_amount=Decimal("100.00"),
        payment_frequency="monthly",
        next_payment_date=now,
        promotion_info="0% interest if paid within 6 months",
        late_fee=Decimal("25.00"),
        bnpl_provider="Affirm",
        created_at=now,
        updated_at=now,
    )
    assert bnpl_response.original_amount == Decimal("600.00")
    assert bnpl_response.installment_count == 6
    assert bnpl_response.next_payment_date == now
    assert bnpl_response.promotion_info == "0% interest if paid within 6 months"

    # Test validation of incorrect account type
    with pytest.raises(ValidationError, match="Value error at account_type"):
        BNPLAccountResponse(
            id=1,
            name="Invalid Type",
            account_type="checking",  # Wrong type
            current_balance=Decimal("300.00"),
            available_balance=Decimal("300.00"),
            original_amount=Decimal("400.00"),
            installment_count=4,
            installments_paid=1,
            installment_amount=Decimal("100.00"),
            payment_frequency="monthly",
            bnpl_provider="Affirm",
            created_at=now,
            updated_at=now,
        )


def test_bnpl_payment_frequency_validation():
    """Test payment frequency validation in BNPL account schemas."""
    # Test valid payment frequencies
    valid_frequencies = ["weekly", "biweekly", "monthly"]

    for frequency in valid_frequencies:
        bnpl = BNPLAccountCreate(
            name="Frequency Test",
            account_type="bnpl",
            current_balance=Decimal("300.00"),
            available_balance=Decimal("300.00"),
            original_amount=Decimal("400.00"),
            installment_count=4,
            installments_paid=1,
            installment_amount=Decimal("100.00"),
            payment_frequency=frequency,
            bnpl_provider="Affirm",
        )
        assert bnpl.payment_frequency == frequency

    # Test invalid payment frequency
    with pytest.raises(
        ValidationError, match="value is not a valid enumeration member"
    ):
        BNPLAccountCreate(
            name="Invalid Frequency",
            account_type="bnpl",
            current_balance=Decimal("300.00"),
            available_balance=Decimal("300.00"),
            original_amount=Decimal("400.00"),
            installment_count=4,
            installments_paid=1,
            installment_amount=Decimal("100.00"),
            payment_frequency="quarterly",  # Not in the allowed values
            bnpl_provider="Affirm",
        )


def test_bnpl_provider_validation():
    """Test BNPL provider validation in BNPL account schemas."""
    # Test various valid providers (this list should be updated if the actual validation changes)
    valid_providers = ["Affirm", "Klarna", "Afterpay", "Zip", "PayPal Pay in 4"]

    for provider in valid_providers:
        bnpl = BNPLAccountCreate(
            name="Provider Test",
            account_type="bnpl",
            current_balance=Decimal("300.00"),
            available_balance=Decimal("300.00"),
            original_amount=Decimal("400.00"),
            installment_count=4,
            installments_paid=1,
            installment_amount=Decimal("100.00"),
            payment_frequency="monthly",
            bnpl_provider=provider,
        )
        assert bnpl.bnpl_provider == provider

    # Test custom/other provider
    bnpl = BNPLAccountCreate(
        name="Custom Provider",
        account_type="bnpl",
        current_balance=Decimal("300.00"),
        available_balance=Decimal("300.00"),
        original_amount=Decimal("400.00"),
        installment_count=4,
        installments_paid=1,
        installment_amount=Decimal("100.00"),
        payment_frequency="monthly",
        bnpl_provider="Other BNPL Provider",  # Custom provider name
    )
    assert bnpl.bnpl_provider == "Other BNPL Provider"


def test_bnpl_installment_validation():
    """Test installment validation in BNPL account schemas."""
    # Test valid installment setup
    bnpl = BNPLAccountCreate(
        name="Valid Installments",
        account_type="bnpl",
        current_balance=Decimal("300.00"),
        available_balance=Decimal("300.00"),
        original_amount=Decimal("400.00"),
        installment_count=4,
        installments_paid=2,  # Paid 2 of 4 installments
        installment_amount=Decimal("100.00"),
        payment_frequency="monthly",
        bnpl_provider="Affirm",
    )
    assert bnpl.installment_count == 4
    assert bnpl.installments_paid == 2

    # Test invalid (negative) installment count
    with pytest.raises(ValidationError, match="greater than or equal to 1"):
        BNPLAccountCreate(
            name="Invalid Installments",
            account_type="bnpl",
            current_balance=Decimal("300.00"),
            available_balance=Decimal("300.00"),
            original_amount=Decimal("400.00"),
            installment_count=-1,  # Negative value
            installments_paid=0,
            installment_amount=Decimal("100.00"),
            payment_frequency="monthly",
            bnpl_provider="Affirm",
        )

    # Test invalid (more paid than total) installments
    with pytest.raises(
        ValidationError, match="ensure this value is less than or equal to"
    ):
        BNPLAccountCreate(
            name="Invalid Installments",
            account_type="bnpl",
            current_balance=Decimal("300.00"),
            available_balance=Decimal("300.00"),
            original_amount=Decimal("400.00"),
            installment_count=4,
            installments_paid=5,  # Paid more than total (shouldn't be possible)
            installment_amount=Decimal("100.00"),
            payment_frequency="monthly",
            bnpl_provider="Affirm",
        )
