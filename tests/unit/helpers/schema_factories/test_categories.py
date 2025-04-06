"""
Unit tests for categories schema factory functions.

Tests ensure that categories schema factories produce valid schema instances
that pass validation.
"""

# pylint: disable=no-member

import pytest
from datetime import datetime

from src.schemas.categories import (
    Category,
    CategoryCreate,
    CategoryTree,
    CategoryUpdate,
    CategoryWithBillIDs,
    CategoryWithBillsResponse,
)
from src.utils.datetime_utils import utc_now
from tests.helpers.schema_factories.categories import (
    create_category_schema,
    create_category_update_schema,
    create_category_in_db_schema,
    create_category_tree_schema,
    create_category_with_bill_ids_schema,
    create_category_with_bills_response_schema,
)


def test_create_category_schema():
    """Test creating a CategoryCreate schema with minimal values."""
    schema = create_category_schema()
    
    assert isinstance(schema, CategoryCreate)
    assert schema.name == "Test Category"
    assert schema.description is None
    assert schema.parent_id is None


def test_create_category_schema_with_parent():
    """Test creating a CategoryCreate schema with parent."""
    schema = create_category_schema(
        name="Child Category",
        description="A child category",
        parent_id=1
    )
    
    assert isinstance(schema, CategoryCreate)
    assert schema.name == "Child Category"
    assert schema.description == "A child category"
    assert schema.parent_id == 1


def test_create_category_update_schema_empty():
    """Test creating an empty CategoryUpdate schema."""
    schema = create_category_update_schema()
    
    assert isinstance(schema, CategoryUpdate)
    assert schema.name is None
    assert schema.description is None
    assert schema.parent_id is None


def test_create_category_update_schema_with_values():
    """Test creating a CategoryUpdate schema with all fields."""
    schema = create_category_update_schema(
        name="Updated Category",
        description="Updated description",
        parent_id=2
    )
    
    assert isinstance(schema, CategoryUpdate)
    assert schema.name == "Updated Category"
    assert schema.description == "Updated description"
    assert schema.parent_id == 2


def test_create_category_update_schema_partial():
    """Test creating a CategoryUpdate schema with partial fields."""
    schema = create_category_update_schema(
        name="Renamed Category"
    )
    
    assert isinstance(schema, CategoryUpdate)
    assert schema.name == "Renamed Category"
    assert schema.description is None
    assert schema.parent_id is None


def test_create_category_in_db_schema():
    """Test creating a Category schema with required fields."""
    now = utc_now()
    schema = create_category_in_db_schema(
        id=1,
        created_at=now,
        updated_at=now
    )
    
    assert isinstance(schema, Category)
    assert schema.id == 1
    assert schema.name == "Test Category"
    assert schema.description is None
    assert schema.parent_id is None
    assert schema.full_path == ""
    assert schema.created_at == now
    assert schema.updated_at == now


def test_create_category_in_db_schema_with_all_fields():
    """Test creating a Category schema with all fields."""
    now = utc_now()
    schema = create_category_in_db_schema(
        id=2,
        name="Complete Category",
        description="Complete description",
        parent_id=1,
        full_path="Parent/Complete",
        created_at=now,
        updated_at=now
    )
    
    assert isinstance(schema, Category)
    assert schema.id == 2
    assert schema.name == "Complete Category"
    assert schema.description == "Complete description"
    assert schema.parent_id == 1
    assert schema.full_path == "Parent/Complete"
    assert schema.created_at == now
    assert schema.updated_at == now


def test_create_category_tree_schema():
    """Test creating a CategoryTree schema with default children."""
    schema = create_category_tree_schema(id=1)
    
    assert isinstance(schema, CategoryTree)
    assert schema.id == 1
    assert schema.name == "Parent Category"
    assert len(schema.children) == 2
    assert schema.children[0].name == "Parent Category - Child 1"
    assert schema.children[1].name == "Parent Category - Child 2"
    assert schema.children[0].parent_id == 1
    assert schema.children[1].parent_id == 1


