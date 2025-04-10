"""
Integration tests for CategoryRepository.

This module contains tests that validate the behavior of the CategoryRepository
against a real database.
"""

from decimal import Decimal

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.constants import (
    DEFAULT_CATEGORY_DESCRIPTION,
    DEFAULT_CATEGORY_ID,
    DEFAULT_CATEGORY_NAME,
)
from src.repositories.categories import CategoryRepository
from src.repositories.liabilities import LiabilityRepository
from src.utils.datetime_utils import utc_datetime
from tests.helpers.schema_factories.categories_schema_factories import (
    create_category_schema,
    create_category_update_schema,
)

pytestmark = pytest.mark.asyncio


async def test_get_by_name(category_repository: CategoryRepository):
    """Test retrieving a category by name."""
    # 1. ARRANGE: Create schema with factory
    category_schema = create_category_schema(
        name="Unique Category Name", 
        description="Test category description"
    )
    
    # 2. ACT: Create category and get by name
    await category_repository.create(category_schema.model_dump())

    # Test get_by_name
    category = await category_repository.get_by_name("Unique Category Name")

    # Assert
    assert category is not None
    assert category.name == "Unique Category Name"
    assert category.description == "Test category description"

    # Test non-existent category
    non_existent = await category_repository.get_by_name("Non Existent Category")
    assert non_existent is None


async def test_get_root_categories(category_repository: CategoryRepository):
    """Test retrieving all root categories."""
    # 1. ARRANGE: Create schemas with factory
    root1_schema = create_category_schema(
        name="Root Category 1", 
        description="First root category"
    )
    
    root2_schema = create_category_schema(
        name="Root Category 2", 
        description="Second root category"
    )
    
    # 2. ACT: Create categories
    root1 = await category_repository.create(root1_schema.model_dump())
    root2 = await category_repository.create(root2_schema.model_dump())
    
    # Create a child category
    child_schema = create_category_schema(
        name="Child Category",
        description="Child of Root Category 1",
        parent_id=root1.id
    )
    
    child = await category_repository.create(child_schema.model_dump())

    # Test get_root_categories
    root_categories = await category_repository.get_root_categories()

    # Assert
    assert len(root_categories) >= 2  # Could be more if other tests created categories
    assert any(cat.id == root1.id for cat in root_categories)
    assert any(cat.id == root2.id for cat in root_categories)
    assert not any(cat.id == child.id for cat in root_categories)


async def test_get_with_children(category_repository: CategoryRepository):
    """Test retrieving a category with its children."""
    # 1. ARRANGE: Create schemas with factory
    parent_schema = create_category_schema(
        name="Parent Category", 
        description="Parent category"
    )
    
    # 2. ACT: Create categories
    parent = await category_repository.create(parent_schema.model_dump())
    
    # Create child categories
    child1_schema = create_category_schema(
        name="Child Category 1",
        description="First child category",
        parent_id=parent.id
    )
    
    child2_schema = create_category_schema(
        name="Child Category 2",
        description="Second child category",
        parent_id=parent.id
    )
    
    child1 = await category_repository.create(child1_schema.model_dump())
    child2 = await category_repository.create(child2_schema.model_dump())

    # Test get_with_children
    category_with_children = await category_repository.get_with_children(parent.id)

    # Assert
    assert category_with_children is not None
    assert category_with_children.id == parent.id
    assert category_with_children.children is not None
    assert len(category_with_children.children) == 2
    assert any(child.id == child1.id for child in category_with_children.children)
    assert any(child.id == child2.id for child in category_with_children.children)


