"""
Unit tests for the BaseRepository class.

These tests validate the core functionality of the BaseRepository with real database fixtures.
"""

# pylint: disable=no-member

from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.repositories.base_repository import BaseRepository
from src.utils.datetime_utils import utc_now
from tests.helpers.models.test_basic_db_model import TestBasicDBModel
from tests.helpers.schema_factories.basic_test_schema_factories import (
    create_test_item_schema,
    create_test_item_update_schema,
)

pytestmark = pytest.mark.integration


async def test_create(db_session: AsyncSession):
    """Test creating a new record using a repository."""
    # Arrange
    repo = BaseRepository(db_session, TestBasicDBModel)

    # Schema (simulate service validation)
    item_data = create_test_item_schema(
        name="Test Item",
        description="Test description",
        numeric_value=Decimal("100.00"),
    )

    # Act
    item = await repo.create(item_data.model_dump())

    # Assert
    assert item.id is not None
    assert item.name == "Test Item"
    assert item.description == "Test description"
    assert item.numeric_value == Decimal("100.00")


async def test_get(test_item_repository: BaseRepository, test_item: TestBasicDBModel):
    """Test retrieving a record by ID."""
    # Act
    retrieved_item = await test_item_repository.get(test_item.id)

    # Assert
    assert retrieved_item is not None
    assert retrieved_item.id == test_item.id
    assert retrieved_item.name == test_item.name


async def test_get_nonexistent(test_item_repository: BaseRepository):
    """Test retrieving a nonexistent record returns None."""
    # Act
    retrieved_item = await test_item_repository.get(9999)  # Nonexistent ID

    # Assert
    assert retrieved_item is None


async def test_update(
    test_item_repository: BaseRepository, test_item: TestBasicDBModel
):
    """Test updating a record."""
    # Arrange
    update_data = create_test_item_update_schema(
        name="Updated Item Name", numeric_value=Decimal("200.00")
    )

    # Act
    updated_item = await test_item_repository.update(
        test_item.id, update_data.model_dump()
    )

    # Assert
    assert updated_item is not None
    assert updated_item.id == test_item.id
    assert updated_item.name == "Updated Item Name"
    assert updated_item.description == test_item.description  # Unchanged
    assert updated_item.numeric_value == Decimal("200.00")


async def test_update_nonexistent(test_item_repository: BaseRepository):
    """Test updating a nonexistent record returns None."""
    # Arrange
    update_data = create_test_item_update_schema(
        name="Updated Item Name", numeric_value=Decimal("200.00")
    )

    # Act
    updated_item = await test_item_repository.update(
        9999, update_data.model_dump()
    )  # Nonexistent ID

    # Assert
    assert updated_item is None


async def test_delete(db_session: AsyncSession):
    """Test deleting a record."""
    # Arrange
    repo = BaseRepository(db_session, TestBasicDBModel)

    # Create test item
    item_data = create_test_item_schema(
        name="Delete Test Item",
        description="Item to delete",
        numeric_value=Decimal("100.00"),
    )
    created_item = await repo.create(item_data.model_dump())

    # Verify item exists
    assert await repo.get(created_item.id) is not None

    # Act
    deleted = await repo.delete(created_item.id)

    # Assert
    assert deleted is True
    assert await repo.get(created_item.id) is None


async def test_delete_nonexistent(test_item_repository: BaseRepository):
    """Test deleting a nonexistent record returns False."""
    # Act
    deleted = await test_item_repository.delete(9999)  # Nonexistent ID

    # Assert
    assert deleted is False


async def test_get_multi(db_session: AsyncSession):
    """Test retrieving multiple records with filtering."""
    # Arrange
    repo = BaseRepository(db_session, TestBasicDBModel)

    # Create test items
    item_data_1 = create_test_item_schema(
        name="Test Item 1",
        description="Active item",
        numeric_value=Decimal("100.00"),
        is_active=True,
    )
    item_data_2 = create_test_item_schema(
        name="Test Item 2",
        description="Inactive item",
        numeric_value=Decimal("200.00"),
        is_active=False,
    )
    item_data_3 = create_test_item_schema(
        name="Test Item 3",
        description="Another active item",
        numeric_value=Decimal("300.00"),
        is_active=True,
    )

    await repo.create(item_data_1.model_dump())
    await repo.create(item_data_2.model_dump())
    await repo.create(item_data_3.model_dump())

    # Act
    active_items = await repo.get_multi(filters={"is_active": True})

    # Assert
    assert len(active_items) >= 2  # At least our created test items
    assert all(item.is_active for item in active_items)


