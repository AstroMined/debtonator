"""
Unit tests for the CreditAccount model.

Tests the CreditAccount model fields, constraints, inheritance,
and polymorphic behavior as part of ADR-016 and ADR-019.
"""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.credit import CreditAccount
from src.models.accounts import Account
from src.utils.datetime_utils import naive_utc_from_date

pytestmark = pytest.mark.asyncio


async def test_credit_account_inheritance(db_session: AsyncSession):
    """Test CreditAccount inherits properly from Account base class."""
    # Create a credit account
    credit_account = CreditAccount(
        name="Test Credit Card",
        account_type="credit",  # This should match polymorphic_identity
        current_balance=Decimal("500.00"),
        available_balance=Decimal("500.00"),
        credit_limit=Decimal("2000.00"),
        statement_balance=Decimal("500.00"),
        minimum_payment=Decimal("25.00"),
        apr=Decimal("0.1499"),  # 14.99%
    )

    # Add to session and commit
    db_session.add(credit_account)
    await db_session.commit()
    await db_session.refresh(credit_account)

    # Verify basic properties
    assert credit_account.id is not None
    assert credit_account.name == "Test Credit Card"
    assert credit_account.account_type == "credit"
    assert credit_account.current_balance == Decimal("500.00")
    assert credit_account.available_balance == Decimal("500.00")

    # Verify credit-specific properties
    assert credit_account.credit_limit == Decimal("2000.00")
    assert credit_account.statement_balance == Decimal("500.00")
    assert credit_account.minimum_payment == Decimal("25.00")
    assert credit_account.apr == Decimal("0.1499")

    # Verify it can be queried as an Account (polymorphic parent)
    test_checking_account = await db_session.get(Account, credit_account.id)
    assert test_checking_account is not None
    assert test_checking_account.name == "Test Credit Card"
    assert test_checking_account.account_type == "credit"
    assert test_checking_account.current_balance == Decimal("500.00")
    assert test_checking_account.available_balance == Decimal("500.00")

    # Verify it can be queried as a CreditAccount (polymorphic child)
    retrieved_credit = await db_session.get(CreditAccount, credit_account.id)
    assert retrieved_credit is not None
    assert retrieved_credit.name == "Test Credit Card"
    assert retrieved_credit.credit_limit == Decimal("2000.00")
    assert retrieved_credit.statement_balance == Decimal("500.00")
    assert retrieved_credit.minimum_payment == Decimal("25.00")
    assert retrieved_credit.apr == Decimal("0.1499")


async def test_credit_account_polymorphic_identity(db_session: AsyncSession):
    """Test the polymorphic identity of CreditAccount is correctly set."""
    # Create a credit account
    credit_account = CreditAccount(
        name="Polymorphic Identity Test",
        account_type="credit",  # This must match polymorphic_identity
        current_balance=Decimal("500.00"),
        available_balance=Decimal("500.00"),
        credit_limit=Decimal("1000.00"),
    )

    # Add to session and commit
    db_session.add(credit_account)
    await db_session.commit()
    await db_session.refresh(credit_account)

    # Query it using polymorphic query with new-style API
    from sqlalchemy import select

    stmt = select(Account).where(Account.id == credit_account.id)
    result = await db_session.execute(stmt)
    found_account = result.scalars().first()

    # Verify it's found with the correct type
    assert found_account is not None
    assert isinstance(found_account, CreditAccount)
    assert found_account.account_type == "credit"


async def test_credit_account_fields(db_session: AsyncSession):
    """Test all fields of CreditAccount model."""
    # Create a credit account with all fields populated
    statement_date = naive_utc_from_date(2025, 3, 15)
    due_date = naive_utc_from_date(2025, 4, 10)
    credit_account = CreditAccount(
        name="Full Fields Test",
        account_type="credit",
        current_balance=Decimal("750.00"),
        available_balance=Decimal("750.00"),
        institution="Test Bank",
        currency="USD",
        account_number="5432-1098-7654-3210",
        url="https://testbank.com/credit",
        logo_path="/images/testcredit.png",
        is_closed=False,
        description="Test credit account with all fields",
        credit_limit=Decimal("3000.00"),
        statement_balance=Decimal("750.00"),
        statement_due_date=due_date,
        minimum_payment=Decimal("35.00"),
        apr=Decimal("0.1999"),  # 19.99%
        annual_fee=Decimal("95.00"),
        rewards_program="Cash Back Plus",
        autopay_status="minimum",
        last_statement_date=statement_date,
        next_action_date=due_date,
        next_action_amount=Decimal("35.00"),
    )

    # Add to session and commit
    db_session.add(credit_account)
    await db_session.commit()
    await db_session.refresh(credit_account)

    # Verify all base Account fields
    assert credit_account.name == "Full Fields Test"
    assert credit_account.account_type == "credit"
    assert credit_account.current_balance == Decimal("750.00")
    assert credit_account.available_balance == Decimal("750.00")
    assert credit_account.institution == "Test Bank"
    assert credit_account.currency == "USD"
    assert credit_account.account_number == "5432-1098-7654-3210"
    assert credit_account.url == "https://testbank.com/credit"
    assert credit_account.logo_path == "/images/testcredit.png"
    assert credit_account.is_closed is False
    assert credit_account.description == "Test credit account with all fields"
    assert credit_account.next_action_date.year == 2025
    assert credit_account.next_action_date.month == 4
    assert credit_account.next_action_date.day == 10
    assert credit_account.next_action_amount == Decimal("35.00")

    # Verify all CreditAccount-specific fields
    assert credit_account.credit_limit == Decimal("3000.00")
    assert credit_account.statement_balance == Decimal("750.00")
    assert credit_account.statement_due_date.year == 2025
    assert credit_account.statement_due_date.month == 4
    assert credit_account.statement_due_date.day == 10
    assert credit_account.minimum_payment == Decimal("35.00")
    assert credit_account.apr == Decimal("0.1999")
    assert credit_account.annual_fee == Decimal("95.00")
    assert credit_account.rewards_program == "Cash Back Plus"
    assert credit_account.autopay_status == "minimum"
    assert credit_account.last_statement_date.year == 2025
    assert credit_account.last_statement_date.month == 3
    assert credit_account.last_statement_date.day == 15


