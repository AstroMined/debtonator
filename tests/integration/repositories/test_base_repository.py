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


@pytest.mark.asyncio
async def test_create(db_session: AsyncSession):
    """
    Test creating a new record using a repository.
    
    This test verifies that the BaseRepository.create method correctly
    creates a new record in the database with the provided data.
    
    Args:
        db_session: Database session for repository operations
    """
    # 1. ARRANGE: Set up repository
    repo = BaseRepository(db_session, TestBasicDBModel)

    # 2. SCHEMA: Create and validate through schema factory
    item_data = create_test_item_schema(
        name="Test Item",
        description="Test description",
        numeric_value=Decimal("100.00"),
    )

    # 3. ACT: Pass validated data to repository
    item = await repo.create(item_data.model_dump())

    # 4. ASSERT: Verify the operation results
    assert item.id is not None
    assert item.name == "Test Item"
    assert item.description == "Test description"
    assert item.numeric_value == Decimal("100.00")


@pytest.mark.asyncio
async def test_get(test_item_repository: BaseRepository, test_item: TestBasicDBModel):
    """
    Test retrieving a record by ID.
    
    This test verifies that the BaseRepository.get method correctly
    retrieves a record from the database by its ID.
    
    Args:
        test_item_repository: Repository for TestBasicDBModel
        test_item: Test item fixture
    """
    # 1. ARRANGE: Repository and test item are provided by fixtures

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Retrieve the item by ID
    retrieved_item = await test_item_repository.get(test_item.id)

    # 4. ASSERT: Verify the operation results
    assert retrieved_item is not None
    assert retrieved_item.id == test_item.id
    assert retrieved_item.name == test_item.name


@pytest.mark.asyncio
async def test_get_nonexistent(test_item_repository: BaseRepository):
    """
    Test retrieving a nonexistent record returns None.
    
    This test verifies that the BaseRepository.get method correctly
    returns None when attempting to retrieve a nonexistent record.
    
    Args:
        test_item_repository: Repository for TestBasicDBModel
    """
    # 1. ARRANGE: Repository is provided by fixture

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Attempt to retrieve a nonexistent item
    retrieved_item = await test_item_repository.get(9999)  # Nonexistent ID

    # 4. ASSERT: Verify the operation results
    assert retrieved_item is None


@pytest.mark.asyncio
async def test_update(
    test_item_repository: BaseRepository, test_item: TestBasicDBModel
):
    """
    Test updating a record.
    
    This test verifies that the BaseRepository.update method correctly
    updates a record in the database with the provided data.
    
    Args:
        test_item_repository: Repository for TestBasicDBModel
        test_item: Test item fixture
    """
    # 1. ARRANGE: Repository and test item are provided by fixtures

    # 2. SCHEMA: Create and validate through schema factory
    update_data = create_test_item_update_schema(
        name="Updated Item Name", numeric_value=Decimal("200.00")
    )

    # 3. ACT: Pass validated data to repository
    updated_item = await test_item_repository.update(
        test_item.id, update_data.model_dump()
    )

    # 4. ASSERT: Verify the operation results
    assert updated_item is not None
    assert updated_item.id == test_item.id
    assert updated_item.name == "Updated Item Name"
    assert updated_item.description == test_item.description  # Unchanged
    assert updated_item.numeric_value == Decimal("200.00")


@pytest.mark.asyncio
async def test_update_nonexistent(test_item_repository: BaseRepository):
    """
    Test updating a nonexistent record returns None.
    
    This test verifies that the BaseRepository.update method correctly
    returns None when attempting to update a nonexistent record.
    
    Args:
        test_item_repository: Repository for TestBasicDBModel
    """
    # 1. ARRANGE: Repository is provided by fixture

    # 2. SCHEMA: Create and validate through schema factory
    update_data = create_test_item_update_schema(
        name="Updated Item Name", numeric_value=Decimal("200.00")
    )

    # 3. ACT: Attempt to update a nonexistent item
    updated_item = await test_item_repository.update(
        9999, update_data.model_dump()
    )  # Nonexistent ID

    # 4. ASSERT: Verify the operation results
    assert updated_item is None


