from datetime import datetime, timezone
from decimal import Decimal
import pytest
from pydantic import ValidationError

from src.schemas.balance_history import (
    BalanceHistoryBase,
    BalanceHistoryCreate,
    BalanceHistory,
    BalanceTrend,
)


# Test valid object creation
def test_balance_history_base_valid():
    """Test valid balance history base schema"""
    data = BalanceHistoryBase(
        account_id=1,
        balance=Decimal("100.00"),
        available_credit=Decimal("500.00"),
        is_reconciled=True,
        notes="Initial balance entry"
    )
    
    assert data.account_id == 1
    assert data.balance == Decimal("100.00")
    assert data.available_credit == Decimal("500.00")
    assert data.is_reconciled is True
    assert data.notes == "Initial balance entry"


def test_balance_history_base_minimal():
    """Test balance history base schema with only required fields"""
    data = BalanceHistoryBase(
        account_id=1,
        balance=Decimal("100.00")
    )
    
    assert data.account_id == 1
    assert data.balance == Decimal("100.00")
    assert data.available_credit is None
    assert data.is_reconciled is False
    assert data.notes is None


def test_balance_history_create_valid():
    """Test valid balance history create schema"""
    data = BalanceHistoryCreate(
        account_id=1,
        balance=Decimal("100.00"),
        available_credit=Decimal("500.00"),
        is_reconciled=True,
        notes="Initial balance entry"
    )
    
    assert data.account_id == 1
    assert data.balance == Decimal("100.00")
    assert data.available_credit == Decimal("500.00")
    assert data.is_reconciled is True
    assert data.notes == "Initial balance entry"


def test_balance_history_valid():
    """Test valid balance history schema with all fields"""
    now = datetime.now(timezone.utc)
    
    data = BalanceHistory(
        id=1,
        account_id=2,
        balance=Decimal("100.00"),
        available_credit=Decimal("500.00"),
        is_reconciled=True,
        notes="Initial balance entry",
        timestamp=now,
        created_at=now,
        updated_at=now
    )
    
    assert data.id == 1
    assert data.account_id == 2
    assert data.balance == Decimal("100.00")
    assert data.available_credit == Decimal("500.00")
    assert data.is_reconciled is True
    assert data.notes == "Initial balance entry"
    assert data.timestamp == now
    assert data.created_at == now
    assert data.updated_at == now


def test_balance_trend_valid():
    """Test valid balance trend schema with all fields"""
    start_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(2025, 1, 31, tzinfo=timezone.utc)
    
    data = BalanceTrend(
        account_id=1,
        start_date=start_date,
        end_date=end_date,
        start_balance=Decimal("1000.00"),
        end_balance=Decimal("1500.00"),
        net_change=Decimal("500.00"),
        average_balance=Decimal("1250.00"),
        min_balance=Decimal("900.00"),
        max_balance=Decimal("1600.00"),
        trend_direction="increasing",
        volatility=Decimal("75.50")
    )
    
    assert data.account_id == 1
    assert data.start_date == start_date
    assert data.end_date == end_date
    assert data.start_balance == Decimal("1000.00")
    assert data.end_balance == Decimal("1500.00")
    assert data.net_change == Decimal("500.00")
    assert data.average_balance == Decimal("1250.00")
    assert data.min_balance == Decimal("900.00")
    assert data.max_balance == Decimal("1600.00")
    assert data.trend_direction == "increasing"
    assert data.volatility == Decimal("75.50")


# Test field validations
def test_account_id_validation():
    """Test account_id field validation"""
    # Test account_id <= 0
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        BalanceHistoryBase(account_id=0, balance=Decimal("100.00"))
    
    with pytest.raises(ValidationError, match="Input should be greater than 0"):
        BalanceHistoryBase(account_id=-1, balance=Decimal("100.00"))
    
    # Test valid account_id
    data = BalanceHistoryBase(account_id=1, balance=Decimal("100.00"))
    assert data.account_id == 1


def test_notes_length_validation():
    """Test notes length validation"""
    # Test notes too long
    with pytest.raises(ValidationError, match="String should have at most 500 characters"):
        BalanceHistoryBase(
            account_id=1, 
            balance=Decimal("100.00"), 
            notes="X" * 501
        )
    
    # Test valid notes length
    data = BalanceHistoryBase(
        account_id=1, 
        balance=Decimal("100.00"), 
        notes="X" * 500
    )
    assert len(data.notes) == 500


# Test decimal precision
def test_decimal_precision():
    """Test decimal precision validation for monetary fields"""
    # Test too many decimal places on balance
    with pytest.raises(ValidationError, match="Decimal input should have no more than 2 decimal places"):
        BalanceHistoryBase(account_id=1, balance=Decimal("100.123"))
    
    # Test too many decimal places on available_credit
    with pytest.raises(ValidationError, match="Decimal input should have no more than 2 decimal places"):
        BalanceHistoryBase(
            account_id=1, 
            balance=Decimal("100.00"), 
            available_credit=Decimal("500.123")
        )
    
    # Test valid decimal places
    data = BalanceHistoryBase(
        account_id=1, 
        balance=Decimal("100.12"), 
        available_credit=Decimal("500.12")
    )
    assert data.balance == Decimal("100.12")
    assert data.available_credit == Decimal("500.12")


