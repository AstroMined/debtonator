"""
Category schema factory functions.

This module provides factory functions for creating valid Category-related
Pydantic schema instances for use in tests.
"""

from datetime import datetime
from typing import Any, Dict, List, Optional

from src.schemas.categories import (
    Category,
    CategoryCreate,
    CategoryTree,
    CategoryUpdate,
    CategoryWithBillIDs,
    CategoryWithBillsResponse,
)
from tests.helpers.schema_factories.base import factory_function, utc_now

# Note: The following classes have been removed in the code refactoring:
# - CategoryWithChildren (replaced by CategoryTree)
# - CategoryWithParent (functionality now in service layer via composition)
# - CategoryWithBills (replaced by CategoryWithBillsResponse)


@factory_function(CategoryCreate)
def create_category_schema(
    name: str = "Test Category",
    description: Optional[str] = None,
    parent_id: Optional[int] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid CategoryCreate schema instance.

    Args:
        name: Category name
        description: Optional description for the category
        parent_id: Optional parent category ID for hierarchical categories
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create CategoryCreate schema
    """
    data = {
        "name": name,
        **kwargs,
    }

    if description is not None:
        data["description"] = description

    if parent_id is not None:
        data["parent_id"] = parent_id

    return data


@factory_function(CategoryUpdate)
def create_category_update_schema(
    name: Optional[str] = None,
    description: Optional[str] = None,
    parent_id: Optional[int] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid CategoryUpdate schema instance.

    Args:
        name: Updated category name (optional)
        description: Updated description (optional)
        parent_id: Updated parent category ID (optional)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create CategoryUpdate schema
    """
    data = {**kwargs}

    if name is not None:
        data["name"] = name

    if description is not None:
        data["description"] = description

    if parent_id is not None:
        data["parent_id"] = parent_id

    return data


@factory_function(Category)
def create_category_in_db_schema(
    id: int,
    name: str = "Test Category",
    description: Optional[str] = None,
    parent_id: Optional[int] = None,
    full_path: str = "",
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid Category schema instance.

    Args:
        id: Unique category identifier
        name: Category name
        description: Optional description for the category
        parent_id: Optional parent category ID for hierarchical categories
        full_path: Full hierarchical path of the category
        created_at: Creation timestamp (defaults to now)
        updated_at: Last update timestamp (defaults to now)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create Category schema
    """
    if created_at is None:
        created_at = utc_now()

    if updated_at is None:
        updated_at = utc_now()

    data = {
        "id": id,
        "name": name,
        "created_at": created_at,
        "updated_at": updated_at,
        "full_path": full_path,
        **kwargs,
    }

    if description is not None:
        data["description"] = description

    if parent_id is not None:
        data["parent_id"] = parent_id

    return data


@factory_function(CategoryTree)
def create_category_tree_schema(
    id: int,
    name: str = "Parent Category",
    description: Optional[str] = None,
    parent_id: Optional[int] = None,
    full_path: str = "",
    children: Optional[List[Dict[str, Any]]] = None,
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid CategoryTree schema instance.

    Args:
        id: Unique category identifier
        name: Category name
        description: Optional description for the category
        parent_id: Optional parent category ID for hierarchical categories
        full_path: Full hierarchical path of the category
        children: List of child categories (creates 2 if None)
        created_at: Creation timestamp (defaults to now)
        updated_at: Last update timestamp (defaults to now)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create CategoryTree schema
    """
    # Create base category data
    base_data = create_category_in_db_schema(
        id=id,
        name=name,
        description=description,
        parent_id=parent_id,
        full_path=full_path,
        created_at=created_at,
        updated_at=updated_at,
    )

    # Create default children if none provided
    if children is None:
        children = [
            create_category_in_db_schema(
                id=id + 1,
                name=f"{name} - Child 1",
                parent_id=id,
                full_path=(
                    f"{full_path}/{name}/Child 1" if full_path else f"{name}/Child 1"
                ),
            ),
            create_category_in_db_schema(
                id=id + 2,
                name=f"{name} - Child 2",
                parent_id=id,
                full_path=(
                    f"{full_path}/{name}/Child 2" if full_path else f"{name}/Child 2"
                ),
            ),
        ]

    data = {
        **base_data,
        "children": children,
        **kwargs,
    }

    return data


@factory_function(CategoryWithBillIDs)
def create_category_with_bill_ids_schema(
    id: int,
    name: str = "Category With Bills",
    description: Optional[str] = None,
    parent_id: Optional[int] = None,
    full_path: str = "",
    children_ids: Optional[List[int]] = None,
    bill_ids: Optional[List[int]] = None,
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid CategoryWithBillIDs schema instance.

    Args:
        id: Unique category identifier
        name: Category name
        description: Optional description for the category
        parent_id: Optional parent category ID for hierarchical categories
        full_path: Full hierarchical path of the category
        children_ids: List of child category IDs
        bill_ids: List of liability IDs associated with this category
        created_at: Creation timestamp (defaults to now)
        updated_at: Last update timestamp (defaults to now)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create CategoryWithBillIDs schema
    """
    # Create base category data
    base_data = create_category_in_db_schema(
        id=id,
        name=name,
        description=description,
        parent_id=parent_id,
        full_path=full_path,
        created_at=created_at,
        updated_at=updated_at,
    )

    # Default IDs if none provided
    if children_ids is None:
        children_ids = [id + 1, id + 2]

    if bill_ids is None:
        bill_ids = [101, 102, 103]

    data = {
        **base_data,
        "children_ids": children_ids,
        "bill_ids": bill_ids,
        **kwargs,
    }

    return data


@factory_function(CategoryWithBillsResponse)
def create_category_with_bills_response_schema(
    id: int,
    name: str = "Category With Bills",
    description: Optional[str] = None,
    parent_id: Optional[int] = None,
    full_path: str = "",
    children: Optional[List[Dict[str, Any]]] = None,
    bills: Optional[List[Dict[str, Any]]] = None,
    created_at: Optional[datetime] = None,
    updated_at: Optional[datetime] = None,
    **kwargs: Any,
) -> Dict[str, Any]:
    """
    Create a valid CategoryWithBillsResponse schema instance.

    Args:
        id: Unique category identifier
        name: Category name
        description: Optional description for the category
        parent_id: Optional parent category ID for hierarchical categories
        full_path: Full hierarchical path of the category
        children: List of child categories (creates 2 if None)
        bills: List of simplified bill dictionaries (creates 2 if None)
        created_at: Creation timestamp (defaults to now)
        updated_at: Last update timestamp (defaults to now)
        **kwargs: Additional fields to override

    Returns:
        Dict[str, Any]: Data to create CategoryWithBillsResponse schema
    """
    # Create base category tree
    tree_data = create_category_tree_schema(
        id=id,
        name=name,
        description=description,
        parent_id=parent_id,
        full_path=full_path,
        children=children,
        created_at=created_at,
        updated_at=updated_at,
    )

    # Default bills if none provided
    if bills is None:
        now = utc_now()
        bills = [
            {
                "id": 101,
                "name": "Test Bill 1",
                "amount": 100.00,
                "due_date": now,
                "status": "pending",
                "paid": False,
            },
            {
                "id": 102,
                "name": "Test Bill 2",
                "amount": 200.00,
                "due_date": now,
                "status": "pending",
                "paid": False,
            },
        ]

    data = {
        **tree_data,
        "bills": bills,
        **kwargs,
    }

    return data
