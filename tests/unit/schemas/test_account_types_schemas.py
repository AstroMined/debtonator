"""
Unit tests for account type schemas.

Tests the account type schemas for validation and serialization
as part of ADR-016 Account Type Expansion and ADR-019 Banking Account Types Expansion.
"""

from decimal import Decimal

import pytest
from pydantic import ValidationError

from src.registry.account_types import account_type_registry
from src.schemas.account_types.banking.bnpl import BNPLAccountCreate
from src.schemas.account_types.banking.checking import (
    CheckingAccountCreate,
    CheckingAccountResponse,
)
from src.schemas.account_types.banking.credit import (
    CreditAccountCreate,
    CreditAccountResponse,
)
from src.schemas.account_types.banking.ewa import EWAAccountCreate
from src.schemas.account_types.banking.payment_app import PaymentAppAccountCreate
from src.schemas.account_types.banking.savings import (
    SavingsAccountCreate,
    SavingsAccountResponse,
)
from src.schemas.accounts import AccountCreate, AccountUpdate, validate_account_type
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


def test_account_type_registry():
    """Test account type registry lookup and validation."""
    # Verify registry contains expected types
    valid_types = [
        "checking",
        "savings",
        "credit",
        "payment_app",
        "bnpl",
        "ewa",
        "investment",
        "loan",
        "mortgage",
        "bill",
        "prepaid",
    ]

    for account_type in valid_types:
        assert account_type_registry.is_valid_account_type(account_type)

    # Test with invalid account type
    assert not account_type_registry.is_valid_account_type("invalid_type")

    # Test getting all types
    all_types = account_type_registry.get_all_types()
    assert len(all_types) >= len(valid_types)

    # Check structure of returned type info
    for type_info in all_types:
        assert "id" in type_info
        assert "name" in type_info
        assert "description" in type_info


def test_checking_account_create_schema():
    """Test the checking account create schema."""
    # Test with minimum required fields
    checking = CheckingAccountCreate(
        name="Basic Checking",
        account_type="checking",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
    )
    assert checking.name == "Basic Checking"
    assert checking.account_type == "checking"
    assert checking.current_balance == Decimal("1000.00")

    # Test with all fields
    checking = CheckingAccountCreate(
        name="Full Checking",
        account_type="checking",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
        institution="Test Bank",
        currency="USD",
        account_number="1234567890",
        routing_number="987654321",
        has_overdraft_protection=True,
        overdraft_limit=Decimal("500.00"),
        monthly_fee=Decimal("5.00"),
        interest_rate=Decimal("0.0025"),  # 0.25%
        iban="DE89370400440532013000",
        swift_bic="COBADEFFXXX",
        sort_code="12-34-56",
        branch_code="001",
        account_format="local",
    )
    assert checking.routing_number == "987654321"
    assert checking.has_overdraft_protection is True
    assert checking.overdraft_limit == Decimal("500.00")
    assert checking.monthly_fee == Decimal("5.00")
    assert checking.interest_rate == Decimal("0.0025")

    # Test validation of incorrect account type
    with pytest.raises(ValidationError, match="Value error at account_type"):
        CheckingAccountCreate(
            name="Invalid Type",
            account_type="savings",  # Wrong type
            current_balance=Decimal("1000.00"),
            available_balance=Decimal("1000.00"),
        )

    # Test validation of money decimals
    with pytest.raises(ValidationError):
        CheckingAccountCreate(
            name="Invalid Decimal",
            account_type="checking",
            current_balance=Decimal("1000.12345"),  # Too many decimal places
            available_balance=Decimal("1000.00"),
        )