# Test datetime UTC validation
def test_datetime_utc_validation():
    """Test datetime UTC validation per ADR-011"""
    now_utc = datetime.now(timezone.utc)
    
    # Test naive datetime in timestamp
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        BalanceHistory(
            id=1,
            account_id=1,
            balance=Decimal("100.00"),
            timestamp=datetime.now(),  # Naive datetime
            created_at=now_utc,
            updated_at=now_utc
        )
    
    # Test non-UTC timezone in created_at
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        BalanceHistory(
            id=1,
            account_id=1,
            balance=Decimal("100.00"),
            timestamp=now_utc,
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now().replace(tzinfo=timezone(offset=timezone(hours=5)))  # Non-UTC timezone
        )


# Test custom validators
def test_trend_direction_validation():
    """Test trend_direction validator"""
    start_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
    end_date = datetime(2025, 1, 31, tzinfo=timezone.utc)
    
    # Test invalid trend_direction
    with pytest.raises(ValidationError, match="trend_direction must be one of"):
        BalanceTrend(
            account_id=1,
            start_date=start_date,
            end_date=end_date,
            start_balance=Decimal("1000.00"),
            end_balance=Decimal("1500.00"),
            net_change=Decimal("500.00"),
            average_balance=Decimal("1250.00"),
            min_balance=Decimal("900.00"),
            max_balance=Decimal("1600.00"),
            trend_direction="upward",  # Invalid value
            volatility=Decimal("75.50")
        )
    
    # Test valid trend_direction values
    for direction in ["increasing", "decreasing", "stable"]:
        data = BalanceTrend(
            account_id=1,
            start_date=start_date,
            end_date=end_date,
            start_balance=Decimal("1000.00"),
            end_balance=Decimal("1500.00"),
            net_change=Decimal("500.00"),
            average_balance=Decimal("1250.00"),
            min_balance=Decimal("900.00"),
            max_balance=Decimal("1600.00"),
            trend_direction=direction,
            volatility=Decimal("75.50")
        )
        assert data.trend_direction == direction


def test_date_range_validation():
    """Test date range validation (end_date not before start_date)"""
    # Test end_date before start_date
    with pytest.raises(ValidationError, match="end_date must not be before start_date"):
        BalanceTrend(
            account_id=1,
            start_date=datetime(2025, 1, 31, tzinfo=timezone.utc),
            end_date=datetime(2025, 1, 1, tzinfo=timezone.utc),  # Before start_date
            start_balance=Decimal("1000.00"),
            end_balance=Decimal("1500.00"),
            net_change=Decimal("500.00"),
            average_balance=Decimal("1250.00"),
            min_balance=Decimal("900.00"),
            max_balance=Decimal("1600.00"),
            trend_direction="increasing",
            volatility=Decimal("75.50")
        )
    
    # Test end_date equal to start_date (valid)
    same_date = datetime(2025, 1, 15, tzinfo=timezone.utc)
    data = BalanceTrend(
        account_id=1,
        start_date=same_date,
        end_date=same_date,
        start_balance=Decimal("1000.00"),
        end_balance=Decimal("1500.00"),
        net_change=Decimal("500.00"),
        average_balance=Decimal("1250.00"),
        min_balance=Decimal("900.00"),
        max_balance=Decimal("1600.00"),
        trend_direction="increasing",
        volatility=Decimal("75.50")
    )
    assert data.start_date == data.end_date


def test_net_change_validation():
    """Test net_change validation (must equal end_balance - start_balance)"""
    # Test incorrect net_change
    with pytest.raises(ValidationError, match="net_change must equal end_balance - start_balance"):
        BalanceTrend(
            account_id=1,
            start_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
            end_date=datetime(2025, 1, 31, tzinfo=timezone.utc),
            start_balance=Decimal("1000.00"),
            end_balance=Decimal("1500.00"),
            net_change=Decimal("400.00"),  # Should be 500.00
            average_balance=Decimal("1250.00"),
            min_balance=Decimal("900.00"),
            max_balance=Decimal("1600.00"),
            trend_direction="increasing",
            volatility=Decimal("75.50")
        )
    
    # Test correct net_change
    data = BalanceTrend(
        account_id=1,
        start_date=datetime(2025, 1, 1, tzinfo=timezone.utc),
        end_date=datetime(2025, 1, 31, tzinfo=timezone.utc),
        start_balance=Decimal("1000.00"),
        end_balance=Decimal("1500.00"),
        net_change=Decimal("500.00"),  # Correct value
        average_balance=Decimal("1250.00"),
        min_balance=Decimal("900.00"),
        max_balance=Decimal("1600.00"),
        trend_direction="increasing",
        volatility=Decimal("75.50")
    )
    assert data.net_change == data.end_balance - data.start_balance
