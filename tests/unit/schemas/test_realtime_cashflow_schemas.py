from datetime import datetime, timedelta, timezone
from decimal import Decimal
from zoneinfo import ZoneInfo  # Only needed for non-UTC timezone tests

import pytest
from pydantic import ValidationError

from src.schemas.realtime_cashflow import (AccountBalance, AccountType,
                                           RealtimeCashflow,
                                           RealtimeCashflowResponse)


# Test valid object creation
def test_account_balance_valid():
    """Test valid account balance schema creation"""
    # Test checking account
    checking_account = AccountBalance(
        account_id=1,
        name="Main Checking",
        type=AccountType.CHECKING,
        current_balance=Decimal("1000.00"),
    )

    assert checking_account.account_id == 1
    assert checking_account.name == "Main Checking"
    assert checking_account.type == AccountType.CHECKING
    assert checking_account.current_balance == Decimal("1000.00")
    assert checking_account.available_credit is None
    assert checking_account.total_limit is None

    # Test credit account
    credit_account = AccountBalance(
        account_id=2,
        name="Credit Card",
        type=AccountType.CREDIT,
        current_balance=Decimal("-500.00"),
        available_credit=Decimal("4500.00"),
        total_limit=Decimal("5000.00"),
    )

    assert credit_account.account_id == 2
    assert credit_account.name == "Credit Card"
    assert credit_account.type == AccountType.CREDIT
    assert credit_account.current_balance == Decimal("-500.00")
    assert credit_account.available_credit == Decimal("4500.00")
    assert credit_account.total_limit == Decimal("5000.00")


def test_realtime_cashflow_valid():
    """Test valid realtime cashflow schema creation"""
    now = datetime.now(timezone.utc)
    next_week = now + timedelta(days=7)

    checking_account = AccountBalance(
        account_id=1,
        name="Main Checking",
        type=AccountType.CHECKING,
        current_balance=Decimal("1000.00"),
    )

    credit_account = AccountBalance(
        account_id=2,
        name="Credit Card",
        type=AccountType.CREDIT,
        current_balance=Decimal("-500.00"),
        available_credit=Decimal("4500.00"),
        total_limit=Decimal("5000.00"),
    )

    cashflow = RealtimeCashflow(
        timestamp=now,
        account_balances=[checking_account, credit_account],
        total_available_funds=Decimal("1000.00"),
        total_available_credit=Decimal("4500.00"),
        total_liabilities_due=Decimal("500.00"),
        net_position=Decimal("500.00"),  # 1000 - 500
        next_bill_due=next_week,
        days_until_next_bill=7,
        minimum_balance_required=Decimal("200.00"),
        projected_deficit=Decimal("-100.00"),
    )

    assert cashflow.timestamp == now
    assert len(cashflow.account_balances) == 2
    assert cashflow.total_available_funds == Decimal("1000.00")
    assert cashflow.total_available_credit == Decimal("4500.00")
    assert cashflow.total_liabilities_due == Decimal("500.00")
    assert cashflow.net_position == Decimal("500.00")
    assert cashflow.next_bill_due == next_week
    assert cashflow.days_until_next_bill == 7
    assert cashflow.minimum_balance_required == Decimal("200.00")
    assert cashflow.projected_deficit == Decimal("-100.00")


def test_realtime_cashflow_default_values():
    """Test realtime cashflow with default values"""
    before = datetime.now(timezone.utc)

    checking_account = AccountBalance(
        account_id=1,
        name="Main Checking",
        type=AccountType.CHECKING,
        current_balance=Decimal("1000.00"),
    )

    cashflow = RealtimeCashflow(
        account_balances=[checking_account],
        total_available_funds=Decimal("1000.00"),
        total_available_credit=Decimal("0.00"),
        total_liabilities_due=Decimal("0.00"),
        net_position=Decimal("1000.00"),
        minimum_balance_required=Decimal("0.00"),
    )

    after = datetime.now(timezone.utc)

    assert before <= cashflow.timestamp <= after
    assert len(cashflow.account_balances) == 1
    assert cashflow.next_bill_due is None
    assert cashflow.days_until_next_bill is None
    assert cashflow.projected_deficit is None


def test_realtime_cashflow_response_valid():
    """Test valid realtime cashflow response schema creation"""
    now = datetime.now(timezone.utc)

    checking_account = AccountBalance(
        account_id=1,
        name="Main Checking",
        type=AccountType.CHECKING,
        current_balance=Decimal("1000.00"),
    )

    cashflow = RealtimeCashflow(
        timestamp=now,
        account_balances=[checking_account],
        total_available_funds=Decimal("1000.00"),
        total_available_credit=Decimal("0.00"),
        total_liabilities_due=Decimal("0.00"),
        net_position=Decimal("1000.00"),
        minimum_balance_required=Decimal("200.00"),
    )

    response = RealtimeCashflowResponse(data=cashflow, last_updated=now)

    assert response.data == cashflow
    assert response.last_updated == now


