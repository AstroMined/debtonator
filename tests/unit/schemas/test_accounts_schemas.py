"""
Unit tests for account schemas.

Tests the account schema validation and serialization
as part of ADR-016 Account Type Expansion.
"""

from datetime import datetime, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo  # Only needed for non-UTC timezone tests

import pytest
from pydantic import ValidationError

from src.schemas.accounts import (
    AccountBase,
    AccountInDB,
    AccountUpdate,
    AvailableCreditResponse,
    StatementBalanceHistory,
    validate_account_type,
    validate_credit_account_field,
)
from src.utils.datetime_utils import utc_datetime, utc_now


def test_account_base_valid():
    """Test valid account base schema"""
    statement_date = datetime.now(timezone.utc)
    account = AccountBase(
        name="Test Account",
        account_type="checking",  # Updated from type to account_type
        current_balance=Decimal("1000.00"),  # Added current_balance
        available_balance=Decimal("1000.00"),
        last_statement_date=statement_date,
    )
    assert account.name == "Test Account"
    assert account.account_type == "checking"  # Updated field name
    assert account.current_balance == Decimal("1000.00")  # New field
    assert account.available_balance == Decimal("1000.00")
    assert account.last_statement_date == statement_date


def test_account_base_name_validation():
    """Test name field validation"""
    # Test empty name
    with pytest.raises(
        ValidationError, match="String should have at least 1 character"
    ):
        AccountBase(name="", account_type="checking")  # Updated field name

    # Test too long name
    with pytest.raises(
        ValidationError, match="String should have at most 50 characters"
    ):
        AccountBase(name="A" * 51, account_type="checking")  # Updated field name


def test_account_base_decimal_validation():
    """Test decimal field validation"""
    # Test decimal places (too many decimal places)
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        AccountBase(
            name="Test Account",
            account_type="checking",  # Updated field name
            current_balance=Decimal("100.00"),  # Added current_balance
            available_balance=Decimal("100.123"),  # Too many decimal places
        )

    # Test valid decimal places (0 decimals)
    valid_account = AccountBase(
        name="Test Account",
        account_type="checking",  # Updated field name
        current_balance=Decimal("100"),  # Added current_balance
        available_balance=Decimal("100"),
    )
    assert valid_account.available_balance == Decimal("100")

    # Test valid decimal places (1 decimal)
    valid_account = AccountBase(
        name="Test Account",
        account_type="checking",  # Updated field name
        current_balance=Decimal("100.5"),  # Added current_balance
        available_balance=Decimal("100.5"),
    )
    assert valid_account.available_balance == Decimal("100.5")

    # Test valid decimal places (2 decimals)
    valid_account = AccountBase(
        name="Test Account",
        account_type="checking",  # Updated field name
        current_balance=Decimal("100.50"),  # Added current_balance
        available_balance=Decimal("100.50"),
    )
    assert valid_account.available_balance == Decimal("100.50")

    # Test negative available credit
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        AccountBase(
            name="Test Account",
            account_type="credit",  # Updated field name
            current_balance=Decimal("0.00"),  # Added current_balance
            available_balance=Decimal("0.00"),
            available_credit=Decimal("-100.00"),
        )


def test_validate_credit_account_field_function():
    """Test the validate_credit_account_field function directly."""
    # Create validator function for testing
    validator = validate_credit_account_field("total_limit")

    # Test case with None account type (should not validate/raise error)
    class MockInfoNoneType:
        def __init__(self):
            self.data = {"account_type": None}  # Updated field name

    # This tests when account_type is None
    result = validator(Decimal("1000.00"), MockInfoNoneType())
    assert result == Decimal("1000.00")

    # When value is None, should always return None
    assert validator(None, MockInfoNoneType()) is None

    # Test with checking account type (should raise error)
    class MockInfoChecking:
        def __init__(self):
            self.data = {"account_type": "checking"}  # Updated field name

    with pytest.raises(
        ValueError, match="Total Limit can only be set for credit accounts"
    ):
        validator(Decimal("1000.00"), MockInfoChecking())

    # Test with credit account type (should pass)
    class MockInfoCredit:
        def __init__(self):
            self.data = {"account_type": "credit"}  # Updated field name

    result = validator(Decimal("1000.00"), MockInfoCredit())
    assert result == Decimal("1000.00")


