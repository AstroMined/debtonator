import pytest
from decimal import Decimal
from datetime import date
from httpx import AsyncClient

@pytest.fixture
async def bill_split_create_data():
    data = {
        "bill_id": 1,  # Will be replaced with actual bill ID in tests
        "account_id": 1,  # Will be replaced with actual account ID in tests
        "amount": "100.00"
    }
    return data

@pytest.mark.asyncio
async def test_create_bill_split(setup_db, client: AsyncClient, bill_split_create_data):
    # First create an account and a bill to reference
    account_data = {
        "name": "Test Account",
        "type": "checking",
        "available_balance": "1000.00",
        "created_at": str(date.today()),
        "updated_at": str(date.today())
    }
    account_response = await client.post("/api/v1/accounts/", json=account_data)
    assert account_response.status_code == 201
    account_id = account_response.json()["id"]

    bill_data = {
        "month": "01",  # January
        "day_of_month": 15,
        "bill_name": "Test Bill",
        "amount": "200.00",
        "account_id": account_id,
        "account_name": "Test Account",  # Add account_name
        "auto_pay": False,
        "paid": False
    }
    bill_response = await client.post("/api/v1/bills/", json=bill_data)
    assert bill_response.status_code == 201
    bill_id = bill_response.json()["id"]

    # Update test data with actual IDs
    bill_split_create_data["bill_id"] = bill_id
    bill_split_create_data["account_id"] = account_id

    # Create bill split
    response = await client.post("/api/v1/bill-splits/", json=bill_split_create_data)
    assert response.status_code == 201
    
    data = response.json()
    assert data["bill_id"] == bill_split_create_data["bill_id"]
    assert data["account_id"] == bill_split_create_data["account_id"]
    assert Decimal(data["amount"]) == Decimal(bill_split_create_data["amount"])
    assert "id" in data

