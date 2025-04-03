from datetime import date, datetime, timedelta
from decimal import Decimal

import pytest
from httpx import AsyncClient

from src.models.accounts import Account
from src.models.liabilities import Liability
from src.models.payment_schedules import PaymentSchedule


@pytest.fixture
async def test_account(db_session):
    account = Account(
        name="Test Account",
        type="checking",
        available_balance=Decimal("1000.00"),
        created_at=date.today(),
        updated_at=date.today(),
    )
    db_session.add(account)
    await db_session.commit()
    return account


@pytest.fixture
async def test_liability(db_session, test_account, test_category):
    liability = Liability(
        name="Test Bill",
        amount=Decimal("100.00"),
        due_date=date.today() + timedelta(days=7),
        category_id=test_category.id,
        primary_account_id=test_account.id,
        auto_pay=False,
        auto_pay_enabled=False,
        paid=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(liability)
    await db_session.commit()
    return liability


@pytest.fixture
async def test_schedule(db_session, test_liability, test_account):
    schedule = PaymentSchedule(
        liability_id=test_liability.id,
        account_id=test_account.id,
        scheduled_date=date.today() + timedelta(days=5),
        amount=Decimal("100.00"),
        description="Test schedule",
        auto_process=False,
        processed=False,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow(),
    )
    db_session.add(schedule)
    await db_session.commit()
    return schedule


async def test_create_payment_schedule(
    client: AsyncClient, test_liability, test_account
):
    schedule_data = {
        "liability_id": test_liability.id,
        "account_id": test_account.id,
        "scheduled_date": (date.today() + timedelta(days=5)).isoformat(),
        "amount": 100.00,
        "description": "Test schedule",
    }

    response = await client.post("/api/v1/payment-schedules/", json=schedule_data)
    assert response.status_code == 200

    data = response.json()
    assert data["liability_id"] == test_liability.id
    assert data["account_id"] == test_account.id
    assert float(data["amount"]) == 100.00
    assert not data["processed"]


async def test_create_schedule_invalid_liability(client: AsyncClient, test_account):
    schedule_data = {
        "liability_id": 999999,  # Non-existent liability
        "account_id": test_account.id,
        "scheduled_date": (date.today() + timedelta(days=5)).isoformat(),
        "amount": 100.00,
    }

    response = await client.post("/api/v1/payment-schedules/", json=schedule_data)
    assert response.status_code == 400
    assert "Liability not found" in response.json()["detail"]


async def test_get_payment_schedule(client: AsyncClient, test_schedule):
    response = await client.get(f"/api/v1/payment-schedules/{test_schedule.id}")
    assert response.status_code == 200

    data = response.json()
    assert data["id"] == test_schedule.id
    assert float(data["amount"]) == 100.00


async def test_get_schedules_by_date_range(client: AsyncClient, test_schedule):
    start_date = date.today().isoformat()
    end_date = (date.today() + timedelta(days=7)).isoformat()

    response = await client.get(
        "/api/v1/payment-schedules/by-date-range/",
        params={"start_date": start_date, "end_date": end_date},
    )
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == test_schedule.id


async def test_get_schedules_by_liability(
    client: AsyncClient, test_schedule, test_liability
):
    response = await client.get(
        f"/api/v1/payment-schedules/by-liability/{test_liability.id}"
    )
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == test_schedule.id


async def test_process_schedule(client: AsyncClient, test_schedule):
    response = await client.post(
        f"/api/v1/payment-schedules/{test_schedule.id}/process"
    )
    assert response.status_code == 200

    data = response.json()
    assert data["processed"]
    assert data["processed_date"] is not None


async def test_process_already_processed_schedule(
    client: AsyncClient, test_schedule, db_session
):
    # First process
    await client.post(f"/api/v1/payment-schedules/{test_schedule.id}/process")

    # Try to process again
    response = await client.post(
        f"/api/v1/payment-schedules/{test_schedule.id}/process"
    )
    assert response.status_code == 400
    assert "Schedule already processed" in response.json()["detail"]


async def test_delete_schedule(client: AsyncClient, test_schedule):
    response = await client.delete(f"/api/v1/payment-schedules/{test_schedule.id}")
    assert response.status_code == 200
    assert response.json()["message"] == "Payment schedule deleted successfully"


async def test_delete_processed_schedule(
    client: AsyncClient, test_schedule, db_session
):
    # First process the schedule
    await client.post(f"/api/v1/payment-schedules/{test_schedule.id}/process")

    # Try to delete
    response = await client.delete(f"/api/v1/payment-schedules/{test_schedule.id}")
    assert response.status_code == 400
    assert "Cannot delete processed schedule" in response.json()["detail"]


async def test_process_due_schedules(client: AsyncClient, test_schedule, db_session):
    # Set schedule to auto-process and due today
    test_schedule.auto_process = True
    test_schedule.scheduled_date = date.today()
    await db_session.commit()

    response = await client.post("/api/v1/payment-schedules/process-due")
    assert response.status_code == 200

    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == test_schedule.id
    assert data[0]["processed"]
