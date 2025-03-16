import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.services.income_categories import IncomeCategoryService
from src.schemas.income_categories import IncomeCategoryCreate

@pytest.fixture(scope="function")
async def sample_category(db_session: AsyncSession):
    service = IncomeCategoryService(db_session)
    category = IncomeCategoryCreate(
        name="Salary",
        description="Regular employment income"
    )
    return await service.create_category(category)

async def test_create_income_category(client: AsyncClient):
    """Test creating a new income category"""
    response = await client.post(
        "/api/v1/income/categories",
        json={
            "name": "Freelance",
            "description": "Income from freelance work"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["name"] == "Freelance"
    assert data["description"] == "Income from freelance work"

async def test_list_income_categories(
    client: AsyncClient,
    sample_category
):
    """Test listing all income categories"""
    response = await client.get("/api/v1/income/categories")
    print("Response:", response.status_code, response.json())
    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1
    assert any(category["name"] == "Salary" for category in data)

async def test_get_income_category(
    client: AsyncClient,
    sample_category
):
    """Test getting a specific income category"""
    response = await client.get(f"/api/v1/income/categories/{sample_category.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Salary"
    assert data["description"] == "Regular employment income"

async def test_update_income_category(
    client: AsyncClient,
    sample_category
):
    """Test updating an income category"""
    response = await client.put(
        f"/api/v1/income/categories/{sample_category.id}",
        json={
            "name": "Updated Salary",
            "description": "Updated description"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["name"] == "Updated Salary"
    assert data["description"] == "Updated description"

async def test_delete_income_category(
    client: AsyncClient,
    sample_category
):
    """Test deleting an income category"""
    response = await client.delete(f"/api/v1/income/categories/{sample_category.id}")
    assert response.status_code == 204

async def test_get_nonexistent_category(client: AsyncClient):
    """Test getting a non-existent category"""
    response = await client.get("/api/v1/income/categories/999")
    assert response.status_code == 404

async def test_update_nonexistent_category(client: AsyncClient):
    """Test updating a non-existent category"""
    response = await client.put(
        "/api/v1/income/categories/999",
        json={"name": "Test"}
    )
    assert response.status_code == 404

async def test_delete_nonexistent_category(client: AsyncClient):
    """Test deleting a non-existent category"""
    response = await client.delete("/api/v1/income/categories/999")
    assert response.status_code == 404

async def test_create_duplicate_category(
    client: AsyncClient,
    sample_category
):
    """Test creating a category with duplicate name"""
    response = await client.post(
        "/api/v1/income/categories",
        json={
            "name": "Salary",
            "description": "Duplicate name"
        }
    )
    assert response.status_code == 409
