"""
Unit tests for the BNPLAccount model.

Tests the BNPLAccount model fields, constraints, inheritance,
and polymorphic behavior as part of ADR-016 and ADR-019.
"""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.bnpl import BNPLAccount
from src.models.accounts import Account
from src.utils.datetime_utils import naive_utc_from_date

pytestmark = pytest.mark.asyncio


async def test_bnpl_account_inheritance(db_session: AsyncSession):
    """Test BNPLAccount inherits properly from Account base class."""
    # Create a BNPL account
    next_payment_date = naive_utc_from_date(2025, 5, 15)
    bnpl_account = BNPLAccount(
        name="Test Affirm Purchase",
        account_type="bnpl",  # This should match polymorphic_identity
        current_balance=Decimal("300.00"),  # Remaining balance
        available_balance=Decimal("300.00"),
        original_amount=Decimal("400.00"),
        installment_count=4,
        installments_paid=1,
        installment_amount=Decimal("100.00"),
        payment_frequency="monthly",
        next_payment_date=next_payment_date,
        bnpl_provider="Affirm",
    )

    # Add to session and commit
    db_session.add(bnpl_account)
    await db_session.commit()
    await db_session.refresh(bnpl_account)

    # Verify basic properties
    assert bnpl_account.id is not None
    assert bnpl_account.name == "Test Affirm Purchase"
    assert bnpl_account.account_type == "bnpl"
    assert bnpl_account.current_balance == Decimal("300.00")
    assert bnpl_account.available_balance == Decimal("300.00")

    # Verify BNPL-specific properties
    assert bnpl_account.original_amount == Decimal("400.00")
    assert bnpl_account.installment_count == 4
    assert bnpl_account.installments_paid == 1
    assert bnpl_account.installment_amount == Decimal("100.00")
    assert bnpl_account.payment_frequency == "monthly"
    assert bnpl_account.next_payment_date == next_payment_date
    assert bnpl_account.bnpl_provider == "Affirm"

    # Verify it can be queried as an Account (polymorphic parent)
    base_account = await db_session.get(Account, bnpl_account.id)
    assert base_account is not None
    assert base_account.name == "Test Affirm Purchase"
    assert base_account.account_type == "bnpl"
    assert base_account.current_balance == Decimal("300.00")
    assert base_account.available_balance == Decimal("300.00")

    # Verify it can be queried as a BNPLAccount (polymorphic child)
    retrieved_bnpl = await db_session.get(BNPLAccount, bnpl_account.id)
    assert retrieved_bnpl is not None
    assert retrieved_bnpl.name == "Test Affirm Purchase"
    assert retrieved_bnpl.original_amount == Decimal("400.00")
    assert retrieved_bnpl.installment_count == 4
    assert retrieved_bnpl.installments_paid == 1
    assert retrieved_bnpl.installment_amount == Decimal("100.00")
    assert retrieved_bnpl.payment_frequency == "monthly"
    assert retrieved_bnpl.bnpl_provider == "Affirm"


async def test_bnpl_account_polymorphic_identity(db_session: AsyncSession):
    """Test the polymorphic identity of BNPLAccount is correctly set."""
    # Create a BNPL account
    bnpl_account = BNPLAccount(
        name="Polymorphic Identity Test",
        account_type="bnpl",  # This must match polymorphic_identity
        current_balance=Decimal("500.00"),
        available_balance=Decimal("500.00"),
        original_amount=Decimal("600.00"),
        installment_count=6,
        installments_paid=1,
        installment_amount=Decimal("100.00"),
        payment_frequency="biweekly",
        bnpl_provider="Klarna",
    )

    # Add to session and commit
    db_session.add(bnpl_account)
    await db_session.commit()
    await db_session.refresh(bnpl_account)

    # Query it using polymorphic query
    all_accounts = (await db_session.execute(db_session.query(Account))).scalars().all()

    # Find our account in the results
    found_account = None
    for account in all_accounts:
        if account.id == bnpl_account.id:
            found_account = account
            break

    # Verify it's found with the correct type
    assert found_account is not None
    assert isinstance(found_account, BNPLAccount)
    assert found_account.account_type == "bnpl"


