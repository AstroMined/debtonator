from datetime import date, timedelta
from decimal import Decimal
import pytest
from httpx import AsyncClient

from src.models.accounts import Account
from src.models.income import Income
from src.models.deposit_schedules import DepositSchedule

@pytest.fixture
async def test_account(db_session):
    account = Account(
        name="Test Checking",
        type="checking",
        available_balance=Decimal("1000.00")
    )
    db_session.add(account)
    await db_session.commit()
    return account

@pytest.fixture
async def test_income(db_session, test_account):
    income = Income(
        date=date.today(),
        source="Test Income",
        amount=Decimal("2000.00"),
        deposited=False,
        account_id=test_account.id
    )
    db_session.add(income)
    await db_session.commit()
    return income

@pytest.fixture
async def test_deposit_schedule(db_session, test_income, test_account):
    schedule = DepositSchedule(
        income_id=test_income.id,
        account_id=test_account.id,
        schedule_date=date.today() + timedelta(days=1),
        amount=Decimal("1000.00"),
        recurring=False,
        status="pending"
    )
    db_session.add(schedule)
    await db_session.commit()
    return schedule

async def test_create_deposit_schedule(client: AsyncClient, test_income, test_account):
    response = await client.post(
        "/api/v1/deposit-schedules/",
        json={
            "income_id": test_income.id,
            "account_id": test_account.id,
            "schedule_date": (date.today() + timedelta(days=1)).isoformat(),
            "amount": "1000.00",
            "recurring": False,
            "status": "pending"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["income_id"] == test_income.id
    assert data["account_id"] == test_account.id
    assert data["amount"] == "1000.00"

async def test_create_deposit_schedule_invalid_amount(
    client: AsyncClient, test_income, test_account
):
    response = await client.post(
        "/api/v1/deposit-schedules/",
        json={
            "income_id": test_income.id,
            "account_id": test_account.id,
            "schedule_date": (date.today() + timedelta(days=1)).isoformat(),
            "amount": "3000.00",  # More than income amount
            "recurring": False,
            "status": "pending"
        }
    )
    assert response.status_code == 400
    assert response.json()["detail"] == "Schedule amount cannot exceed income amount"

async def test_get_deposit_schedule(client: AsyncClient, test_deposit_schedule):
    response = await client.get(f"/api/v1/deposit-schedules/{test_deposit_schedule.id}")
    assert response.status_code == 200
    data = response.json()
    assert data["id"] == test_deposit_schedule.id
    assert data["amount"] == "1000.00"

async def test_get_deposit_schedule_not_found(client: AsyncClient):
    response = await client.get("/api/v1/deposit-schedules/999")
    assert response.status_code == 404
    assert response.json()["detail"] == "Deposit schedule not found"

async def test_update_deposit_schedule(client: AsyncClient, test_deposit_schedule):
    response = await client.put(
        f"/api/v1/deposit-schedules/{test_deposit_schedule.id}",
        json={
            "amount": "500.00",
            "status": "completed"
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert data["amount"] == "500.00"
    assert data["status"] == "completed"

async def test_delete_deposit_schedule(client: AsyncClient, test_deposit_schedule):
    response = await client.delete(f"/api/v1/deposit-schedules/{test_deposit_schedule.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Deposit schedule deleted successfully"

    # Verify deletion
    response = await client.get(f"/api/v1/deposit-schedules/{test_deposit_schedule.id}")
    assert response.status_code == 404

async def test_list_deposit_schedules(client: AsyncClient, test_deposit_schedule):
    response = await client.get("/api/v1/deposit-schedules/")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert any(s["id"] == test_deposit_schedule.id for s in data)

async def test_list_deposit_schedules_with_filters(
    client: AsyncClient, test_deposit_schedule, test_income, test_account
):
    response = await client.get(
        "/api/v1/deposit-schedules/",
        params={
            "income_id": test_income.id,
            "account_id": test_account.id,
            "status": "pending",
            "from_date": date.today().isoformat(),
            "to_date": (date.today() + timedelta(days=7)).isoformat()
        }
    )
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(s["income_id"] == test_income.id for s in data)
    assert all(s["account_id"] == test_account.id for s in data)
    assert all(s["status"] == "pending" for s in data)

async def test_get_pending_deposits(client: AsyncClient, test_deposit_schedule, test_account):
    response = await client.get(f"/api/v1/deposit-schedules/pending/{test_account.id}")
    assert response.status_code == 200
    data = response.json()
    assert len(data) > 0
    assert all(s["status"] == "pending" for s in data)
    assert all(s["account_id"] == test_account.id for s in data)