async def test_get_multi_with_skip_and_limit(
    test_item_repository: BaseRepository, test_items: list
):
    """Test pagination with skip and limit parameters."""
    # Act - Get second page (skip first 2, limit to 2)
    page = await test_item_repository.get_multi(skip=2, limit=2)

    # Assert
    assert len(page) == 2


async def test_get_paginated(db_session: AsyncSession):
    """Test paginated results with total count."""
    # Arrange
    repo = BaseRepository(db_session, TestBasicDBModel)

    # Create 5 test items with the same active status for filtering
    for i in range(5):
        item_data = create_test_item_schema(
            name=f"Pagination Total Test {i}",
            description=f"Pagination test item {i}",
            numeric_value=Decimal(f"{i}00.00"),
            is_active=True,
        )
        await repo.create(item_data.model_dump())

    # Act - Get first page with filter
    items, total = await repo.get_paginated(
        page=1, items_per_page=3, filters={"is_active": True}
    )

    # Assert
    assert len(items) == 3  # First page limited to 3 items
    assert total >= 5  # At least our created items


async def test_bulk_create(db_session: AsyncSession):
    """Test creating multiple records in a batch."""
    # Arrange
    repo = BaseRepository(db_session, TestBasicDBModel)

    # Prepare bulk data with schema factories
    bulk_data = [
        create_test_item_schema(
            name="Bulk Item 1",
            description="First bulk item",
            numeric_value=Decimal("100.00"),
            is_active=True,
        ).model_dump(),
        create_test_item_schema(
            name="Bulk Item 2",
            description="Second bulk item",
            numeric_value=Decimal("200.00"),
            is_active=True,
        ).model_dump(),
        create_test_item_schema(
            name="Bulk Item 3",
            description="Third bulk item",
            numeric_value=Decimal("300.00"),
            is_active=False,
        ).model_dump(),
    ]

    # Act
    created_items = await repo.bulk_create(bulk_data)

    # Assert
    assert len(created_items) == 3
    assert all(item.id is not None for item in created_items)
    assert created_items[0].name == "Bulk Item 1"
    assert created_items[1].description == "Second bulk item"
    assert created_items[2].numeric_value == Decimal("300.00")


async def test_bulk_update(db_session: AsyncSession):
    """Test updating multiple records in a batch."""
    # Arrange
    repo = BaseRepository(db_session, TestBasicDBModel)

    # Create test items
    item_ids = []
    for i in range(3):
        item_data = create_test_item_schema(
            name=f"Bulk Update Test {i}",
            description=f"Item for bulk update {i}",
            numeric_value=Decimal(f"{i}00.00"),
        )
        item = await repo.create(item_data.model_dump())
        item_ids.append(item.id)

    # Act - Update all items' numeric value using update schema
    update_data = create_test_item_update_schema(
        numeric_value=Decimal("999.00")
    ).model_dump()
    updated_items = await repo.bulk_update(item_ids, update_data)

    # Assert
    assert len(updated_items) == 3
    assert all(item is not None for item in updated_items)
    assert all(item.numeric_value == Decimal("999.00") for item in updated_items)


async def test_transaction_commit(db_session: AsyncSession):
    """Test transaction context manager with successful commit."""
    # Arrange
    repo = BaseRepository(db_session, TestBasicDBModel)

    # Act
    async with repo.transaction() as tx_repo:
        # Create item within transaction
        item_data = create_test_item_schema(
            name="Transaction Test",
            description="Item created in transaction",
            numeric_value=Decimal("100.00"),
        )
        item = await tx_repo.create(item_data.model_dump())

    # Outside transaction, verify item was created
    retrieved_item = await repo.get(item.id)

    # Assert
    assert retrieved_item is not None
    assert retrieved_item.name == "Transaction Test"


async def test_transaction_rollback(db_session: AsyncSession):
    """Test transaction context manager with rollback on exception."""
    # Arrange
    repo = BaseRepository(db_session, TestBasicDBModel)
    current_time = utc_now()
    item_name = f"Rollback Test {current_time.isoformat()}"

    # Act
    try:
        async with repo.transaction() as tx_repo:
            # Create item within transaction
            item_data = create_test_item_schema(
                name=item_name,
                description="Item that should be rolled back",
                numeric_value=Decimal("100.00"),
            )
            await tx_repo.create(item_data.model_dump())

            # Raise exception to trigger rollback
            raise ValueError("Test exception to trigger rollback")
    except ValueError:
        pass  # Expected exception

    # Outside transaction, verify item was not created
    result = await db_session.execute(
        select(TestBasicDBModel).where(TestBasicDBModel.name == item_name)
    )
    item = result.scalars().first()

    # Assert
    assert item is None  # Transaction was rolled back