def test_realtime_cashflow_response_default_values():
    """Test realtime cashflow response with default values"""
    before = datetime.now(timezone.utc)

    checking_account = AccountBalance(
        account_id=1,
        name="Main Checking",
        type=AccountType.CHECKING,
        current_balance=Decimal("1000.00"),
    )

    cashflow = RealtimeCashflow(
        account_balances=[checking_account],
        total_available_funds=Decimal("1000.00"),
        total_available_credit=Decimal("0.00"),
        total_liabilities_due=Decimal("0.00"),
        net_position=Decimal("1000.00"),
        minimum_balance_required=Decimal("200.00"),
    )

    response = RealtimeCashflowResponse(data=cashflow)

    after = datetime.now(timezone.utc)

    assert response.data == cashflow
    assert before <= response.last_updated <= after


# Test field validations
def test_enum_validation():
    """Test account type enum validation"""
    # Test invalid account type
    with pytest.raises(
        ValidationError, match="Input should be 'checking', 'savings' or 'credit'"
    ):
        AccountBalance(
            account_id=1,
            name="Invalid Account",
            type="invalid",  # Invalid value
            current_balance=Decimal("1000.00"),
        )


def test_credit_fields_validation():
    """Test credit account fields validation"""
    # Test missing available_credit
    with pytest.raises(ValidationError, match="Field is required for credit accounts"):
        AccountBalance(
            account_id=1,
            name="Credit Card",
            type=AccountType.CREDIT,
            current_balance=Decimal("-500.00"),
            # Missing available_credit
            total_limit=Decimal("5000.00"),
        )

    # Test missing total_limit
    with pytest.raises(ValidationError, match="Field is required for credit accounts"):
        AccountBalance(
            account_id=1,
            name="Credit Card",
            type=AccountType.CREDIT,
            current_balance=Decimal("-500.00"),
            available_credit=Decimal("4500.00"),
            # Missing total_limit
        )


def test_positive_fields_validation():
    """Test positive value validation"""
    # Test account_id <= 0
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        AccountBalance(
            account_id=0,  # Invalid value
            name="Main Checking",
            type=AccountType.CHECKING,
            current_balance=Decimal("1000.00"),
        )

    # Test negative available_credit
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        AccountBalance(
            account_id=1,
            name="Credit Card",
            type=AccountType.CREDIT,
            current_balance=Decimal("-500.00"),
            available_credit=Decimal("-1.00"),  # Invalid value
            total_limit=Decimal("5000.00"),
        )

    # Test total_limit <= 0
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        AccountBalance(
            account_id=1,
            name="Credit Card",
            type=AccountType.CREDIT,
            current_balance=Decimal("-500.00"),
            available_credit=Decimal("4500.00"),
            total_limit=Decimal("0.00"),  # Invalid value
        )

    # Test negative total_available_credit
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        RealtimeCashflow(
            account_balances=[
                AccountBalance(
                    account_id=1,
                    name="Main Checking",
                    type=AccountType.CHECKING,
                    current_balance=Decimal("1000.00"),
                )
            ],
            total_available_funds=Decimal("1000.00"),
            total_available_credit=Decimal("-1.00"),  # Invalid value
            total_liabilities_due=Decimal("0.00"),
            net_position=Decimal("1000.00"),
            minimum_balance_required=Decimal("200.00"),
        )

    # Test negative total_liabilities_due
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        RealtimeCashflow(
            account_balances=[
                AccountBalance(
                    account_id=1,
                    name="Main Checking",
                    type=AccountType.CHECKING,
                    current_balance=Decimal("1000.00"),
                )
            ],
            total_available_funds=Decimal("1000.00"),
            total_available_credit=Decimal("0.00"),
            total_liabilities_due=Decimal("-1.00"),  # Invalid value
            net_position=Decimal("1000.00"),
            minimum_balance_required=Decimal("200.00"),
        )

    # Test negative days_until_next_bill
    with pytest.raises(
        ValidationError, match="Input should be greater than or equal to 0"
    ):
        RealtimeCashflow(
            account_balances=[
                AccountBalance(
                    account_id=1,
                    name="Main Checking",
                    type=AccountType.CHECKING,
                    current_balance=Decimal("1000.00"),
                )
            ],
            total_available_funds=Decimal("1000.00"),
            total_available_credit=Decimal("0.00"),
            total_liabilities_due=Decimal("0.00"),
            net_position=Decimal("1000.00"),
            days_until_next_bill=-1,  # Invalid value
            minimum_balance_required=Decimal("200.00"),
        )


