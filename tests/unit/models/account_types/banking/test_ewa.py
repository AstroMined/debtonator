"""
Unit tests for the EWAAccount model.

Tests the EWAAccount model fields, constraints, inheritance,
and polymorphic behavior as part of ADR-016 and ADR-019.
"""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.ewa import EWAAccount
from src.models.accounts import Account
from src.utils.datetime_utils import naive_utc_from_date

pytestmark = pytest.mark.asyncio


async def test_ewa_account_inheritance(db_session: AsyncSession):
    """Test EWAAccount inherits properly from Account base class."""
    # Create an EWA account
    next_payday = naive_utc_from_date(2025, 5, 15)
    ewa_account = EWAAccount(
        name="Test DailyPay",
        account_type="ewa",  # This should match polymorphic_identity
        current_balance=Decimal("150.00"),  # Amount already advanced
        available_balance=Decimal("150.00"),
        provider="DailyPay",
        max_advance_percentage=Decimal("0.50"),  # 50%
        next_payday=next_payday,
    )

    # Add to session and commit
    db_session.add(ewa_account)
    await db_session.commit()
    await db_session.refresh(ewa_account)

    # Verify basic properties
    assert ewa_account.id is not None
    assert ewa_account.name == "Test DailyPay"
    assert ewa_account.account_type == "ewa"
    assert ewa_account.current_balance == Decimal("150.00")
    assert ewa_account.available_balance == Decimal("150.00")

    # Verify EWA-specific properties
    assert ewa_account.provider == "DailyPay"
    assert ewa_account.max_advance_percentage == Decimal("0.50")
    assert ewa_account.next_payday == next_payday

    # Verify it can be queried as an Account (polymorphic parent)
    base_account = await db_session.get(Account, ewa_account.id)
    assert base_account is not None
    assert base_account.name == "Test DailyPay"
    assert base_account.account_type == "ewa"
    assert base_account.current_balance == Decimal("150.00")
    assert base_account.available_balance == Decimal("150.00")

    # Verify it can be queried as an EWAAccount (polymorphic child)
    retrieved_ewa = await db_session.get(EWAAccount, ewa_account.id)
    assert retrieved_ewa is not None
    assert retrieved_ewa.name == "Test DailyPay"
    assert retrieved_ewa.provider == "DailyPay"
    assert retrieved_ewa.max_advance_percentage == Decimal("0.50")
    assert retrieved_ewa.next_payday == next_payday


async def test_ewa_account_polymorphic_identity(db_session: AsyncSession):
    """Test the polymorphic identity of EWAAccount is correctly set."""
    # Create an EWA account
    ewa_account = EWAAccount(
        name="Polymorphic Identity Test",
        account_type="ewa",  # This must match polymorphic_identity
        current_balance=Decimal("100.00"),
        available_balance=Decimal("100.00"),
        provider="Payactiv",
    )

    # Add to session and commit
    db_session.add(ewa_account)
    await db_session.commit()
    await db_session.refresh(ewa_account)

    # Query it using polymorphic query
    all_accounts = (await db_session.execute(db_session.query(Account))).scalars().all()

    # Find our account in the results
    found_account = None
    for account in all_accounts:
        if account.id == ewa_account.id:
            found_account = account
            break

    # Verify it's found with the correct type
    assert found_account is not None
    assert isinstance(found_account, EWAAccount)
    assert found_account.account_type == "ewa"


