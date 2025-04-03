"""
Unit tests for the SavingsAccount model.

Tests the SavingsAccount model fields, constraints, inheritance,
and polymorphic behavior as part of ADR-016 and ADR-019.
"""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.account_types.banking.savings import SavingsAccount
from src.models.accounts import Account
from src.utils.datetime_utils import naive_utc_from_date

pytestmark = pytest.mark.asyncio


async def test_savings_account_inheritance(db_session: AsyncSession):
    """Test SavingsAccount inherits properly from Account base class."""
    # Create a savings account
    savings_account = SavingsAccount(
        name="Test Savings",
        account_type="savings",  # This should match polymorphic_identity
        current_balance=Decimal("5000.00"),
        available_balance=Decimal("5000.00"),
        interest_rate=Decimal("0.0150"),  # 1.50%
        compound_frequency="monthly",
    )

    # Add to session and commit
    db_session.add(savings_account)
    await db_session.commit()
    await db_session.refresh(savings_account)

    # Verify basic properties
    assert savings_account.id is not None
    assert savings_account.name == "Test Savings"
    assert savings_account.account_type == "savings"
    assert savings_account.current_balance == Decimal("5000.00")
    assert savings_account.available_balance == Decimal("5000.00")

    # Verify savings-specific properties
    assert savings_account.interest_rate == Decimal("0.0150")
    assert savings_account.compound_frequency == "monthly"

    # Verify it can be queried as an Account (polymorphic parent)
    base_account = await db_session.get(Account, savings_account.id)
    assert base_account is not None
    assert base_account.name == "Test Savings"
    assert base_account.account_type == "savings"
    assert base_account.current_balance == Decimal("5000.00")
    assert base_account.available_balance == Decimal("5000.00")

    # Verify it can be queried as a SavingsAccount (polymorphic child)
    retrieved_savings = await db_session.get(SavingsAccount, savings_account.id)
    assert retrieved_savings is not None
    assert retrieved_savings.name == "Test Savings"
    assert retrieved_savings.interest_rate == Decimal("0.0150")
    assert retrieved_savings.compound_frequency == "monthly"


async def test_savings_account_polymorphic_identity(db_session: AsyncSession):
    """Test the polymorphic identity of SavingsAccount is correctly set."""
    # Create a savings account
    savings_account = SavingsAccount(
        name="Polymorphic Identity Test",
        account_type="savings",  # This must match polymorphic_identity
        current_balance=Decimal("5000.00"),
        available_balance=Decimal("5000.00"),
    )

    # Add to session and commit
    db_session.add(savings_account)
    await db_session.commit()
    await db_session.refresh(savings_account)

    # Query it using polymorphic query
    all_accounts = (await db_session.execute(db_session.query(Account))).scalars().all()

    # Find our account in the results
    found_account = None
    for account in all_accounts:
        if account.id == savings_account.id:
            found_account = account
            break

    # Verify it's found with the correct type
    assert found_account is not None
    assert isinstance(found_account, SavingsAccount)
    assert found_account.account_type == "savings"


async def test_savings_account_fields(db_session: AsyncSession):
    """Test all fields of SavingsAccount model."""
    # Create a savings account with all fields populated
    savings_account = SavingsAccount(
        name="Full Fields Test",
        account_type="savings",
        current_balance=Decimal("10000.00"),
        available_balance=Decimal("10000.00"),
        institution="Test Bank",
        currency="USD",
        account_number="987654321-02",
        url="https://testbank.com/savings",
        logo_path="/images/testsavings.png",
        is_closed=False,
        description="Test savings account with all fields",
        interest_rate=Decimal("0.0275"),  # 2.75%
        compound_frequency="daily",
        interest_earned_ytd=Decimal("125.75"),
        withdrawal_limit=6,
        minimum_balance=Decimal("500.00"),
        next_action_date=naive_utc_from_date(2025, 5, 1),
        next_action_amount=Decimal("50.00"),
    )

    # Add to session and commit
    db_session.add(savings_account)
    await db_session.commit()
    await db_session.refresh(savings_account)

    # Verify all base Account fields
    assert savings_account.name == "Full Fields Test"
    assert savings_account.account_type == "savings"
    assert savings_account.current_balance == Decimal("10000.00")
    assert savings_account.available_balance == Decimal("10000.00")
    assert savings_account.institution == "Test Bank"
    assert savings_account.currency == "USD"
    assert savings_account.account_number == "987654321-02"
    assert savings_account.url == "https://testbank.com/savings"
    assert savings_account.logo_path == "/images/testsavings.png"
    assert savings_account.is_closed is False
    assert savings_account.description == "Test savings account with all fields"
    assert savings_account.next_action_date.year == 2025
    assert savings_account.next_action_date.month == 5
    assert savings_account.next_action_date.day == 1
    assert savings_account.next_action_amount == Decimal("50.00")

    # Verify all SavingsAccount-specific fields
    assert savings_account.interest_rate == Decimal("0.0275")
    assert savings_account.compound_frequency == "daily"
    assert savings_account.interest_earned_ytd == Decimal("125.75")
    assert savings_account.withdrawal_limit == 6
    assert savings_account.minimum_balance == Decimal("500.00")


