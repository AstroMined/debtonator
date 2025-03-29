from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.models.transaction_history import TransactionType
from src.schemas.transaction_history import (
    TransactionHistoryCreate as TransactionCreate,
)
from src.services.transactions import TransactionService


@pytest.fixture
async def test_account(db_session: AsyncSession) -> Account:
    """Create a test account"""
    account = Account(
        name="Test Account", type="checking", available_balance=Decimal("1000.00")
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account


@pytest.fixture
def transaction_create_data() -> TransactionCreate:
    """Create test transaction data"""
    return TransactionCreate(
        amount=Decimal("100.00"),
        transaction_type=TransactionType.DEBIT,
        description="Test transaction",
        transaction_date=datetime.now(timezone.utc),
    )


async def test_create_transaction(
    db_session: AsyncSession,
    test_account: Account,
    transaction_create_data: TransactionCreate,
):
    """Test creating a transaction"""
    service = TransactionService(db_session)
    initial_balance = test_account.available_balance

    # Create transaction
    transaction = await service.create_transaction(
        test_account.id, transaction_create_data
    )

    # Verify transaction was created
    assert transaction.id is not None
    assert transaction.account_id == test_account.id
    assert transaction.amount == transaction_create_data.amount
    assert transaction.transaction_type == transaction_create_data.transaction_type
    assert transaction.description == transaction_create_data.description

    # Verify account balance was updated
    await db_session.refresh(test_account)
    expected_balance = initial_balance - transaction_create_data.amount
    assert test_account.available_balance == expected_balance


async def test_get_transaction(
    db_session: AsyncSession,
    test_account: Account,
    transaction_create_data: TransactionCreate,
):
    """Test retrieving a transaction"""
    service = TransactionService(db_session)

    # Create transaction
    created_transaction = await service.create_transaction(
        test_account.id, transaction_create_data
    )

    # Get transaction
    retrieved_transaction = await service.get_transaction(created_transaction.id)

    # Verify transaction details
    assert retrieved_transaction is not None
    assert retrieved_transaction.id == created_transaction.id
    assert retrieved_transaction.amount == created_transaction.amount
    assert (
        retrieved_transaction.transaction_type == created_transaction.transaction_type
    )


async def test_get_account_transactions(
    db_session: AsyncSession,
    test_account: Account,
    transaction_create_data: TransactionCreate,
):
    """Test retrieving transactions for an account"""
    service = TransactionService(db_session)

    # Create multiple transactions
    transactions = []
    for i in range(3):
        transaction = await service.create_transaction(
            test_account.id, transaction_create_data
        )
        transactions.append(transaction)

    # Get transactions
    retrieved_transactions, total = await service.get_account_transactions(
        test_account.id, skip=0, limit=10
    )

    # Verify transactions
    assert total == 3
    assert len(retrieved_transactions) == 3
    for transaction in retrieved_transactions:
        assert transaction.account_id == test_account.id


async def test_update_transaction(
    db_session: AsyncSession,
    test_account: Account,
    transaction_create_data: TransactionCreate,
):
    """Test updating a transaction"""
    service = TransactionService(db_session)
    initial_balance = test_account.available_balance

    # Create transaction
    transaction = await service.create_transaction(
        test_account.id, transaction_create_data
    )

    # Update transaction amount
    new_amount = Decimal("200.00")
    updated_transaction = await service.update_transaction(
        transaction.id,
        TransactionCreate(
            amount=new_amount,
            transaction_type=transaction.transaction_type,
            description=transaction.description,
            transaction_date=transaction.transaction_date,
        ),
    )

    # Verify transaction was updated
    assert updated_transaction.amount == new_amount

    # Verify account balance was adjusted correctly
    await db_session.refresh(test_account)
    expected_balance = initial_balance - new_amount
    assert test_account.available_balance == expected_balance


async def test_delete_transaction(
    db_session: AsyncSession,
    test_account: Account,
    transaction_create_data: TransactionCreate,
):
    """Test deleting a transaction"""
    service = TransactionService(db_session)
    initial_balance = test_account.available_balance

    # Create transaction
    transaction = await service.create_transaction(
        test_account.id, transaction_create_data
    )

    # Delete transaction
    success = await service.delete_transaction(transaction.id)
    assert success is True

    # Verify transaction was deleted
    deleted_transaction = await service.get_transaction(transaction.id)
    assert deleted_transaction is None

    # Verify account balance was restored
    await db_session.refresh(test_account)
    assert test_account.available_balance == initial_balance
