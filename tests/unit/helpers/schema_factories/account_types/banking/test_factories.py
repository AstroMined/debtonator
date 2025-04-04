"""
Unit tests for banking account type schema factories.

Tests ensure that schema factories produce valid schema instances
that pass validation.
"""

import pytest
from decimal import Decimal
from datetime import datetime, timedelta, timezone

from src.schemas.account_types.banking.checking import (
    CheckingAccountCreate,
    CheckingAccountResponse,
)
from src.schemas.account_types.banking.savings import (
    SavingsAccountCreate,
    SavingsAccountResponse,
)
from src.schemas.account_types.banking.credit import (
    CreditAccountCreate,
    CreditAccountResponse,
)
from src.schemas.account_types.banking.payment_app import (
    PaymentAppAccountCreate,
    PaymentAppAccountResponse,
)
from src.schemas.account_types.banking.bnpl import (
    BNPLAccountCreate,
    BNPLAccountResponse,
)
from src.schemas.account_types.banking.ewa import (
    EWAAccountCreate,
    EWAAccountResponse,
)

from tests.helpers.schema_factories.account_types.banking.checking import (
    create_checking_account_schema,
    create_checking_account_response_schema,
)
from tests.helpers.schema_factories.account_types.banking.savings import (
    create_savings_account_schema,
    create_savings_account_response_schema,
)
from tests.helpers.schema_factories.account_types.banking.credit import (
    create_credit_account_schema,
    create_credit_account_response_schema,
)
from tests.helpers.schema_factories.account_types.banking.payment_app import (
    create_payment_app_account_schema,
    create_payment_app_account_response_schema,
)
from tests.helpers.schema_factories.account_types.banking.bnpl import (
    create_bnpl_account_schema,
    create_bnpl_account_response_schema,
)
from tests.helpers.schema_factories.account_types.banking.ewa import (
    create_ewa_account_schema,
    create_ewa_account_response_schema,
)


class TestCheckingAccountFactories:
    """Tests for CheckingAccount schema factories."""

    def test_create_checking_account_schema(self):
        """Test creating a CheckingAccountCreate schema."""
        schema = create_checking_account_schema()
        assert isinstance(schema, CheckingAccountCreate)
        assert schema.account_type == "checking"
        assert schema.name == "Test Checking Account"
        assert schema.institution == "Test Bank"
        assert schema.routing_number == "123456789"
        assert schema.has_overdraft_protection is False
        assert schema.account_format == "local"

    def test_create_checking_account_schema_with_overdraft(self):
        """Test creating a CheckingAccountCreate schema with overdraft protection."""
        schema = create_checking_account_schema(
            has_overdraft_protection=True,
            overdraft_limit=Decimal("200.00"),
        )
        assert schema.has_overdraft_protection is True
        assert schema.overdraft_limit == Decimal("200.00")

    def test_create_checking_account_schema_with_international(self):
        """Test creating a CheckingAccountCreate schema with international fields."""
        schema = create_checking_account_schema(
            iban="DE89370400440532013000",
            swift_bic="DEUTDEFF",
            sort_code="123456",
            branch_code="12345",
            account_format="iban",
        )
        assert schema.iban == "DE89370400440532013000"
        assert schema.swift_bic == "DEUTDEFF"
        assert schema.sort_code == "123456"
        assert schema.branch_code == "12345"
        assert schema.account_format == "iban"

    def test_create_checking_account_response_schema(self):
        """Test creating a CheckingAccountResponse schema."""
        now = datetime.now(timezone.utc)
        schema = create_checking_account_response_schema(
            id=123,
            created_at=now,
            updated_at=now,
        )
        assert isinstance(schema, CheckingAccountResponse)
        assert schema.id == 123
        assert schema.account_type == "checking"
        assert schema.created_at == now
        assert schema.updated_at == now


