from datetime import date, timedelta
from decimal import Decimal
import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.main import app
from src.models.income import Income

@pytest.mark.asyncio
async def test_analyze_income_trends(client: AsyncClient, db_session: AsyncSession):
    # Create test data
    today = date.today()
    request_data = {
        "start_date": (today - timedelta(days=90)).isoformat(),
        "end_date": today.isoformat(),
        "min_confidence": 0.5
    }
    
    response = await client.post("/api/v1/income-analysis/trends", json=request_data)
    assert response.status_code == 400  # Should fail with no data
    assert "No income records found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_analyze_source_trends(client: AsyncClient, db_session: AsyncSession, base_account):
    # Create test income data
    source = "Test Source"
    amount = Decimal("1000.00")
    today = date.today()
    
    # Create multiple income records for the same source
    for i in range(3):
        income = Income(
            date=today - timedelta(days=i*30),
            source=source,
            amount=amount,
            deposited=False,
            undeposited_amount=amount,
            account_id=base_account.id,
            recurring=False,
            created_at=today,
            updated_at=today
        )
        db_session.add(income)
    
    await db_session.commit()
    
    response = await client.get(
        f"/api/v1/income-analysis/trends/source/{source}",
        params={
            "start_date": (today - timedelta(days=90)).isoformat(),
            "end_date": today.isoformat(),
            "min_confidence": 0.5
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["patterns"]) > 0
    assert data["patterns"][0]["source"] == source
    assert Decimal(data["patterns"][0]["average_amount"]) == amount
    assert data["overall_predictability_score"] > 0

@pytest.mark.asyncio
async def test_analyze_period_trends(client: AsyncClient, db_session: AsyncSession, base_account):
    # Create test income data
    today = date.today()
    start_date = today - timedelta(days=90)
    
    # Create multiple income records with different sources
    sources = ["Source A", "Source B"]
    for source in sources:
        for i in range(3):
            income = Income(
                date=today - timedelta(days=i*30),
                source=source,
                amount=Decimal("1000.00"),
                deposited=False,
                undeposited_amount=Decimal("1000.00"),
                account_id=base_account.id,
                recurring=False,
                created_at=today,
                updated_at=today
            )
            db_session.add(income)
    
    await db_session.commit()
    
    response = await client.get(
        "/api/v1/income-analysis/trends/period",
        params={
            "start_date": start_date.isoformat(),
            "end_date": today.isoformat(),
            "min_confidence": 0.5
        }
    )
    
    assert response.status_code == 200
    data = response.json()
    assert len(data["patterns"]) >= len(sources)
    assert data["analysis_date"] == today.isoformat()
    assert data["data_start_date"] >= start_date.isoformat()
    assert data["data_end_date"] <= today.isoformat()

@pytest.mark.asyncio
async def test_analyze_trends_invalid_dates(client: AsyncClient, db_session: AsyncSession):
    # Test with end date before start date
    today = date.today()
    response = await client.get(
        "/api/v1/income-analysis/trends/period",
        params={
            "start_date": today.isoformat(),
            "end_date": (today - timedelta(days=1)).isoformat(),
            "min_confidence": 0.5
        }
    )
    
    assert response.status_code == 400
    assert "No income records found" in response.json()["detail"]

@pytest.mark.asyncio
async def test_analyze_trends_invalid_confidence(client: AsyncClient, db_session: AsyncSession):
    # Test with invalid confidence score
    today = date.today()
    request_data = {
        "start_date": (today - timedelta(days=90)).isoformat(),
        "end_date": today.isoformat(),
        "min_confidence": 1.5  # Invalid confidence score > 1.0
    }
    
    response = await client.post("/api/v1/income-analysis/trends", json=request_data)
    assert response.status_code == 422  # Validation error