def test_credit_account_create_schema():
    """Test the credit account create schema."""
    # Test with minimum required fields
    credit = CreditAccountCreate(
        name="Basic Credit Card",
        account_type="credit",
        current_balance=Decimal("500.00"),
        available_balance=Decimal("500.00"),
        credit_limit=Decimal("2000.00"),
    )
    assert credit.name == "Basic Credit Card"
    assert credit.account_type == "credit"
    assert credit.credit_limit == Decimal("2000.00")

    # Test with all fields
    statement_date = utc_now()
    credit = CreditAccountCreate(
        name="Full Credit Card",
        account_type="credit",
        current_balance=Decimal("500.00"),
        available_balance=Decimal("500.00"),
        institution="Test Bank",
        currency="USD",
        account_number="5432-1098-7654-3210",
        credit_limit=Decimal("3000.00"),
        statement_balance=Decimal("750.00"),
        statement_due_date=statement_date,
        minimum_payment=Decimal("35.00"),
        apr=Decimal("0.1999"),  # 19.99%
        annual_fee=Decimal("95.00"),
        rewards_program="Cash Back Plus",
        autopay_status="minimum",
        last_statement_date=statement_date,
    )
    assert credit.credit_limit == Decimal("3000.00")
    assert credit.statement_balance == Decimal("750.00")
    assert credit.minimum_payment == Decimal("35.00")
    assert credit.apr == Decimal("0.1999")
    assert credit.annual_fee == Decimal("95.00")
    assert credit.rewards_program == "Cash Back Plus"

    # Test validation of incorrect account type
    with pytest.raises(ValidationError, match="Value error at account_type"):
        CreditAccountCreate(
            name="Invalid Type",
            account_type="checking",  # Wrong type
            current_balance=Decimal("500.00"),
            available_balance=Decimal("500.00"),
            credit_limit=Decimal("2000.00"),
        )

    # Test validation of credit-specific field
    with pytest.raises(ValidationError, match="credit_limit"):
        CreditAccountCreate(
            name="Invalid Credit Limit",
            account_type="credit",
            current_balance=Decimal("500.00"),
            available_balance=Decimal("500.00"),
            # Missing required credit_limit
        )


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

    # Test with all fields
    savings = SavingsAccountCreate(
        name="Full Savings",
        account_type="savings",
        current_balance=Decimal("5000.00"),
        available_balance=Decimal("5000.00"),
        institution="Test Bank",
        currency="USD",
        account_number="9876543210",
        interest_rate=Decimal("0.0250"),  # 2.5%
        compound_frequency="daily",
        interest_earned_ytd=Decimal("25.50"),
        withdrawal_limit=6,
        minimum_balance=Decimal("500.00"),
    )
    assert savings.interest_rate == Decimal("0.0250")
    assert savings.compound_frequency == "daily"
    assert savings.interest_earned_ytd == Decimal("25.50")
    assert savings.withdrawal_limit == 6
    assert savings.minimum_balance == Decimal("500.00")

    # Test validation of incorrect account type
    with pytest.raises(ValidationError, match="Value error at account_type"):
        SavingsAccountCreate(
            name="Invalid Type",
            account_type="checking",  # Wrong type
            current_balance=Decimal("5000.00"),
            available_balance=Decimal("5000.00"),
        )


def test_payment_app_account_create_schema():
    """Test the payment app account create schema."""
    # Test with minimum required fields
    payment_app = PaymentAppAccountCreate(
        name="Basic Payment App",
        account_type="payment_app",
        current_balance=Decimal("200.00"),
        available_balance=Decimal("200.00"),
        platform="PayPal",
    )
    assert payment_app.name == "Basic Payment App"
    assert payment_app.account_type == "payment_app"
    assert payment_app.platform == "PayPal"

    # Test with all fields
    payment_app = PaymentAppAccountCreate(
        name="Full Payment App",
        account_type="payment_app",
        current_balance=Decimal("350.00"),
        available_balance=Decimal("350.00"),
        institution="PayPal, Inc.",
        currency="USD",
        account_number="user@example.com",
        platform="PayPal",
        has_debit_card=True,
        card_last_four="5678",
        linked_account_ids="1,2,3",
        supports_direct_deposit=True,
        supports_crypto=True,
    )
    assert payment_app.platform == "PayPal"
    assert payment_app.has_debit_card is True
    assert payment_app.card_last_four == "5678"
    assert payment_app.linked_account_ids == "1,2,3"
    assert payment_app.supports_direct_deposit is True
    assert payment_app.supports_crypto is True

    # Test validation of incorrect account type
    with pytest.raises(ValidationError, match="Value error at account_type"):
        PaymentAppAccountCreate(
            name="Invalid Type",
            account_type="checking",  # Wrong type
            current_balance=Decimal("200.00"),
            available_balance=Decimal("200.00"),
            platform="PayPal",
        )

    # Test validation of payment app-specific field
    with pytest.raises(ValidationError, match="platform"):
        PaymentAppAccountCreate(
            name="Invalid Platform",
            account_type="payment_app",
            current_balance=Decimal("200.00"),
            available_balance=Decimal("200.00"),
            # Missing required platform
        )


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


