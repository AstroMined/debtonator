"""
Unit tests for the CheckingAccount model.

Tests the CheckingAccount model fields, constraints, inheritance,
and polymorphic behavior as part of ADR-016 and ADR-019.
"""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.checking import CheckingAccount
from src.models.accounts import Account
from src.utils.datetime_utils import naive_utc_from_date

pytestmark = pytest.mark.asyncio


async def test_checking_account_inheritance(db_session: AsyncSession):
    """Test CheckingAccount inherits properly from Account base class."""
    # Create a checking account
    checking_account = CheckingAccount(
        name="Test Checking",
        account_type="checking",  # This should match polymorphic_identity
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
        routing_number="123456789",
        has_overdraft_protection=True,
        overdraft_limit=Decimal("500.00"),
    )

    # Add to session and commit
    db_session.add(checking_account)
    await db_session.commit()
    await db_session.refresh(checking_account)

    # Verify basic properties
    assert checking_account.id is not None
    assert checking_account.name == "Test Checking"
    assert checking_account.account_type == "checking"
    assert checking_account.current_balance == Decimal("1000.00")
    assert checking_account.available_balance == Decimal("1000.00")

    # Verify checking-specific properties
    assert checking_account.routing_number == "123456789"
    assert checking_account.has_overdraft_protection is True
    assert checking_account.overdraft_limit == Decimal("500.00")

    # Verify it can be queried as an Account (polymorphic parent)
    test_checking_account = await db_session.get(Account, checking_account.id)
    assert test_checking_account is not None
    assert test_checking_account.name == "Test Checking"
    assert test_checking_account.account_type == "checking"
    assert test_checking_account.current_balance == Decimal("1000.00")
    assert test_checking_account.available_balance == Decimal("1000.00")

    # Verify it can be queried as a CheckingAccount (polymorphic child)
    retrieved_checking = await db_session.get(CheckingAccount, checking_account.id)
    assert retrieved_checking is not None
    assert retrieved_checking.name == "Test Checking"
    assert retrieved_checking.routing_number == "123456789"
    assert retrieved_checking.has_overdraft_protection is True
    assert retrieved_checking.overdraft_limit == Decimal("500.00")


async def test_checking_account_polymorphic_identity(db_session: AsyncSession):
    """Test the polymorphic identity of CheckingAccount is correctly set."""
    # Create a checking account
    checking_account = CheckingAccount(
        name="Polymorphic Identity Test",
        account_type="checking",  # This must match polymorphic_identity
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
    )

    # Add to session and commit
    db_session.add(checking_account)
    await db_session.commit()
    await db_session.refresh(checking_account)

    # Query it using polymorphic query with new-style API
    from sqlalchemy import select

    stmt = select(Account).where(Account.id == checking_account.id)
    result = await db_session.execute(stmt)
    found_account = result.scalars().first()

    # Verify it's found with the correct type
    assert found_account is not None
    assert isinstance(found_account, CheckingAccount)
    assert found_account.account_type == "checking"


async def test_checking_account_fields(db_session: AsyncSession):
    """Test all fields of CheckingAccount model."""
    # Create a checking account with all fields populated
    checking_account = CheckingAccount(
        name="Full Fields Test",
        account_type="checking",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
        institution="Test Bank",
        currency="USD",
        account_number="123456789-01",
        url="https://testbank.com",
        logo_path="/images/testbank.png",
        is_closed=False,
        description="Primary Test Checking with all fields",
        routing_number="123456789",
        has_overdraft_protection=True,
        overdraft_limit=Decimal("500.00"),
        monthly_fee=Decimal("5.99"),
        interest_rate=Decimal("0.0025"),  # 0.25%
        iban="DE89370400440532013000",
        swift_bic="TESTBIC1",
        sort_code="12-34-56",
        branch_code="001",
        account_format="iban",
        next_action_date=naive_utc_from_date(2025, 5, 1),
        next_action_amount=Decimal("25.00"),
    )

    # Add to session and commit
    db_session.add(checking_account)
    await db_session.commit()
    await db_session.refresh(checking_account)

    # Verify all base Account fields
    assert checking_account.name == "Full Fields Test"
    assert checking_account.account_type == "checking"
    assert checking_account.current_balance == Decimal("1000.00")
    assert checking_account.available_balance == Decimal("1000.00")
    assert checking_account.institution == "Test Bank"
    assert checking_account.currency == "USD"
    assert checking_account.account_number == "123456789-01"
    assert checking_account.url == "https://testbank.com"
    assert checking_account.logo_path == "/images/testbank.png"
    assert checking_account.is_closed is False
    assert checking_account.description == "Primary Test Checking with all fields"
    assert checking_account.next_action_date.year == 2025
    assert checking_account.next_action_date.month == 5
    assert checking_account.next_action_date.day == 1
    assert checking_account.next_action_amount == Decimal("25.00")

    # Verify all CheckingAccount-specific fields
    assert checking_account.routing_number == "123456789"
    assert checking_account.has_overdraft_protection is True
    assert checking_account.overdraft_limit == Decimal("500.00")
    assert checking_account.monthly_fee == Decimal("5.99")
    assert checking_account.interest_rate == Decimal("0.0025")
    assert checking_account.iban == "DE89370400440532013000"
    assert checking_account.swift_bic == "TESTBIC1"
    assert checking_account.sort_code == "12-34-56"
    assert checking_account.branch_code == "001"
    assert checking_account.account_format == "iban"