@pytest.mark.asyncio
async def test_delete(db_session: AsyncSession):
    """
    Test deleting a record.
    
    This test verifies that the BaseRepository.delete method correctly
    deletes a record from the database.
    
    Args:
        db_session: Database session for repository operations
    """
    # 1. ARRANGE: Set up repository and create test item
    repo = BaseRepository(db_session, TestBasicDBModel)

    # 2. SCHEMA: Create and validate through schema factory
    item_data = create_test_item_schema(
        name="Delete Test Item",
        description="Item to delete",
        numeric_value=Decimal("100.00"),
    )
    
    # Create item to delete
    created_item = await repo.create(item_data.model_dump())

    # Verify item exists
    assert await repo.get(created_item.id) is not None

    # 3. ACT: Delete the item
    deleted = await repo.delete(created_item.id)

    # 4. ASSERT: Verify the operation results
    assert deleted is True
    assert await repo.get(created_item.id) is None


@pytest.mark.asyncio
async def test_delete_nonexistent(test_item_repository: BaseRepository):
    """
    Test deleting a nonexistent record returns False.
    
    This test verifies that the BaseRepository.delete method correctly
    returns False when attempting to delete a nonexistent record.
    
    Args:
        test_item_repository: Repository for TestBasicDBModel
    """
    # 1. ARRANGE: Repository is provided by fixture

    # 2. SCHEMA: Not applicable for this operation

    # 3. ACT: Attempt to delete a nonexistent item
    deleted = await test_item_repository.delete(9999)  # Nonexistent ID

    # 4. ASSERT: Verify the operation results
    assert deleted is False


@pytest.mark.asyncio
async def test_get_multi(db_session: AsyncSession):
    """
    Test retrieving multiple records with filtering.
    
    This test verifies that the BaseRepository.get_multi method correctly
    retrieves multiple records from the database with filtering.
    
    Args:
        db_session: Database session for repository operations
    """
    # 1. ARRANGE: Set up repository and create test items
    repo = BaseRepository(db_session, TestBasicDBModel)

    # 2. SCHEMA: Create and validate through schema factory
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

    # Create test items
    await repo.create(item_data_1.model_dump())
    await repo.create(item_data_2.model_dump())
    await repo.create(item_data_3.model_dump())

    # 3. ACT: Retrieve active items
    active_items = await repo.get_multi(filters={"is_active": True})

    # 4. ASSERT: Verify the operation results
    assert len(active_items) >= 2  # At least our created test items
    assert all(item.is_active for item in active_items)


@pytest.mark.asyncio
async def test_get_multi_with_skip_and_limit(
    test_item_repository: BaseRepository, test_items: list
):
    """
    Test pagination with skip and limit parameters.
    
    This test verifies that the BaseRepository.get_multi method correctly
    implements pagination with skip and limit parameters.
    
    Args:
        test_item_repository: Repository for TestBasicDBModel
        test_items: List of test items
    """
    # 1. ARRANGE: Repository and test items are provided by fixtures

    # 2. SCHEMA: Not applicable for this read operation

    # 3. ACT: Get second page (skip first 2, limit to 2)
    page = await test_item_repository.get_multi(skip=2, limit=2)

    # 4. ASSERT: Verify the operation results
    assert len(page) == 2


@pytest.mark.asyncio
async def test_get_paginated(db_session: AsyncSession):
    """
    Test paginated results with total count.
    
    This test verifies that the BaseRepository.get_paginated method correctly
    returns paginated results with a total count.
    
    Args:
        db_session: Database session for repository operations
    """
    # 1. ARRANGE: Set up repository and create test items
    repo = BaseRepository(db_session, TestBasicDBModel)

    # 2. SCHEMA: Create and validate through schema factory
    # Create 5 test items with the same active status for filtering
    for i in range(5):
        item_data = create_test_item_schema(
            name=f"Pagination Total Test {i}",
            description=f"Pagination test item {i}",
            numeric_value=Decimal(f"{i}00.00"),
            is_active=True,
        )
        await repo.create(item_data.model_dump())

    # 3. ACT: Get first page with filter
    items, total = await repo.get_paginated(
        page=1, items_per_page=3, filters={"is_active": True}
    )

    # 4. ASSERT: Verify the operation results
    assert len(items) == 3  # First page limited to 3 items
    assert total >= 5  # At least our created items


