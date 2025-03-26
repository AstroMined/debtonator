"""
Integration tests for CategoryRepository.

This module contains tests that validate the behavior of the CategoryRepository
against a real database.
"""

from datetime import datetime, timezone
from decimal import Decimal

import pytest
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from src.constants import (DEFAULT_CATEGORY_DESCRIPTION, DEFAULT_CATEGORY_ID,
                           DEFAULT_CATEGORY_NAME)
from src.models.categories import Category
from src.models.liabilities import Liability
from src.repositories.categories import CategoryRepository
from src.repositories.liabilities import LiabilityRepository
from src.utils.datetime_utils import utc_datetime

pytestmark = pytest.mark.asyncio


async def test_get_by_name(db_session: AsyncSession):
    """Test retrieving a category by name."""
    # Create repository
    repo = CategoryRepository(db_session)

    # Create category
    await repo.create(
        {"name": "Unique Category Name", "description": "Test category description"}
    )

    # Test get_by_name
    category = await repo.get_by_name("Unique Category Name")

    # Assert
    assert category is not None
    assert category.name == "Unique Category Name"
    assert category.description == "Test category description"

    # Test non-existent category
    non_existent = await repo.get_by_name("Non Existent Category")
    assert non_existent is None


async def test_get_root_categories(db_session: AsyncSession):
    """Test retrieving all root categories."""
    # Create repository
    repo = CategoryRepository(db_session)

    # Create root categories
    root1 = await repo.create(
        {"name": "Root Category 1", "description": "First root category"}
    )

    root2 = await repo.create(
        {"name": "Root Category 2", "description": "Second root category"}
    )

    # Create a child category
    child = await repo.create(
        {
            "name": "Child Category",
            "description": "Child of Root Category 1",
            "parent_id": root1.id,
        }
    )

    # Test get_root_categories
    root_categories = await repo.get_root_categories()

    # Assert
    assert len(root_categories) >= 2  # Could be more if other tests created categories
    assert any(cat.id == root1.id for cat in root_categories)
    assert any(cat.id == root2.id for cat in root_categories)
    assert not any(cat.id == child.id for cat in root_categories)


async def test_get_with_children(db_session: AsyncSession):
    """Test retrieving a category with its children."""
    # Create repository
    repo = CategoryRepository(db_session)

    # Create parent category
    parent = await repo.create(
        {"name": "Parent Category", "description": "Parent category"}
    )

    # Create child categories
    child1 = await repo.create(
        {
            "name": "Child Category 1",
            "description": "First child category",
            "parent_id": parent.id,
        }
    )

    child2 = await repo.create(
        {
            "name": "Child Category 2",
            "description": "Second child category",
            "parent_id": parent.id,
        }
    )

    # Test get_with_children
    category_with_children = await repo.get_with_children(parent.id)

    # Assert
    assert category_with_children is not None
    assert category_with_children.id == parent.id
    assert category_with_children.children is not None
    assert len(category_with_children.children) == 2
    assert any(child.id == child1.id for child in category_with_children.children)
    assert any(child.id == child2.id for child in category_with_children.children)


async def test_get_with_parent(db_session: AsyncSession):
    """Test retrieving a category with its parent."""
    # Create repository
    repo = CategoryRepository(db_session)

    # Create parent category
    parent = await repo.create(
        {"name": "Parent For Child", "description": "Parent category"}
    )

    # Create child category
    child = await repo.create(
        {
            "name": "Child With Parent",
            "description": "Child category",
            "parent_id": parent.id,
        }
    )

    # Test get_with_parent
    category_with_parent = await repo.get_with_parent(child.id)

    # Assert
    assert category_with_parent is not None
    assert category_with_parent.id == child.id
    assert category_with_parent.parent is not None
    assert category_with_parent.parent.id == parent.id
    assert category_with_parent.parent.name == "Parent For Child"