def test_decimal_precision():
    """Test decimal precision validation"""
    # Test too many decimal places in current_balance
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        AccountBalance(
            account_id=1,
            name="Main Checking",
            type=AccountType.CHECKING,
            current_balance=Decimal("1000.123"),  # Invalid precision
        )

    # Test too many decimal places in available_credit
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        AccountBalance(
            account_id=1,
            name="Credit Card",
            type=AccountType.CREDIT,
            current_balance=Decimal("-500.00"),
            available_credit=Decimal("4500.123"),  # Invalid precision
            total_limit=Decimal("5000.00"),
        )

    # Test too many decimal places in total_available_funds
    with pytest.raises(ValidationError, match="Input should be a multiple of 0.01"):
        RealtimeCashflow(
            account_balances=[
                AccountBalance(
                    account_id=1,
                    name="Main Checking",
                    type=AccountType.CHECKING,
                    current_balance=Decimal("1000.00"),
                )
            ],
            total_available_funds=Decimal("1000.123"),  # Invalid precision
            total_available_credit=Decimal("0.00"),
            total_liabilities_due=Decimal("0.00"),
            net_position=Decimal("1000.00"),
            minimum_balance_required=Decimal("200.00"),
        )


def test_string_length_validation():
    """Test string length validation"""
    # Test empty name
    with pytest.raises(
        ValidationError, match="String should have at least 1 character"
    ):
        AccountBalance(
            account_id=1,
            name="",  # Empty string
            type=AccountType.CHECKING,
            current_balance=Decimal("1000.00"),
        )

    # Test name too long
    with pytest.raises(
        ValidationError, match="String should have at most 255 characters"
    ):
        AccountBalance(
            account_id=1,
            name="X" * 256,  # Too long
            type=AccountType.CHECKING,
            current_balance=Decimal("1000.00"),
        )


def test_duplicate_account_validation():
    """Test duplicate account validation"""
    # Test duplicate account IDs
    with pytest.raises(
        ValidationError, match="Duplicate account IDs found in account_balances"
    ):
        RealtimeCashflow(
            account_balances=[
                AccountBalance(
                    account_id=1,
                    name="Checking 1",
                    type=AccountType.CHECKING,
                    current_balance=Decimal("1000.00"),
                ),
                AccountBalance(
                    account_id=1,  # Duplicate ID
                    name="Checking 2",
                    type=AccountType.CHECKING,
                    current_balance=Decimal("2000.00"),
                ),
            ],
            total_available_funds=Decimal("3000.00"),
            total_available_credit=Decimal("0.00"),
            total_liabilities_due=Decimal("0.00"),
            net_position=Decimal("3000.00"),
            minimum_balance_required=Decimal("200.00"),
        )


def test_net_position_validation():
    """Test net position calculation validation"""
    # Test incorrect net position
    with pytest.raises(
        ValidationError,
        match="net_position must equal total_available_funds - total_liabilities_due",
    ):
        RealtimeCashflow(
            account_balances=[
                AccountBalance(
                    account_id=1,
                    name="Main Checking",
                    type=AccountType.CHECKING,
                    current_balance=Decimal("1000.00"),
                )
            ],
            total_available_funds=Decimal("1000.00"),
            total_available_credit=Decimal("0.00"),
            total_liabilities_due=Decimal("200.00"),
            net_position=Decimal("900.00"),  # Should be 800.00
            minimum_balance_required=Decimal("200.00"),
        )

    # Test valid net position with small (but valid) rounding difference
    cashflow = RealtimeCashflow(
        account_balances=[
            AccountBalance(
                account_id=1,
                name="Main Checking",
                type=AccountType.CHECKING,
                current_balance=Decimal("1000.00"),
            )
        ],
        total_available_funds=Decimal("1000.00"),
        total_available_credit=Decimal("0.00"),
        total_liabilities_due=Decimal("200.00"),
        net_position=Decimal("800.00"),  # Exact difference (no rounding needed)
        minimum_balance_required=Decimal("200.00"),
    )
    # Verify the net position is exactly 800.00
    assert cashflow.net_position == Decimal("800.00")


def test_min_items_validation():
    """Test minimum items validation"""
    # Test empty account_balances
    with pytest.raises(ValidationError, match="List should have at least 1 item"):
        RealtimeCashflow(
            account_balances=[],  # Empty list
            total_available_funds=Decimal("0.00"),
            total_available_credit=Decimal("0.00"),
            total_liabilities_due=Decimal("0.00"),
            net_position=Decimal("0.00"),
            minimum_balance_required=Decimal("0.00"),
        )


