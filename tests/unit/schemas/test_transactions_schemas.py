from datetime import datetime
from decimal import Decimal
from zoneinfo import ZoneInfo

import pytest
from pydantic import ValidationError

from src.schemas.transaction_history import TransactionHistoryBase as TransactionBase
from src.schemas.transaction_history import (
    TransactionHistoryCreate as TransactionCreate,
)
from src.schemas.transaction_history import TransactionHistoryInDB
from src.schemas.transaction_history import TransactionHistoryInDB as Transaction
from src.schemas.transaction_history import TransactionHistoryList as TransactionList
from src.schemas.transaction_history import (
    TransactionHistoryUpdate as TransactionUpdate,
)
from src.schemas.transaction_history import TransactionType


def test_transaction_base_valid():
    """Test valid transaction base schema"""
    transaction_date = datetime.now(ZoneInfo("UTC"))
    transaction = TransactionBase(
        amount=Decimal("100.00"),
        transaction_type=TransactionType.CREDIT,
        description="Test transaction",
        transaction_date=transaction_date,
    )
    assert transaction.amount == Decimal("100.00")
    assert transaction.transaction_type == TransactionType.CREDIT
    assert transaction.description == "Test transaction"
    assert transaction.transaction_date == transaction_date


def test_transaction_base_invalid_date():
    """Test invalid transaction date validation"""
    # Test naive datetime
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        TransactionBase(
            amount=Decimal("100.00"),
            transaction_type=TransactionType.CREDIT,
            transaction_date=datetime.now(),
        )

    # Test non-UTC timezone
    non_utc_date = datetime.now(ZoneInfo("America/New_York"))
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        TransactionBase(
            amount=Decimal("100.00"),
            transaction_type=TransactionType.CREDIT,
            transaction_date=non_utc_date,
        )


def test_transaction_update_valid():
    """Test valid transaction update schema"""
    transaction_date = datetime.now(ZoneInfo("UTC"))
    update = TransactionUpdate(
        id=1,  # Add required id field
        amount=Decimal("150.00"),
        transaction_type=TransactionType.DEBIT,
        transaction_date=transaction_date,
    )
    assert update.amount == Decimal("150.00")
    assert update.transaction_type == TransactionType.DEBIT
    assert update.transaction_date == transaction_date


def test_transaction_update_invalid_date():
    """Test invalid date in transaction update"""
    # Test naive datetime
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        TransactionUpdate(
            id=1, amount=Decimal("150.00"), transaction_date=datetime.now()
        )

    # Test non-UTC timezone
    non_utc_date = datetime.now(ZoneInfo("America/New_York"))
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        TransactionUpdate(id=1, amount=Decimal("150.00"), transaction_date=non_utc_date)


def test_transaction_in_db_valid():
    """Test valid transaction in DB schema"""
    now = datetime.now(ZoneInfo("UTC"))
    transaction = TransactionHistoryInDB(
        id=1,
        account_id=1,
        amount=Decimal("100.00"),
        transaction_type=TransactionType.CREDIT,
        transaction_date=now,
        created_at=now,
        updated_at=now,
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
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        TransactionHistoryInDB(
            id=1,
            account_id=1,
            amount=Decimal("100.00"),
            transaction_type=TransactionType.CREDIT,
            transaction_date=now,
            created_at=naive_now,
            updated_at=now,
        )

    # Test naive updated_at
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        TransactionHistoryInDB(
            id=1,
            account_id=1,
            amount=Decimal("100.00"),
            transaction_type=TransactionType.CREDIT,
            transaction_date=now,
            created_at=now,
            updated_at=naive_now,
        )

    # Test non-UTC timezone
    non_utc = datetime.now(ZoneInfo("America/New_York"))
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        TransactionHistoryInDB(
            id=1,
            account_id=1,
            amount=Decimal("100.00"),
            transaction_type=TransactionType.CREDIT,
            transaction_date=now,
            created_at=non_utc,
            updated_at=now,
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
        updated_at=now,
    )
    transaction_list = TransactionList(items=[transaction], total=1)
    assert len(transaction_list.items) == 1
    assert transaction_list.total == 1
    assert transaction_list.items[0].id == 1
    assert transaction_list.items[0].amount == Decimal("100.00")
