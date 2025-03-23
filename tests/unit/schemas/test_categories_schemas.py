from datetime import datetime, timezone
from zoneinfo import ZoneInfo  # Only needed for non-UTC timezone tests

import pytest
from pydantic import ValidationError

from src.schemas.categories import (Category, CategoryBase, CategoryCreate,
                                    CategoryUpdate, CategoryWithBills,
                                    CategoryWithChildren, CategoryWithParent)
from src.schemas.liabilities import LiabilityBase


# Test valid object creation
def test_category_base_valid():
    """Test valid category base schema"""
    data = CategoryBase(name="Test Category", description="Test description")

    assert data.name == "Test Category"
    assert data.description == "Test description"
    assert data.parent_id is None


def test_category_base_with_parent():
    """Test category base with parent ID"""
    data = CategoryBase(
        name="Test Subcategory", description="Test description", parent_id=1
    )

    assert data.name == "Test Subcategory"
    assert data.description == "Test description"
    assert data.parent_id == 1


def test_category_create_valid():
    """Test valid category create schema"""
    data = CategoryCreate(
        name="New Category", description="New category description", parent_id=1
    )

    assert data.name == "New Category"
    assert data.description == "New category description"
    assert data.parent_id == 1


def test_category_update_valid():
    """Test valid category update schema"""
    # Test partial update with just name
    data1 = CategoryUpdate(name="Updated Name")
    assert data1.name == "Updated Name"
    assert data1.description is None
    assert data1.parent_id is None

    # Test partial update with just description
    data2 = CategoryUpdate(description="Updated description")
    assert data2.name is None
    assert data2.description == "Updated description"
    assert data2.parent_id is None

    # Test partial update with just parent_id
    data3 = CategoryUpdate(parent_id=2)
    assert data3.name is None
    assert data3.description is None
    assert data3.parent_id == 2

    # Test full update
    data4 = CategoryUpdate(
        name="Updated Name", description="Updated description", parent_id=2
    )
    assert data4.name == "Updated Name"
    assert data4.description == "Updated description"
    assert data4.parent_id == 2


def test_category_valid():
    """Test valid category schema"""
    now = datetime.now(timezone.utc)

    data = Category(
        id=1,
        name="Test Category",
        description="Test description",
        parent_id=None,
        created_at=now,
        updated_at=now,
    )

    assert data.id == 1
    assert data.name == "Test Category"
    assert data.description == "Test description"
    assert data.parent_id is None
    assert data.created_at == now
    assert data.updated_at == now
    assert data.full_path == ""  # Default empty string


def test_category_with_children_valid():
    """Test valid category with children schema"""
    now = datetime.now(timezone.utc)

    # Create parent category
    parent = CategoryWithChildren(
        id=1,
        name="Parent Category",
        description="Parent description",
        created_at=now,
        updated_at=now,
    )

    # Create child categories
    child1 = CategoryWithChildren(
        id=2,
        name="Child Category 1",
        description="Child 1 description",
        parent_id=1,
        created_at=now,
        updated_at=now,
    )

    child2 = CategoryWithChildren(
        id=3,
        name="Child Category 2",
        description="Child 2 description",
        parent_id=1,
        created_at=now,
        updated_at=now,
    )

    # Set children for parent
    parent.children = [child1, child2]

    # Assertions
    assert parent.id == 1
    assert parent.name == "Parent Category"
    assert len(parent.children) == 2
    assert parent.children[0].id == 2
    assert parent.children[0].name == "Child Category 1"
    assert parent.children[1].id == 3
    assert parent.children[1].name == "Child Category 2"


def test_category_with_parent_valid():
    """Test valid category with parent schema"""
    now = datetime.now(timezone.utc)

    # Create parent category
    parent = CategoryWithChildren(
        id=1,
        name="Parent Category",
        description="Parent description",
        created_at=now,
        updated_at=now,
    )

    # Create child category with parent
    child = CategoryWithParent(
        id=2,
        name="Child Category",
        description="Child description",
        parent_id=1,
        parent=parent,  # Set parent object
        created_at=now,
        updated_at=now,
    )

    # Assertions
    assert child.id == 2
    assert child.name == "Child Category"
    assert child.parent_id == 1
    assert child.parent is not None
    assert child.parent.id == 1
    assert child.parent.name == "Parent Category"