def test_account_base_credit_validation():
    """Test credit account specific validation"""
    # Test total_limit on non-credit account
    with pytest.raises(
        ValidationError, match="Total Limit can only be set for credit accounts"
    ):
        AccountBase(
            name="Test Account",
            account_type="checking",  # Updated field name
            current_balance=Decimal("0.00"),  # Added current_balance
            available_balance=Decimal("0.00"),
            total_limit=Decimal("1000.00"),
        )

    # Test available_credit on non-credit account
    with pytest.raises(
        ValidationError, match="Available Credit can only be set for credit accounts"
    ):
        AccountBase(
            name="Test Account",
            account_type="checking",  # Updated field name
            current_balance=Decimal("0.00"),  # Added current_balance
            available_balance=Decimal("0.00"),
            available_credit=Decimal("1000.00"),
        )

    # Test valid credit account
    account = AccountBase(
        name="Credit Card",
        account_type="credit",  # Updated field name
        current_balance=Decimal("-2000.00"),  # Added current_balance
        available_balance=Decimal("-2000.00"),
        total_limit=Decimal("5000.00"),
        available_credit=Decimal("3000.00"),
    )
    assert account.total_limit == Decimal("5000.00")
    assert account.available_credit == Decimal("3000.00")

    # Test account type transition
    # Create a credit account with credit-specific fields
    credit_account = AccountBase(
        name="Credit Card",
        account_type="credit",  # Updated field name
        current_balance=Decimal("-2000.00"),  # Added current_balance
        available_balance=Decimal("-2000.00"),
        total_limit=Decimal("5000.00"),
        available_credit=Decimal("3000.00"),
    )

    # Now try to update it to a checking account without removing credit fields
    # This should fail validation
    update_data = {
        "account_type": "checking",  # Updated field name
        # Keeping credit fields which should be invalid for checking
        "total_limit": Decimal("5000.00"),
        "available_credit": Decimal("3000.00"),
    }

    with pytest.raises(ValidationError):
        AccountUpdate(**update_data)


def test_account_base_invalid_statement_date():
    """Test invalid statement date validation"""
    # Test naive datetime
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        AccountBase(
            name="Test Account",
            account_type="checking",  # Updated field name
            current_balance=Decimal("1000.00"),  # Added current_balance
            available_balance=Decimal("1000.00"),
            last_statement_date=datetime.now(),
        )

    # Test non-UTC timezone
    non_utc_date = datetime.now(ZoneInfo("America/New_York"))
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        AccountBase(
            name="Test Account",
            account_type="checking",  # Updated field name
            current_balance=Decimal("1000.00"),  # Added current_balance
            available_balance=Decimal("1000.00"),
            last_statement_date=non_utc_date,
        )

    # Test with datetime_utils.py functions
    # Create account with UTC datetime from datetime_utils
    now = utc_now()
    account = AccountBase(
        name="Test Account",
        account_type="checking",  # Updated field name
        current_balance=Decimal("1000.00"),  # Added current_balance
        available_balance=Decimal("1000.00"),
        last_statement_date=now,
    )

    # Verify datetime is preserved correctly
    assert account.last_statement_date == now

    # Test with utc_datetime function
    specific_date = utc_datetime(2025, 3, 15, 14, 30)
    account = AccountBase(
        name="Test Account",
        account_type="checking",  # Updated field name
        current_balance=Decimal("1000.00"),  # Added current_balance
        available_balance=Decimal("1000.00"),
        last_statement_date=specific_date,
    )

    # Verify datetime is preserved correctly
    assert account.last_statement_date == specific_date
    assert specific_date.year == 2025
    assert specific_date.month == 3
    assert specific_date.day == 15


def test_account_update_valid():
    """Test valid account update schema"""
    statement_date = datetime.now(timezone.utc)
    update = AccountUpdate(
        name="Updated Account",
        account_type="savings",  # Updated field name
        last_statement_date=statement_date,
    )
    assert update.name == "Updated Account"
    assert update.account_type == "savings"  # Updated field name
    assert update.last_statement_date == statement_date


