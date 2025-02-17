from datetime import datetime
from decimal import Decimal
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.base_model import naive_utc_now, naive_utc_from_date
from src.models.accounts import Account
from src.models.transaction_history import TransactionHistory, TransactionType


@pytest.fixture(scope="function")
async def test_account(db_session: AsyncSession) -> Account:
    account = Account(
        name="Test Account",
        type="checking",
        available_balance=Decimal("1000.00")
    )
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)
    return account

async def test_datetime_handling():
    """Test proper datetime handling in TransactionHistory model"""
    # Create instance with explicit datetime values
    instance = TransactionHistory(
        account_id=1,
        amount=Decimal("100.00"),
        transaction_type=TransactionType.DEBIT,
        description="Test transaction",
        transaction_date=naive_utc_from_date(2025, 3, 15),
        created_at=naive_utc_from_date(2025, 3, 15),
        updated_at=naive_utc_from_date(2025, 3, 15)
    )

    # Verify all datetime fields are naive (no tzinfo)
    assert instance.transaction_date.tzinfo is None
    assert instance.created_at.tzinfo is None
    assert instance.updated_at.tzinfo is None

    # Verify transaction_date components
    assert instance.transaction_date.year == 2025
    assert instance.transaction_date.month == 3
    assert instance.transaction_date.day == 15
    assert instance.transaction_date.hour == 0
    assert instance.transaction_date.minute == 0
    assert instance.transaction_date.second == 0

    # Verify created_at components
    assert instance.created_at.year == 2025
    assert instance.created_at.month == 3
    assert instance.created_at.day == 15
    assert instance.created_at.hour == 0
    assert instance.created_at.minute == 0
    assert instance.created_at.second == 0

    # Verify updated_at components
    assert instance.updated_at.year == 2025
    assert instance.updated_at.month == 3
    assert instance.updated_at.day == 15
    assert instance.updated_at.hour == 0
    assert instance.updated_at.minute == 0
    assert instance.updated_at.second == 0

async def test_default_datetime_handling():
    """Test default datetime values are properly set"""
    instance = TransactionHistory(
        account_id=1,
        amount=Decimal("100.00"),
        transaction_type=TransactionType.DEBIT,
        description="Test transaction",
        transaction_date=naive_utc_now()
    )

    # Verify created_at and updated_at are set and naive
    assert instance.created_at is not None
    assert instance.updated_at is not None
    assert instance.created_at.tzinfo is None
    assert instance.updated_at.tzinfo is None
    assert instance.transaction_date.tzinfo is None

@pytest.mark.asyncio
async def test_create_transaction_history(db_session: AsyncSession, test_account: Account):
    """Test creating a transaction history record."""
    transaction = TransactionHistory(
        account_id=test_account.id,
        amount=Decimal("100.00"),
        transaction_type=TransactionType.DEBIT,
        description="Test transaction",
        transaction_date=naive_utc_now()
    )
    db_session.add(transaction)
    await db_session.commit()
    await db_session.refresh(transaction)

    assert transaction.id is not None
    assert transaction.account_id == test_account.id
    assert transaction.amount == Decimal("100.00")
    assert transaction.transaction_type == TransactionType.DEBIT
    assert transaction.description == "Test transaction"

    # Check that the datetime fields are naive (tzinfo=None), consistent with ADR
    assert transaction.transaction_date.tzinfo is None
    assert transaction.created_at.tzinfo is None
    assert transaction.updated_at.tzinfo is None

@pytest.mark.asyncio
async def test_transaction_history_relationships(db_session: AsyncSession, test_account: Account):
    """Test transaction history relationships."""
    transaction = TransactionHistory(
        account_id=test_account.id,
        amount=Decimal("100.00"),
        transaction_type=TransactionType.DEBIT,
        description="Test transaction",
        transaction_date=naive_utc_now()
    )
    db_session.add(transaction)
    await db_session.commit()
    await db_session.refresh(transaction)

    # Refresh test_account to load relationships
    await db_session.refresh(test_account, ['transactions'])

    # Test account relationship
    assert transaction.account is not None
    assert transaction.account.id == test_account.id
    assert transaction.account.name == test_account.name
    assert transaction.transaction_date.tzinfo is None
    assert transaction.created_at.tzinfo is None
    assert transaction.updated_at.tzinfo is None

    # Test relationship from the account side
    assert transaction in test_account.transactions