class TestSavingsAccountFactories:
    """Tests for SavingsAccount schema factories."""

    def test_create_savings_account_schema(self):
        """Test creating a SavingsAccountCreate schema."""
        schema = create_savings_account_schema()
        assert isinstance(schema, SavingsAccountCreate)
        assert schema.account_type == "savings"
        assert schema.name == "Test Savings Account"
        assert schema.institution == "Test Bank"
        assert schema.interest_rate == Decimal("2.0")
        assert schema.compound_frequency == "monthly"
        assert schema.withdrawal_limit == 6
        assert schema.minimum_balance == Decimal("100.00")

    def test_create_savings_account_schema_with_custom_values(self):
        """Test creating a SavingsAccountCreate schema with custom values."""
        schema = create_savings_account_schema(
            name="High-Yield Savings",
            interest_rate=Decimal("3.5"),
            compound_frequency="daily",
            withdrawal_limit=3,
            minimum_balance=Decimal("500.00"),
            interest_earned_ytd=Decimal("75.25"),
        )
        assert schema.name == "High-Yield Savings"
        assert schema.interest_rate == Decimal("3.5")
        assert schema.compound_frequency == "daily"
        assert schema.withdrawal_limit == 3
        assert schema.minimum_balance == Decimal("500.00")
        assert schema.interest_earned_ytd == Decimal("75.25")

    def test_create_savings_account_response_schema(self):
        """Test creating a SavingsAccountResponse schema."""
        now = datetime.now(timezone.utc)
        schema = create_savings_account_response_schema(
            id=456,
            created_at=now,
            updated_at=now,
        )
        assert isinstance(schema, SavingsAccountResponse)
        assert schema.id == 456
        assert schema.account_type == "savings"
        assert schema.created_at == now
        assert schema.updated_at == now


class TestCreditAccountFactories:
    """Tests for CreditAccount schema factories."""

    def test_create_credit_account_schema(self):
        """Test creating a CreditAccountCreate schema."""
        schema = create_credit_account_schema()
        assert isinstance(schema, CreditAccountCreate)
        assert schema.account_type == "credit"
        assert schema.name == "Test Credit Card"
        assert schema.institution == "Test Bank"
        assert schema.credit_limit == Decimal("5000.00")
        assert schema.current_balance < 0  # Credit accounts have negative balances
        assert schema.statement_balance is not None
        assert schema.statement_due_date is not None
        assert schema.apr == Decimal("15.99")

    def test_create_credit_account_schema_with_custom_values(self):
        """Test creating a CreditAccountCreate schema with custom values."""
        schema = create_credit_account_schema(
            name="Rewards Card",
            credit_limit=Decimal("10000.00"),
            current_balance=Decimal("-2500.00"),
            statement_balance=Decimal("2500.00"),
            minimum_payment=Decimal("50.00"),
            apr=Decimal("18.99"),
            annual_fee=Decimal("95.00"),
            rewards_program="Cash Back",
            autopay_status="minimum",
        )
        assert schema.name == "Rewards Card"
        assert schema.credit_limit == Decimal("10000.00")
        assert schema.current_balance == Decimal("-2500.00")
        assert schema.statement_balance == Decimal("2500.00")
        assert schema.minimum_payment == Decimal("50.00")
        assert schema.apr == Decimal("18.99")
        assert schema.annual_fee == Decimal("95.00")
        assert schema.rewards_program == "Cash Back"
        assert schema.autopay_status == "minimum"

    def test_create_credit_account_response_schema(self):
        """Test creating a CreditAccountResponse schema."""
        now = datetime.now(timezone.utc)
        schema = create_credit_account_response_schema(
            id=789,
            created_at=now,
            updated_at=now,
        )
        assert isinstance(schema, CreditAccountResponse)
        assert schema.id == 789
        assert schema.account_type == "credit"
        assert schema.created_at == now
        assert schema.updated_at == now


class TestPaymentAppAccountFactories:
    """Tests for PaymentAppAccount schema factories."""

    def test_create_payment_app_account_schema(self):
        """Test creating a PaymentAppAccountCreate schema."""
        schema = create_payment_app_account_schema()
        assert isinstance(schema, PaymentAppAccountCreate)
        assert schema.account_type == "payment_app"
        assert schema.name == "Test Payment App"
        assert schema.institution == "PayPal"
        assert schema.platform == "PayPal"
        assert schema.has_debit_card is False
        assert schema.supports_direct_deposit is True
        assert schema.supports_crypto is False

    def test_create_payment_app_account_schema_with_debit_card(self):
        """Test creating a PaymentAppAccountCreate schema with debit card."""
        schema = create_payment_app_account_schema(
            has_debit_card=True,
            card_last_four="4321",
        )
        assert schema.has_debit_card is True
        assert schema.card_last_four == "4321"

    def test_create_payment_app_account_schema_with_linked_accounts(self):
        """Test creating a PaymentAppAccountCreate schema with linked accounts."""
        schema = create_payment_app_account_schema(
            platform="Venmo",
            linked_account_ids="123,456,789",
            supports_crypto=True,
        )
        assert schema.platform == "Venmo"
        assert schema.linked_account_ids == "123,456,789"
        assert schema.supports_crypto is True

    def test_create_payment_app_account_response_schema(self):
        """Test creating a PaymentAppAccountResponse schema."""
        now = datetime.now(timezone.utc)
        schema = create_payment_app_account_response_schema(
            id=101,
            created_at=now,
            updated_at=now,
        )
        assert isinstance(schema, PaymentAppAccountResponse)
        assert schema.id == 101
        assert schema.account_type == "payment_app"
        assert schema.created_at == now
        assert schema.updated_at == now