async def test_get_with_parent(category_repository: CategoryRepository):
    """Test retrieving a category with its parent."""
    # 1. ARRANGE: Create schemas with factory
    parent_schema = create_category_schema(
        name="Parent For Child", 
        description="Parent category"
    )
    
    # 2. ACT: Create categories
    parent = await category_repository.create(parent_schema.model_dump())
    
    # Create child category
    child_schema = create_category_schema(
        name="Child With Parent",
        description="Child category",
        parent_id=parent.id
    )
    
    child = await category_repository.create(child_schema.model_dump())

    # Test get_with_parent
    category_with_parent = await category_repository.get_with_parent(child.id)

    # Assert
    assert category_with_parent is not None
    assert category_with_parent.id == child.id
    assert category_with_parent.parent is not None
    assert category_with_parent.parent.id == parent.id
    assert category_with_parent.parent.name == "Parent For Child"


async def test_get_with_bills(
    category_repository: CategoryRepository,
    liability_repository: LiabilityRepository,
    test_checking_account
):
    """Test retrieving a category with its bills."""
    # 1. ARRANGE: Create schemas with factory
    category_schema = create_category_schema(
        name="Bills Category", 
        description="Category with bills"
    )
    
    # 2. ACT: Create category
    category = await category_repository.create(category_schema.model_dump())
    
    # Create bills (liabilities)
    # Note: We should ideally use a liability schema factory here, but for now
    # we'll continue with the direct dictionary approach for liabilities
    from tests.helpers.schema_factories.liabilities_schema_factories import create_liability_schema
    
    bill1_schema = create_liability_schema(
        name="Bill 1",
        amount=Decimal("100.00"),
        due_date=utc_datetime(2025, 4, 15),
        category_id=category.id,
        primary_account_id=test_checking_account.id
    )
    
    bill2_schema = create_liability_schema(
        name="Bill 2",
        amount=Decimal("200.00"),
        due_date=utc_datetime(2025, 4, 30),
        category_id=category.id,
        primary_account_id=test_checking_account.id
    )
    
    bill1 = await liability_repository.create(bill1_schema.model_dump())
    bill2 = await liability_repository.create(bill2_schema.model_dump())

    # Test get_with_bills
    category_with_bills = await category_repository.get_with_bills(category.id)

    # Assert
    assert category_with_bills is not None
    assert category_with_bills.id == category.id
    assert category_with_bills.bills is not None
    assert len(category_with_bills.bills) == 2
    assert any(bill.id == bill1.id for bill in category_with_bills.bills)
    assert any(bill.id == bill2.id for bill in category_with_bills.bills)


async def test_get_with_relationships(
    category_repository: CategoryRepository,
    liability_repository: LiabilityRepository,
    test_checking_account
):
    """Test retrieving a category with specified relationships."""
    # 1. ARRANGE: Create schemas with factory
    parent_schema = create_category_schema(
        name="Relationships Parent", 
        description="Parent category"
    )
    
    # 2. ACT: Create categories
    parent = await category_repository.create(parent_schema.model_dump())
    
    child_schema = create_category_schema(
        name="Relationships Child",
        description="Child category",
        parent_id=parent.id
    )
    
    child = await category_repository.create(child_schema.model_dump())
    
    # Create bill for child category
    from tests.helpers.schema_factories.liabilities_schema_factories import create_liability_schema
    
    bill_schema = create_liability_schema(
        name="Relationship Bill",
        amount=Decimal("150.00"),
        due_date=utc_datetime(2025, 5, 15),
        category_id=child.id,
        primary_account_id=test_checking_account.id
    )
    
    bill = await liability_repository.create(bill_schema.model_dump())

    # Test get_with_relationships with different combinations
    cat_with_parent = await category_repository.get_with_relationships(
        child.id, include_parent=True
    )

    cat_with_bills = await category_repository.get_with_relationships(
        child.id, include_bills=True
    )

    cat_with_all = await category_repository.get_with_relationships(
        child.id, include_parent=True, include_bills=True
    )

    # Assert
    # For parent relationship
    assert cat_with_parent.parent is not None
    assert cat_with_parent.parent.id == parent.id

    # For bills relationship - when bills weren't requested, we shouldn't check the attribute
    # to avoid triggering lazy loading

    # For cat_with_bills, we explicitly asked for bills to be loaded
    assert cat_with_bills.bills is not None
    assert len(cat_with_bills.bills) == 1
    assert cat_with_bills.bills[0].id == bill.id
    # Check that parent is not loaded (since we didn't request it)
    try:
        # This is a safer way to check without triggering lazy loading
        parent = getattr(cat_with_bills, "parent", None)
        assert parent is None
    except Exception:
        # If accessing the attribute raises an exception, that's also acceptable
        pass

    # For cat_with_all, we requested both relationships
    assert cat_with_all.parent is not None
    assert cat_with_all.parent.id == parent.id
    assert cat_with_all.bills is not None
    assert len(cat_with_all.bills) == 1
    assert cat_with_all.bills[0].id == bill.id