@pytest.mark.asyncio
async def test_transaction_history_string_representation(db_session: AsyncSession, test_account: Account):
    """Test the string representation of a transaction history record."""
    transaction = TransactionHistory(
        account_id=test_account.id,
        amount=Decimal("100.00"),
        transaction_type=TransactionType.DEBIT,
        description="Test transaction",
        transaction_date=naive_utc_now()
    )
    db_session.add(transaction)
    await db_session.commit()
    await db_session.refresh(transaction)

    expected_str = (
        f"<TransactionHistory(id={transaction.id}, "
        f"account_id={test_account.id}, "
        f"amount=100.00, "
        f"type=debit, "
        f"date={transaction.transaction_date})>"
    )
    assert str(transaction) == expected_str
    assert repr(transaction) == expected_str
    assert transaction.transaction_date.tzinfo is None
    assert transaction.created_at.tzinfo is None
    assert transaction.updated_at.tzinfo is None

@pytest.mark.asyncio
async def test_transaction_history_cascade_delete(db_session: AsyncSession, test_account: Account):
    """Test that transaction history records are deleted when account is deleted."""
    transaction = TransactionHistory(
        account_id=test_account.id,
        amount=Decimal("100.00"),
        transaction_type=TransactionType.DEBIT,
        description="Test transaction",
        transaction_date=naive_utc_now()
    )
    db_session.add(transaction)
    await db_session.commit()

    # Delete the account
    await db_session.delete(test_account)
    await db_session.commit()

    # Verify transaction record is also deleted (cascade)
    result = await db_session.get(TransactionHistory, transaction.id)
    assert result is None

@pytest.mark.asyncio
async def test_transaction_types(db_session: AsyncSession, test_account: Account):
    """Test both credit and debit transaction types."""
    # Create a debit transaction
    debit = TransactionHistory(
        account_id=test_account.id,
        amount=Decimal("100.00"),
        transaction_type=TransactionType.DEBIT,
        description="Debit transaction",
        transaction_date=naive_utc_now()
    )
    db_session.add(debit)
    await db_session.commit()

    # Create a credit transaction
    credit = TransactionHistory(
        account_id=test_account.id,
        amount=Decimal("50.00"),
        transaction_type=TransactionType.CREDIT,
        description="Credit transaction",
        transaction_date=naive_utc_now()
    )
    db_session.add(credit)
    await db_session.commit()

    # Refresh test_account to load relationships
    await db_session.refresh(test_account, ['transactions'])

    # Verify both transactions exist with correct types
    transactions = test_account.transactions
    assert len(transactions) == 2
    assert any(t.transaction_type == TransactionType.DEBIT for t in transactions)
    assert any(t.transaction_type == TransactionType.CREDIT for t in transactions)

    # Verify datetime fields are naive for both transactions
    for transaction in transactions:
        assert transaction.transaction_date.tzinfo is None
        assert transaction.created_at.tzinfo is None
        assert transaction.updated_at.tzinfo is None

@pytest.mark.asyncio
async def test_optional_description(db_session: AsyncSession, test_account: Account):
    """Test creating a transaction without a description."""
    transaction = TransactionHistory(
        account_id=test_account.id,
        amount=Decimal("100.00"),
        transaction_type=TransactionType.DEBIT,
        transaction_date=naive_utc_now()
    )
    db_session.add(transaction)
    await db_session.commit()
    await db_session.refresh(transaction)

    assert transaction.id is not None
    assert transaction.description is None
    assert transaction.transaction_date.tzinfo is None
    assert transaction.created_at.tzinfo is None
    assert transaction.updated_at.tzinfo is None