async def test_ewa_account_fields(db_session: AsyncSession):
    """Test all fields of EWAAccount model."""
    # Create an EWA account with all fields populated
    period_start = naive_utc_from_date(2025, 5, 1)
    period_end = naive_utc_from_date(2025, 5, 14)
    payday = naive_utc_from_date(2025, 5, 15)

    ewa_account = EWAAccount(
        name="Full Fields Test",
        account_type="ewa",
        current_balance=Decimal("250.00"),
        available_balance=Decimal("250.00"),
        institution="Payactiv, Inc.",
        currency="USD",
        account_number="EWA-12345",
        url="https://payactiv.com/account",
        logo_path="/images/payactiv.png",
        is_closed=False,
        description="Test EWA account with all fields",
        provider="Payactiv",
        max_advance_percentage=Decimal("0.50"),  # 50%
        per_transaction_fee=Decimal("2.99"),
        pay_period_start=period_start,
        pay_period_end=period_end,
        next_payday=payday,
        next_action_date=payday,
        next_action_amount=Decimal("250.00"),
    )

    # Add to session and commit
    db_session.add(ewa_account)
    await db_session.commit()
    await db_session.refresh(ewa_account)

    # Verify all base Account fields
    assert ewa_account.name == "Full Fields Test"
    assert ewa_account.account_type == "ewa"
    assert ewa_account.current_balance == Decimal("250.00")
    assert ewa_account.available_balance == Decimal("250.00")
    assert ewa_account.institution == "Payactiv, Inc."
    assert ewa_account.currency == "USD"
    assert ewa_account.account_number == "EWA-12345"
    assert ewa_account.url == "https://payactiv.com/account"
    assert ewa_account.logo_path == "/images/payactiv.png"
    assert ewa_account.is_closed is False
    assert ewa_account.description == "Test EWA account with all fields"
    assert ewa_account.next_action_date.year == 2025
    assert ewa_account.next_action_date.month == 5
    assert ewa_account.next_action_date.day == 15
    assert ewa_account.next_action_amount == Decimal("250.00")

    # Verify all EWAAccount-specific fields
    assert ewa_account.provider == "Payactiv"
    assert ewa_account.max_advance_percentage == Decimal("0.50")
    assert ewa_account.per_transaction_fee == Decimal("2.99")
    assert ewa_account.pay_period_start.year == 2025
    assert ewa_account.pay_period_start.month == 5
    assert ewa_account.pay_period_start.day == 1
    assert ewa_account.pay_period_end.year == 2025
    assert ewa_account.pay_period_end.month == 5
    assert ewa_account.pay_period_end.day == 14
    assert ewa_account.next_payday.year == 2025
    assert ewa_account.next_payday.month == 5
    assert ewa_account.next_payday.day == 15


async def test_ewa_account_minimal_fields(db_session: AsyncSession):
    """Test EWAAccount can be created with only required fields."""
    # Create an EWA account with only required fields
    ewa_account = EWAAccount(
        name="Minimal EWA",
        account_type="ewa",
        current_balance=Decimal("100.00"),
        available_balance=Decimal("100.00"),
        provider="DailyPay",  # Only provider is required specific field
    )

    # Add to session and commit
    db_session.add(ewa_account)
    await db_session.commit()
    await db_session.refresh(ewa_account)

    # Verify required fields
    assert ewa_account.id is not None
    assert ewa_account.name == "Minimal EWA"
    assert ewa_account.account_type == "ewa"
    assert ewa_account.current_balance == Decimal("100.00")
    assert ewa_account.available_balance == Decimal("100.00")
    assert ewa_account.provider == "DailyPay"

    # Verify optional fields are None
    assert ewa_account.max_advance_percentage is None
    assert ewa_account.per_transaction_fee is None
    assert ewa_account.pay_period_start is None
    assert ewa_account.pay_period_end is None
    assert ewa_account.next_payday is None