@pytest.mark.asyncio
async def test_bulk_create(db_session: AsyncSession):
    """
    Test creating multiple records in a batch.
    
    This test verifies that the BaseRepository.bulk_create method correctly
    creates multiple records in the database in a single operation.
    
    Args:
        db_session: Database session for repository operations
    """
    # 1. ARRANGE: Set up repository
    repo = BaseRepository(db_session, TestBasicDBModel)

    # 2. SCHEMA: Create and validate through schema factory
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

    # 3. ACT: Create multiple items in a batch
    created_items = await repo.bulk_create(bulk_data)

    # 4. ASSERT: Verify the operation results
    assert len(created_items) == 3
    assert all(item.id is not None for item in created_items)
    assert created_items[0].name == "Bulk Item 1"
    assert created_items[1].description == "Second bulk item"
    assert created_items[2].numeric_value == Decimal("300.00")


@pytest.mark.asyncio
async def test_bulk_update(db_session: AsyncSession):
    """
    Test updating multiple records in a batch.
    
    This test verifies that the BaseRepository.bulk_update method correctly
    updates multiple records in the database in a single operation.
    
    Args:
        db_session: Database session for repository operations
    """
    # 1. ARRANGE: Set up repository and create test items
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

    # 2. SCHEMA: Create and validate through schema factory
    update_data = create_test_item_update_schema(
        numeric_value=Decimal("999.00")
    ).model_dump()

    # 3. ACT: Update all items' numeric value
    updated_items = await repo.bulk_update(item_ids, update_data)

    # 4. ASSERT: Verify the operation results
    assert len(updated_items) == 3
    assert all(item is not None for item in updated_items)
    assert all(item.numeric_value == Decimal("999.00") for item in updated_items)


@pytest.mark.asyncio
async def test_transaction_commit(db_session: AsyncSession):
    """
    Test transaction context manager with successful commit.
    
    This test verifies that the BaseRepository.transaction context manager
    correctly commits changes to the database when no exceptions are raised.
    
    Args:
        db_session: Database session for repository operations
    """
    # 1. ARRANGE: Set up repository
    repo = BaseRepository(db_session, TestBasicDBModel)

    # 2. SCHEMA: Create and validate through schema factory
    item_data = create_test_item_schema(
        name="Transaction Test",
        description="Item created in transaction",
        numeric_value=Decimal("100.00"),
    )

    # 3. ACT: Create item within transaction
    async with repo.transaction() as tx_repo:
        item = await tx_repo.create(item_data.model_dump())

    # 4. ASSERT: Verify the operation results (outside transaction)
    retrieved_item = await repo.get(item.id)
    assert retrieved_item is not None
    assert retrieved_item.name == "Transaction Test"


@pytest.mark.asyncio
async def test_transaction_rollback(db_session: AsyncSession):
    """
    Test transaction context manager with rollback on exception.
    
    This test verifies that the BaseRepository.transaction context manager
    correctly rolls back changes to the database when an exception is raised.
    
    Args:
        db_session: Database session for repository operations
    """
    # 1. ARRANGE: Set up repository
    repo = BaseRepository(db_session, TestBasicDBModel)
    current_time = utc_now()
    item_name = f"Rollback Test {current_time.isoformat()}"

    # 2. SCHEMA: Create and validate through schema factory
    item_data = create_test_item_schema(
        name=item_name,
        description="Item that should be rolled back",
        numeric_value=Decimal("100.00"),
    )

    # 3. ACT: Create item within transaction and raise exception
    try:
        async with repo.transaction() as tx_repo:
            await tx_repo.create(item_data.model_dump())
            # Raise exception to trigger rollback
            raise ValueError("Test exception to trigger rollback")
    except ValueError:
        pass  # Expected exception

    # 4. ASSERT: Verify the operation results (transaction was rolled back)
    result = await db_session.execute(
        select(TestBasicDBModel).where(TestBasicDBModel.name == item_name)
    )
    item = result.scalars().first()
    assert item is None  # Transaction was rolled back