def test_ewa_account_create_schema():
    """Test the EWA account create schema."""
    # Test with minimum required fields
    ewa = EWAAccountCreate(
        name="Basic EWA",
        account_type="ewa",
        current_balance=Decimal("150.00"),
        available_balance=Decimal("150.00"),
        provider="DailyPay",
    )
    assert ewa.name == "Basic EWA"
    assert ewa.account_type == "ewa"
    assert ewa.provider == "DailyPay"

    # Test with all fields including dates
    period_start = utc_now()
    period_end = utc_now()
    payday = utc_now()

    ewa = EWAAccountCreate(
        name="Full EWA",
        account_type="ewa",
        current_balance=Decimal("250.00"),
        available_balance=Decimal("250.00"),
        institution="DailyPay, Inc.",
        currency="USD",
        account_number="EWA-12345",
        provider="DailyPay",
        max_advance_percentage=Decimal("0.50"),  # 50%
        per_transaction_fee=Decimal("2.99"),
        pay_period_start=period_start,
        pay_period_end=period_end,
        next_payday=payday,
    )
    assert ewa.provider == "DailyPay"
    assert ewa.max_advance_percentage == Decimal("0.50")
    assert ewa.per_transaction_fee == Decimal("2.99")
    assert ewa.pay_period_start == period_start
    assert ewa.pay_period_end == period_end
    assert ewa.next_payday == payday

    # Test validation of incorrect account type
    with pytest.raises(ValidationError, match="Value error at account_type"):
        EWAAccountCreate(
            name="Invalid Type",
            account_type="checking",  # Wrong type
            current_balance=Decimal("150.00"),
            available_balance=Decimal("150.00"),
            provider="DailyPay",
        )

    # Test validation of EWA-specific field
    with pytest.raises(ValidationError, match="provider"):
        EWAAccountCreate(
            name="Invalid Provider",
            account_type="ewa",
            current_balance=Decimal("150.00"),
            available_balance=Decimal("150.00"),
            # Missing required provider
        )


def test_response_schemas():
    """Test all account type response schemas."""
    now = utc_now()

    # Test CheckingAccountResponse
    checking_response = CheckingAccountResponse(
        id=1,
        name="Checking Response",
        account_type="checking",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
        routing_number="123456789",
        has_overdraft_protection=True,
        overdraft_limit=Decimal("500.00"),
        created_at=now,
        updated_at=now,
    )
    assert checking_response.id == 1
    assert checking_response.name == "Checking Response"
    assert checking_response.account_type == "checking"
    assert checking_response.routing_number == "123456789"
    assert checking_response.has_overdraft_protection is True
    assert checking_response.created_at == now

    # Test CreditAccountResponse
    credit_response = CreditAccountResponse(
        id=2,
        name="Credit Response",
        account_type="credit",
        current_balance=Decimal("500.00"),
        available_balance=Decimal("500.00"),
        credit_limit=Decimal("2000.00"),
        apr=Decimal("0.1499"),
        created_at=now,
        updated_at=now,
    )
    assert credit_response.id == 2
    assert credit_response.name == "Credit Response"
    assert credit_response.account_type == "credit"
    assert credit_response.credit_limit == Decimal("2000.00")
    assert credit_response.apr == Decimal("0.1499")
    assert credit_response.created_at == now

    # Test SavingsAccountResponse
    savings_response = SavingsAccountResponse(
        id=3,
        name="Savings Response",
        account_type="savings",
        current_balance=Decimal("5000.00"),
        available_balance=Decimal("5000.00"),
        interest_rate=Decimal("0.0250"),
        compound_frequency="daily",
        created_at=now,
        updated_at=now,
    )
    assert savings_response.id == 3
    assert savings_response.name == "Savings Response"
    assert savings_response.account_type == "savings"
    assert savings_response.interest_rate == Decimal("0.0250")
    assert savings_response.compound_frequency == "daily"
    assert savings_response.created_at == now


def test_account_create_polymorphic_validation():
    """Test the base AccountCreate schema with account types."""
    # Test with valid account type
    account = AccountCreate(
        name="Basic Account",
        account_type="checking",
        current_balance=Decimal("1000.00"),
        available_balance=Decimal("1000.00"),
    )
    assert account.name == "Basic Account"
    assert account.account_type == "checking"

    # Test with invalid account type
    with pytest.raises(ValueError, match="Invalid account type"):
        AccountCreate(
            name="Invalid Account",
            account_type="invalid_type",
            current_balance=Decimal("1000.00"),
            available_balance=Decimal("1000.00"),
        )


def test_account_update_polymorphic_validation():
    """Test the AccountUpdate schema with account types."""
    # Test with valid account type
    update = AccountUpdate(
        account_type="checking",
    )
    assert update.account_type == "checking"

    # Test with invalid account type
    with pytest.raises(ValueError, match="Invalid account type"):
        AccountUpdate(
            account_type="invalid_type",
        )
