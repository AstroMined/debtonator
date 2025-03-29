"""
Unit tests for the BaseRepository class.

These tests validate the core functionality of the BaseRepository with real database fixtures.
"""

from datetime import date, datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.accounts import Account
from src.repositories.base_repository import BaseRepository
from src.schemas.accounts import AccountCreate

pytestmark = pytest.mark.integration


async def test_create(db_session: AsyncSession):
    """Test creating a new record using a repository."""
    # Arrange
    repo = BaseRepository(db_session, Account)

    # Schema (simulate service validation)
    account_data = AccountCreate(
        name="Test Account", type="checking", available_balance=Decimal("1000.00")
    )

    # Act
    account = await repo.create(account_data.model_dump())

    # Assert
    assert account.id is not None
    assert account.name == "Test Account"
    assert account.type == "checking"
    assert account.available_balance == Decimal("1000.00")


async def test_get(db_session: AsyncSession):
    """Test retrieving a record by ID."""
    # Arrange
    repo = BaseRepository(db_session, Account)

    # Create test account
    account_data = AccountCreate(
        name="Get Test Account", type="savings", available_balance=Decimal("500.00")
    )
    created_account = await repo.create(account_data.model_dump())

    # Act
    retrieved_account = await repo.get(created_account.id)

    # Assert
    assert retrieved_account is not None
    assert retrieved_account.id == created_account.id
    assert retrieved_account.name == "Get Test Account"
    assert retrieved_account.type == "savings"
    assert retrieved_account.available_balance == Decimal("500.00")


async def test_get_nonexistent(db_session: AsyncSession):
    """Test retrieving a nonexistent record returns None."""
    # Arrange
    repo = BaseRepository(db_session, Account)

    # Act
    retrieved_account = await repo.get(9999)  # Nonexistent ID

    # Assert
    assert retrieved_account is None


async def test_update(db_session: AsyncSession):
    """Test updating a record."""
    # Arrange
    repo = BaseRepository(db_session, Account)

    # Create test account
    account_data = AccountCreate(
        name="Update Test Account",
        type="checking",
        available_balance=Decimal("1500.00"),
    )
    created_account = await repo.create(account_data.model_dump())

    # Act
    updated_data = {
        "name": "Updated Account Name",
        "available_balance": Decimal("2000.00"),
    }
    updated_account = await repo.update(created_account.id, updated_data)

    # Assert
    assert updated_account is not None
    assert updated_account.id == created_account.id
    assert updated_account.name == "Updated Account Name"
    assert updated_account.type == "checking"  # Unchanged
    assert updated_account.available_balance == Decimal("2000.00")


async def test_update_nonexistent(db_session: AsyncSession):
    """Test updating a nonexistent record returns None."""
    # Arrange
    repo = BaseRepository(db_session, Account)

    # Act
    updated_data = {
        "name": "Updated Account Name",
        "available_balance": Decimal("2000.00"),
    }
    updated_account = await repo.update(9999, updated_data)  # Nonexistent ID

    # Assert
    assert updated_account is None


async def test_delete(db_session: AsyncSession):
    """Test deleting a record."""
    # Arrange
    repo = BaseRepository(db_session, Account)

    # Create test account
    account_data = AccountCreate(
        name="Delete Test Account",
        type="checking",
        available_balance=Decimal("100.00"),
    )
    created_account = await repo.create(account_data.model_dump())

    # Verify account exists
    assert await repo.get(created_account.id) is not None

    # Act
    deleted = await repo.delete(created_account.id)

    # Assert
    assert deleted is True
    assert await repo.get(created_account.id) is None


async def test_delete_nonexistent(db_session: AsyncSession):
    """Test deleting a nonexistent record returns False."""
    # Arrange
    repo = BaseRepository(db_session, Account)

    # Act
    deleted = await repo.delete(9999)  # Nonexistent ID

    # Assert
    assert deleted is False


async def test_get_multi(db_session: AsyncSession):
    """Test retrieving multiple records with filtering."""
    # Arrange
    repo = BaseRepository(db_session, Account)

    # Create test accounts
    account_data_1 = AccountCreate(
        name="Test Account 1", type="checking", available_balance=Decimal("1000.00")
    )
    account_data_2 = AccountCreate(
        name="Test Account 2", type="savings", available_balance=Decimal("2000.00")
    )
    account_data_3 = AccountCreate(
        name="Test Account 3", type="checking", available_balance=Decimal("3000.00")
    )

    await repo.create(account_data_1.model_dump())
    await repo.create(account_data_2.model_dump())
    await repo.create(account_data_3.model_dump())

    # Act
    checking_accounts = await repo.get_multi(filters={"type": "checking"})

    # Assert
    assert len(checking_accounts) >= 2  # At least our created test accounts
    assert all(account.type == "checking" for account in checking_accounts)


