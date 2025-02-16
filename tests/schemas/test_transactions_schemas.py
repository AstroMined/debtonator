from datetime import datetime
from decimal import Decimal
import pytest
from zoneinfo import ZoneInfo
from pydantic import ValidationError

from src.schemas.transactions import (
    TransactionBase,
    TransactionCreate,
    TransactionUpdate,
    TransactionInDB,
    Transaction,
    TransactionList,
    TransactionType
)

def test_transaction_base_valid():
    """Test valid transaction base schema"""
    transaction_date = datetime.now(ZoneInfo("UTC"))
    transaction = TransactionBase(
        amount=Decimal("100.00"),
        transaction_type=TransactionType.CREDIT,
        description="Test transaction",
        transaction_date=transaction_date
    )
    assert transaction.amount == Decimal("100.00")
    assert transaction.transaction_type == TransactionType.CREDIT
    assert transaction.description == "Test transaction"
    assert transaction.transaction_date == transaction_date

def test_transaction_base_invalid_date():
    """Test invalid transaction date validation"""
    # Test naive datetime
    with pytest.raises(ValidationError, match="Transaction date must be timezone-aware"):
        TransactionBase(
            amount=Decimal("100.00"),
            transaction_type=TransactionType.CREDIT,
            transaction_date=datetime.now()
        )

    # Test non-UTC timezone
    non_utc_date = datetime.now(ZoneInfo("America/New_York"))
    with pytest.raises(ValidationError, match="Transaction date must be in UTC timezone"):
        TransactionBase(
            amount=Decimal("100.00"),
            transaction_type=TransactionType.CREDIT,
            transaction_date=non_utc_date
        )

def test_transaction_update_valid():
    """Test valid transaction update schema"""
    transaction_date = datetime.now(ZoneInfo("UTC"))
    update = TransactionUpdate(
        amount=Decimal("150.00"),
        transaction_type=TransactionType.DEBIT,
        transaction_date=transaction_date
    )
    assert update.amount == Decimal("150.00")
    assert update.transaction_type == TransactionType.DEBIT
    assert update.transaction_date == transaction_date

def test_transaction_update_invalid_date():
    """Test invalid date in transaction update"""
    # Test naive datetime
    with pytest.raises(ValidationError, match="Transaction date must be timezone-aware"):
        TransactionUpdate(
            amount=Decimal("150.00"),
            transaction_date=datetime.now()
        )

    # Test non-UTC timezone
    non_utc_date = datetime.now(ZoneInfo("America/New_York"))
    with pytest.raises(ValidationError, match="Transaction date must be in UTC timezone"):
        TransactionUpdate(
            amount=Decimal("150.00"),
            transaction_date=non_utc_date
        )

def test_transaction_in_db_valid():
    """Test valid transaction in DB schema"""
    now = datetime.now(ZoneInfo("UTC"))
    transaction = TransactionInDB(
        id=1,
        account_id=1,
        amount=Decimal("100.00"),
        transaction_type=TransactionType.CREDIT,
        transaction_date=now,
        created_at=now,
        updated_at=now
    )
    assert transaction.id == 1
    assert transaction.account_id == 1
    assert transaction.amount == Decimal("100.00")
    assert transaction.transaction_type == TransactionType.CREDIT
    assert transaction.transaction_date == now
    assert transaction.created_at == now
    assert transaction.updated_at == now

def test_transaction_in_db_invalid_timestamps():
    """Test invalid timestamps in DB schema"""
    now = datetime.now(ZoneInfo("UTC"))
    naive_now = datetime.now()

    # Test naive created_at
    with pytest.raises(ValidationError, match="Timestamp must be timezone-aware"):
        TransactionInDB(
            id=1,
            account_id=1,
            amount=Decimal("100.00"),
            transaction_type=TransactionType.CREDIT,
            transaction_date=now,
            created_at=naive_now,
            updated_at=now
        )

    # Test naive updated_at
    with pytest.raises(ValidationError, match="Timestamp must be timezone-aware"):
        TransactionInDB(
            id=1,
            account_id=1,
            amount=Decimal("100.00"),
            transaction_type=TransactionType.CREDIT,
            transaction_date=now,
            created_at=now,
            updated_at=naive_now
        )

    # Test non-UTC timezone
    non_utc = datetime.now(ZoneInfo("America/New_York"))
    with pytest.raises(ValidationError, match="Timestamp must be in UTC timezone"):
        TransactionInDB(
            id=1,
            account_id=1,
            amount=Decimal("100.00"),
            transaction_type=TransactionType.CREDIT,
            transaction_date=now,
            created_at=non_utc,
            updated_at=now
        )

def test_transaction_list_valid():
    """Test valid transaction list schema"""
    now = datetime.now(ZoneInfo("UTC"))
    transaction = Transaction(
        id=1,
        account_id=1,
        amount=Decimal("100.00"),
        transaction_type=TransactionType.CREDIT,
        transaction_date=now,
        created_at=now,
        updated_at=now
    )
    transaction_list = TransactionList(
        items=[transaction],
        total=1
    )
    assert len(transaction_list.items) == 1
    assert transaction_list.total == 1
    assert transaction_list.items[0].id == 1
    assert transaction_list.items[0].amount == Decimal("100.00")