async def test_get_with_bills(db_session: AsyncSession):
    """Test retrieving a category with its bills."""
    # Create repositories
    category_repo = CategoryRepository(db_session)
    liability_repo = LiabilityRepository(db_session)

    # Create category
    category = await category_repo.create(
        {"name": "Bills Category", "description": "Category with bills"}
    )

    # Create bills (liabilities)
    bill1 = await liability_repo.create(
        {
            "name": "Bill 1",
            "amount": Decimal("100.00"),
            "due_date": utc_datetime(2025, 4, 15),
            "category_id": category.id,
        }
    )

    bill2 = await liability_repo.create(
        {
            "name": "Bill 2",
            "amount": Decimal("200.00"),
            "due_date": utc_datetime(2025, 4, 30),
            "category_id": category.id,
        }
    )

    # Test get_with_bills
    category_with_bills = await category_repo.get_with_bills(category.id)

    # Assert
    assert category_with_bills is not None
    assert category_with_bills.id == category.id
    assert category_with_bills.bills is not None
    assert len(category_with_bills.bills) == 2
    assert any(bill.id == bill1.id for bill in category_with_bills.bills)
    assert any(bill.id == bill2.id for bill in category_with_bills.bills)


async def test_get_with_relationships(db_session: AsyncSession):
    """Test retrieving a category with specified relationships."""
    # Create repositories
    category_repo = CategoryRepository(db_session)
    liability_repo = LiabilityRepository(db_session)

    # Create categories
    parent = await category_repo.create(
        {"name": "Relationships Parent", "description": "Parent category"}
    )

    child = await category_repo.create(
        {
            "name": "Relationships Child",
            "description": "Child category",
            "parent_id": parent.id,
        }
    )

    # Create bill for child category
    bill = await liability_repo.create(
        {
            "name": "Relationship Bill",
            "amount": Decimal("150.00"),
            "due_date": utc_datetime(2025, 5, 15),
            "category_id": child.id,
        }
    )

    # Test get_with_relationships with different combinations
    cat_with_parent = await category_repo.get_with_relationships(
        child.id, include_parent=True
    )

    cat_with_bills = await category_repo.get_with_relationships(
        child.id, include_bills=True
    )

    cat_with_all = await category_repo.get_with_relationships(
        child.id, include_parent=True, include_bills=True
    )

    # Assert
    assert cat_with_parent.parent is not None
    assert cat_with_parent.parent.id == parent.id
    assert not hasattr(cat_with_parent, "bills") or len(cat_with_parent.bills) == 0

    assert cat_with_bills.bills is not None
    assert len(cat_with_bills.bills) == 1
    assert cat_with_bills.bills[0].id == bill.id
    assert cat_with_bills.parent is None

    assert cat_with_all.parent is not None
    assert cat_with_all.parent.id == parent.id
    assert cat_with_all.bills is not None
    assert len(cat_with_all.bills) == 1
    assert cat_with_all.bills[0].id == bill.id


async def test_get_children(db_session: AsyncSession):
    """Test retrieving immediate children of a category."""
    # Create repository
    repo = CategoryRepository(db_session)

    # Create parent category
    parent = await repo.create(
        {"name": "Get Children Parent", "description": "Parent category"}
    )

    # Create child categories
    child1 = await repo.create(
        {
            "name": "Get Children Child 1",
            "description": "First child category",
            "parent_id": parent.id,
        }
    )

    child2 = await repo.create(
        {
            "name": "Get Children Child 2",
            "description": "Second child category",
            "parent_id": parent.id,
        }
    )

    # Create grandchild category
    grandchild = await repo.create(
        {
            "name": "Get Children Grandchild",
            "description": "Grandchild category",
            "parent_id": child1.id,
        }
    )

    # Test get_children
    children = await repo.get_children(parent.id)

    # Assert
    assert len(children) == 2
    assert any(child.id == child1.id for child in children)
    assert any(child.id == child2.id for child in children)
    assert not any(child.id == grandchild.id for child in children)


async def test_get_ancestors(db_session: AsyncSession):
    """Test retrieving all ancestors of a category."""
    # Create repository
    repo = CategoryRepository(db_session)

    # Create category hierarchy
    grandparent = await repo.create(
        {"name": "Ancestor Grandparent", "description": "Grandparent category"}
    )

    parent = await repo.create(
        {
            "name": "Ancestor Parent",
            "description": "Parent category",
            "parent_id": grandparent.id,
        }
    )

    child = await repo.create(
        {
            "name": "Ancestor Child",
            "description": "Child category",
            "parent_id": parent.id,
        }
    )

    # Test get_ancestors
    ancestors = await repo.get_ancestors(child.id)

    # Assert
    assert len(ancestors) == 2
    assert ancestors[0].id == parent.id  # Direct parent first
    assert ancestors[1].id == grandparent.id