class TestBNPLAccountFactories:
    """Tests for BNPLAccount schema factories."""

    def test_create_bnpl_account_schema(self):
        """Test creating a BNPLAccountCreate schema."""
        schema = create_bnpl_account_schema()
        assert isinstance(schema, BNPLAccountCreate)
        assert schema.account_type == "bnpl"
        assert schema.name == "Test BNPL Account"
        assert schema.institution == "Affirm"
        assert schema.bnpl_provider == "Affirm"
        assert schema.original_amount == Decimal("400.00")
        assert schema.installment_count == 4
        assert schema.installments_paid == 0
        assert schema.installment_amount == Decimal("100.00")
        assert schema.payment_frequency == "biweekly"
        assert schema.next_payment_date is not None

    def test_create_bnpl_account_schema_with_custom_values(self):
        """Test creating a BNPLAccountCreate schema with custom values."""
        schema = create_bnpl_account_schema(
            name="Laptop Purchase",
            original_amount=Decimal("1200.00"),
            installment_count=6,
            installments_paid=2,
            installment_amount=Decimal("200.00"),
            payment_frequency="monthly",
            promotion_info="0% interest for 6 months",
            late_fee=Decimal("10.00"),
            bnpl_provider="Klarna",
        )
        assert schema.name == "Laptop Purchase"
        assert schema.original_amount == Decimal("1200.00")
        assert schema.installment_count == 6
        assert schema.installments_paid == 2
        assert schema.installment_amount == Decimal("200.00")
        assert schema.payment_frequency == "monthly"
        assert schema.promotion_info == "0% interest for 6 months"
        assert schema.late_fee == Decimal("10.00")
        assert schema.bnpl_provider == "Klarna"
        assert schema.current_balance == Decimal("800.00")  # 4 remaining installments

    def test_create_bnpl_account_response_schema(self):
        """Test creating a BNPLAccountResponse schema."""
        now = datetime.now(timezone.utc)
        schema = create_bnpl_account_response_schema(
            id=202,
            created_at=now,
            updated_at=now,
        )
        assert isinstance(schema, BNPLAccountResponse)
        assert schema.id == 202
        assert schema.account_type == "bnpl"
        assert schema.created_at == now
        assert schema.updated_at == now


class TestEWAAccountFactories:
    """Tests for EWAAccount schema factories."""

    def test_create_ewa_account_schema(self):
        """Test creating an EWAAccountCreate schema."""
        schema = create_ewa_account_schema()
        assert isinstance(schema, EWAAccountCreate)
        assert schema.account_type == "ewa"
        assert schema.name == "Test EWA Account"
        assert schema.institution == "DailyPay"
        assert schema.provider == "DailyPay"
        assert schema.max_advance_percentage == Decimal("50.0")
        assert schema.per_transaction_fee == Decimal("1.99")
        assert schema.pay_period_start is not None
        assert schema.pay_period_end is not None
        assert schema.next_payday is not None
        assert schema.pay_period_end > schema.pay_period_start
        assert schema.next_payday > schema.pay_period_end

    def test_create_ewa_account_schema_with_custom_values(self):
        """Test creating an EWAAccountCreate schema with custom values."""
        now = datetime.now(timezone.utc)
        pay_period_start = now - timedelta(days=10)
        pay_period_end = now + timedelta(days=4)
        next_payday = pay_period_end + timedelta(days=2)
        
        schema = create_ewa_account_schema(
            name="Early Pay Access",
            provider="Payactiv",
            max_advance_percentage=Decimal("40.0"),
            per_transaction_fee=Decimal("2.50"),
            pay_period_start=pay_period_start,
            pay_period_end=pay_period_end,
            next_payday=next_payday,
        )
        assert schema.name == "Early Pay Access"
        assert schema.provider == "Payactiv"
        assert schema.max_advance_percentage == Decimal("40.0")
        assert schema.per_transaction_fee == Decimal("2.50")
        assert schema.pay_period_start == pay_period_start
        assert schema.pay_period_end == pay_period_end
        assert schema.next_payday == next_payday

    def test_create_ewa_account_response_schema(self):
        """Test creating an EWAAccountResponse schema."""
        now = datetime.now(timezone.utc)
        schema = create_ewa_account_response_schema(
            id=303,
            created_at=now,
            updated_at=now,
        )
        assert isinstance(schema, EWAAccountResponse)
        assert schema.id == 303
        assert schema.account_type == "ewa"
        assert schema.created_at == now
        assert schema.updated_at == now