# Test datetime UTC validation
def test_datetime_utc_validation():
    """Test datetime UTC validation per ADR-011"""
    checking_account = AccountBalance(
        account_id=1,
        name="Main Checking",
        type=AccountType.CHECKING,
        current_balance=Decimal("1000.00"),
    )

    # Test naive datetime in timestamp
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        RealtimeCashflow(
            timestamp=datetime.now(),  # Naive datetime
            account_balances=[checking_account],
            total_available_funds=Decimal("1000.00"),
            total_available_credit=Decimal("0.00"),
            total_liabilities_due=Decimal("0.00"),
            net_position=Decimal("1000.00"),
            minimum_balance_required=Decimal("200.00"),
        )

    # Test non-UTC timezone in timestamp
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        RealtimeCashflow(
            timestamp=datetime.now(ZoneInfo("America/New_York")),  # Non-UTC timezone
            account_balances=[checking_account],
            total_available_funds=Decimal("1000.00"),
            total_available_credit=Decimal("0.00"),
            total_liabilities_due=Decimal("0.00"),
            net_position=Decimal("1000.00"),
            minimum_balance_required=Decimal("200.00"),
        )

    # Test naive datetime in next_bill_due
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        RealtimeCashflow(
            account_balances=[checking_account],
            total_available_funds=Decimal("1000.00"),
            total_available_credit=Decimal("0.00"),
            total_liabilities_due=Decimal("0.00"),
            net_position=Decimal("1000.00"),
            next_bill_due=datetime.now(),  # Naive datetime
            minimum_balance_required=Decimal("200.00"),
        )

    # Test non-UTC timezone in next_bill_due
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        RealtimeCashflow(
            account_balances=[checking_account],
            total_available_funds=Decimal("1000.00"),
            total_available_credit=Decimal("0.00"),
            total_liabilities_due=Decimal("0.00"),
            net_position=Decimal("1000.00"),
            next_bill_due=datetime.now(
                ZoneInfo("America/New_York")
            ),  # Non-UTC timezone
            minimum_balance_required=Decimal("200.00"),
        )

    # Test naive datetime in last_updated
    cashflow = RealtimeCashflow(
        account_balances=[checking_account],
        total_available_funds=Decimal("1000.00"),
        total_available_credit=Decimal("0.00"),
        total_liabilities_due=Decimal("0.00"),
        net_position=Decimal("1000.00"),
        minimum_balance_required=Decimal("200.00"),
    )

    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        RealtimeCashflowResponse(
            data=cashflow, last_updated=datetime.now()  # Naive datetime
        )

    # Test non-UTC timezone in last_updated
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        RealtimeCashflowResponse(
            data=cashflow,
            last_updated=datetime.now(ZoneInfo("America/New_York")),  # Non-UTC timezone
        )


def test_required_fields():
    """Test required fields validation"""
    # Missing required fields in AccountBalance
    with pytest.raises(ValidationError, match="Field required"):
        AccountBalance(
            name="Main Checking",
            type=AccountType.CHECKING,
            current_balance=Decimal("1000.00"),
        )

    with pytest.raises(ValidationError, match="Field required"):
        AccountBalance(
            account_id=1, type=AccountType.CHECKING, current_balance=Decimal("1000.00")
        )

    with pytest.raises(ValidationError, match="Field required"):
        AccountBalance(
            account_id=1, name="Main Checking", current_balance=Decimal("1000.00")
        )

    with pytest.raises(ValidationError, match="Field required"):
        AccountBalance(account_id=1, name="Main Checking", type=AccountType.CHECKING)

    # Missing required fields in RealtimeCashflow
    checking_account = AccountBalance(
        account_id=1,
        name="Main Checking",
        type=AccountType.CHECKING,
        current_balance=Decimal("1000.00"),
    )

    with pytest.raises(ValidationError, match="Field required"):
        RealtimeCashflow(
            total_available_funds=Decimal("1000.00"),
            total_available_credit=Decimal("0.00"),
            total_liabilities_due=Decimal("0.00"),
            net_position=Decimal("1000.00"),
            minimum_balance_required=Decimal("200.00"),
        )

    with pytest.raises(ValidationError, match="Field required"):
        RealtimeCashflow(
            account_balances=[checking_account],
            total_available_credit=Decimal("0.00"),
            total_liabilities_due=Decimal("0.00"),
            net_position=Decimal("1000.00"),
            minimum_balance_required=Decimal("200.00"),
        )

    # Missing required field in RealtimeCashflowResponse
    with pytest.raises(ValidationError, match="Field required"):
        RealtimeCashflowResponse(last_updated=datetime.now(timezone.utc))