async def test_get_multi_with_skip_and_limit(db_session: AsyncSession):
    """Test pagination with skip and limit parameters."""
    # Arrange
    repo = BaseRepository(db_session, Account)

    # Create 5 test accounts
    for i in range(5):
        account_data = AccountCreate(
            name=f"Pagination Test {i}",
            type="checking",
            available_balance=Decimal(f"{i}000.00"),
        )
        await repo.create(account_data.model_dump())

    # Act - Get second page (skip first 2, limit to 2)
    page = await repo.get_multi(skip=2, limit=2)

    # Assert
    assert len(page) == 2


async def test_get_paginated(db_session: AsyncSession):
    """Test paginated results with total count."""
    # Arrange
    repo = BaseRepository(db_session, Account)

    # Create 5 test accounts with the same type for filtering
    for i in range(5):
        account_data = AccountCreate(
            name=f"Pagination Total Test {i}",
            type="savings",
            available_balance=Decimal(f"{i}000.00"),
        )
        await repo.create(account_data.model_dump())

    # Act - Get first page with filter
    items, total = await repo.get_paginated(
        page=1, items_per_page=3, filters={"type": "savings"}
    )

    # Assert
    assert len(items) == 3  # First page limited to 3 items
    assert total >= 5  # At least our created items


async def test_bulk_create(db_session: AsyncSession):
    """Test creating multiple records in a batch."""
    # Arrange
    repo = BaseRepository(db_session, Account)

    # Prepare bulk data (simulating validated data)
    bulk_data = [
        {
            "name": "Bulk Account 1",
            "type": "checking",
            "available_balance": Decimal("1000.00"),
        },
        {
            "name": "Bulk Account 2",
            "type": "savings",
            "available_balance": Decimal("2000.00"),
        },
        {
            "name": "Bulk Account 3",
            "type": "credit",
            "available_balance": Decimal("-500.00"),
            "total_limit": Decimal("5000.00"),
        },
    ]

    # Act
    created_accounts = await repo.bulk_create(bulk_data)

    # Assert
    assert len(created_accounts) == 3
    assert all(account.id is not None for account in created_accounts)
    assert created_accounts[0].name == "Bulk Account 1"
    assert created_accounts[1].type == "savings"
    assert created_accounts[2].available_balance == Decimal("-500.00")


async def test_bulk_update(db_session: AsyncSession):
    """Test updating multiple records in a batch."""
    # Arrange
    repo = BaseRepository(db_session, Account)

    # Create test accounts
    account_ids = []
    for i in range(3):
        account_data = AccountCreate(
            name=f"Bulk Update Test {i}",
            type="checking",
            available_balance=Decimal(f"{i}000.00"),
        )
        account = await repo.create(account_data.model_dump())
        account_ids.append(account.id)

    # Act - Update all accounts' available balance
    update_data = {"available_balance": Decimal("9999.00")}
    updated_accounts = await repo.bulk_update(account_ids, update_data)

    # Assert
    assert len(updated_accounts) == 3
    assert all(account is not None for account in updated_accounts)
    assert all(
        account.available_balance == Decimal("9999.00") for account in updated_accounts
    )


async def test_transaction_commit(db_session: AsyncSession):
    """Test transaction context manager with successful commit."""
    # Arrange
    repo = BaseRepository(db_session, Account)

    # Act
    async with repo.transaction() as tx_repo:
        # Create account within transaction
        account_data = AccountCreate(
            name="Transaction Test",
            type="checking",
            available_balance=Decimal("1000.00"),
        )
        account = await tx_repo.create(account_data.model_dump())

    # Outside transaction, verify account was created
    retrieved_account = await repo.get(account.id)

    # Assert
    assert retrieved_account is not None
    assert retrieved_account.name == "Transaction Test"


async def test_transaction_rollback(db_session: AsyncSession):
    """Test transaction context manager with rollback on exception."""
    # Arrange
    repo = BaseRepository(db_session, Account)
    account_name = f"Rollback Test {datetime.now(timezone.utc).isoformat()}"

    # Act
    try:
        async with repo.transaction() as tx_repo:
            # Create account within transaction
            account_data = AccountCreate(
                name=account_name,
                type="checking",
                available_balance=Decimal("1000.00"),
            )
            await tx_repo.create(account_data.model_dump())

            # Raise exception to trigger rollback
            raise ValueError("Test exception to trigger rollback")
    except ValueError:
        pass  # Expected exception

    # Outside transaction, verify account was not created
    result = await db_session.execute(
        select(Account).where(Account.name == account_name)
    )
    account = result.scalars().first()

    # Assert
    assert account is None  # Transaction was rolled back
