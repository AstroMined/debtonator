from datetime import datetime
from decimal import Decimal

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from src.models.accounts import Account
from src.models.liabilities import Liability
from src.models.recurring_bills import RecurringBill


@pytest.fixture(scope="function")
async def test_account(db_session):
    """Create a test account"""
    account = Account(
        name="Test Account", type="checking", available_balance=Decimal("1000.00")
    )
    db_session.add(account)
    await db_session.flush()
    await db_session.refresh(account)
    return account


@pytest.fixture(scope="function")
async def test_recurring_bill(db_session, test_account, base_category):
    """Create a test recurring bill"""
    bill = RecurringBill(
        bill_name="Test Bill",
        amount=Decimal("100.00"),
        day_of_month=15,
        account_id=test_account.id,
        category_id=base_category.id,
        auto_pay=False,
        active=True,
    )
    db_session.add(bill)
    await db_session.flush()
    await db_session.refresh(bill)
    return bill


async def test_create_recurring_bill(client: AsyncClient, test_account, base_category):
    """Test creating a new recurring bill via API"""
    response = await client.post(
        "/api/v1/recurring-bills",
        json={
            "bill_name": "New Test Bill",
            "amount": "150.00",
            "day_of_month": 20,
            "account_id": test_account.id,
            "category_id": base_category.id,
            "auto_pay": True,
            "active": True,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["bill_name"] == "New Test Bill"
    assert data["amount"] == "150.00"
    assert data["day_of_month"] == 20
    assert data["account_id"] == test_account.id
    assert data["category_id"] == base_category.id
    assert data["auto_pay"] is True
    assert data["active"] is True


async def test_create_recurring_bill_invalid_account(
    client: AsyncClient, base_category
):
    """Test creating a recurring bill with nonexistent account"""
    response = await client.post(
        "/api/v1/recurring-bills",
        json={
            "bill_name": "Invalid Account Bill",
            "amount": "150.00",
            "day_of_month": 20,
            "account_id": 999,
            "category_id": base_category.id,
            "auto_pay": True,
            "active": True,
        },
    )

    assert response.status_code == 404
    assert "Account not found" in response.json()["detail"]


async def test_get_recurring_bills(client: AsyncClient, test_recurring_bill):
    """Test retrieving all recurring bills"""
    response = await client.get("/api/v1/recurring-bills")

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == test_recurring_bill.id
    assert data[0]["bill_name"] == test_recurring_bill.bill_name


async def test_get_recurring_bills_inactive(
    client: AsyncClient, db_session, test_account, base_category
):
    """Test retrieving inactive bills"""
    # Create an inactive bill
    inactive_bill = RecurringBill(
        bill_name="Inactive Bill",
        amount=Decimal("75.00"),
        day_of_month=10,
        account_id=test_account.id,
        category_id=base_category.id,
        auto_pay=False,
        active=False,
    )
    db_session.add(inactive_bill)
    await db_session.flush()

    # Test with active_only=false
    response = await client.get("/api/v1/recurring-bills?active_only=false")

    assert response.status_code == 200
    data = response.json()
    inactive_bills = [bill for bill in data if not bill["active"]]
    assert len(inactive_bills) == 1
    assert inactive_bills[0]["bill_name"] == "Inactive Bill"


async def test_get_recurring_bill(client: AsyncClient, test_recurring_bill):
    """Test retrieving a specific recurring bill"""
    response = await client.get(f"/api/v1/recurring-bills/{test_recurring_bill.id}")

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_recurring_bill.id
    assert data["bill_name"] == test_recurring_bill.bill_name
    assert data["amount"] == "100.00"


async def test_get_recurring_bill_not_found(client: AsyncClient):
    """Test retrieving a nonexistent recurring bill"""
    response = await client.get("/api/v1/recurring-bills/999")

    assert response.status_code == 404
    assert "Recurring bill not found" in response.json()["detail"]


async def test_update_recurring_bill(client: AsyncClient, test_recurring_bill):
    """Test updating a recurring bill"""
    response = await client.put(
        f"/api/v1/recurring-bills/{test_recurring_bill.id}",
        json={"bill_name": "Updated Bill Name", "amount": "200.00", "active": False},
    )

    assert response.status_code == 200
    data = response.json()
    assert data["bill_name"] == "Updated Bill Name"
    assert data["amount"] == "200.00"
    assert data["active"] is False


async def test_delete_recurring_bill(client: AsyncClient, test_recurring_bill):
    """Test deleting a recurring bill"""
    response = await client.delete(f"/api/v1/recurring-bills/{test_recurring_bill.id}")

    assert response.status_code == 200
    assert response.json()["message"] == "Recurring bill deleted"

    # Verify deletion
    get_response = await client.get(f"/api/v1/recurring-bills/{test_recurring_bill.id}")
    assert get_response.status_code == 404


async def test_generate_bills(client: AsyncClient, test_recurring_bill):
    """Test generating liabilities for a recurring bill"""
    response = await client.post(
        f"/api/v1/recurring-bills/{test_recurring_bill.id}/generate",
        json={"month": 3, "year": 2025},
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["name"] == test_recurring_bill.bill_name
    assert data[0]["amount"] == "100.00"
    assert data[0]["recurring"] is True
    assert data[0]["recurring_bill_id"] == test_recurring_bill.id
    assert (
        data[0]["category_id"] == test_recurring_bill.category_id
    )  # Category should match the recurring bill
    assert data[0]["auto_pay"] is False


async def test_generate_bills_for_month(client: AsyncClient, test_recurring_bill):
    """Test generating liabilities for all recurring bills in a month"""
    response = await client.post(
        "/api/v1/recurring-bills/generate-month", json={"month": 3, "year": 2025}
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) >= 1  # Should have at least our test bill
    generated_bill = next(
        bill for bill in data if bill["recurring_bill_id"] == test_recurring_bill.id
    )
    assert generated_bill["name"] == test_recurring_bill.bill_name
    assert generated_bill["amount"] == "100.00"
    assert generated_bill["recurring"] is True
    assert generated_bill["category_id"] == test_recurring_bill.category_id
    assert generated_bill["auto_pay"] is False


async def test_generate_bills_duplicate_period(
    client: AsyncClient, test_recurring_bill
):
    """Test attempting to generate bills for a period that already has bills"""
    # Generate bills for the first time
    await client.post(
        f"/api/v1/recurring-bills/{test_recurring_bill.id}/generate",
        json={"month": 3, "year": 2025},
    )

    # Try to generate again for the same period
    response = await client.post(
        f"/api/v1/recurring-bills/{test_recurring_bill.id}/generate",
        json={"month": 3, "year": 2025},
    )

    assert response.status_code == 400
    assert "Could not generate bills" in response.json()["detail"]