async def test_bnpl_account_fields(db_session: AsyncSession):
    """Test all fields of BNPLAccount model."""
    # Create a BNPL account with all fields populated
    next_payment_date = naive_utc_from_date(2025, 5, 15)
    bnpl_account = BNPLAccount(
        name="Full Fields Test",
        account_type="bnpl",
        current_balance=Decimal("450.00"),
        available_balance=Decimal("450.00"),
        institution="Affirm, Inc.",
        currency="USD",
        account_number="BNPL-12345",
        url="https://affirm.com/account",
        logo_path="/images/affirm.png",
        is_closed=False,
        description="Test BNPL account with all fields",
        original_amount=Decimal("600.00"),
        installment_count=6,
        installments_paid=1,
        installment_amount=Decimal("100.00"),
        payment_frequency="monthly",
        next_payment_date=next_payment_date,
        promotion_info="0% interest if paid within 6 months",
        late_fee=Decimal("25.00"),
        bnpl_provider="Affirm",
        next_action_date=next_payment_date,
        next_action_amount=Decimal("100.00"),
    )

    # Add to session and commit
    db_session.add(bnpl_account)
    await db_session.commit()
    await db_session.refresh(bnpl_account)

    # Verify all base Account fields
    assert bnpl_account.name == "Full Fields Test"
    assert bnpl_account.account_type == "bnpl"
    assert bnpl_account.current_balance == Decimal("450.00")
    assert bnpl_account.available_balance == Decimal("450.00")
    assert bnpl_account.institution == "Affirm, Inc."
    assert bnpl_account.currency == "USD"
    assert bnpl_account.account_number == "BNPL-12345"
    assert bnpl_account.url == "https://affirm.com/account"
    assert bnpl_account.logo_path == "/images/affirm.png"
    assert bnpl_account.is_closed is False
    assert bnpl_account.description == "Test BNPL account with all fields"
    assert bnpl_account.next_action_date.year == 2025
    assert bnpl_account.next_action_date.month == 5
    assert bnpl_account.next_action_date.day == 15
    assert bnpl_account.next_action_amount == Decimal("100.00")

    # Verify all BNPLAccount-specific fields
    assert bnpl_account.original_amount == Decimal("600.00")
    assert bnpl_account.installment_count == 6
    assert bnpl_account.installments_paid == 1
    assert bnpl_account.installment_amount == Decimal("100.00")
    assert bnpl_account.payment_frequency == "monthly"
    assert bnpl_account.next_payment_date.year == 2025
    assert bnpl_account.next_payment_date.month == 5
    assert bnpl_account.next_payment_date.day == 15
    assert bnpl_account.promotion_info == "0% interest if paid within 6 months"
    assert bnpl_account.late_fee == Decimal("25.00")
    assert bnpl_account.bnpl_provider == "Affirm"


async def test_bnpl_account_minimal_fields(db_session: AsyncSession):
    """Test BNPLAccount can be created with only required fields."""
    # Create a BNPL account with only required fields
    bnpl_account = BNPLAccount(
        name="Minimal BNPL",
        account_type="bnpl",
        current_balance=Decimal("400.00"),
        available_balance=Decimal("400.00"),
        original_amount=Decimal("400.00"),
        installment_count=4,
        installments_paid=0,
        installment_amount=Decimal("100.00"),
        payment_frequency="monthly",
        bnpl_provider="Afterpay",
    )

    # Add to session and commit
    db_session.add(bnpl_account)
    await db_session.commit()
    await db_session.refresh(bnpl_account)

    # Verify required fields
    assert bnpl_account.id is not None
    assert bnpl_account.name == "Minimal BNPL"
    assert bnpl_account.account_type == "bnpl"
    assert bnpl_account.current_balance == Decimal("400.00")
    assert bnpl_account.available_balance == Decimal("400.00")
    assert bnpl_account.original_amount == Decimal("400.00")
    assert bnpl_account.installment_count == 4
    assert bnpl_account.installments_paid == 0
    assert bnpl_account.installment_amount == Decimal("100.00")
    assert bnpl_account.payment_frequency == "monthly"
    assert bnpl_account.bnpl_provider == "Afterpay"

    # Verify optional fields are None
    assert bnpl_account.next_payment_date is None
    assert bnpl_account.promotion_info is None
    assert bnpl_account.late_fee is None


async def test_bnpl_account_decimal_precision(db_session: AsyncSession):
    """Test decimal precision handling for money fields."""
    # Create account with 4 decimal places in money fields
    bnpl_account = BNPLAccount(
        name="Precision Test",
        account_type="bnpl",
        current_balance=Decimal("399.9999"),
        available_balance=Decimal("399.9999"),
        original_amount=Decimal("499.9999"),
        installment_count=5,
        installments_paid=1,
        installment_amount=Decimal("100.0000"),
        payment_frequency="monthly",
        bnpl_provider="Klarna",
        late_fee=Decimal("25.5555"),
    )

    db_session.add(bnpl_account)
    await db_session.commit()
    await db_session.refresh(bnpl_account)

    # Verify precision is maintained at 4 decimal places (per ADR-013)
    assert bnpl_account.current_balance == Decimal("399.9999")
    assert bnpl_account.available_balance == Decimal("399.9999")
    assert bnpl_account.original_amount == Decimal("499.9999")
    assert bnpl_account.installment_amount == Decimal("100.0000")
    assert bnpl_account.late_fee == Decimal("25.5555")

    # Verify exponent in each Decimal field
    assert bnpl_account.current_balance.as_tuple().exponent == -4
    assert bnpl_account.available_balance.as_tuple().exponent == -4
    assert bnpl_account.original_amount.as_tuple().exponent == -4
    assert bnpl_account.installment_amount.as_tuple().exponent == -4
    assert bnpl_account.late_fee.as_tuple().exponent == -4