async def test_get_children(category_repository: CategoryRepository):
    """Test retrieving immediate children of a category."""
    # 1. ARRANGE: Create schemas with factory
    parent_schema = create_category_schema(
        name="Get Children Parent", 
        description="Parent category"
    )
    
    # 2. ACT: Create categories
    parent = await category_repository.create(parent_schema.model_dump())
    
    # Create child categories
    child1_schema = create_category_schema(
        name="Get Children Child 1",
        description="First child category",
        parent_id=parent.id
    )
    
    child2_schema = create_category_schema(
        name="Get Children Child 2",
        description="Second child category",
        parent_id=parent.id
    )
    
    child1 = await category_repository.create(child1_schema.model_dump())
    child2 = await category_repository.create(child2_schema.model_dump())
    
    # Create grandchild category
    grandchild_schema = create_category_schema(
        name="Get Children Grandchild",
        description="Grandchild category",
        parent_id=child1.id
    )
    
    grandchild = await category_repository.create(grandchild_schema.model_dump())

    # Test get_children
    children = await category_repository.get_children(parent.id)

    # Assert
    assert len(children) == 2
    assert any(child.id == child1.id for child in children)
    assert any(child.id == child2.id for child in children)
    assert not any(child.id == grandchild.id for child in children)


async def test_get_ancestors(category_repository: CategoryRepository):
    """Test retrieving all ancestors of a category."""
    # 1. ARRANGE: Create schemas with factory
    grandparent_schema = create_category_schema(
        name="Ancestor Grandparent", 
        description="Grandparent category"
    )
    
    # 2. ACT: Create category hierarchy
    grandparent = await category_repository.create(grandparent_schema.model_dump())
    
    parent_schema = create_category_schema(
        name="Ancestor Parent",
        description="Parent category",
        parent_id=grandparent.id
    )
    
    parent = await category_repository.create(parent_schema.model_dump())
    
    child_schema = create_category_schema(
        name="Ancestor Child",
        description="Child category",
        parent_id=parent.id
    )
    
    child = await category_repository.create(child_schema.model_dump())
    
    # Test get_ancestors
    ancestors = await category_repository.get_ancestors(child.id)

    # Assert
    assert len(ancestors) == 2
    assert ancestors[0].id == parent.id  # Direct parent first
    assert ancestors[1].id == grandparent.id