def test_account_update_validation():
    """Test account update validation"""
    # Test name length
    with pytest.raises(
        ValidationError, match="String should have at least 1 character"
    ):
        AccountUpdate(name="")

    # Test credit account validation
    with pytest.raises(
        ValidationError, match="Total Limit can only be set for credit accounts"
    ):
        AccountUpdate(
            account_type="checking", total_limit=Decimal("1000.00")
        )  # Updated field name

    # Test too many decimal places
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        AccountUpdate(available_balance=Decimal("100.123"))

    # Test valid decimal formats
    update1 = AccountUpdate(available_balance=Decimal("100"))  # 0 decimal places
    assert update1.available_balance == Decimal("100")

    update2 = AccountUpdate(available_balance=Decimal("100.5"))  # 1 decimal place
    assert update2.available_balance == Decimal("100.5")

    update3 = AccountUpdate(available_balance=Decimal("100.50"))  # 2 decimal places
    assert update3.available_balance == Decimal("100.50")

    # Test valid credit account update
    update = AccountUpdate(
        account_type="credit",  # Updated field name
        total_limit=Decimal("5000.00"),
        available_credit=Decimal("3000.00"),
    )
    assert update.total_limit == Decimal("5000.00")
    assert update.available_credit == Decimal("3000.00")


def test_account_update_invalid_statement_date():
    """Test invalid statement date in update"""
    # Test naive datetime
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        AccountUpdate(name="Updated Account", last_statement_date=datetime.now())

    # Test non-UTC timezone
    non_utc_date = datetime.now(ZoneInfo("America/New_York"))
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        AccountUpdate(name="Updated Account", last_statement_date=non_utc_date)


def test_account_in_db_valid():
    """Test valid account in DB schema"""
    now = datetime.now(timezone.utc)
    account = AccountInDB(
        id=1,
        name="Test Account",
        account_type="credit",  # Updated field name
        current_balance=Decimal("0.00"),  # Added current_balance
        available_balance=Decimal("0.00"),
        created_at=now,
        updated_at=now,
    )
    assert account.id == 1
    assert account.name == "Test Account"
    assert account.account_type == "credit"  # Updated field name
    assert account.created_at == now
    assert account.updated_at == now


def test_account_in_db_validation():
    """Test account in DB validation"""
    now = datetime.now(timezone.utc)

    # Test invalid ID
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        AccountInDB(
            id=0,
            name="Test Account",
            account_type="credit",  # Updated field name
            current_balance=Decimal("0.00"),  # Added current_balance
            available_balance=Decimal("0.00"),
            created_at=now,
            updated_at=now,
        )

    # Test name length
    with pytest.raises(
        ValidationError, match="String should have at least 1 character"
    ):
        AccountInDB(
            id=1,
            name="",
            account_type="credit",  # Updated field name
            current_balance=Decimal("0.00"),  # Added current_balance
            available_balance=Decimal("0.00"),
            created_at=now,
            updated_at=now,
        )


def test_account_in_db_invalid_timestamps():
    """Test invalid timestamps in DB schema"""
    now = datetime.now(timezone.utc)
    naive_now = datetime.now()

    # Test naive created_at
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        AccountInDB(
            id=1,
            name="Test Account",
            account_type="credit",  # Updated field name
            current_balance=Decimal("0.00"),  # Added current_balance
            available_balance=Decimal("0.00"),
            created_at=naive_now,
            updated_at=now,
        )

    # Test naive updated_at
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        AccountInDB(
            id=1,
            name="Test Account",
            account_type="credit",  # Updated field name
            current_balance=Decimal("0.00"),  # Added current_balance
            available_balance=Decimal("0.00"),
            created_at=now,
            updated_at=naive_now,
        )

    # Test non-UTC timezone
    non_utc = datetime.now(ZoneInfo("America/New_York"))
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        AccountInDB(
            id=1,
            name="Test Account",
            account_type="credit",  # Updated field name
            current_balance=Decimal("0.00"),  # Added current_balance
            available_balance=Decimal("0.00"),
            created_at=non_utc,
            updated_at=now,
        )


def test_statement_balance_history_valid():
    """Test valid statement balance history schema"""
    now = datetime.now(timezone.utc)
    history = StatementBalanceHistory(
        statement_date=now,
        statement_balance=Decimal("1000.00"),
        minimum_payment=Decimal("25.00"),
        due_date=now,
    )
    assert history.statement_date == now
    assert history.statement_balance == Decimal("1000.00")
    assert history.minimum_payment == Decimal("25.00")
    assert history.due_date == now


