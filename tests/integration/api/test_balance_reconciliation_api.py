from datetime import datetime
from decimal import Decimal
import pytest
from httpx import AsyncClient
from sqlalchemy import select

from src.models.accounts import Account
from src.models.balance_reconciliation import BalanceReconciliation

@pytest.fixture(scope="function")
async def test_account(db_session):
    """Create a test account"""
    account = Account(
        name="Test Account",
        type="checking",
        available_balance=Decimal("1000.00"),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(account)
    await db_session.commit()
    await db_session.refresh(account)
    return account

@pytest.fixture(scope="function")
async def test_reconciliation(db_session, test_account):
    """Create a test reconciliation record"""
    reconciliation = BalanceReconciliation(
        account_id=test_account.id,
        previous_balance=Decimal("1000.00"),
        new_balance=Decimal("1100.00"),
        adjustment_amount=Decimal("100.00"),
        reason="Test reconciliation",
        reconciliation_date=datetime.utcnow(),
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    db_session.add(reconciliation)
    await db_session.commit()
    await db_session.refresh(reconciliation)
    return reconciliation

async def test_create_reconciliation(client: AsyncClient, test_account):
    """Test creating a new reconciliation record via API"""
    response = await client.post(
        f"/api/v1/accounts/{test_account.id}/reconcile",
        json={
            "account_id": test_account.id,
            "previous_balance": "1000.00",
            "new_balance": "1100.00",
            "reason": "Test reconciliation"
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["account_id"] == test_account.id
    assert data["previous_balance"] == "1000.00"
    assert data["new_balance"] == "1100.00"
    assert data["adjustment_amount"] == "100.00"
    assert data["reason"] == "Test reconciliation"

async def test_create_reconciliation_mismatched_account(client: AsyncClient, test_account):
    """Test creating a reconciliation with mismatched account IDs"""
    response = await client.post(
        f"/api/v1/accounts/{test_account.id}/reconcile",
        json={
            "account_id": test_account.id + 1,
            "previous_balance": "1000.00",
            "new_balance": "1100.00",
            "reason": "Test reconciliation"
        }
    )
    
    assert response.status_code == 400
    assert "Account ID in path must match account ID in request body" in response.json()["detail"]

async def test_create_reconciliation_invalid_account(client: AsyncClient):
    """Test creating a reconciliation for a nonexistent account"""
    response = await client.post(
        "/api/v1/accounts/999/reconcile",
        json={
            "account_id": 999,
            "previous_balance": "1000.00",
            "new_balance": "1100.00",
            "reason": "Test reconciliation"
        }
    )
    
    assert response.status_code == 404
    assert "Account with id 999 not found" in response.json()["detail"]

async def test_get_account_reconciliations(client: AsyncClient, test_account, test_reconciliation):
    """Test retrieving reconciliation history for an account"""
    response = await client.get(f"/api/v1/accounts/{test_account.id}/reconciliations")
    
    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == test_reconciliation.id
    assert data[0]["account_id"] == test_account.id

async def test_get_reconciliation(client: AsyncClient, test_account, test_reconciliation):
    """Test retrieving a specific reconciliation record"""
    response = await client.get(
        f"/api/v1/accounts/{test_account.id}/reconciliations/{test_reconciliation.id}"
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_reconciliation.id
    assert data["account_id"] == test_account.id
    assert data["previous_balance"] == "1000.00"
    assert data["new_balance"] == "1100.00"

async def test_get_reconciliation_wrong_account(client: AsyncClient, test_reconciliation):
    """Test retrieving a reconciliation record with wrong account ID"""
    response = await client.get(
        f"/api/v1/accounts/999/reconciliations/{test_reconciliation.id}"
    )
    
    assert response.status_code == 404
    assert "Reconciliation record not found for this account" in response.json()["detail"]

async def test_update_reconciliation(client: AsyncClient, test_account, test_reconciliation):
    """Test updating a reconciliation record"""
    response = await client.patch(
        f"/api/v1/accounts/{test_account.id}/reconciliations/{test_reconciliation.id}",
        json={"reason": "Updated reason"}
    )
    
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_reconciliation.id
    assert data["reason"] == "Updated reason"

async def test_update_reconciliation_wrong_account(client: AsyncClient, test_reconciliation):
    """Test updating a reconciliation record with wrong account ID"""
    response = await client.patch(
        f"/api/v1/accounts/999/reconciliations/{test_reconciliation.id}",
        json={"reason": "Updated reason"}
    )
    
    assert response.status_code == 404
    assert "Reconciliation record not found for this account" in response.json()["detail"]

async def test_delete_reconciliation(client: AsyncClient, test_account, test_reconciliation):
    """Test deleting a reconciliation record"""
    response = await client.delete(
        f"/api/v1/accounts/{test_account.id}/reconciliations/{test_reconciliation.id}"
    )
    
    assert response.status_code == 200
    assert response.json()["message"] == "Reconciliation record deleted successfully"

async def test_delete_reconciliation_wrong_account(client: AsyncClient, test_reconciliation):
    """Test deleting a reconciliation record with wrong account ID"""
    response = await client.delete(
        f"/api/v1/accounts/999/reconciliations/{test_reconciliation.id}"
    )
    
    assert response.status_code == 404
    assert "Reconciliation record not found for this account" in response.json()["detail"]
