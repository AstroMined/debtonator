"""
Unit tests for the PaymentAppAccount model.

Tests the PaymentAppAccount model fields, constraints, inheritance,
and polymorphic behavior as part of ADR-016 and ADR-019.
"""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.payment_app import PaymentAppAccount
from src.models.accounts import Account
from src.utils.datetime_utils import naive_utc_from_date

pytestmark = pytest.mark.asyncio


async def test_payment_app_account_inheritance(db_session: AsyncSession):
    """Test PaymentAppAccount inherits properly from Account base class."""
    # Create a payment app account
    payment_app_account = PaymentAppAccount(
        name="Test PayPal",
        account_type="payment_app",  # This should match polymorphic_identity
        current_balance=Decimal("200.00"),
        available_balance=Decimal("200.00"),
        platform="PayPal",
        has_debit_card=True,
        card_last_four="1234",
    )

    # Add to session and commit
    db_session.add(payment_app_account)
    await db_session.commit()
    await db_session.refresh(payment_app_account)

    # Verify basic properties
    assert payment_app_account.id is not None
    assert payment_app_account.name == "Test PayPal"
    assert payment_app_account.account_type == "payment_app"
    assert payment_app_account.current_balance == Decimal("200.00")
    assert payment_app_account.available_balance == Decimal("200.00")

    # Verify payment_app-specific properties
    assert payment_app_account.platform == "PayPal"
    assert payment_app_account.has_debit_card is True
    assert payment_app_account.card_last_four == "1234"

    # Verify it can be queried as an Account (polymorphic parent)
    base_account = await db_session.get(Account, payment_app_account.id)
    assert base_account is not None
    assert base_account.name == "Test PayPal"
    assert base_account.account_type == "payment_app"
    assert base_account.current_balance == Decimal("200.00")
    assert base_account.available_balance == Decimal("200.00")

    # Verify it can be queried as a PaymentAppAccount (polymorphic child)
    retrieved_payment_app = await db_session.get(
        PaymentAppAccount, payment_app_account.id
    )
    assert retrieved_payment_app is not None
    assert retrieved_payment_app.name == "Test PayPal"
    assert retrieved_payment_app.platform == "PayPal"
    assert retrieved_payment_app.has_debit_card is True
    assert retrieved_payment_app.card_last_four == "1234"


async def test_payment_app_account_polymorphic_identity(db_session: AsyncSession):
    """Test the polymorphic identity of PaymentAppAccount is correctly set."""
    # Create a payment app account
    payment_app_account = PaymentAppAccount(
        name="Polymorphic Identity Test",
        account_type="payment_app",  # This must match polymorphic_identity
        current_balance=Decimal("100.00"),
        available_balance=Decimal("100.00"),
        platform="Venmo",
    )

    # Add to session and commit
    db_session.add(payment_app_account)
    await db_session.commit()
    await db_session.refresh(payment_app_account)

    # Query it using polymorphic query
    all_accounts = (await db_session.execute(db_session.query(Account))).scalars().all()

    # Find our account in the results
    found_account = None
    for account in all_accounts:
        if account.id == payment_app_account.id:
            found_account = account
            break

    # Verify it's found with the correct type
    assert found_account is not None
    assert isinstance(found_account, PaymentAppAccount)
    assert found_account.account_type == "payment_app"


async def test_payment_app_account_fields(db_session: AsyncSession):
    """Test all fields of PaymentAppAccount model."""
    # Create a payment app account with all fields populated
    payment_app_account = PaymentAppAccount(
        name="Full Fields Test",
        account_type="payment_app",
        current_balance=Decimal("350.00"),
        available_balance=Decimal("350.00"),
        institution="PayPal, Inc.",
        currency="USD",
        account_number="user@example.com",  # For payment apps this is often email/username
        url="https://paypal.com",
        logo_path="/images/paypal.png",
        is_closed=False,
        description="Test payment app account with all fields",
        platform="PayPal",
        has_debit_card=True,
        card_last_four="5678",
        linked_account_ids="1,2,3",  # Comma-separated list of linked account IDs
        supports_direct_deposit=True,
        supports_crypto=True,
        next_action_date=naive_utc_from_date(2025, 5, 1),
        next_action_amount=Decimal("50.00"),
    )

    # Add to session and commit
    db_session.add(payment_app_account)
    await db_session.commit()
    await db_session.refresh(payment_app_account)

    # Verify all base Account fields
    assert payment_app_account.name == "Full Fields Test"
    assert payment_app_account.account_type == "payment_app"
    assert payment_app_account.current_balance == Decimal("350.00")
    assert payment_app_account.available_balance == Decimal("350.00")
    assert payment_app_account.institution == "PayPal, Inc."
    assert payment_app_account.currency == "USD"
    assert payment_app_account.account_number == "user@example.com"
    assert payment_app_account.url == "https://paypal.com"
    assert payment_app_account.logo_path == "/images/paypal.png"
    assert payment_app_account.is_closed is False
    assert payment_app_account.description == "Test payment app account with all fields"
    assert payment_app_account.next_action_date.year == 2025
    assert payment_app_account.next_action_date.month == 5
    assert payment_app_account.next_action_date.day == 1
    assert payment_app_account.next_action_amount == Decimal("50.00")

    # Verify all PaymentAppAccount-specific fields
    assert payment_app_account.platform == "PayPal"
    assert payment_app_account.has_debit_card is True
    assert payment_app_account.card_last_four == "5678"
    assert payment_app_account.linked_account_ids == "1,2,3"
    assert payment_app_account.supports_direct_deposit is True
    assert payment_app_account.supports_crypto is True