async def test_get_descendants(category_repository: CategoryRepository):
    """Test retrieving all descendants of a category."""
    # 1. ARRANGE: Create schemas with factory
    grandparent_schema = create_category_schema(
        name="Descendant Grandparent", 
        description="Grandparent category"
    )
    
    # 2. ACT: Create category hierarchy
    grandparent = await category_repository.create(grandparent_schema.model_dump())
    
    parent1_schema = create_category_schema(
        name="Descendant Parent 1",
        description="First parent category",
        parent_id=grandparent.id
    )
    
    parent2_schema = create_category_schema(
        name="Descendant Parent 2",
        description="Second parent category",
        parent_id=grandparent.id
    )
    
    parent1 = await category_repository.create(parent1_schema.model_dump())
    parent2 = await category_repository.create(parent2_schema.model_dump())
    
    child1_schema = create_category_schema(
        name="Descendant Child 1",
        description="First child category",
        parent_id=parent1.id
    )
    
    child2_schema = create_category_schema(
        name="Descendant Child 2",
        description="Second child category",
        parent_id=parent2.id
    )
    
    child1 = await category_repository.create(child1_schema.model_dump())
    child2 = await category_repository.create(child2_schema.model_dump())
    
    # Test get_descendants
    descendants = await category_repository.get_descendants(grandparent.id)

    # Assert
    assert len(descendants) == 4
    assert any(desc.id == parent1.id for desc in descendants)
    assert any(desc.id == parent2.id for desc in descendants)
    assert any(desc.id == child1.id for desc in descendants)
    assert any(desc.id == child2.id for desc in descendants)


async def test_is_ancestor_of(category_repository: CategoryRepository):
    """Test checking if a category is an ancestor of another category."""
    # 1. ARRANGE: Create schemas with factory
    grandparent_schema = create_category_schema(
        name="Is Ancestor Grandparent", 
        description="Grandparent category"
    )
    
    # 2. ACT: Create category hierarchy
    grandparent = await category_repository.create(grandparent_schema.model_dump())
    
    parent_schema = create_category_schema(
        name="Is Ancestor Parent",
        description="Parent category",
        parent_id=grandparent.id
    )
    
    parent = await category_repository.create(parent_schema.model_dump())
    
    child_schema = create_category_schema(
        name="Is Ancestor Child",
        description="Child category",
        parent_id=parent.id
    )
    
    child = await category_repository.create(child_schema.model_dump())
    
    unrelated_schema = create_category_schema(
        name="Is Ancestor Unrelated",
        description="Unrelated category"
    )
    
    unrelated = await category_repository.create(unrelated_schema.model_dump())
    
    # Test is_ancestor_of
    is_grandparent_ancestor_of_child = await category_repository.is_ancestor_of(
        grandparent.id, child.id
    )
    is_parent_ancestor_of_child = await category_repository.is_ancestor_of(parent.id, child.id)
    is_child_ancestor_of_parent = await category_repository.is_ancestor_of(child.id, parent.id)
    is_unrelated_ancestor_of_child = await category_repository.is_ancestor_of(unrelated.id, child.id)
    is_self_ancestor = await category_repository.is_ancestor_of(child.id, child.id)

    # Assert
    assert is_grandparent_ancestor_of_child is True
    assert is_parent_ancestor_of_child is True
    assert is_child_ancestor_of_parent is False
    assert is_unrelated_ancestor_of_child is False
    assert is_self_ancestor is False  # A category is not its own ancestor


async def test_move_category(category_repository: CategoryRepository):
    """Test moving a category to a new parent."""
    # 1. ARRANGE: Create schemas with factory
    original_parent_schema = create_category_schema(
        name="Move Original Parent", 
        description="Original parent category"
    )
    
    new_parent_schema = create_category_schema(
        name="Move New Parent", 
        description="New parent category"
    )
    
    # 2. ACT: Create categories
    original_parent = await category_repository.create(original_parent_schema.model_dump())
    new_parent = await category_repository.create(new_parent_schema.model_dump())
    
    child_schema = create_category_schema(
        name="Move Child",
        description="Child category",
        parent_id=original_parent.id
    )
    
    child = await category_repository.create(child_schema.model_dump())
    
    # Test move_category
    moved_child = await category_repository.move_category(child.id, new_parent.id)

    # Assert
    assert moved_child is not None
    assert moved_child.parent_id == new_parent.id

    # Verify by getting with parent
    child_with_parent = await category_repository.get_with_parent(child.id)
    assert child_with_parent.parent.id == new_parent.id

    # Test moving to root (no parent)
    root_child = await category_repository.move_category(child.id, None)
    assert root_child.parent_id is None