async def test_get_descendants(db_session: AsyncSession):
    """Test retrieving all descendants of a category."""
    # Create repository
    repo = CategoryRepository(db_session)

    # Create category hierarchy
    grandparent = await repo.create(
        {"name": "Descendant Grandparent", "description": "Grandparent category"}
    )

    parent1 = await repo.create(
        {
            "name": "Descendant Parent 1",
            "description": "First parent category",
            "parent_id": grandparent.id,
        }
    )

    parent2 = await repo.create(
        {
            "name": "Descendant Parent 2",
            "description": "Second parent category",
            "parent_id": grandparent.id,
        }
    )

    child1 = await repo.create(
        {
            "name": "Descendant Child 1",
            "description": "First child category",
            "parent_id": parent1.id,
        }
    )

    child2 = await repo.create(
        {
            "name": "Descendant Child 2",
            "description": "Second child category",
            "parent_id": parent2.id,
        }
    )

    # Test get_descendants
    descendants = await repo.get_descendants(grandparent.id)

    # Assert
    assert len(descendants) == 4
    assert any(desc.id == parent1.id for desc in descendants)
    assert any(desc.id == parent2.id for desc in descendants)
    assert any(desc.id == child1.id for desc in descendants)
    assert any(desc.id == child2.id for desc in descendants)


async def test_is_ancestor_of(db_session: AsyncSession):
    """Test checking if a category is an ancestor of another category."""
    # Create repository
    repo = CategoryRepository(db_session)

    # Create category hierarchy
    grandparent = await repo.create(
        {"name": "Is Ancestor Grandparent", "description": "Grandparent category"}
    )

    parent = await repo.create(
        {
            "name": "Is Ancestor Parent",
            "description": "Parent category",
            "parent_id": grandparent.id,
        }
    )

    child = await repo.create(
        {
            "name": "Is Ancestor Child",
            "description": "Child category",
            "parent_id": parent.id,
        }
    )

    unrelated = await repo.create(
        {"name": "Is Ancestor Unrelated", "description": "Unrelated category"}
    )

    # Test is_ancestor_of
    is_grandparent_ancestor_of_child = await repo.is_ancestor_of(
        grandparent.id, child.id
    )
    is_parent_ancestor_of_child = await repo.is_ancestor_of(parent.id, child.id)
    is_child_ancestor_of_parent = await repo.is_ancestor_of(child.id, parent.id)
    is_unrelated_ancestor_of_child = await repo.is_ancestor_of(unrelated.id, child.id)
    is_self_ancestor = await repo.is_ancestor_of(child.id, child.id)

    # Assert
    assert is_grandparent_ancestor_of_child is True
    assert is_parent_ancestor_of_child is True
    assert is_child_ancestor_of_parent is False
    assert is_unrelated_ancestor_of_child is False
    assert is_self_ancestor is False  # A category is not its own ancestor


async def test_move_category(db_session: AsyncSession):
    """Test moving a category to a new parent."""
    # Create repository
    repo = CategoryRepository(db_session)

    # Create categories
    original_parent = await repo.create(
        {"name": "Move Original Parent", "description": "Original parent category"}
    )

    new_parent = await repo.create(
        {"name": "Move New Parent", "description": "New parent category"}
    )

    child = await repo.create(
        {
            "name": "Move Child",
            "description": "Child category",
            "parent_id": original_parent.id,
        }
    )

    # Test move_category
    moved_child = await repo.move_category(child.id, new_parent.id)

    # Assert
    assert moved_child is not None
    assert moved_child.parent_id == new_parent.id

    # Verify by getting with parent
    child_with_parent = await repo.get_with_parent(child.id)
    assert child_with_parent.parent.id == new_parent.id

    # Test moving to root (no parent)
    root_child = await repo.move_category(child.id, None)
    assert root_child.parent_id is None


async def test_get_category_path(db_session: AsyncSession):
    """Test getting the full path of a category."""
    # Create repository
    repo = CategoryRepository(db_session)

    # Create category hierarchy
    grandparent = await repo.create(
        {"name": "Path Grandparent", "description": "Grandparent category"}
    )

    parent = await repo.create(
        {
            "name": "Path Parent",
            "description": "Parent category",
            "parent_id": grandparent.id,
        }
    )

    child = await repo.create(
        {"name": "Path Child", "description": "Child category", "parent_id": parent.id}
    )

    # Test get_category_path
    child_path = await repo.get_category_path(child.id)
    parent_path = await repo.get_category_path(parent.id)
    grandparent_path = await repo.get_category_path(grandparent.id)

    # Assert
    assert child_path == "Path Grandparent > Path Parent > Path Child"
    assert parent_path == "Path Grandparent > Path Parent"
    assert grandparent_path == "Path Grandparent"