def test_statement_balance_history_validation():
    """Test statement balance history validation"""
    now = datetime.now(timezone.utc)

    # Test too many decimal places
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        StatementBalanceHistory(
            statement_date=now, statement_balance=Decimal("1000.123")
        )

    # Test valid decimal places
    valid_history = StatementBalanceHistory(
        statement_date=now, statement_balance=Decimal("1000.00")
    )
    assert valid_history.statement_balance == Decimal("1000.00")

    valid_history = StatementBalanceHistory(
        statement_date=now, statement_balance=Decimal("1000.5")
    )
    assert valid_history.statement_balance == Decimal("1000.5")

    valid_history = StatementBalanceHistory(
        statement_date=now, statement_balance=Decimal("1000")
    )
    assert valid_history.statement_balance == Decimal("1000")

    # Test negative minimum payment
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        StatementBalanceHistory(
            statement_date=now,
            statement_balance=Decimal("1000.00"),
            minimum_payment=Decimal("-25.00"),
        )


def test_statement_balance_history_invalid_dates():
    """Test invalid dates in statement balance history"""
    now = datetime.now(timezone.utc)
    naive_now = datetime.now()

    # Test naive statement date
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        StatementBalanceHistory(
            statement_date=naive_now, statement_balance=Decimal("1000.00"), due_date=now
        )

    # Test naive due date
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        StatementBalanceHistory(
            statement_date=now, statement_balance=Decimal("1000.00"), due_date=naive_now
        )

    # Test non-UTC timezone
    non_utc = datetime.now(ZoneInfo("America/New_York"))
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        StatementBalanceHistory(
            statement_date=non_utc, statement_balance=Decimal("1000.00"), due_date=now
        )


def test_money_field_type():
    """Test the MoneyDecimal type with annotated validation"""
    # Create an account with money fields to test the type validation
    account = AvailableCreditResponse(
        account_id=1,
        account_name="Test Credit Card",
        total_limit=Decimal("5000.00"),
        current_balance=Decimal("2500.00"),
        pending_transactions=Decimal("500.00"),
        adjusted_balance=Decimal("3000.00"),
        available_credit=Decimal("2000.00"),
    )

    # Verify all money fields have proper values
    assert account.total_limit == Decimal("5000.00")
    assert account.current_balance == Decimal("2500.00")
    assert account.pending_transactions == Decimal("500.00")
    assert account.adjusted_balance == Decimal("3000.00")
    assert account.available_credit == Decimal("2000.00")

    # Test validation error with too many decimal places
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        AvailableCreditResponse(
            account_id=1,
            account_name="Test Credit Card",
            total_limit=Decimal("5000.123"),  # Too many decimal places
            current_balance=Decimal("2500.00"),
            pending_transactions=Decimal("500.00"),
            adjusted_balance=Decimal("3000.00"),
            available_credit=Decimal("2000.00"),
        )

    # Test validation with gt constraint
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        AvailableCreditResponse(
            account_id=1,
            account_name="Test Credit Card",
            total_limit=Decimal("0.00"),  # Not greater than 0
            current_balance=Decimal("0.00"),
            pending_transactions=Decimal("0.00"),
            adjusted_balance=Decimal("0.00"),
            available_credit=Decimal("0.00"),
        )

    # Test validation with ge constraint
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        AvailableCreditResponse(
            account_id=1,
            account_name="Test Credit Card",
            total_limit=Decimal("5000.00"),
            current_balance=Decimal("2500.00"),
            pending_transactions=Decimal("500.00"),
            adjusted_balance=Decimal("3000.00"),
            available_credit=Decimal("-0.01"),  # Negative value violates ge=0
        )


def test_validate_account_type():
    """Test the validate_account_type function"""
    # Test with valid account types
    valid_types = [
        "checking",
        "savings",
        "credit",
        "payment_app",
        "bnpl",
        "ewa",
        "investment",
        "loan",
        "bill",
    ]

    for account_type in valid_types:
        result = validate_account_type(account_type)
        assert result == account_type

    # Test with invalid account type
    with pytest.raises(ValueError, match="Invalid account type"):
        validate_account_type("not_a_valid_type")