async def test_checking_account_without_international_fields(db_session: AsyncSession):
    """Test CheckingAccount can be created without international fields."""
    # Create a checking account without international fields
    checking_account = CheckingAccount(
        name="Domestic Checking",
        account_type="checking",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
        routing_number="123456789",
        has_overdraft_protection=False,
    )

    # Add to session and commit
    db_session.add(checking_account)
    await db_session.commit()
    await db_session.refresh(checking_account)

    # Verify international fields are None or defaults
    assert checking_account.iban is None
    assert checking_account.swift_bic is None
    assert checking_account.sort_code is None
    assert checking_account.branch_code is None
    assert checking_account.account_format == "local"  # Default value


async def test_checking_account_overdraft_validation(db_session: AsyncSession):
    """Test overdraft fields behave correctly."""
    # Create account with overdraft protection but without limit
    checking_account = CheckingAccount(
        name="Overdraft Test",
        account_type="checking",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
        routing_number="123456789",
        has_overdraft_protection=True,  # Enabled but no limit specified
        overdraft_limit=None,
    )

    # Add to session and commit
    db_session.add(checking_account)
    await db_session.commit()
    await db_session.refresh(checking_account)

    # Verify account was created (model-level validation doesn't happen here,
    # it's delegated to Pydantic schema validators)
    assert checking_account.id is not None
    assert checking_account.has_overdraft_protection is True
    assert checking_account.overdraft_limit is None

    # Update the overdraft limit
    checking_account.overdraft_limit = Decimal("750.00")
    await db_session.commit()
    await db_session.refresh(checking_account)

    # Verify limit was updated
    assert checking_account.overdraft_limit == Decimal("750.00")

    # Disable overdraft protection
    checking_account.has_overdraft_protection = False
    checking_account.overdraft_limit = None  # Clear limit when disabling
    await db_session.commit()
    await db_session.refresh(checking_account)

    # Verify changes
    assert checking_account.has_overdraft_protection is False
    assert checking_account.overdraft_limit is None


async def test_checking_account_decimal_precision(db_session: AsyncSession):
    """Test decimal precision handling for money fields."""
    # Create account with 4 decimal places in money fields
    checking_account = CheckingAccount(
        name="Precision Test",
        account_type="checking",
        current_balance=Decimal("1000.1234"),
        available_balance=Decimal("1000.5678"),
        routing_number="123456789",
        has_overdraft_protection=True,
        overdraft_limit=Decimal("500.9876"),
        monthly_fee=Decimal("9.9999"),
    )

    db_session.add(checking_account)
    await db_session.commit()
    await db_session.refresh(checking_account)

    # Verify precision is maintained at 4 decimal places (per ADR-013)
    assert checking_account.current_balance == Decimal("1000.1234")
    assert checking_account.available_balance == Decimal("1000.5678")
    assert checking_account.overdraft_limit == Decimal("500.9876")
    assert checking_account.monthly_fee == Decimal("9.9999")

    # Verify exponent in each Decimal field
    assert checking_account.current_balance.as_tuple().exponent == -4
    assert checking_account.available_balance.as_tuple().exponent == -4
    assert checking_account.overdraft_limit.as_tuple().exponent == -4
    assert checking_account.monthly_fee.as_tuple().exponent == -4


async def test_checking_account_repr(db_session: AsyncSession):
    """Test the __repr__ method of CheckingAccount model."""
    # Create a checking account
    checking_account = CheckingAccount(
        name="Repr Test", account_type="checking", routing_number="123456789"
    )

    db_session.add(checking_account)
    await db_session.commit()

    # Test the __repr__ method
    repr_str = repr(checking_account)
    assert "CheckingAccount" in repr_str
    assert str(checking_account.id) in repr_str
    assert "Repr Test" in repr_str