async def test_find_categories_by_prefix(db_session: AsyncSession):
    """Test finding categories whose names start with a given prefix."""
    # Create repository
    repo = CategoryRepository(db_session)

    # Create categories
    await repo.create({"name": "Prefix Test One", "description": "First test category"})

    await repo.create(
        {"name": "Prefix Test Two", "description": "Second test category"}
    )

    await repo.create({"name": "Other Category", "description": "Other category"})

    # Test find_categories_by_prefix
    prefix_matches = await repo.find_categories_by_prefix("Prefix")

    # Assert
    assert len(prefix_matches) == 2
    assert any(cat.name == "Prefix Test One" for cat in prefix_matches)
    assert any(cat.name == "Prefix Test Two" for cat in prefix_matches)
    assert not any(cat.name == "Other Category" for cat in prefix_matches)


async def test_get_category_with_bill_count(db_session: AsyncSession):
    """Test getting a category with the count of bills assigned to it."""
    # Create repositories
    category_repo = CategoryRepository(db_session)
    liability_repo = LiabilityRepository(db_session)

    # Create category
    category = await category_repo.create(
        {"name": "Bill Count Category", "description": "Category for bill count test"}
    )

    # Create bills
    await liability_repo.create(
        {
            "name": "Bill Count Bill 1",
            "amount": Decimal("100.00"),
            "due_date": utc_datetime(2025, 6, 15),
            "category_id": category.id,
        }
    )

    await liability_repo.create(
        {
            "name": "Bill Count Bill 2",
            "amount": Decimal("200.00"),
            "due_date": utc_datetime(2025, 6, 30),
            "category_id": category.id,
        }
    )

    # Test get_category_with_bill_count
    category_with_count, bill_count = await category_repo.get_category_with_bill_count(
        category.id
    )

    # Assert
    assert category_with_count is not None
    assert category_with_count.id == category.id
    assert bill_count == 2


async def test_get_categories_with_bill_counts(db_session: AsyncSession):
    """Test getting all categories with bill counts."""
    # Create repositories
    category_repo = CategoryRepository(db_session)
    liability_repo = LiabilityRepository(db_session)

    # Create categories
    category1 = await category_repo.create(
        {
            "name": "Bill Counts Category 1",
            "description": "First category for bill counts test",
        }
    )

    category2 = await category_repo.create(
        {
            "name": "Bill Counts Category 2",
            "description": "Second category for bill counts test",
        }
    )

    category3 = await category_repo.create(
        {
            "name": "Bill Counts Category 3",
            "description": "Third category for bill counts test",
        }
    )

    # Create bills
    await liability_repo.create(
        {
            "name": "Bill Counts Bill 1",
            "amount": Decimal("100.00"),
            "due_date": utc_datetime(2025, 7, 15),
            "category_id": category1.id,
        }
    )

    await liability_repo.create(
        {
            "name": "Bill Counts Bill 2",
            "amount": Decimal("200.00"),
            "due_date": utc_datetime(2025, 7, 30),
            "category_id": category1.id,
        }
    )

    await liability_repo.create(
        {
            "name": "Bill Counts Bill 3",
            "amount": Decimal("300.00"),
            "due_date": utc_datetime(2025, 8, 15),
            "category_id": category2.id,
        }
    )

    # Category3 has no bills

    # Test get_categories_with_bill_counts
    categories_with_counts = await category_repo.get_categories_with_bill_counts()

    # Assert
    assert len(categories_with_counts) >= 3  # Could be more from other tests

    # Find our test categories in the results
    category1_result = next(
        (item for item in categories_with_counts if item[0].id == category1.id), None
    )
    category2_result = next(
        (item for item in categories_with_counts if item[0].id == category2.id), None
    )
    category3_result = next(
        (item for item in categories_with_counts if item[0].id == category3.id), None
    )

    assert category1_result is not None
    assert category1_result[1] == 2

    assert category2_result is not None
    assert category2_result[1] == 1

    assert category3_result is not None
    assert category3_result[1] == 0


