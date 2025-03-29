from datetime import datetime

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.categories import Category
from src.models.liabilities import Liability
from src.schemas.categories import CategoryCreate, CategoryTree, CategoryUpdate, CategoryWithBillsResponse
from src.services.categories import CategoryError, CategoryService


@pytest.fixture
async def category_service(db_session: AsyncSession) -> CategoryService:
    return CategoryService(db_session)


@pytest.fixture
async def root_category(db_session: AsyncSession) -> Category:
    category = Category(
        name="Root Category",
        description="Root Description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


@pytest.fixture
async def child_category(db_session: AsyncSession, root_category: Category) -> Category:
    category = Category(
        name="Child Category",
        description="Child Description",
        parent_id=root_category.id,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


async def test_create_category(category_service: CategoryService):
    category_data = CategoryCreate(name="New Category", description="New Description")
    category = await category_service.create_category(category_data)
    assert category.name == "New Category"
    assert category.description == "New Description"


async def test_create_category_with_parent(
    category_service: CategoryService, root_category: Category
):
    category_data = CategoryCreate(
        name="New Child Category",
        description="Child Description",
        parent_id=root_category.id,
    )
    category = await category_service.create_category(category_data)
    assert category.name == "New Child Category"
    assert category.parent_id == root_category.id

    # Use service method instead of model property
    full_path = await category_service.get_full_path(category)
    assert full_path == f"{root_category.name} > {category.name}"


async def test_create_duplicate_category(
    category_service: CategoryService, root_category: Category
):
    category_data = CategoryCreate(
        name=root_category.name, description="Another Description"
    )
    with pytest.raises(
        CategoryError, match=f"Category with name '{root_category.name}' already exists"
    ):
        await category_service.create_category(category_data)


async def test_create_category_with_nonexistent_parent(
    category_service: CategoryService,
):
    category_data = CategoryCreate(
        name="Invalid Child", description="Description", parent_id=999
    )
    with pytest.raises(
        CategoryError, match="Parent category with ID 999 does not exist"
    ):
        await category_service.create_category(category_data)


async def test_prevent_circular_reference(
    category_service: CategoryService, root_category: Category, child_category: Category
):
    # Try to make the root category a child of its own child
    update_data = CategoryUpdate(parent_id=child_category.id)
    # This should raise a CategoryError
    with pytest.raises(CategoryError):
        await category_service.update_category(root_category.id, update_data)
        await category_service.db.commit()


async def test_get_categories(
    category_service: CategoryService, root_category: Category
):
    categories = await category_service.get_categories()
    assert len(categories) >= 1
    assert any(c.id == root_category.id for c in categories)


async def test_update_category(
    category_service: CategoryService, root_category: Category
):
    update_data = CategoryUpdate(
        name="Updated Root Category", description="Updated Description"
    )
    updated_category = await category_service.update_category(
        root_category.id, update_data
    )
    assert updated_category is not None
    assert updated_category.name == "Updated Root Category"
    assert updated_category.description == "Updated Description"


async def test_get_category_with_children(
    category_service: CategoryService, root_category: Category, child_category: Category
):
    category = await category_service.get_category_with_children(root_category.id)
    assert category is not None
    assert len(category.children) == 1
    assert category.children[0].id == child_category.id


async def test_get_category_with_parent(
    category_service: CategoryService, child_category: Category, root_category: Category
):
    category = await category_service.get_category_with_parent(child_category.id)
    assert category is not None
    assert category.parent.id == root_category.id


async def test_get_nonexistent_category(category_service: CategoryService):
    category = await category_service.get_category(999)
    assert category is None


async def test_update_nonexistent_category(category_service: CategoryService):
    update_data = CategoryUpdate(
        name="Updated Category", description="Updated Description"
    )
    updated_category = await category_service.update_category(999, update_data)
    assert updated_category is None


async def test_get_root_categories(
    category_service: CategoryService, root_category: Category, child_category: Category
):
    categories = await category_service.get_root_categories()
    assert len(categories) == 1
    assert categories[0].id == root_category.id
    assert len(categories[0].children) == 1
    assert categories[0].children[0].id == child_category.id


async def test_delete_category_with_children(
    category_service: CategoryService, root_category: Category, child_category: Category
):
    with pytest.raises(
        CategoryError, match="Cannot delete category that has child categories"
    ):
        await category_service.delete_category(root_category.id)


async def test_delete_nonexistent_category(category_service: CategoryService):
    success = await category_service.delete_category(999)
    assert success is False


async def test_get_full_path(
    category_service: CategoryService, root_category: Category, child_category: Category
):
    grandchild_data = CategoryCreate(
        name="Grandchild Category",
        description="Grandchild Description",
        parent_id=child_category.id,
    )
    grandchild = await category_service.create_category(grandchild_data)

    # Test get_full_path service method
    full_path = await category_service.get_full_path(grandchild)
    assert (
        full_path == f"{root_category.name} > {child_category.name} > {grandchild.name}"
    )

    # Test intermediate paths
    child_path = await category_service.get_full_path(child_category)
    assert child_path == f"{root_category.name} > {child_category.name}"

    root_path = await category_service.get_full_path(root_category)
    assert root_path == root_category.name


async def test_get_nonexistent_category_by_name(category_service: CategoryService):
    category = await category_service.get_category_by_name("Nonexistent Category")
    assert category is None


async def test_is_ancestor_of(
    category_service: CategoryService, root_category: Category, child_category: Category
):
    """Test the is_ancestor_of service method"""
    # Create a grandchild category
    grandchild_data = CategoryCreate(
        name="Grandchild Category",
        description="Grandchild Description",
        parent_id=child_category.id,
    )
    grandchild = await category_service.create_category(grandchild_data)

    # Test ancestor relationships
    assert await category_service.is_ancestor_of(root_category, child_category)
    assert await category_service.is_ancestor_of(root_category, grandchild)
    assert await category_service.is_ancestor_of(child_category, grandchild)

    # Test non-ancestor relationships
    assert not await category_service.is_ancestor_of(child_category, root_category)
    assert not await category_service.is_ancestor_of(grandchild, child_category)
    assert not await category_service.is_ancestor_of(grandchild, root_category)


async def test_is_ancestor_of_with_none(
    category_service: CategoryService, root_category: Category
):
    """Test is_ancestor_of with None parameter"""
    assert not await category_service.is_ancestor_of(root_category, None)
    assert not await category_service.is_ancestor_of(None, root_category)
    assert not await category_service.is_ancestor_of(None, None)


async def test_get_full_path_with_none(category_service: CategoryService):
    """Test get_full_path with None parameter"""
    full_path = await category_service.get_full_path(None)
    assert full_path == ""


# Tests for new composition methods

@pytest.fixture
async def liability(db_session: AsyncSession, root_category: Category) -> Liability:
    """Fixture to create a test liability (bill) for composition tests"""
    liability = Liability(
        name="Test Bill",
        amount=150.00,
        due_date=datetime.utcnow(),
        description="Test bill description",
        category_id=root_category.id,
        primary_account_id=1,  # Assuming account ID 1 exists or isn't enforced in tests
        recurring=False,
        status="pending",
        paid=False,
    )
    db_session.add(liability)
    await db_session.commit()
    await db_session.refresh(liability)
    return liability


async def test_compose_category_tree(
    category_service: CategoryService, root_category: Category, child_category: Category
):
    """Test the compose_category_tree method that builds rich tree structures"""
    
    # Create a grandchild category
    grandchild_data = CategoryCreate(
        name="Grandchild Category",
        description="Grandchild Description",
        parent_id=child_category.id,
    )
    grandchild = await category_service.create_category(grandchild_data)
    
    # Test composition for full tree structure
    tree = await category_service.compose_category_tree(root_category.id)
    
    # Verify the structure matches our expectations
    assert isinstance(tree, CategoryTree)
    assert tree.id == root_category.id
    assert tree.name == root_category.name
    assert len(tree.children) == 1
    
    # Check first level child
    assert tree.children[0].id == child_category.id
    assert tree.children[0].name == child_category.name
    assert len(tree.children[0].children) == 1
    
    # Check second level grandchild
    assert tree.children[0].children[0].id == grandchild.id
    assert tree.children[0].children[0].name == grandchild.name
    
    # Verify path is correctly populated
    assert tree.full_path == root_category.name
    assert tree.children[0].full_path == f"{root_category.name} > {child_category.name}"
    assert tree.children[0].children[0].full_path == (
        f"{root_category.name} > {child_category.name} > {grandchild.name}"
    )
    
    # Test depth limiting (just test depth=1)
    limited_tree = await category_service.compose_category_tree(root_category.id, depth=1)
    assert len(limited_tree.children) == 1
    assert limited_tree.children[0].id == child_category.id
    assert limited_tree.children[0].children == []  # No grandchildren at depth 1


async def test_compose_category_with_bills(
    category_service: CategoryService, 
    root_category: Category, 
    child_category: Category,
    liability: Liability
):
    """Test the compose_category_with_bills method that builds rich response objects with bills"""
    
    # Test composition for a category with bills
    response = await category_service.compose_category_with_bills(root_category.id)
    
    # Verify the response structure
    assert isinstance(response, CategoryWithBillsResponse)
    assert response.id == root_category.id
    assert response.name == root_category.name
    
    # Verify bills are included and formatted correctly
    assert len(response.bills) == 1
    assert response.bills[0]["id"] == liability.id
    assert response.bills[0]["name"] == liability.name
    assert response.bills[0]["amount"] == liability.amount
    assert response.bills[0]["status"] == liability.status.value
    assert response.bills[0]["paid"] == liability.paid
    
    # Verify children are included
    assert len(response.children) == 1
    assert response.children[0].id == child_category.id
    assert response.children[0].name == child_category.name
    
    # Child category should have no bills in this test
    assert len(response.children[0].bills) == 0
