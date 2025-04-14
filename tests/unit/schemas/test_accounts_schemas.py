"""
Unit tests for account schemas.

Tests the account schema validation and serialization,
including base account schemas and account type validation.
Implements testing for ADR-016 Account Type Expansion.
"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.schemas.accounts import (
    AccountBase,
    AccountInDB,
    AccountStatementHistoryResponse,
    AccountUpdate,
    AvailableCreditResponse,
    StatementBalanceHistory,
    validate_account_type,
    validate_credit_account_field,
)
from src.utils.datetime_utils import utc_now


def test_validate_account_type_function():
    """Test the validate_account_type function directly."""
    # Test with valid account types
    valid_types = ["checking", "savings", "credit", "payment_app", "bnpl", "ewa"]
    for account_type in valid_types:
        result = validate_account_type(account_type)
        assert result == account_type

    # Test with invalid account type
    with pytest.raises(ValueError):
        validate_account_type("invalid_type")


def test_account_update():
    """Test the AccountUpdate schema basic functionality."""
    # Test with valid account type
    update = AccountUpdate(
        account_type="checking",
    )
    assert update.account_type == "checking"

    # Test with invalid account type works at schema level
    # as validation was moved to service layer per code comment:
    # "Removed account_type validator to avoid conflicts with discriminated unions"
    update = AccountUpdate(
        account_type="invalid_type",
    )
    assert update.account_type == "invalid_type"


def test_account_base_schema():
    """Test the base schema for account data."""
    # Test with minimum required fields
    account = AccountBase(
        name="Test Account",
        account_type="checking",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
    )
    assert account.name == "Test Account"
    assert account.account_type == "checking"
    assert account.current_balance == Decimal("1000.00")
    assert account.available_balance == Decimal("1000.00")
    assert account.is_closed is False  # Default value
    assert account.currency == "USD"  # Default value

    # Test with all fields
    account = AccountBase(
        name="Full Account",
        account_type="checking",
        description="Primary checking account",
        current_balance=Decimal("1500.00"),
        available_balance=Decimal("1450.00"),
        institution="Test Bank",
        currency="EUR",
        is_closed=False,
        account_number="1234567890",
        url="https://example.com",
        logo_path="/path/to/logo.png",
    )
    assert account.name == "Full Account"
    assert account.description == "Primary checking account"
    assert account.institution == "Test Bank"
    assert account.currency == "EUR"
    assert account.account_number == "1234567890"
    assert account.url == "https://example.com"
    assert account.logo_path == "/path/to/logo.png"

    # Test validation of currency
    with pytest.raises(ValidationError):
        AccountBase(
            name="Invalid Currency",
            account_type="checking",
            current_balance=Decimal("1000.00"),
            available_balance=Decimal("1000.00"),
            currency="DOLLAR",  # Invalid currency (should be 3 characters)
        )

    # Note: In our architecture, it's not the base schema's responsibility to validate
    # account type-specific fields. That validation happens at the discriminated union level.
    # We're removing this test to align with our polymorphic design pattern.
    
    # To properly test account type validation, we should use the AccountCreateUnion
    # discriminated union type for validation, which is tested separately in 
    # tests/unit/schemas/account_types/test_account_type_unions.py


def test_validate_credit_account_field_function():
    """Test the validator for credit account specific fields."""
    # Create a validator for testing
    validator = validate_credit_account_field("test_field")

    # Define test validation info with credit account type
    class ValidationInfo:
        def __init__(self, account_type):
            self.data = {"account_type": account_type}

    # Test with credit account type and a value
    result = validator(Decimal("100.00"), ValidationInfo("credit"))
    assert result == Decimal("100.00")

    # Test with non-credit account type and a value
    with pytest.raises(ValueError):
        validator(Decimal("100.00"), ValidationInfo("checking"))

    # Test with None value (should be accepted regardless of account type)
    result = validator(None, ValidationInfo("checking"))
    assert result is None

    # Test with credit account type and None value
    result = validator(None, ValidationInfo("credit"))
    assert result is None


def test_account_in_db_schema():
    """Test the AccountInDB schema."""
    # Create a current datetime for testing
    now = utc_now()

    # Test with required fields
    account = AccountInDB(
        id=1,
        name="Test Account",
        account_type="checking",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
        created_at=now,
        updated_at=now,
    )
    assert account.id == 1
    assert account.name == "Test Account"
    assert account.account_type == "checking"
    assert account.created_at == now
    assert account.updated_at == now

    # Test with invalid id
    with pytest.raises(ValidationError):
        AccountInDB(
            id=0,  # Invalid id (must be > 0)
            name="Test Account",
            account_type="checking",
            current_balance=Decimal("1000.00"),
            available_balance=Decimal("1000.00"),
            created_at=now,
            updated_at=now,
        )


def test_statement_balance_history_schema():
    """Test the StatementBalanceHistory schema."""
    # Create a current datetime for testing
    now = utc_now()

    # Test with required fields
    history = StatementBalanceHistory(
        statement_date=now,
        statement_balance=Decimal("1000.00"),
    )
    assert history.statement_date == now
    assert history.statement_balance == Decimal("1000.00")
    assert history.minimum_payment is None
    assert history.due_date is None

    # Test with all fields
    due_date = utc_now()
    history = StatementBalanceHistory(
        statement_date=now,
        statement_balance=Decimal("1000.00"),
        minimum_payment=Decimal("25.00"),
        due_date=due_date,
    )
    assert history.statement_date == now
    assert history.statement_balance == Decimal("1000.00")
    assert history.minimum_payment == Decimal("25.00")
    assert history.due_date == due_date

    # Test validation of minimum payment
    with pytest.raises(ValidationError):
        StatementBalanceHistory(
            statement_date=now,
            statement_balance=Decimal("1000.00"),
            minimum_payment=Decimal("-25.00"),  # Invalid negative value
        )


def test_account_statement_history_response_schema():
    """Test the AccountStatementHistoryResponse schema."""
    # Create a current datetime for testing
    now = utc_now()

    # Create statement history entries for testing
    statement1 = StatementBalanceHistory(
        statement_date=now,
        statement_balance=Decimal("1000.00"),
        minimum_payment=Decimal("25.00"),
    )
    statement2 = StatementBalanceHistory(
        statement_date=utc_now(),
        statement_balance=Decimal("950.00"),
        minimum_payment=Decimal("25.00"),
    )

    # Test with required fields
    history_response = AccountStatementHistoryResponse(
        account_id=1,
        account_name="Test Account",
    )
    assert history_response.account_id == 1
    assert history_response.account_name == "Test Account"
    assert history_response.statement_history == []

    # Test with statement history
    history_response = AccountStatementHistoryResponse(
        account_id=1,
        account_name="Test Account",
        statement_history=[statement1, statement2],
    )
    assert history_response.account_id == 1
    assert history_response.account_name == "Test Account"
    assert len(history_response.statement_history) == 2
    assert history_response.statement_history[0].statement_balance == Decimal("1000.00")
    assert history_response.statement_history[1].statement_balance == Decimal("950.00")


def test_available_credit_response_schema():
    """Test the AvailableCreditResponse schema."""
    # Test with required fields
    credit_response = AvailableCreditResponse(
        account_id=1,
        account_name="Credit Card",
        total_limit=Decimal("5000.00"),
        current_balance=Decimal("1000.00"),
        pending_transactions=Decimal("200.00"),
        adjusted_balance=Decimal("1200.00"),
        available_credit=Decimal("3800.00"),
    )
    assert credit_response.account_id == 1
    assert credit_response.account_name == "Credit Card"
    assert credit_response.total_limit == Decimal("5000.00")
    assert credit_response.current_balance == Decimal("1000.00")
    assert credit_response.pending_transactions == Decimal("200.00")
    assert credit_response.adjusted_balance == Decimal("1200.00")
    assert credit_response.available_credit == Decimal("3800.00")

    # Test validation of total_limit
    with pytest.raises(ValidationError):
        AvailableCreditResponse(
            account_id=1,
            account_name="Credit Card",
            total_limit=Decimal("0.00"),  # Invalid (must be > 0)
            current_balance=Decimal("1000.00"),
            pending_transactions=Decimal("200.00"),
            adjusted_balance=Decimal("1200.00"),
            available_credit=Decimal("3800.00"),
        )

    # Test validation of available_credit
    with pytest.raises(ValidationError):
        AvailableCreditResponse(
            account_id=1,
            account_name="Credit Card",
            total_limit=Decimal("5000.00"),
            current_balance=Decimal("1000.00"),
            pending_transactions=Decimal("200.00"),
            adjusted_balance=Decimal("1200.00"),
            available_credit=Decimal("-100.00"),  # Invalid (must be >= 0)
        )