async def test_credit_account_optional_fields(db_session: AsyncSession):
    """Test CreditAccount can be created with only required fields."""
    # Create a credit account with only required fields
    credit_account = CreditAccount(
        name="Minimal Credit Card",
        account_type="credit",
        current_balance=Decimal("0.00"),
        available_balance=Decimal("0.00"),
        credit_limit=Decimal("1000.00"),
    )

    # Add to session and commit
    db_session.add(credit_account)
    await db_session.commit()
    await db_session.refresh(credit_account)

    # Verify required fields
    assert credit_account.id is not None
    assert credit_account.name == "Minimal Credit Card"
    assert credit_account.account_type == "credit"
    assert credit_account.current_balance == Decimal("0.00")
    assert credit_account.available_balance == Decimal("0.00")
    assert credit_account.credit_limit == Decimal("1000.00")

    # Verify optional fields are None
    assert credit_account.statement_balance is None
    assert credit_account.statement_due_date is None
    assert credit_account.minimum_payment is None
    assert credit_account.apr is None
    assert credit_account.annual_fee is None
    assert credit_account.rewards_program is None
    assert credit_account.autopay_status is None
    assert credit_account.last_statement_date is None


async def test_credit_account_decimal_precision(db_session: AsyncSession):
    """Test decimal precision handling for money fields."""
    # Create account with 4 decimal places in money fields
    credit_account = CreditAccount(
        name="Precision Test",
        account_type="credit",
        current_balance=Decimal("750.1234"),
        available_balance=Decimal("750.5678"),
        credit_limit=Decimal("3000.9876"),
        statement_balance=Decimal("750.4321"),
        minimum_payment=Decimal("35.6789"),
        apr=Decimal("0.1999"),  # 19.99%
        annual_fee=Decimal("95.5432"),
    )

    db_session.add(credit_account)
    await db_session.commit()
    await db_session.refresh(credit_account)

    # Verify precision is maintained at 4 decimal places (per ADR-013)
    assert credit_account.current_balance == Decimal("750.1234")
    assert credit_account.available_balance == Decimal("750.5678")
    assert credit_account.credit_limit == Decimal("3000.9876")
    assert credit_account.statement_balance == Decimal("750.4321")
    assert credit_account.minimum_payment == Decimal("35.6789")
    assert credit_account.annual_fee == Decimal("95.5432")

    # Verify exponent in each Decimal field
    assert credit_account.current_balance.as_tuple().exponent == -4
    assert credit_account.available_balance.as_tuple().exponent == -4
    assert credit_account.credit_limit.as_tuple().exponent == -4
    assert credit_account.statement_balance.as_tuple().exponent == -4
    assert credit_account.minimum_payment.as_tuple().exponent == -4
    assert credit_account.annual_fee.as_tuple().exponent == -4

    # APR is stored with 4 decimal places (percentage)
    assert credit_account.apr == Decimal("0.1999")
    assert credit_account.apr.as_tuple().exponent == -4


async def test_credit_account_autopay_options(db_session: AsyncSession):
    """Test different autopay options for credit accounts."""
    # Create and test various autopay options
    autopay_options = ["none", "minimum", "full_balance", "fixed_amount"]

    for option in autopay_options:
        credit_account = CreditAccount(
            name=f"Autopay {option.title()}",
            account_type="credit",
            current_balance=Decimal("500.00"),
            available_balance=Decimal("500.00"),
            credit_limit=Decimal("2000.00"),
            autopay_status=option,
        )

        db_session.add(credit_account)
        await db_session.commit()
        await db_session.refresh(credit_account)

        # Verify autopay option was saved
        assert credit_account.autopay_status == option

        # Clean up for next iteration
        await db_session.delete(credit_account)
        await db_session.commit()


async def test_credit_account_repr(db_session: AsyncSession):
    """Test the __repr__ method of CreditAccount model."""
    # Create a credit account
    credit_account = CreditAccount(
        name="Repr Test", account_type="credit", credit_limit=Decimal("1000.00")
    )

    db_session.add(credit_account)
    await db_session.commit()

    # Test the __repr__ method
    repr_str = repr(credit_account)
    assert "CreditAccount" in repr_str
    assert str(credit_account.id) in repr_str
    assert "Repr Test" in repr_str