@pytest.mark.asyncio
async def test_get_bill_splits(setup_db, client: AsyncClient, bill_split_create_data):
    # First create the necessary data
    account_data = {
        "name": "Test Account",
        "type": "checking",
        "available_balance": "1000.00",
        "created_at": str(date.today()),
        "updated_at": str(date.today())
    }
    account_response = await client.post("/api/v1/accounts/", json=account_data)
    account_id = account_response.json()["id"]

    bill_data = {
        "month": "01",  # January
        "day_of_month": 15,
        "bill_name": "Test Bill",
        "amount": "200.00",
        "account_id": account_id,
        "account_name": "Test Account",  # Add account_name
        "auto_pay": False,
        "paid": False
    }
    bill_response = await client.post("/api/v1/bills/", json=bill_data)
    bill_id = bill_response.json()["id"]

    # Create two splits for the same bill
    split1_data = {
        "bill_id": bill_id,
        "account_id": account_id,
        "amount": "100.00"
    }
    split2_data = {
        "bill_id": bill_id,
        "account_id": account_id,
        "amount": "100.00"
    }
    await client.post("/api/v1/bill-splits/", json=split1_data)
    await client.post("/api/v1/bill-splits/", json=split2_data)

    # Get splits for the bill
    response = await client.get(f"/api/v1/bill-splits/{bill_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert all(split["bill_id"] == bill_id for split in data)
    assert sum(Decimal(split["amount"]) for split in data) == Decimal("200.00")

@pytest.mark.asyncio
async def test_get_account_splits(setup_db, client: AsyncClient):
    # Create test account
    account_data = {
        "name": "Test Account",
        "type": "checking",
        "available_balance": "1000.00",
        "created_at": str(date.today()),
        "updated_at": str(date.today())
    }
    account_response = await client.post("/api/v1/accounts/", json=account_data)
    account_id = account_response.json()["id"]

    # Create two bills
    bill_data1 = {
        "month": "01",  # January
        "day_of_month": 15,
        "bill_name": "Test Bill 1",
        "amount": "200.00",
        "account_id": account_id,
        "account_name": "Test Account",  # Add account_name
        "auto_pay": False,
        "paid": False
    }
    bill_data2 = {
        "month": "01",  # January
        "day_of_month": 20,
        "bill_name": "Test Bill 2",
        "amount": "300.00",
        "account_id": account_id,
        "account_name": "Test Account",  # Add account_name
        "auto_pay": False,
        "paid": False
    }
    bill1_response = await client.post("/api/v1/bills/", json=bill_data1)
    bill2_response = await client.post("/api/v1/bills/", json=bill_data2)
    
    # Create splits for both bills using the same account
    split1_data = {
        "bill_id": bill1_response.json()["id"],
        "account_id": account_id,
        "amount": "100.00"
    }
    split2_data = {
        "bill_id": bill2_response.json()["id"],
        "account_id": account_id,
        "amount": "150.00"
    }
    await client.post("/api/v1/bill-splits/", json=split1_data)
    await client.post("/api/v1/bill-splits/", json=split2_data)

    # Get splits for the account
    response = await client.get(f"/api/v1/bill-splits/account/{account_id}")
    assert response.status_code == 200
    
    data = response.json()
    assert len(data) == 2
    assert all(split["account_id"] == account_id for split in data)

@pytest.mark.asyncio
async def test_update_bill_split(setup_db, client: AsyncClient, bill_split_create_data):
    # Create necessary test data
    account_data = {
        "name": "Test Account",
        "type": "checking",
        "available_balance": "1000.00",
        "created_at": str(date.today()),
        "updated_at": str(date.today())
    }
    account_response = await client.post("/api/v1/accounts/", json=account_data)
    account_id = account_response.json()["id"]

    bill_data = {
        "month": "01",  # January
        "day_of_month": 15,
        "bill_name": "Test Bill",
        "amount": "200.00",
        "account_id": account_id,
        "account_name": "Test Account",  # Add account_name
        "auto_pay": False,
        "paid": False
    }
    bill_response = await client.post("/api/v1/bills/", json=bill_data)
    bill_id = bill_response.json()["id"]

    # Create initial split
    split_data = {
        "bill_id": bill_id,
        "account_id": account_id,
        "amount": "100.00"
    }
    create_response = await client.post("/api/v1/bill-splits/", json=split_data)
    created_split = create_response.json()

    # Update the split
    update_data = {
        "amount": "150.00"
    }
    response = await client.put(f"/api/v1/bill-splits/{created_split['id']}", json=update_data)
    assert response.status_code == 200
    
    data = response.json()
    assert Decimal(data["amount"]) == Decimal(update_data["amount"])

@pytest.mark.asyncio
async def test_delete_bill_split(setup_db, client: AsyncClient):
    # Create necessary test data
    account_data = {
        "name": "Test Account",
        "type": "checking",
        "available_balance": "1000.00",
        "created_at": str(date.today()),
        "updated_at": str(date.today())
    }
    account_response = await client.post("/api/v1/accounts/", json=account_data)
    account_id = account_response.json()["id"]

    bill_data = {
        "month": "01",  # January
        "day_of_month": 15,
        "bill_name": "Test Bill",
        "amount": "200.00",
        "account_id": account_id,
        "account_name": "Test Account",  # Add account_name
        "auto_pay": False,
        "paid": False
    }
    bill_response = await client.post("/api/v1/bills/", json=bill_data)
    bill_id = bill_response.json()["id"]

    # Create split to delete
    split_data = {
        "bill_id": bill_id,
        "account_id": account_id,
        "amount": "100.00"
    }
    create_response = await client.post("/api/v1/bill-splits/", json=split_data)
    created_split = create_response.json()

    # Delete the split
    response = await client.delete(f"/api/v1/bill-splits/{created_split['id']}")
    assert response.status_code == 200

    # Verify deletion
    get_response = await client.get(f"/api/v1/bill-splits/{bill_id}")
    assert get_response.status_code == 200
    assert len(get_response.json()) == 0

@pytest.mark.asyncio
async def test_delete_bill_splits(setup_db, client: AsyncClient):
    # Create necessary test data
    account_data = {
        "name": "Test Account",
        "type": "checking",
        "available_balance": "1000.00",
        "created_at": str(date.today()),
        "updated_at": str(date.today())
    }
    account_response = await client.post("/api/v1/accounts/", json=account_data)
    account_id = account_response.json()["id"]

    bill_data = {
        "month": "01",  # January
        "day_of_month": 15,
        "bill_name": "Test Bill",
        "amount": "200.00",
        "account_id": account_id,
        "account_name": "Test Account",  # Add account_name
        "auto_pay": False,
        "paid": False
    }
    bill_response = await client.post("/api/v1/bills/", json=bill_data)
    bill_id = bill_response.json()["id"]

    # Create multiple splits
    split1_data = {
        "bill_id": bill_id,
        "account_id": account_id,
        "amount": "100.00"
    }
    split2_data = {
        "bill_id": bill_id,
        "account_id": account_id,
        "amount": "100.00"
    }
    await client.post("/api/v1/bill-splits/", json=split1_data)
    await client.post("/api/v1/bill-splits/", json=split2_data)

    # Delete all splits for the bill
    response = await client.delete(f"/api/v1/bill-splits/bill/{bill_id}")
    assert response.status_code == 200

    # Verify deletion
    get_response = await client.get(f"/api/v1/bill-splits/{bill_id}")
    assert get_response.status_code == 200
    assert len(get_response.json()) == 0

@pytest.mark.asyncio
async def test_create_bill_split_validation(setup_db, client: AsyncClient):
    # Test invalid bill_id
    invalid_data = {
        "bill_id": 999,  # Non-existent bill
        "account_id": 1,
        "amount": "100.00"
    }
    response = await client.post("/api/v1/bill-splits/", json=invalid_data)
    assert response.status_code == 400

    # Test missing required field
    incomplete_data = {
        "bill_id": 1
        # Missing amount and account_id
    }
    response = await client.post("/api/v1/bill-splits/", json=incomplete_data)
    assert response.status_code == 422

@pytest.mark.asyncio
async def test_get_nonexistent_bill_splits(setup_db, client: AsyncClient):
    response = await client.get("/api/v1/bill-splits/999")
    assert response.status_code == 200
    assert len(response.json()) == 0

@pytest.mark.asyncio
async def test_update_nonexistent_bill_split(setup_db, client: AsyncClient):
    update_data = {
        "amount": "150.00"
    }
    response = await client.put("/api/v1/bill-splits/999", json=update_data)
    assert response.status_code == 404

@pytest.mark.asyncio
async def test_delete_nonexistent_bill_split(setup_db, client: AsyncClient):
    response = await client.delete("/api/v1/bill-splits/999")
    assert response.status_code == 404
