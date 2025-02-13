import pytest
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime

from src.models.categories import Category
from src.schemas.categories import CategoryCreate, CategoryUpdate
from src.services.categories import CategoryService, CategoryError

@pytest.fixture
async def category_service(db_session: AsyncSession) -> CategoryService:
    return CategoryService(db_session)

@pytest.fixture
async def root_category(db_session: AsyncSession) -> Category:
    category = Category(
        name="Root Category",
        description="Root Description",
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
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
        updated_at=datetime.utcnow()
    )
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category

async def test_create_category(category_service: CategoryService):
    category_data = CategoryCreate(
        name="New Category",
        description="New Description"
    )
    category = await category_service.create_category(category_data)
    assert category.name == "New Category"
    assert category.description == "New Description"

async def test_create_category_with_parent(category_service: CategoryService, root_category: Category):
    category_data = CategoryCreate(
        name="New Child Category",
        description="Child Description",
        parent_id=root_category.id
    )
    category = await category_service.create_category(category_data)
    assert category.name == "New Child Category"
    assert category.parent_id == root_category.id
    assert category.full_path == f"{root_category.name} > {category.name}"

async def test_create_duplicate_category(category_service: CategoryService, root_category: Category):
    category_data = CategoryCreate(
        name=root_category.name,
        description="Another Description"
    )
    with pytest.raises(CategoryError, match=f"Category with name '{root_category.name}' already exists"):
        await category_service.create_category(category_data)

async def test_create_category_with_nonexistent_parent(category_service: CategoryService):
    category_data = CategoryCreate(
        name="Invalid Child",
        description="Description",
        parent_id=999
    )
    with pytest.raises(CategoryError, match="Parent category with ID 999 does not exist"):
        await category_service.create_category(category_data)

async def test_prevent_circular_reference(category_service: CategoryService, root_category: Category, child_category: Category):
    # Try to make the root category a child of its own child
    update_data = CategoryUpdate(
        parent_id=child_category.id
    )
    # This should raise a CategoryError
    with pytest.raises(CategoryError):
        await category_service.update_category(root_category.id, update_data)
        await category_service.db.commit()

async def test_get_categories(category_service: CategoryService, root_category: Category):
    categories = await category_service.get_categories()
    assert len(categories) >= 1
    assert any(c.id == root_category.id for c in categories)

async def test_update_category(category_service: CategoryService, root_category: Category):
    update_data = CategoryUpdate(
        name="Updated Root Category",
        description="Updated Description"
    )
    updated_category = await category_service.update_category(root_category.id, update_data)
    assert updated_category is not None
    assert updated_category.name == "Updated Root Category"
    assert updated_category.description == "Updated Description"

async def test_get_category_with_children(category_service: CategoryService, root_category: Category, child_category: Category):
    category = await category_service.get_category_with_children(root_category.id)
    assert category is not None
    assert len(category.children) == 1
    assert category.children[0].id == child_category.id

async def test_get_category_with_parent(category_service: CategoryService, child_category: Category, root_category: Category):
    category = await category_service.get_category_with_parent(child_category.id)
    assert category is not None
    assert category.parent.id == root_category.id

async def test_get_nonexistent_category(category_service: CategoryService):
    category = await category_service.get_category(999)
    assert category is None

async def test_update_nonexistent_category(category_service: CategoryService):
    update_data = CategoryUpdate(
        name="Updated Category",
        description="Updated Description"
    )
    updated_category = await category_service.update_category(999, update_data)
    assert updated_category is None

async def test_get_root_categories(category_service: CategoryService, root_category: Category, child_category: Category):
    categories = await category_service.get_root_categories()
    assert len(categories) == 1
    assert categories[0].id == root_category.id
    assert len(categories[0].children) == 1
    assert categories[0].children[0].id == child_category.id

async def test_delete_category_with_children(category_service: CategoryService, root_category: Category, child_category: Category):
    with pytest.raises(CategoryError, match="Cannot delete category that has child categories"):
        await category_service.delete_category(root_category.id)


async def test_delete_nonexistent_category(category_service: CategoryService):
    success = await category_service.delete_category(999)
    assert success is False

async def test_full_path_property(category_service: CategoryService, root_category: Category, child_category: Category):
    grandchild_data = CategoryCreate(
        name="Grandchild Category",
        description="Grandchild Description",
        parent_id=child_category.id
    )
    grandchild = await category_service.create_category(grandchild_data)
    assert grandchild.full_path == f"{root_category.name} > {child_category.name} > {grandchild.name}"

async def test_get_nonexistent_category_by_name(category_service: CategoryService):
    category = await category_service.get_category_by_name("Nonexistent Category")
    assert category is None