async def test_delete_if_unused(db_session: AsyncSession):
    """Test deleting a category only if it has no children and no bills."""
    # Create repositories
    category_repo = CategoryRepository(db_session)
    liability_repo = LiabilityRepository(db_session)

    # Create categories
    parent = await category_repo.create(
        {"name": "Delete Parent", "description": "Parent category"}
    )

    child = await category_repo.create(
        {
            "name": "Delete Child",
            "description": "Child category",
            "parent_id": parent.id,
        }
    )

    with_bill = await category_repo.create(
        {"name": "Delete With Bill", "description": "Category with bill"}
    )

    empty = await category_repo.create(
        {"name": "Delete Empty", "description": "Empty category"}
    )

    # Create bill
    await liability_repo.create(
        {
            "name": "Delete Bill",
            "amount": Decimal("100.00"),
            "due_date": utc_datetime(2025, 8, 15),
            "category_id": with_bill.id,
        }
    )

    # Test delete_if_unused
    parent_deleted = await category_repo.delete_if_unused(parent.id)
    with_bill_deleted = await category_repo.delete_if_unused(with_bill.id)
    empty_deleted = await category_repo.delete_if_unused(empty.id)

    # Assert
    assert parent_deleted is False  # Should not delete (has child)
    assert with_bill_deleted is False  # Should not delete (has bill)
    assert empty_deleted is True  # Should delete (no children, no bills)

    # Verify
    parent_check = await category_repo.get(parent.id)
    with_bill_check = await category_repo.get(with_bill.id)
    empty_check = await category_repo.get(empty.id)

    assert parent_check is not None
    assert with_bill_check is not None
    assert empty_check is None


async def test_get_default_category_id(db_session: AsyncSession):
    """Test retrieving the default 'Uncategorized' category ID."""
    # Create repository
    repo = CategoryRepository(db_session)

    # Get default category ID
    default_id = await repo.get_default_category_id()

    # Assert
    assert default_id == DEFAULT_CATEGORY_ID

    # Verify the category exists and has the correct attributes
    default_category = await repo.get(default_id)
    assert default_category is not None
    assert default_category.name == DEFAULT_CATEGORY_NAME
    assert default_category.description == DEFAULT_CATEGORY_DESCRIPTION
    assert default_category.system is True


async def test_system_category_protection(db_session: AsyncSession):
    """Test that system categories are protected from modification and deletion."""
    # Create repository
    repo = CategoryRepository(db_session)

    # Get default category ID
    default_id = await repo.get_default_category_id()

    # Attempt to modify the default category
    with pytest.raises(ValueError) as excinfo:
        await repo.update(default_id, {"name": "Modified Name"})
    assert "Cannot modify system category" in str(excinfo.value)

    # Attempt to delete the default category
    with pytest.raises(ValueError) as excinfo:
        await repo.delete(default_id)
    assert "Cannot delete system category" in str(excinfo.value)

    # Test delete_if_unused on system category
    can_delete = await repo.delete_if_unused(default_id)
    assert can_delete is False


async def test_create_system_category(db_session: AsyncSession):
    """Test creating a custom system category and verifying its protection."""
    # Create repository
    repo = CategoryRepository(db_session)

    # Create a system category
    system_category = await repo.create(
        {
            "name": "Test System Category",
            "description": "A test system category",
            "system": True,
        }
    )

    # Verify it was created correctly
    assert system_category.system is True

    # Attempt to modify
    with pytest.raises(ValueError):
        await repo.update(system_category.id, {"name": "Modified System Category"})

    # Attempt to delete
    with pytest.raises(ValueError):
        await repo.delete(system_category.id)


async def test_move_system_category(db_session: AsyncSession):
    """Test that system categories cannot be moved."""
    # Create repository
    repo = CategoryRepository(db_session)

    # Get default category ID
    default_id = await repo.get_default_category_id()

    # Create another category
    other_category = await repo.create(
        {
            "name": "Other Category for Move",
            "description": "Another category",
        }
    )

    # Attempt to move the default category
    with pytest.raises(ValueError) as excinfo:
        await repo.move_category(default_id, other_category.id)
    assert "Cannot move system category" in str(excinfo.value)