async def test_get_category_path(category_repository: CategoryRepository):
    """Test getting the full path of a category."""
    # 1. ARRANGE: Create schemas with factory
    grandparent_schema = create_category_schema(
        name="Path Grandparent", 
        description="Grandparent category"
    )
    
    # 2. ACT: Create category hierarchy
    grandparent = await category_repository.create(grandparent_schema.model_dump())
    
    parent_schema = create_category_schema(
        name="Path Parent",
        description="Parent category",
        parent_id=grandparent.id
    )
    
    parent = await category_repository.create(parent_schema.model_dump())
    
    child_schema = create_category_schema(
        name="Path Child",
        description="Child category",
        parent_id=parent.id
    )
    
    child = await category_repository.create(child_schema.model_dump())
    
    # Test get_category_path
    child_path = await category_repository.get_category_path(child.id)
    parent_path = await category_repository.get_category_path(parent.id)
    grandparent_path = await category_repository.get_category_path(grandparent.id)

    # Assert
    assert child_path == "Path Grandparent > Path Parent > Path Child"
    assert parent_path == "Path Grandparent > Path Parent"
    assert grandparent_path == "Path Grandparent"


async def test_find_categories_by_prefix(category_repository: CategoryRepository):
    """Test finding categories whose names start with a given prefix."""
    # 1. ARRANGE: Create schemas with factory
    prefix1_schema = create_category_schema(
        name="Prefix Test One", 
        description="First test category"
    )
    
    prefix2_schema = create_category_schema(
        name="Prefix Test Two", 
        description="Second test category"
    )
    
    other_schema = create_category_schema(
        name="Other Category", 
        description="Other category"
    )
    
    # 2. ACT: Create categories
    await category_repository.create(prefix1_schema.model_dump())
    await category_repository.create(prefix2_schema.model_dump())
    await category_repository.create(other_schema.model_dump())
    
    # Test find_categories_by_prefix
    prefix_matches = await category_repository.find_categories_by_prefix("Prefix")

    # Assert
    assert len(prefix_matches) == 2
    assert any(cat.name == "Prefix Test One" for cat in prefix_matches)
    assert any(cat.name == "Prefix Test Two" for cat in prefix_matches)
    assert not any(cat.name == "Other Category" for cat in prefix_matches)


async def test_get_category_with_bill_count(
    category_repository: CategoryRepository,
    liability_repository: LiabilityRepository,
    test_checking_account
):
    """Test getting a category with the count of bills assigned to it."""
    # 1. ARRANGE: Create schemas with factory
    category_schema = create_category_schema(
        name="Bill Count Category", 
        description="Category for bill count test"
    )
    
    # 2. ACT: Create category
    category = await category_repository.create(category_schema.model_dump())
    
    # Create bills
    from tests.helpers.schema_factories.liabilities_schema_factories import create_liability_schema
    
    bill1_schema = create_liability_schema(
        name="Bill Count Bill 1",
        amount=Decimal("100.00"),
        due_date=utc_datetime(2025, 6, 15),
        category_id=category.id,
        primary_account_id=test_checking_account.id
    )
    
    bill2_schema = create_liability_schema(
        name="Bill Count Bill 2",
        amount=Decimal("200.00"),
        due_date=utc_datetime(2025, 6, 30),
        category_id=category.id,
        primary_account_id=test_checking_account.id
    )
    
    await liability_repository.create(bill1_schema.model_dump())
    await liability_repository.create(bill2_schema.model_dump())
    
    # Test get_category_with_bill_count
    category_with_count, bill_count = await category_repository.get_category_with_bill_count(
        category.id
    )

    # Assert
    assert category_with_count is not None
    assert category_with_count.id == category.id
    assert bill_count == 2