async def test_savings_account_optional_fields(db_session: AsyncSession):
    """Test SavingsAccount can be created with only required fields."""
    # Create a savings account with only required fields
    savings_account = SavingsAccount(
        name="Minimal Savings",
        account_type="savings",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
    )

    # Add to session and commit
    db_session.add(savings_account)
    await db_session.commit()
    await db_session.refresh(savings_account)

    # Verify required fields
    assert savings_account.id is not None
    assert savings_account.name == "Minimal Savings"
    assert savings_account.account_type == "savings"
    assert savings_account.current_balance == Decimal("1000.00")
    assert savings_account.available_balance == Decimal("1000.00")

    # Verify optional fields are None
    assert savings_account.interest_rate is None
    assert savings_account.compound_frequency is None
    assert savings_account.interest_earned_ytd is None
    assert savings_account.withdrawal_limit is None
    assert savings_account.minimum_balance is None


async def test_savings_account_decimal_precision(db_session: AsyncSession):
    """Test decimal precision handling for money fields."""
    # Create account with 4 decimal places in money fields
    savings_account = SavingsAccount(
        name="Precision Test",
        account_type="savings",
        current_balance=Decimal("10000.1234"),
        available_balance=Decimal("10000.5678"),
        interest_rate=Decimal("0.0375"),  # 3.75%
        interest_earned_ytd=Decimal("125.9876"),
        minimum_balance=Decimal("500.4321"),
    )

    db_session.add(savings_account)
    await db_session.commit()
    await db_session.refresh(savings_account)

    # Verify precision is maintained at 4 decimal places (per ADR-013)
    assert savings_account.current_balance == Decimal("10000.1234")
    assert savings_account.available_balance == Decimal("10000.5678")
    assert savings_account.interest_earned_ytd == Decimal("125.9876")
    assert savings_account.minimum_balance == Decimal("500.4321")

    # Verify exponent in each Decimal field
    assert savings_account.current_balance.as_tuple().exponent == -4
    assert savings_account.available_balance.as_tuple().exponent == -4
    assert savings_account.interest_earned_ytd.as_tuple().exponent == -4
    assert savings_account.minimum_balance.as_tuple().exponent == -4

    # Interest rate is stored with 4 decimal places (percentage)
    assert savings_account.interest_rate == Decimal("0.0375")
    assert savings_account.interest_rate.as_tuple().exponent == -4


async def test_savings_account_compound_frequencies(db_session: AsyncSession):
    """Test different compound frequency options for savings accounts."""
    # Create and test various compound frequency options
    compound_options = ["daily", "monthly", "quarterly", "annually"]

    for option in compound_options:
        savings_account = SavingsAccount(
            name=f"Compound {option.title()}",
            account_type="savings",
            current_balance=Decimal("5000.00"),
            available_balance=Decimal("5000.00"),
            interest_rate=Decimal("0.02"),  # 2%
            compound_frequency=option,
        )

        db_session.add(savings_account)
        await db_session.commit()
        await db_session.refresh(savings_account)

        # Verify compound frequency was saved
        assert savings_account.compound_frequency == option

        # Clean up for next iteration
        await db_session.delete(savings_account)
        await db_session.commit()


async def test_savings_account_repr(db_session: AsyncSession):
    """Test the __repr__ method of SavingsAccount model."""
    # Create a savings account
    savings_account = SavingsAccount(name="Repr Test", account_type="savings")

    db_session.add(savings_account)
    await db_session.commit()

    # Test the __repr__ method
    repr_str = repr(savings_account)
    assert "SavingsAccount" in repr_str
    assert str(savings_account.id) in repr_str
    assert "Repr Test" in repr_str
