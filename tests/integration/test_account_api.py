import pytest
from decimal import Decimal
from datetime import date
from httpx import AsyncClient

@pytest.fixture
async def account_create_data():
    data = {
        "name": "Test Checking",
        "type": "checking",
        "available_balance": "1000.00",
        "created_at": str(date.today()),
        "updated_at": str(date.today())
    }
    print(f"\nAccount create data: {data}")
    return data

@pytest.fixture
async def credit_account_create_data():
    data = {
        "name": "Test Credit Card",
        "type": "credit",
        "available_balance": "-500.00",
        "total_limit": "2000.00",
        "available_credit": "1500.00",
        "last_statement_balance": "500.00",
        "last_statement_date": str(date.today()),
        "created_at": str(date.today()),
        "updated_at": str(date.today())
    }
    print(f"\nCredit account create data: {data}")
    return data

@pytest.mark.asyncio
async def test_create_checking_account(setup_db, client: AsyncClient, account_create_data):
    # Ensure proper JSON formatting
    json_data = {
        "name": account_create_data["name"],
        "type": account_create_data["type"],
        "available_balance": account_create_data["available_balance"],
        "created_at": account_create_data["created_at"],
        "updated_at": account_create_data["updated_at"]
    }
    response = await client.post("/api/v1/accounts/", json=json_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == account_create_data["name"]
    assert data["type"] == account_create_data["type"]
    assert Decimal(data["available_balance"]) == Decimal(account_create_data["available_balance"])
    assert "id" in data

@pytest.mark.asyncio
async def test_create_credit_account(setup_db, client: AsyncClient, credit_account_create_data):
    # Ensure proper JSON formatting
    json_data = {
        "name": credit_account_create_data["name"],
        "type": credit_account_create_data["type"],
        "available_balance": credit_account_create_data["available_balance"],
        "total_limit": credit_account_create_data["total_limit"],
        "available_credit": credit_account_create_data["available_credit"],
        "last_statement_balance": credit_account_create_data["last_statement_balance"],
        "last_statement_date": credit_account_create_data["last_statement_date"],
        "created_at": credit_account_create_data["created_at"],
        "updated_at": credit_account_create_data["updated_at"]
    }
    response = await client.post("/api/v1/accounts/", json=json_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["name"] == credit_account_create_data["name"]
    assert data["type"] == credit_account_create_data["type"]
    assert Decimal(data["available_balance"]) == Decimal(credit_account_create_data["available_balance"])
    assert Decimal(data["total_limit"]) == Decimal(credit_account_create_data["total_limit"])
    assert Decimal(data["available_credit"]) == Decimal(credit_account_create_data["available_credit"])
    assert "id" in data

@pytest.mark.asyncio
async def test_get_account(setup_db, client: AsyncClient, account_create_data):
    # First create an account
    # Ensure proper JSON formatting
    json_data = {
        "name": account_create_data["name"],
        "type": account_create_data["type"],
        "available_balance": account_create_data["available_balance"],
        "created_at": account_create_data["created_at"],
        "updated_at": account_create_data["updated_at"]
    }
    create_response = await client.post("/api/v1/accounts/", json=json_data)
    assert create_response.status_code == 201
    created_account = create_response.json()
    
    # Then fetch it
    response = await client.get(f"/api/v1/accounts/{created_account['id']}")
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == account_create_data["name"]
    assert data["type"] == account_create_data["type"]
    assert Decimal(data["available_balance"]) == Decimal(account_create_data["available_balance"])

@pytest.mark.asyncio
async def test_update_account(setup_db, client: AsyncClient, account_create_data):
    # First create an account
    # Ensure proper JSON formatting
    json_data = {
        "name": account_create_data["name"],
        "type": account_create_data["type"],
        "available_balance": account_create_data["available_balance"],
        "created_at": account_create_data["created_at"],
        "updated_at": account_create_data["updated_at"]
    }
    create_response = await client.post("/api/v1/accounts/", json=json_data)
    assert create_response.status_code == 201
    created_account = create_response.json()
    
    # Update the account
    update_data = {
        "name": "Updated Checking",
        "available_balance": "1500.00"
    }
    response = await client.patch(f"/api/v1/accounts/{created_account['id']}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert data["name"] == update_data["name"]
    assert Decimal(data["available_balance"]) == Decimal(update_data["available_balance"])

@pytest.mark.asyncio
async def test_get_all_accounts(setup_db, client: AsyncClient, account_create_data, credit_account_create_data):
    # Create two accounts
    # Ensure proper JSON formatting for both accounts
    checking_data = {
        "name": account_create_data["name"],
        "type": account_create_data["type"],
        "available_balance": account_create_data["available_balance"],
        "created_at": account_create_data["created_at"],
        "updated_at": account_create_data["updated_at"]
    }
    credit_data = {
        "name": credit_account_create_data["name"],
        "type": credit_account_create_data["type"],
        "available_balance": credit_account_create_data["available_balance"],
        "total_limit": credit_account_create_data["total_limit"],
        "available_credit": credit_account_create_data["available_credit"],
        "last_statement_balance": credit_account_create_data["last_statement_balance"],
        "last_statement_date": credit_account_create_data["last_statement_date"],
        "created_at": credit_account_create_data["created_at"],
        "updated_at": credit_account_create_data["updated_at"]
    }
    await client.post("/api/v1/accounts/", json=checking_data)
    await client.post("/api/v1/accounts/", json=credit_data)
    
    # Fetch all accounts
    response = await client.get("/api/v1/accounts/")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert any(account["name"] == account_create_data["name"] for account in data)
    assert any(account["name"] == credit_account_create_data["name"] for account in data)

@pytest.mark.asyncio
async def test_create_account_validation(setup_db, client: AsyncClient):
    # Test invalid account type
    invalid_data = {
        "name": "Invalid Account",
        "type": "invalid_type",
        "available_balance": "1000.00"
    }
    response = await client.post("/api/v1/accounts/", json=invalid_data)
    assert response.status_code == 422

    # Test missing required field
    incomplete_data = {
        "name": "Incomplete Account"
    }
    response = await client.post("/api/v1/accounts/", json=incomplete_data)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_get_nonexistent_account(setup_db, client: AsyncClient):
    response = await client.get("/api/v1/accounts/999")
    assert response.status_code == 404