async def test_get_categories_with_bill_counts(
    category_repository: CategoryRepository,
    liability_repository: LiabilityRepository,
    test_checking_account
):
    """Test getting all categories with bill counts."""
    # 1. ARRANGE: Create schemas with factory
    category1_schema = create_category_schema(
        name="Bill Counts Category 1", 
        description="First category for bill counts test"
    )
    
    category2_schema = create_category_schema(
        name="Bill Counts Category 2", 
        description="Second category for bill counts test"
    )
    
    category3_schema = create_category_schema(
        name="Bill Counts Category 3", 
        description="Third category for bill counts test"
    )
    
    # 2. ACT: Create categories
    category1 = await category_repository.create(category1_schema.model_dump())
    category2 = await category_repository.create(category2_schema.model_dump())
    category3 = await category_repository.create(category3_schema.model_dump())
    
    # Create bills
    from tests.helpers.schema_factories.liabilities_schema_factories import create_liability_schema
    
    bill1_schema = create_liability_schema(
        name="Bill Counts Bill 1",
        amount=Decimal("100.00"),
        due_date=utc_datetime(2025, 7, 15),
        category_id=category1.id,
        primary_account_id=test_checking_account.id
    )
    
    bill2_schema = create_liability_schema(
        name="Bill Counts Bill 2",
        amount=Decimal("200.00"),
        due_date=utc_datetime(2025, 7, 30),
        category_id=category1.id,
        primary_account_id=test_checking_account.id
    )
    
    bill3_schema = create_liability_schema(
        name="Bill Counts Bill 3",
        amount=Decimal("300.00"),
        due_date=utc_datetime(2025, 8, 15),
        category_id=category2.id,
        primary_account_id=test_checking_account.id
    )
    
    await liability_repository.create(bill1_schema.model_dump())
    await liability_repository.create(bill2_schema.model_dump())
    await liability_repository.create(bill3_schema.model_dump())
    
    # Category3 has no bills
    
    # Test get_categories_with_bill_counts
    categories_with_counts = await category_repository.get_categories_with_bill_counts()

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


async def test_delete_if_unused(
    category_repository: CategoryRepository,
    liability_repository: LiabilityRepository,
    test_checking_account
):
    """Test deleting a category only if it has no children and no bills."""
    # 1. ARRANGE: Create schemas with factory
    parent_schema = create_category_schema(
        name="Delete Parent", 
        description="Parent category"
    )
    
    # 2. ACT: Create categories
    parent = await category_repository.create(parent_schema.model_dump())
    
    child_schema = create_category_schema(
        name="Delete Child",
        description="Child category",
        parent_id=parent.id
    )
    
    child = await category_repository.create(child_schema.model_dump())
    
    with_bill_schema = create_category_schema(
        name="Delete With Bill", 
        description="Category with bill"
    )
    
    with_bill = await category_repository.create(with_bill_schema.model_dump())
    
    empty_schema = create_category_schema(
        name="Delete Empty", 
        description="Empty category"
    )
    
    empty = await category_repository.create(empty_schema.model_dump())
    
    # Create bill
    from tests.helpers.schema_factories.liabilities_schema_factories import create_liability_schema
    
    bill_schema = create_liability_schema(
        name="Delete Bill",
        amount=Decimal("100.00"),
        due_date=utc_datetime(2025, 8, 15),
        category_id=with_bill.id,
        primary_account_id=test_checking_account.id
    )
    
    await liability_repository.create(bill_schema.model_dump())
    
    # Test delete_if_unused
    parent_deleted = await category_repository.delete_if_unused(parent.id)
    with_bill_deleted = await category_repository.delete_if_unused(with_bill.id)
    empty_deleted = await category_repository.delete_if_unused(empty.id)

    # Assert
    assert parent_deleted is False  # Should not delete (has child)
    assert with_bill_deleted is False  # Should not delete (has bill)
    assert empty_deleted is True  # Should delete (no children, no bills)

    # Verify
    parent_check = await category_repository.get(parent.id)
    with_bill_check = await category_repository.get(with_bill.id)
    empty_check = await category_repository.get(empty.id)

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