async def test_payment_app_account_minimal_fields(db_session: AsyncSession):
    """Test PaymentAppAccount can be created with only required fields."""
    # Create a payment app account with only required fields
    payment_app_account = PaymentAppAccount(
        name="Minimal Payment App",
        account_type="payment_app",
        current_balance=Decimal("0.00"),
        available_balance=Decimal("0.00"),
        platform="Cash App",  # Only platform is required specific field
    )

    # Add to session and commit
    db_session.add(payment_app_account)
    await db_session.commit()
    await db_session.refresh(payment_app_account)

    # Verify required fields
    assert payment_app_account.id is not None
    assert payment_app_account.name == "Minimal Payment App"
    assert payment_app_account.account_type == "payment_app"
    assert payment_app_account.current_balance == Decimal("0.00")
    assert payment_app_account.available_balance == Decimal("0.00")
    assert payment_app_account.platform == "Cash App"

    # Verify optional fields have defaults or are None
    assert payment_app_account.has_debit_card is False  # Default value
    assert payment_app_account.card_last_four is None
    assert payment_app_account.linked_account_ids is None
    assert payment_app_account.supports_direct_deposit is False  # Default value
    assert payment_app_account.supports_crypto is False  # Default value


async def test_payment_app_platforms(db_session: AsyncSession):
    """Test different payment app platforms."""
    # Create and test various payment app platforms
    platforms = ["PayPal", "Venmo", "Cash App", "Google Pay", "Apple Pay", "Zelle"]

    for platform in platforms:
        payment_app_account = PaymentAppAccount(
            name=f"{platform} Account",
            account_type="payment_app",
            current_balance=Decimal("100.00"),
            available_balance=Decimal("100.00"),
            platform=platform,
        )

        db_session.add(payment_app_account)
        await db_session.commit()
        await db_session.refresh(payment_app_account)

        # Verify platform was saved correctly
        assert payment_app_account.platform == platform

        # Clean up for next iteration
        await db_session.delete(payment_app_account)
        await db_session.commit()


async def test_payment_app_account_debit_card_fields(db_session: AsyncSession):
    """Test debit card fields behavior in PaymentAppAccount."""
    # 1. Test with debit card and last four digits
    account_with_card = PaymentAppAccount(
        name="Account With Card",
        account_type="payment_app",
        current_balance=Decimal("200.00"),
        available_balance=Decimal("200.00"),
        platform="PayPal",
        has_debit_card=True,
        card_last_four="9876",
    )

    db_session.add(account_with_card)
    await db_session.commit()
    await db_session.refresh(account_with_card)

    assert account_with_card.has_debit_card is True
    assert account_with_card.card_last_four == "9876"

    # 2. Test without debit card but with last four (not valid in schema but allowed in model)
    account_without_card = PaymentAppAccount(
        name="Account Without Card",
        account_type="payment_app",
        current_balance=Decimal("200.00"),
        available_balance=Decimal("200.00"),
        platform="Venmo",
        has_debit_card=False,
        card_last_four="1234",  # This would be invalid at schema level but fine at model level
    )

    db_session.add(account_without_card)
    await db_session.commit()
    await db_session.refresh(account_without_card)

    assert account_without_card.has_debit_card is False
    assert (
        account_without_card.card_last_four == "1234"
    )  # Still stored even though invalid at schema level

    # 3. Test with debit card but without last four
    account_card_no_last_four = PaymentAppAccount(
        name="Card No Last Four",
        account_type="payment_app",
        current_balance=Decimal("200.00"),
        available_balance=Decimal("200.00"),
        platform="Cash App",
        has_debit_card=True,
        card_last_four=None,  # This would be invalid at schema level but fine at model level
    )

    db_session.add(account_card_no_last_four)
    await db_session.commit()
    await db_session.refresh(account_card_no_last_four)

    assert account_card_no_last_four.has_debit_card is True
    assert (
        account_card_no_last_four.card_last_four is None
    )  # Still None even though invalid at schema level


async def test_payment_app_account_linked_accounts(db_session: AsyncSession):
    """Test linked_account_ids field handling."""
    # Test with multiple linked account IDs
    payment_app_account = PaymentAppAccount(
        name="Linked Accounts Test",
        account_type="payment_app",
        current_balance=Decimal("500.00"),
        available_balance=Decimal("500.00"),
        platform="PayPal",
        linked_account_ids="1,2,3,4,5",  # Comma-separated list
    )

    db_session.add(payment_app_account)
    await db_session.commit()
    await db_session.refresh(payment_app_account)

    # Verify linked_account_ids was saved correctly
    assert payment_app_account.linked_account_ids == "1,2,3,4,5"

    # Test conversion to actual IDs (would typically be done in service layer)
    linked_ids = [
        int(id_str) for id_str in payment_app_account.linked_account_ids.split(",")
    ]
    assert linked_ids == [1, 2, 3, 4, 5]

    # Update linked accounts
    payment_app_account.linked_account_ids = "6,7,8"
    await db_session.commit()
    await db_session.refresh(payment_app_account)

    # Verify update worked
    assert payment_app_account.linked_account_ids == "6,7,8"


async def test_payment_app_account_repr(db_session: AsyncSession):
    """Test the __repr__ method of PaymentAppAccount model."""
    # Create a payment app account
    payment_app_account = PaymentAppAccount(
        name="Repr Test", account_type="payment_app", platform="Venmo"
    )

    db_session.add(payment_app_account)
    await db_session.commit()

    # Test the __repr__ method
    repr_str = repr(payment_app_account)
    assert "PaymentAppAccount" in repr_str
    assert str(payment_app_account.id) in repr_str
    assert "Repr Test" in repr_str
    assert "Venmo" in repr_str  # Platform is included in __repr__
