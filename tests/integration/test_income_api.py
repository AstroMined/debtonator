import pytest
from decimal import Decimal
from datetime import date
from httpx import AsyncClient

@pytest.fixture
async def account_create_data():
    return {
        "name": "Test Checking",
        "type": "checking",
        "available_balance": "1000.00",
        "created_at": str(date.today()),
        "updated_at": str(date.today())
    }

@pytest.fixture
def income_create_data():
    def _income_create_data(account_id: int):
        return {
            "date": str(date.today()),
            "source": "Test Paycheck",
            "amount": "2000.00",
            "deposited": False,
            "account_id": account_id
        }
    return _income_create_data

@pytest.fixture
async def test_account(client: AsyncClient, account_create_data):
    response = await client.post("/api/v1/accounts/", json=account_create_data)
    assert response.status_code == 201
    return response.json()

@pytest.mark.asyncio
async def test_create_income(client: AsyncClient, test_account, income_create_data):
    income_data = income_create_data(test_account["id"])
    response = await client.post("/api/v1/income/", json=income_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["source"] == income_data["source"]
    assert Decimal(data["amount"]) == Decimal(income_data["amount"])
    assert data["deposited"] == income_data["deposited"]
    assert data["account_id"] == test_account["id"]
    assert "id" in data

@pytest.mark.asyncio
async def test_get_income(client: AsyncClient, test_account, income_create_data):
    # First create an income entry
    income_data = income_create_data(test_account["id"])
    create_response = await client.post("/api/v1/income/", json=income_data)
    assert create_response.status_code == 201
    created_income = create_response.json()
    
    # Then fetch it
    response = await client.get(f"/api/v1/income/{created_income['id']}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["source"] == income_data["source"]
    assert Decimal(data["amount"]) == Decimal(income_data["amount"])
    assert data["account_id"] == test_account["id"]

@pytest.mark.asyncio
async def test_update_income_deposit_status(client: AsyncClient, test_account, income_create_data):
    # First create an income entry
    income_data = income_create_data(test_account["id"])
    create_response = await client.post("/api/v1/income/", json=income_data)
    assert create_response.status_code == 201
    created_income = create_response.json()
    
    # Update deposit status
    update_data = {
        "deposited": True
    }
    response = await client.put(f"/api/v1/income/{created_income['id']}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["deposited"] is True
    
    # Verify account balance was updated
    account_response = await client.get(f"/api/v1/accounts/{test_account['id']}")
    assert account_response.status_code == 200
    updated_account = account_response.json()
    assert Decimal(updated_account["available_balance"]) == Decimal(test_account["available_balance"]) + Decimal(income_data["amount"])

@pytest.mark.asyncio
async def test_get_all_income(client: AsyncClient, test_account, income_create_data):
    # Create multiple income entries
    income_data = income_create_data(test_account["id"])
    await client.post("/api/v1/income/", json=income_data)
    
    income_data["source"] = "Second Paycheck"
    await client.post("/api/v1/income/", json=income_data)
    
    # Fetch all income entries
    response = await client.get("/api/v1/income/")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert any(income["source"] == "Test Paycheck" for income in data)
    assert any(income["source"] == "Second Paycheck" for income in data)

@pytest.mark.asyncio
async def test_create_income_validation(client: AsyncClient, test_account):
    # Test missing required fields
    invalid_data = {
        "source": "Invalid Income"
    }
    response = await client.post("/api/v1/income/", json=invalid_data)
    assert response.status_code == 422

    # Test invalid account_id
    invalid_data = {
        "date": str(date.today()),
        "source": "Test Income",
        "amount": "1000.00",
        "deposited": False,
        "account_id": 999
    }
    response = await client.post("/api/v1/income/", json=invalid_data)
    assert response.status_code == 404

    # Test negative amount
    invalid_data = {
        "date": str(date.today()),
        "source": "Test Income",
        "amount": "-1000.00",
        "deposited": False,
        "account_id": test_account["id"]
    }
    response = await client.post("/api/v1/income/", json=invalid_data)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_get_nonexistent_income(client: AsyncClient):
    response = await client.get("/api/v1/income/999")
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_filter_income_by_account(client: AsyncClient, test_account, income_create_data):
    # Create income for our test account
    income_data = income_create_data(test_account["id"])
    await client.post("/api/v1/income/", json=income_data)
    
    # Create another account and income for it
    second_account = await client.post("/api/v1/accounts/", json={
        "name": "Second Checking",
        "type": "checking",
        "available_balance": "1000.00",
        "created_at": str(date.today()),
        "updated_at": str(date.today())
    })
    assert second_account.status_code == 201
    second_account_data = second_account.json()
    
    income_data["account_id"] = second_account_data["id"]
    income_data["source"] = "Other Account Income"
    await client.post("/api/v1/income/", json=income_data)
    
    # Filter income by first account
    response = await client.get(f"/api/v1/income/?account_id={test_account['id']}")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 1
    assert data[0]["source"] == "Test Paycheck"
    assert data[0]["account_id"] == test_account["id"]

@pytest.mark.asyncio
async def test_update_income_amount_updates_balance(client: AsyncClient, test_account, income_create_data):
    # Create and deposit income
    income_data = income_create_data(test_account["id"])
    create_response = await client.post("/api/v1/income/", json=income_data)
    assert create_response.status_code == 201
    created_income = create_response.json()
    
    # Mark as deposited
    await client.put(f"/api/v1/income/{created_income['id']}/deposit")
    
    # Update amount
    update_data = {
        "amount": "2500.00"  # Increase from original 2000.00
    }
    response = await client.put(f"/api/v1/income/{created_income['id']}", json=update_data)
    assert response.status_code == 200
    
    # Verify account balance reflects the change
    account_response = await client.get(f"/api/v1/accounts/{test_account['id']}")
    assert account_response.status_code == 200
    updated_account = account_response.json()
    assert Decimal(updated_account["available_balance"]) == Decimal(test_account["available_balance"]) + Decimal(update_data["amount"])