async def test_ewa_account_decimal_precision(db_session: AsyncSession):
    """Test decimal precision handling for money fields."""
    # Create account with 4 decimal places in money fields
    ewa_account = EWAAccount(
        name="Precision Test",
        account_type="ewa",
        current_balance=Decimal("123.4567"),
        available_balance=Decimal("123.4567"),
        provider="Payactiv",
        max_advance_percentage=Decimal("0.5000"),  # 50%
        per_transaction_fee=Decimal("2.9900"),
    )

    db_session.add(ewa_account)
    await db_session.commit()
    await db_session.refresh(ewa_account)

    # Verify precision is maintained at 4 decimal places (per ADR-013)
    assert ewa_account.current_balance == Decimal("123.4567")
    assert ewa_account.available_balance == Decimal("123.4567")
    assert ewa_account.per_transaction_fee == Decimal("2.9900")

    # Verify exponent in each Decimal field
    assert ewa_account.current_balance.as_tuple().exponent == -4
    assert ewa_account.available_balance.as_tuple().exponent == -4
    assert ewa_account.per_transaction_fee.as_tuple().exponent == -4

    # Percentage is stored with 4 decimal places
    assert ewa_account.max_advance_percentage == Decimal("0.5000")
    assert ewa_account.max_advance_percentage.as_tuple().exponent == -4


async def test_ewa_providers(db_session: AsyncSession):
    """Test different EWA provider options."""
    # Create and test various EWA providers
    providers = ["Payactiv", "DailyPay", "Even", "Branch", "Instant"]

    for provider in providers:
        ewa_account = EWAAccount(
            name=f"{provider} Account",
            account_type="ewa",
            current_balance=Decimal("100.00"),
            available_balance=Decimal("100.00"),
            provider=provider,
        )

        db_session.add(ewa_account)
        await db_session.commit()
        await db_session.refresh(ewa_account)

        # Verify provider was saved correctly
        assert ewa_account.provider == provider

        # Clean up for next iteration
        await db_session.delete(ewa_account)
        await db_session.commit()


async def test_ewa_pay_period_management(db_session: AsyncSession):
    """Test pay period field handling in EWAAccount."""
    # Create initial pay period
    period_start = naive_utc_from_date(2025, 5, 1)
    period_end = naive_utc_from_date(2025, 5, 14)
    payday = naive_utc_from_date(2025, 5, 15)

    ewa_account = EWAAccount(
        name="Pay Period Test",
        account_type="ewa",
        current_balance=Decimal("200.00"),
        available_balance=Decimal("200.00"),
        provider="DailyPay",
        max_advance_percentage=Decimal("0.60"),  # 60%
        pay_period_start=period_start,
        pay_period_end=period_end,
        next_payday=payday,
    )

    db_session.add(ewa_account)
    await db_session.commit()
    await db_session.refresh(ewa_account)

    # Verify initial state
    assert ewa_account.pay_period_start == period_start
    assert ewa_account.pay_period_end == period_end
    assert ewa_account.next_payday == payday

    # Simulate advancing to next pay period
    next_period_start = naive_utc_from_date(2025, 5, 16)
    next_period_end = naive_utc_from_date(2025, 5, 31)
    next_payday = naive_utc_from_date(2025, 6, 1)

    ewa_account.pay_period_start = next_period_start
    ewa_account.pay_period_end = next_period_end
    ewa_account.next_payday = next_payday
    ewa_account.current_balance = Decimal("0.00")  # Reset after payday
    await db_session.commit()
    await db_session.refresh(ewa_account)

    # Verify new pay period
    assert ewa_account.pay_period_start == next_period_start
    assert ewa_account.pay_period_end == next_period_end
    assert ewa_account.next_payday == next_payday
    assert ewa_account.current_balance == Decimal("0.00")


async def test_ewa_account_repr(db_session: AsyncSession):
    """Test the __repr__ method of EWAAccount model."""
    # Create an EWA account
    ewa_account = EWAAccount(name="Repr Test", account_type="ewa", provider="Payactiv")

    db_session.add(ewa_account)
    await db_session.commit()

    # Test the __repr__ method
    repr_str = repr(ewa_account)
    assert "EWAAccount" in repr_str
    assert str(ewa_account.id) in repr_str
    assert "Repr Test" in repr_str
    assert "Payactiv" in repr_str  # Provider is included in __repr__