def test_create_category_tree_schema_with_custom_children():
    """Test creating a CategoryTree schema with custom children."""
    now = utc_now()
    custom_children = [
        {
            "id": 10,
            "name": "Custom Child",
            "parent_id": 5,
            "full_path": "Parent/Custom Child",
            "created_at": now,
            "updated_at": now
        }
    ]
    
    schema = create_category_tree_schema(
        id=5,
        name="Parent",
        full_path="Parent",
        children=custom_children
    )
    
    assert isinstance(schema, CategoryTree)
    assert schema.id == 5
    assert schema.name == "Parent"
    assert len(schema.children) == 1
    assert schema.children[0].id == 10
    assert schema.children[0].name == "Custom Child"
    assert schema.children[0].parent_id == 5
    assert schema.children[0].full_path == "Parent/Custom Child"


def test_create_category_with_bill_ids_schema():
    """Test creating a CategoryWithBillIDs schema with default values."""
    schema = create_category_with_bill_ids_schema(id=1)
    
    assert isinstance(schema, CategoryWithBillIDs)
    assert schema.id == 1
    assert schema.name == "Category With Bills"
    assert len(schema.children_ids) == 2
    assert schema.children_ids == [2, 3]
    assert len(schema.bill_ids) == 3
    assert schema.bill_ids == [101, 102, 103]


def test_create_category_with_bill_ids_schema_custom():
    """Test creating a CategoryWithBillIDs schema with custom values."""
    schema = create_category_with_bill_ids_schema(
        id=5,
        name="Custom Bills Category",
        children_ids=[10, 11, 12],
        bill_ids=[201, 202]
    )
    
    assert isinstance(schema, CategoryWithBillIDs)
    assert schema.id == 5
    assert schema.name == "Custom Bills Category"
    assert len(schema.children_ids) == 3
    assert schema.children_ids == [10, 11, 12]
    assert len(schema.bill_ids) == 2
    assert schema.bill_ids == [201, 202]


def test_create_category_with_bills_response_schema():
    """Test creating a CategoryWithBillsResponse schema with default values."""
    schema = create_category_with_bills_response_schema(id=1)
    
    assert isinstance(schema, CategoryWithBillsResponse)
    assert schema.id == 1
    assert schema.name == "Category With Bills"
    assert len(schema.children) == 2
    assert len(schema.bills) == 2
    assert schema.bills[0]["id"] == 101
    assert schema.bills[1]["id"] == 102
    assert schema.bills[0]["name"] == "Test Bill 1"
    assert schema.bills[0]["amount"] == 100.00


def test_create_category_with_bills_response_schema_custom():
    """Test creating a CategoryWithBillsResponse schema with custom values."""
    now = utc_now()
    custom_bills = [
        {
            "id": 301,
            "name": "Custom Bill",
            "amount": 350.00,
            "due_date": now,
            "status": "pending",
            "paid": False,
        }
    ]
    
    custom_children = [
        {
            "id": 15,
            "name": "Custom Response Child",
            "parent_id": 10,
            "full_path": "Custom Response/Child",
            "created_at": now,
            "updated_at": now
        }
    ]
    
    schema = create_category_with_bills_response_schema(
        id=10,
        name="Custom Response",
        bills=custom_bills,
        children=custom_children
    )
    
    assert isinstance(schema, CategoryWithBillsResponse)
    assert schema.id == 10
    assert schema.name == "Custom Response"
    assert len(schema.children) == 1
    assert schema.children[0].id == 15
    assert schema.children[0].name == "Custom Response Child"
    assert len(schema.bills) == 1
    assert schema.bills[0]["id"] == 301
    assert schema.bills[0]["name"] == "Custom Bill"
    assert schema.bills[0]["amount"] == 350.00