def test_category_with_bills_valid():
    """Test valid category with bills schema"""
    now = datetime.now(timezone.utc)

    # Create liability
    liability = LiabilityBase(
        name="Test Liability",
        amount=100.00,
        description="Test liability description",
        due_date=now.replace(day=now.day + 1),  # Due date in the future
        category_id=1,
        primary_account_id=1,
    )

    # Create category with bills
    category = CategoryWithBills(
        id=1, name="Bills Category", created_at=now, updated_at=now, bills=[liability]
    )

    # Assertions
    assert category.id == 1
    assert category.name == "Bills Category"
    assert len(category.bills) == 1
    assert category.bills[0].name == "Test Liability"
    assert category.bills[0].amount == 100.00


# Test field validations
def test_name_validation():
    """Test name field validation"""
    # Test name cannot be empty
    with pytest.raises(ValidationError, match="Field required"):
        CategoryBase(description="Missing name")

    # Test name length validation
    with pytest.raises(
        ValidationError, match="String should have at most 100 characters"
    ):
        CategoryBase(name="X" * 101)

    # Test valid name at the limit
    data = CategoryBase(name="X" * 100)
    assert len(data.name) == 100


def test_description_validation():
    """Test description field validation"""
    # Test description length validation
    with pytest.raises(
        ValidationError, match="String should have at most 500 characters"
    ):
        CategoryBase(name="Test Category", description="X" * 501)

    # Test valid description at the limit
    data = CategoryBase(name="Test Category", description="X" * 500)
    assert len(data.description) == 500


def test_parent_id_self_reference():
    """Test validation that a category cannot be its own parent"""
    # The validator function in CategoryCreate and CategoryUpdate checks values.get('id')
    # Let's test this by using create_category_with_context and update_category_with_context

    # Helper function to simulate validation context for CategoryCreate
    def create_category_with_context(category_id):
        # Create a category and manually call the validator with context
        category = CategoryCreate(name="Test Category", parent_id=category_id)
        # Simulate validation context by manually calling validator
        try:
            CategoryCreate.validate_parent_id(category.parent_id, {"id": category_id})
            return True
        except ValueError:
            return False

    # Helper function to simulate validation context for CategoryUpdate
    def update_category_with_context(category_id):
        # Create a category update and manually call the validator with context
        category = CategoryUpdate(parent_id=category_id)
        # Simulate validation context by manually calling validator
        try:
            CategoryUpdate.validate_parent_id(category.parent_id, {"id": category_id})
            return True
        except ValueError:
            return False

    # Test invalid self-reference (same ID and parent_id)
    assert create_category_with_context(5) is False  # Should fail validation
    assert update_category_with_context(10) is False  # Should fail validation

    # Test valid reference (different ID and parent_id)
    # Create a category with different ID in validation context
    category1 = CategoryCreate(name="Test Category", parent_id=5)
    assert CategoryCreate.validate_parent_id(category1.parent_id, {"id": 6}) == 5

    # Create an update with different ID in validation context
    category2 = CategoryUpdate(parent_id=15)
    assert CategoryUpdate.validate_parent_id(category2.parent_id, {"id": 16}) == 15


# Test datetime UTC validation
def test_datetime_utc_validation():
    """Test datetime UTC validation per ADR-011"""
    # Test naive datetime
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        Category(
            id=1,
            name="Test Category",
            created_at=datetime.now(),  # Naive datetime
            updated_at=datetime.now(timezone.utc),
        )

    # Test non-UTC timezone
    with pytest.raises(ValidationError, match="Datetime must be UTC"):
        Category(
            id=1,
            name="Test Category",
            created_at=datetime.now(timezone.utc),
            updated_at=datetime.now(ZoneInfo("America/New_York")),  # Non-UTC timezone
        )

    # Test valid UTC datetime
    now = datetime.now(timezone.utc)
    data = Category(id=1, name="Test Category", created_at=now, updated_at=now)
    assert data.created_at == now
    assert data.updated_at == now


# Test hierarchical structure
def test_nested_category_hierarchy():
    """Test nested category hierarchy"""
    now = datetime.now(timezone.utc)

    # Create a three-level hierarchy
    grandparent = CategoryWithChildren(
        id=1, name="Grandparent", created_at=now, updated_at=now
    )

    parent = CategoryWithChildren(
        id=2, name="Parent", parent_id=1, created_at=now, updated_at=now
    )

    child = CategoryWithChildren(
        id=3, name="Child", parent_id=2, created_at=now, updated_at=now
    )

    # Link the hierarchy
    parent.children = [child]
    grandparent.children = [parent]

    # Assertions for the structure
    assert grandparent.id == 1
    assert len(grandparent.children) == 1
    assert grandparent.children[0].id == 2
    assert len(grandparent.children[0].children) == 1
    assert grandparent.children[0].children[0].id == 3