async def test_bnpl_payment_frequencies(db_session: AsyncSession):
    """Test different payment frequency options for BNPL accounts."""
    # Create and test various payment frequency options
    frequency_options = ["weekly", "biweekly", "monthly"]

    for option in frequency_options:
        bnpl_account = BNPLAccount(
            name=f"{option.title()} Payment Plan",
            account_type="bnpl",
            current_balance=Decimal("300.00"),
            available_balance=Decimal("300.00"),
            original_amount=Decimal("400.00"),
            installment_count=4,
            installments_paid=1,
            installment_amount=Decimal("100.00"),
            payment_frequency=option,
            bnpl_provider="Affirm",
        )

        db_session.add(bnpl_account)
        await db_session.commit()
        await db_session.refresh(bnpl_account)

        # Verify payment frequency was saved correctly
        assert bnpl_account.payment_frequency == option

        # Clean up for next iteration
        await db_session.delete(bnpl_account)
        await db_session.commit()


async def test_bnpl_providers(db_session: AsyncSession):
    """Test different BNPL provider options."""
    # Create and test various BNPL providers
    providers = ["Affirm", "Klarna", "Afterpay", "Zip", "Sezzle"]

    for provider in providers:
        bnpl_account = BNPLAccount(
            name=f"{provider} Purchase",
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

        db_session.add(bnpl_account)
        await db_session.commit()
        await db_session.refresh(bnpl_account)

        # Verify provider was saved correctly
        assert bnpl_account.bnpl_provider == provider

        # Clean up for next iteration
        await db_session.delete(bnpl_account)
        await db_session.commit()


async def test_bnpl_installment_tracking(db_session: AsyncSession):
    """Test installment tracking fields work correctly."""
    # Create a BNPL account with initial values
    bnpl_account = BNPLAccount(
        name="Installment Tracking Test",
        account_type="bnpl",
        current_balance=Decimal("300.00"),
        available_balance=Decimal("300.00"),
        original_amount=Decimal("400.00"),
        installment_count=4,
        installments_paid=1,
        installment_amount=Decimal("100.00"),
        payment_frequency="monthly",
        next_payment_date=naive_utc_from_date(2025, 5, 15),
        bnpl_provider="Affirm",
    )

    db_session.add(bnpl_account)
    await db_session.commit()
    await db_session.refresh(bnpl_account)

    # Verify initial state
    assert bnpl_account.installment_count == 4
    assert bnpl_account.installments_paid == 1
    assert bnpl_account.current_balance == Decimal("300.00")

    # Simulate payment of another installment
    bnpl_account.installments_paid = 2
    bnpl_account.current_balance = Decimal("200.00")
    bnpl_account.next_payment_date = naive_utc_from_date(2025, 6, 15)
    await db_session.commit()
    await db_session.refresh(bnpl_account)

    # Verify updated state
    assert bnpl_account.installments_paid == 2
    assert bnpl_account.current_balance == Decimal("200.00")
    assert bnpl_account.next_payment_date.month == 6

    # Simulate payment of all installments
    bnpl_account.installments_paid = 4
    bnpl_account.current_balance = Decimal("0.00")
    bnpl_account.next_payment_date = None
    bnpl_account.is_closed = True  # Account should be closed when fully paid
    await db_session.commit()
    await db_session.refresh(bnpl_account)

    # Verify final state
    assert bnpl_account.installments_paid == 4
    assert bnpl_account.current_balance == Decimal("0.00")
    assert bnpl_account.next_payment_date is None
    assert bnpl_account.is_closed is True


async def test_bnpl_account_repr(db_session: AsyncSession):
    """Test the __repr__ method of BNPLAccount model."""
    # Create a BNPL account
    bnpl_account = BNPLAccount(
        name="Repr Test",
        account_type="bnpl",
        original_amount=Decimal("400.00"),
        installment_count=4,
        installments_paid=0,
        installment_amount=Decimal("100.00"),
        payment_frequency="monthly",
        bnpl_provider="Klarna",
    )

    db_session.add(bnpl_account)
    await db_session.commit()

    # Test the __repr__ method
    repr_str = repr(bnpl_account)
    assert "BNPLAccount" in repr_str
    assert str(bnpl_account.id) in repr_str
    assert "Repr Test" in repr_str
    assert "Klarna" in repr_str  # Provider is included in __repr__
