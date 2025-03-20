import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.categories import Category
from src.schemas.categories import CategoryCreate


@pytest.fixture(scope="function")
async def test_category(db_session: AsyncSession) -> Category:
    category = Category(name="Test Category", description="Test Description")
    db_session.add(category)
    await db_session.commit()
    await db_session.refresh(category)
    return category


async def test_create_category(client: AsyncClient):
    response = await client.post(
        "/api/v1/categories/",
        json={"name": "New Category", "description": "New Description"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "New Category"
    assert data["description"] == "New Description"


async def test_create_duplicate_category(client: AsyncClient, test_category: Category):
    response = await client.post(
        "/api/v1/categories/",
        json={"name": test_category.name, "description": "Another Description"},
    )
    assert response.status_code == 400
    assert "already exists" in response.json()["detail"]


async def test_get_category(client: AsyncClient, test_category: Category):
    response = await client.get(f"/api/v1/categories/{test_category.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == test_category.name
    assert data["description"] == test_category.description


async def test_get_nonexistent_category(client: AsyncClient):
    response = await client.get("/api/v1/categories/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


async def test_list_categories(client: AsyncClient, test_category: Category):
    response = await client.get("/api/v1/categories/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(category["id"] == test_category.id for category in data)


async def test_update_category(client: AsyncClient, test_category: Category):
    response = await client.put(
        f"/api/v1/categories/{test_category.id}",
        json={"name": "Updated Category", "description": "Updated Description"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Category"
    assert data["description"] == "Updated Description"


async def test_update_nonexistent_category(client: AsyncClient):
    response = await client.put(
        "/api/v1/categories/999",
        json={"name": "Updated Category", "description": "Updated Description"},
    )
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


async def test_delete_category(client: AsyncClient, test_category: Category):
    response = await client.delete(f"/api/v1/categories/{test_category.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Category deleted successfully"

    # Verify category is deleted
    response = await client.get(f"/api/v1/categories/{test_category.id}")
    assert response.status_code == 404


async def test_delete_nonexistent_category(client: AsyncClient):
    response = await client.delete("/api/v1/categories/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Category not found"


async def test_get_category_with_bills(client: AsyncClient, test_category: Category):
    response = await client.get(f"/api/v1/categories/{test_category.id}/bills")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_category.id
    assert "bills" in data
    assert isinstance(data["bills"], list)
