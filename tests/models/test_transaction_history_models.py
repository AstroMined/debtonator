from datetime import datetime
from decimal import Decimal
import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.transaction_history import TransactionHistory, TransactionType

pytestmark = pytest.mark.asyncio

@pytest.fixture(scope="function")
async def test_account(db_session: AsyncSession) -> Account:
    account = Account(
        name="Test Account",
        type="checking",
        available_balance=Decimal("1000.00"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account

async def test_create_transaction_history(
    db_session: AsyncSession,
    test_account: Account
):
    """Test creating a transaction history record."""
    transaction = TransactionHistory(
        account_id=test_account.id,
        amount=Decimal("100.00"),
        transaction_type=TransactionType.DEBIT,
        description="Test transaction",
        transaction_date=datetime.utcnow()
    )
    db_session.add(transaction)
    await db_session.commit()
    await db_session.refresh(transaction)

    assert transaction.id is not None
    assert transaction.account_id == test_account.id
    assert transaction.amount == Decimal("100.00")
    assert transaction.transaction_type == TransactionType.DEBIT
    assert transaction.description == "Test transaction"
    assert isinstance(transaction.transaction_date, datetime)
    assert isinstance(transaction.created_at, datetime)
    assert isinstance(transaction.updated_at, datetime)

async def test_transaction_history_relationships(
    db_session: AsyncSession,
    test_account: Account
):
    """Test transaction history relationships."""
    transaction = TransactionHistory(
        account_id=test_account.id,
        amount=Decimal("100.00"),
        transaction_type=TransactionType.DEBIT,
        description="Test transaction",
        transaction_date=datetime.utcnow()
    )
    db_session.add(transaction)
    await db_session.commit()
    await db_session.refresh(transaction)

    # Test account relationship
    assert transaction.account is not None
    assert transaction.account.id == test_account.id
    assert transaction.account.name == test_account.name

    # Test relationship from account side
    assert transaction in test_account.transactions

async def test_transaction_history_string_representation(
    db_session: AsyncSession,
    test_account: Account
):
    """Test the string representation of a transaction history record."""
    transaction = TransactionHistory(
        account_id=test_account.id,
        amount=Decimal("100.00"),
        transaction_type=TransactionType.DEBIT,
        description="Test transaction",
        transaction_date=datetime.utcnow()
    )
    db_session.add(transaction)
    await db_session.commit()

    expected_str = (
        f"<TransactionHistory(id={transaction.id}, "
        f"account_id={test_account.id}, "
        f"amount=100.00, "
        f"type=debit, "
        f"date={transaction.transaction_date})>"
    )
    assert str(transaction) == expected_str
    assert repr(transaction) == expected_str

async def test_transaction_history_cascade_delete(
    db_session: AsyncSession,
    test_account: Account
):
    """Test that transaction history records are deleted when account is deleted."""
    transaction = TransactionHistory(
        account_id=test_account.id,
        amount=Decimal("100.00"),
        transaction_type=TransactionType.DEBIT,
        description="Test transaction",
        transaction_date=datetime.utcnow()
    )
    db_session.add(transaction)
    await db_session.commit()

    # Delete the account
    await db_session.delete(test_account)
    await db_session.commit()

    # Verify transaction record is also deleted
    result = await db_session.get(TransactionHistory, transaction.id)
    assert result is None

async def test_transaction_types(
    db_session: AsyncSession,
    test_account: Account
):
    """Test both credit and debit transaction types."""
    # Create debit transaction
    debit = TransactionHistory(
        account_id=test_account.id,
        amount=Decimal("100.00"),
        transaction_type=TransactionType.DEBIT,
        description="Debit transaction",
        transaction_date=datetime.utcnow()
    )
    db_session.add(debit)
    await db_session.commit()

    # Create credit transaction
    credit = TransactionHistory(
        account_id=test_account.id,
        amount=Decimal("50.00"),
        transaction_type=TransactionType.CREDIT,
        description="Credit transaction",
        transaction_date=datetime.utcnow()
    )
    db_session.add(credit)
    await db_session.commit()

    # Verify both transactions exist with correct types
    transactions = test_account.transactions
    assert len(transactions) == 2
    assert any(t.transaction_type == TransactionType.DEBIT for t in transactions)
    assert any(t.transaction_type == TransactionType.CREDIT for t in transactions)

async def test_optional_description(
    db_session: AsyncSession,
    test_account: Account
):
    """Test creating a transaction without a description."""
    transaction = TransactionHistory(
        account_id=test_account.id,
        amount=Decimal("100.00"),
        transaction_type=TransactionType.DEBIT,
        transaction_date=datetime.utcnow()
    )
    db_session.add(transaction)
    await db_session.commit()
    await db_session.refresh(transaction)

    assert transaction.id is not None
    assert transaction.description is None
